"""
T042-T045: TaskService - Business Logic Layer with Event Publishing

Integrates TaskRepository (database operations) with KafkaService (event publishing)
to implement event-driven architecture for all task CRUD operations.

Responsibilities:
- T042: Create task + publish task.created event
- T043: Update task + publish task.updated event
- T044: Complete task + publish task.completed event
- T045: Delete task + publish task.deleted event
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from repositories.task_repository import TaskRepository
from services.kafka_service import KafkaService
from services.recurrence_service import RecurrenceService
from services.reminder_service import ReminderService
from schemas.event_schemas import (
    TaskCreatedEvent,
    TaskCreatedData,
    TaskUpdatedEvent,
    TaskUpdatedData,
    TaskCompletedEvent,
    TaskCompletedData,
    TaskDeletedEvent,
    TaskDeletedData,
)
from models.task import Task


logger = logging.getLogger(__name__)


class TaskService:
    """
    Business logic layer for task operations with event-driven architecture.

    Combines TaskRepository (data persistence) with KafkaService (event publishing)
    and RecurrenceService (recurrence management) to ensure all state changes
    are broadcasted to microservices.
    """

    def __init__(
        self,
        db_session: AsyncSession,
        kafka_service: KafkaService
    ):
        """
        Initialize TaskService.

        Args:
            db_session: SQLAlchemy async session
            kafka_service: Kafka event publishing service
        """
        self.repository = TaskRepository(db_session)
        self.kafka = kafka_service
        self.recurrence_service = RecurrenceService(db_session)
        self.reminder_service = ReminderService(db_session)

    async def create_task(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        tags: Optional[List[str]] = None,
        due_at: Optional[datetime] = None,
        has_recurrence: bool = False,
        recurrence_pattern: Optional[str] = None,
        recurrence_interval: Optional[int] = None,
        recurrence_days_of_week: Optional[List[int]] = None,
        recurrence_day_of_month: Optional[int] = None,
        reminders: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Task:
        """
        T042: Create a new task and publish task.created event.
        T102: Updated to handle reminder creation.

        Args:
            user_id: User UUID who owns the task
            title: Task title (required)
            description: Task description (optional)
            priority: Task priority (high/medium/low)
            tags: List of task tags (optional)
            due_at: Task due date/time (optional)
            has_recurrence: Whether task recurs (optional)
            recurrence_pattern: Recurrence pattern (daily/weekly/monthly)
            recurrence_interval: Recurrence interval (e.g., every N days)
            recurrence_days_of_week: Days of week for weekly recurrence
            recurrence_day_of_month: Day of month for monthly recurrence
            reminders: List of reminder configs [{"remind_before": "PT1H", "channels": ["email"]}]
            **kwargs: Additional fields (backward compatibility)

        Returns:
            Task: Created task object

        Raises:
            Exception: If database operation or event publishing fails
        """
        # Generate UUID for task
        task_id = str(uuid4())

        # Create task in database via repository
        task = Task(
            id=task_id,
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            tags=tags or [],
            due_at=due_at,
            completed=False,
            # Legacy fields for backward compatibility
            notify_email=kwargs.get("notify_email"),
            notifications_enabled=kwargs.get("notifications_enabled", False),
        )

        self.repository.session.add(task)
        await self.repository.session.commit()
        await self.repository.session.refresh(task)

        logger.info(f"Task created in database: task_id={task_id}, user_id={user_id}")

        # T080: Create recurrence if requested
        recurrence_id = None
        if has_recurrence and recurrence_pattern:
            try:
                recurrence = await self.recurrence_service.create_recurrence(
                    task_id=task_id,
                    pattern=recurrence_pattern,
                    interval=recurrence_interval or 1,
                    days_of_week=recurrence_days_of_week,
                    day_of_month=recurrence_day_of_month,
                    initial_due_at=due_at
                )
                recurrence_id = recurrence.id

                # Update task with recurrence_id
                task.recurrence_id = recurrence_id
                await self.repository.session.commit()
                await self.repository.session.refresh(task)

                logger.info(
                    f"Recurrence created for task: task_id={task_id}, "
                    f"pattern={recurrence_pattern}, recurrence_id={recurrence_id}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to create recurrence: task_id={task_id}, error={str(e)}"
                )
                # Continue without recurrence (task still created)

        # T102: Create reminders if provided
        if reminders:
            for reminder_config in reminders:
                try:
                    await self.reminder_service.create_reminder(
                        task_id=task_id,
                        user_id=user_id,
                        remind_before=reminder_config["remind_before"],
                        channels=reminder_config["channels"]
                    )
                    logger.info(
                        f"Reminder created for task: task_id={task_id}, "
                        f"remind_before={reminder_config['remind_before']}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to create reminder: task_id={task_id}, error={str(e)}"
                    )
                    # Continue without this reminder (task still created)

        # T042: Publish task.created event to Kafka
        try:
            event_data = {
                "task_id": task.id,
                "user_id": task.user_id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "tags": task.tags,
                "due_at": task.due_at.isoformat() + "Z" if task.due_at else None,
                "has_recurrence": has_recurrence,
                "recurrence_pattern": recurrence_pattern,
                "recurrence_interval": recurrence_interval,
                "recurrence_days_of_week": recurrence_days_of_week,
                "recurrence_day_of_month": recurrence_day_of_month,
                "created_at": task.created_at.isoformat().replace("+00:00", "Z"),
            }

            await self.kafka.publish_event(
                topic="task-events",
                event_type="task.created.v1",
                data=event_data
            )

            logger.info(f"task.created event published: task_id={task_id}")

        except Exception as e:
            logger.error(
                f"Failed to publish task.created event: task_id={task_id}, error={str(e)}"
            )
            # Event publishing failure should not fail the operation
            # The event will be retried or buffered according to KafkaService config

        return task

    async def update_task(
        self,
        task_id: str,
        user_id: str,
        changes: Dict[str, Any]
    ) -> Task:
        """
        T043: Update an existing task and publish task.updated event.

        Args:
            task_id: Task UUID to update
            user_id: User UUID (for authorization)
            changes: Dictionary of fields to update

        Returns:
            Task: Updated task object

        Raises:
            ValueError: If task not found or user not authorized
            Exception: If database operation fails
        """
        # Get task before update (for change tracking)
        original_task = await self.repository.get_by_id(task_id)
        if not original_task:
            raise ValueError(f"Task {task_id} not found")

        if original_task.user_id != user_id:
            raise ValueError(f"Task {task_id} does not belong to user {user_id}")

        # Track changes for event
        tracked_changes = {}
        for field, new_value in changes.items():
            if hasattr(original_task, field):
                old_value = getattr(original_task, field)
                if old_value != new_value:
                    tracked_changes[field] = {"old": old_value, "new": new_value}

        # Update task in database
        updated_task = await self.repository.update(task_id, user_id, **changes)

        logger.info(
            f"Task updated in database: task_id={task_id}, "
            f"changes={list(tracked_changes.keys())}"
        )

        # T043: Publish task.updated event to Kafka
        if tracked_changes:  # Only publish if there were actual changes
            try:
                event_data = {
                    "task_id": task_id,
                    "user_id": user_id,
                    "changes": tracked_changes,
                    "updated_at": updated_task.updated_at.isoformat().replace("+00:00", "Z"),
                }

                await self.kafka.publish_event(
                    topic="task-events",
                    event_type="task.updated.v1",
                    data=event_data
                )

                logger.info(f"task.updated event published: task_id={task_id}")

            except Exception as e:
                logger.error(
                    f"Failed to publish task.updated event: task_id={task_id}, error={str(e)}"
                )

        return updated_task

    async def complete_task(
        self,
        task_id: str,
        user_id: str
    ) -> Task:
        """
        T044: Mark task as completed and publish task.completed event.

        Critical: This event triggers the Recurring Task Service to create
        the next occurrence if the task has recurrence.

        Args:
            task_id: Task UUID to complete
            user_id: User UUID (for authorization)

        Returns:
            Task: Completed task object

        Raises:
            ValueError: If task not found or user not authorized
            Exception: If database operation fails
        """
        # Get task before completion (need recurrence info for event)
        task = await self.repository.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        if task.user_id != user_id:
            raise ValueError(f"Task {task_id} does not belong to user {user_id}")

        # Mark as completed
        completed_at = datetime.now(timezone.utc)
        updated_task = await self.repository.update(
            task_id,
            user_id,
            completed=True,
            completed_at=completed_at
        )

        logger.info(f"Task marked as completed: task_id={task_id}")

        # T044: Publish task.completed event to Kafka
        # CRITICAL: Include recurrence info for Recurring Task Service
        try:
            # TODO: Fetch recurrence info from task_recurrences table (US1)
            # For now, assume has_recurrence=False
            has_recurrence = False
            recurrence_pattern = None
            recurrence_interval = None
            recurrence_days_of_week = None
            recurrence_day_of_month = None

            event_data = {
                "task_id": task_id,
                "user_id": user_id,
                "completed_at": completed_at.isoformat().replace("+00:00", "Z"),
                "has_recurrence": has_recurrence,
                "recurrence_pattern": recurrence_pattern,
                "recurrence_interval": recurrence_interval,
                "recurrence_days_of_week": recurrence_days_of_week,
                "recurrence_day_of_month": recurrence_day_of_month,
            }

            await self.kafka.publish_event(
                topic="task-events",
                event_type="task.completed.v1",
                data=event_data
            )

            logger.info(
                f"task.completed event published: task_id={task_id}, "
                f"has_recurrence={has_recurrence}"
            )

        except Exception as e:
            logger.error(
                f"Failed to publish task.completed event: task_id={task_id}, error={str(e)}"
            )

        return updated_task

    async def delete_task(
        self,
        task_id: str,
        user_id: str
    ) -> bool:
        """
        T045: Delete a task and publish task.deleted event.

        Args:
            task_id: Task UUID to delete
            user_id: User UUID (for authorization)

        Returns:
            bool: True if task was deleted, False if not found

        Raises:
            ValueError: If user not authorized
            Exception: If database operation fails
        """
        # Verify task exists and belongs to user
        task = await self.repository.get_by_id(task_id)
        if not task:
            return False

        if task.user_id != user_id:
            raise ValueError(f"Task {task_id} does not belong to user {user_id}")

        # Delete from database
        deleted = await self.repository.delete(task_id, user_id)

        if deleted:
            logger.info(f"Task deleted from database: task_id={task_id}")

            # T045: Publish task.deleted event to Kafka
            try:
                event_data = {
                    "task_id": task_id,
                    "user_id": user_id,
                    "deleted_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                }

                await self.kafka.publish_event(
                    topic="task-events",
                    event_type="task.deleted.v1",
                    data=event_data
                )

                logger.info(f"task.deleted event published: task_id={task_id}")

            except Exception as e:
                logger.error(
                    f"Failed to publish task.deleted event: task_id={task_id}, error={str(e)}"
                )

        return deleted

    async def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID (no event published).

        Args:
            task_id: Task UUID

        Returns:
            Optional[Task]: Task object or None if not found
        """
        return await self.repository.get_by_id(task_id)

    async def list_user_tasks(
        self,
        user_id: str,
        completed: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Task]:
        """
        List tasks for a user with optional filtering (no event published).

        Args:
            user_id: User UUID
            completed: Filter by completion status (None = all tasks)
            limit: Maximum tasks to return (pagination)
            offset: Number of tasks to skip (pagination)

        Returns:
            List[Task]: List of task objects
        """
        return await self.repository.get_by_user(
            user_id=user_id,
            completed=completed,
            limit=limit,
            offset=offset
        )


# ============================================================================
# Factory Function
# ============================================================================

def create_task_service(
    db_session: AsyncSession,
    kafka_service: KafkaService
) -> TaskService:
    """
    Factory function to create TaskService instance.

    Args:
        db_session: SQLAlchemy async session
        kafka_service: Kafka event publishing service

    Returns:
        TaskService: Configured instance
    """
    return TaskService(db_session=db_session, kafka_service=kafka_service)
