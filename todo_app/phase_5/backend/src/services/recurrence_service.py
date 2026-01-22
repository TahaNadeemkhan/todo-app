"""
T081: RecurrenceService - Business logic for managing task recurrence

Handles recurrence creation, updates, and deactivation.
"""

import logging
from typing import Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from repositories.recurrence_repository import RecurrenceRepository
from services.calculators.recurrence_calculator import RecurrenceCalculator
from models.task_recurrence import TaskRecurrence


logger = logging.getLogger(__name__)


class RecurrenceService:
    """
    Business logic layer for task recurrence management.

    Responsibilities:
    - Create recurrence patterns for tasks
    - Calculate next occurrence dates
    - Stop/deactivate recurrence (T081)
    - Update next_due_at after task completion
    """

    def __init__(self, db_session: AsyncSession):
        """
        Initialize RecurrenceService.

        Args:
            db_session: SQLAlchemy async session
        """
        self.repository = RecurrenceRepository(db_session)
        self.calculator = RecurrenceCalculator()

    async def create_recurrence(
        self,
        task_id: str,
        pattern: str,
        interval: int = 1,
        days_of_week: Optional[list[int]] = None,
        day_of_month: Optional[int] = None,
        initial_due_at: Optional[datetime] = None
    ) -> TaskRecurrence:
        """
        Create a recurrence pattern for a task.

        Args:
            task_id: Task UUID
            pattern: Recurrence pattern (daily/weekly/monthly)
            interval: Recurrence interval
            days_of_week: Days of week for weekly recurrence
            day_of_month: Day of month for monthly recurrence
            initial_due_at: Initial task due date (used to calculate next_due_at)

        Returns:
            TaskRecurrence: Created recurrence object

        Raises:
            ValueError: If required parameters missing for pattern
        """
        # Calculate next_due_at if initial_due_at provided
        next_due_at = None
        if initial_due_at:
            next_due_at = self.calculator.calculate_next_occurrence(
                current_date=initial_due_at,
                pattern=pattern,
                interval=interval,
                days_of_week=days_of_week,
                day_of_month=day_of_month
            )

        recurrence = await self.repository.create_recurrence(
            task_id=task_id,
            pattern=pattern,
            interval=interval,
            days_of_week=days_of_week,
            day_of_month=day_of_month,
            next_due_at=next_due_at,
            active=True
        )

        logger.info(
            f"Recurrence created: task_id={task_id}, pattern={pattern}, "
            f"next_due_at={next_due_at}"
        )

        return recurrence

    async def get_recurrence(
        self,
        task_id: str
    ) -> Optional[TaskRecurrence]:
        """
        Get recurrence for a task.

        Args:
            task_id: Task UUID

        Returns:
            TaskRecurrence or None if task has no recurrence
        """
        return await self.repository.get_by_task_id(task_id)

    async def stop_recurrence(
        self,
        task_id: str,
        user_id: str
    ) -> TaskRecurrence:
        """
        T081: Stop recurrence for a task (deactivate).

        This prevents future occurrences from being generated when
        the current task is completed.

        Args:
            task_id: Task UUID
            user_id: User UUID (for authorization)

        Returns:
            Updated TaskRecurrence object (active=False)

        Raises:
            ValueError: If recurrence not found
        """
        recurrence = await self.repository.get_by_task_id(task_id)
        if not recurrence:
            raise ValueError(f"No recurrence found for task {task_id}")

        # Deactivate recurrence
        updated_recurrence = await self.repository.deactivate_recurrence(recurrence.id)

        logger.info(
            f"Recurrence stopped: task_id={task_id}, recurrence_id={recurrence.id}"
        )

        return updated_recurrence

    async def update_next_due_at(
        self,
        task_id: str,
        current_due_at: datetime
    ) -> TaskRecurrence:
        """
        Update next_due_at after task completion.

        Called by Recurring Task Service after creating next occurrence.

        Args:
            task_id: Task UUID
            current_due_at: Current task's due date (just completed)

        Returns:
            Updated TaskRecurrence object

        Raises:
            ValueError: If recurrence not found
        """
        recurrence = await self.repository.get_by_task_id(task_id)
        if not recurrence:
            raise ValueError(f"No recurrence found for task {task_id}")

        # Calculate next occurrence date
        next_due_at = self.calculator.calculate_next_occurrence(
            current_date=current_due_at,
            pattern=recurrence.pattern,
            interval=recurrence.interval,
            days_of_week=recurrence.days_of_week,
            day_of_month=recurrence.day_of_month
        )

        # Update next_due_at
        updated_recurrence = await self.repository.update_next_due_at(
            recurrence_id=recurrence.id,
            next_due_at=next_due_at
        )

        logger.info(
            f"Next due date updated: task_id={task_id}, next_due_at={next_due_at}"
        )

        return updated_recurrence


# ============================================================================
# Factory Function
# ============================================================================

def create_recurrence_service(db_session: AsyncSession) -> RecurrenceService:
    """
    Factory function to create RecurrenceService instance.

    Args:
        db_session: SQLAlchemy async session

    Returns:
        RecurrenceService: Configured instance
    """
    return RecurrenceService(db_session)
