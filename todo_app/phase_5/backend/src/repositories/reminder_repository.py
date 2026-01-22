"""
T096-T097 [P] [US2]: ReminderRepository - Data access layer for TaskReminder

Handles CRUD operations for TaskReminder model:
- create: Create new reminder for a task
- find_unsent_reminders: Query reminders that haven't been sent yet
- mark_as_sent: Update sent_at timestamp after reminder is delivered
- get_by_task_id: Get all reminders for a specific task

Part of TDD Green Phase - implements the data layer for reminder management.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.task import Task
from models.task_reminder import TaskReminder


logger = logging.getLogger(__name__)


class ReminderRepository:
    """
    T096-T097: Repository for TaskReminder data access.

    Responsibilities:
    - CRUD operations for reminders
    - Query reminders that are due to be sent
    - Mark reminders as sent after delivery
    """

    def __init__(self, db_session: AsyncSession):
        """
        Initialize ReminderRepository.

        Args:
            db_session: SQLAlchemy async session
        """
        self.session = db_session

    async def create(
        self,
        task_id: str,
        user_id: str,
        remind_before: str,
        channels: List[str]
    ) -> TaskReminder:
        """
        T096: Create a new reminder for a task.

        Args:
            task_id: Task UUID
            user_id: User UUID
            remind_before: ISO 8601 duration (PT1H, P1D, P1W)
            channels: List of notification channels (email, push)

        Returns:
            TaskReminder: Created reminder object

        Raises:
            Exception: If database operation fails
        """
        reminder = TaskReminder(
            task_id=task_id,
            user_id=user_id,
            remind_before=remind_before,
            channels=channels,
            sent_at=None,
        )

        self.session.add(reminder)
        await self.session.commit()
        await self.session.refresh(reminder)

        logger.info(
            f"Reminder created: reminder_id={reminder.id}, task_id={task_id}, "
            f"remind_before={remind_before}"
        )

        return reminder

    async def find_unsent_reminders(
        self,
        current_time: Optional[datetime] = None
    ) -> List[Tuple[Task, TaskReminder]]:
        """
        T097: Find all reminders that are due to be sent.

        Query logic:
        1. Join Task and TaskReminder
        2. Filter: Task.completed = False (no reminders for completed tasks)
        3. Filter: TaskReminder.sent_at IS NULL (not sent yet)
        4. Filter: Task.due_at - TaskReminder.remind_before <= current_time
           (reminder time has passed)

        Args:
            current_time: Current time (defaults to now)

        Returns:
            List[Tuple[Task, TaskReminder]]: List of (Task, TaskReminder) tuples
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        # Build query
        stmt = (
            select(Task, TaskReminder)
            .join(TaskReminder, Task.id == TaskReminder.task_id)
            .where(
                and_(
                    Task.completed == False,  # Not completed
                    TaskReminder.sent_at.is_(None),  # Not sent yet
                    Task.due_at.isnot(None),  # Has due date
                )
            )
        )

        result = await self.session.execute(stmt)
        all_reminders = result.all()

        # Filter by time (need to parse ISO 8601 duration and calculate)
        due_reminders = []
        for task, reminder in all_reminders:
            # Calculate when reminder should be sent
            remind_time = self._calculate_remind_time(task.due_at, reminder.remind_before)

            if remind_time <= current_time:
                due_reminders.append((task, reminder))

        logger.info(
            f"Found {len(due_reminders)} due reminders out of {len(all_reminders)} unsent"
        )

        return due_reminders

    async def mark_as_sent(
        self,
        reminder_id: int,
        sent_at: Optional[datetime] = None
    ) -> TaskReminder:
        """
        T097: Mark a reminder as sent by updating sent_at timestamp.

        Args:
            reminder_id: Reminder database ID
            sent_at: Timestamp when reminder was sent (defaults to now)

        Returns:
            TaskReminder: Updated reminder object

        Raises:
            ValueError: If reminder not found
        """
        if sent_at is None:
            sent_at = datetime.now(timezone.utc)

        # Get reminder
        stmt = select(TaskReminder).where(TaskReminder.id == reminder_id)
        result = await self.session.execute(stmt)
        reminder = result.scalar_one_or_none()

        if not reminder:
            raise ValueError(f"Reminder {reminder_id} not found")

        # Update sent_at
        reminder.sent_at = sent_at
        await self.session.commit()
        await self.session.refresh(reminder)

        logger.info(f"Reminder marked as sent: reminder_id={reminder_id}, sent_at={sent_at}")

        return reminder

    async def get_by_task_id(
        self,
        task_id: str
    ) -> List[TaskReminder]:
        """
        T097: Get all reminders for a specific task.

        Args:
            task_id: Task UUID

        Returns:
            List[TaskReminder]: List of reminders for the task
        """
        stmt = (
            select(TaskReminder)
            .where(TaskReminder.task_id == task_id)
            .order_by(TaskReminder.created_at.desc())
        )

        result = await self.session.execute(stmt)
        reminders = result.scalars().all()

        return list(reminders)

    async def delete(
        self,
        reminder_id: int
    ) -> bool:
        """
        Delete a reminder by ID.

        Args:
            reminder_id: Reminder database ID

        Returns:
            bool: True if deleted, False if not found
        """
        stmt = select(TaskReminder).where(TaskReminder.id == reminder_id)
        result = await self.session.execute(stmt)
        reminder = result.scalar_one_or_none()

        if not reminder:
            return False

        await self.session.delete(reminder)
        await self.session.commit()

        logger.info(f"Reminder deleted: reminder_id={reminder_id}")

        return True

    def _calculate_remind_time(
        self,
        due_at: datetime,
        remind_before: str
    ) -> datetime:
        """
        Calculate when a reminder should be sent.

        Args:
            due_at: Task due date/time
            remind_before: ISO 8601 duration (PT1H, P1D, P1W)

        Returns:
            datetime: When reminder should be sent

        Examples:
            due_at=2026-01-06 15:00, remind_before="PT1H" → 2026-01-06 14:00
            due_at=2026-01-07 10:00, remind_before="P1D" → 2026-01-06 10:00
        """
        duration = self._parse_iso8601_duration(remind_before)
        remind_time = due_at - duration
        return remind_time

    def _parse_iso8601_duration(self, duration_str: str) -> timedelta:
        """
        Parse ISO 8601 duration to Python timedelta.

        Supported formats:
        - PT1H: 1 hour
        - PT2H: 2 hours
        - P1D: 1 day
        - P1W: 1 week

        Args:
            duration_str: ISO 8601 duration string

        Returns:
            timedelta: Parsed duration

        Raises:
            ValueError: If format is invalid
        """
        if not duration_str:
            raise ValueError("Duration string cannot be empty")

        # Remove 'P' prefix
        if not duration_str.startswith('P'):
            raise ValueError(f"Invalid ISO 8601 duration: {duration_str}")

        duration_str = duration_str[1:]  # Remove 'P'

        # Check if it's a time duration (starts with 'T')
        if duration_str.startswith('T'):
            # Time duration (PT1H, PT2H, etc.)
            duration_str = duration_str[1:]  # Remove 'T'

            # Parse hours
            if duration_str.endswith('H'):
                hours = int(duration_str[:-1])
                return timedelta(hours=hours)
            else:
                raise ValueError(f"Unsupported time duration: PT{duration_str}")

        else:
            # Date duration (P1D, P1W, etc.)
            if duration_str.endswith('D'):
                days = int(duration_str[:-1])
                return timedelta(days=days)
            elif duration_str.endswith('W'):
                weeks = int(duration_str[:-1])
                return timedelta(weeks=weeks)
            else:
                raise ValueError(f"Unsupported date duration: P{duration_str}")


# ============================================================================
# Factory Function
# ============================================================================

def create_reminder_repository(db_session: AsyncSession) -> ReminderRepository:
    """
    Factory function to create ReminderRepository instance.

    Args:
        db_session: SQLAlchemy async session

    Returns:
        ReminderRepository: Configured instance
    """
    return ReminderRepository(db_session)
