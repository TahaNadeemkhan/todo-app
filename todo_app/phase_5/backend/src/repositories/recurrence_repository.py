"""
T074-T075: RecurrenceRepository - Database operations for task_recurrences table

Manages CRUD operations for recurrence patterns linked to tasks.
"""

import logging
from typing import Optional
from datetime import datetime
from uuid import uuid4

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.task_recurrence import TaskRecurrence


logger = logging.getLogger(__name__)


class RecurrenceRepository:
    """
    T074: Repository for task_recurrences table operations.

    Responsibilities:
    - T075: create_recurrence, get_by_task_id, update_next_due_at methods
    - Update recurrence status (active/inactive)
    - Manage recurrence lifecycle
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize RecurrenceRepository.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create_recurrence(
        self,
        task_id: str,
        pattern: str,
        interval: int = 1,
        days_of_week: Optional[list[int]] = None,
        day_of_month: Optional[int] = None,
        next_due_at: Optional[datetime] = None,
        active: bool = True
    ) -> TaskRecurrence:
        """
        T075: Create a new recurrence record.

        Args:
            task_id: Task UUID
            pattern: Recurrence pattern (daily/weekly/monthly)
            interval: Recurrence interval
            days_of_week: Days of week for weekly recurrence (0=Monday)
            day_of_month: Day of month for monthly recurrence (1-31)
            next_due_at: Next scheduled occurrence date
            active: Whether recurrence is active (default: True)

        Returns:
            TaskRecurrence: Created recurrence object

        Raises:
            Exception: If database operation fails
        """
        recurrence = TaskRecurrence(
            id=str(uuid4()),
            task_id=task_id,
            pattern=pattern,
            interval=interval,
            days_of_week=days_of_week,
            day_of_month=day_of_month,
            next_due_at=next_due_at,
            active=active
        )

        self.session.add(recurrence)
        await self.session.commit()
        await self.session.refresh(recurrence)

        logger.info(
            f"Recurrence created: id={recurrence.id}, task_id={task_id}, "
            f"pattern={pattern}, interval={interval}"
        )

        return recurrence

    async def get_by_task_id(
        self,
        task_id: str
    ) -> Optional[TaskRecurrence]:
        """
        T075: Get recurrence by task ID.

        Args:
            task_id: Task UUID

        Returns:
            TaskRecurrence object or None if not found
        """
        query = select(TaskRecurrence).where(TaskRecurrence.task_id == task_id)
        result = await self.session.execute(query)
        recurrence = result.scalar_one_or_none()

        if recurrence:
            logger.debug(f"Recurrence retrieved: task_id={task_id}, pattern={recurrence.pattern}")
        else:
            logger.debug(f"No recurrence found for task_id={task_id}")

        return recurrence

    async def get_by_id(
        self,
        recurrence_id: str
    ) -> Optional[TaskRecurrence]:
        """
        Get recurrence by recurrence ID.

        Args:
            recurrence_id: Recurrence UUID

        Returns:
            TaskRecurrence object or None if not found
        """
        query = select(TaskRecurrence).where(TaskRecurrence.id == recurrence_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_next_due_at(
        self,
        recurrence_id: str,
        next_due_at: datetime
    ) -> TaskRecurrence:
        """
        T075: Update the next_due_at field for a recurrence.

        This is called after creating the next occurrence to schedule
        the following one.

        Args:
            recurrence_id: Recurrence UUID
            next_due_at: Next scheduled occurrence date

        Returns:
            Updated TaskRecurrence object

        Raises:
            ValueError: If recurrence not found
        """
        recurrence = await self.get_by_id(recurrence_id)
        if not recurrence:
            raise ValueError(f"Recurrence {recurrence_id} not found")

        recurrence.next_due_at = next_due_at

        await self.session.commit()
        await self.session.refresh(recurrence)

        logger.info(
            f"Recurrence next_due_at updated: id={recurrence_id}, "
            f"next_due_at={next_due_at}"
        )

        return recurrence

    async def deactivate_recurrence(
        self,
        recurrence_id: str
    ) -> TaskRecurrence:
        """
        Deactivate a recurrence (stop generating next occurrences).

        Args:
            recurrence_id: Recurrence UUID

        Returns:
            Updated TaskRecurrence object

        Raises:
            ValueError: If recurrence not found
        """
        recurrence = await self.get_by_id(recurrence_id)
        if not recurrence:
            raise ValueError(f"Recurrence {recurrence_id} not found")

        recurrence.active = False

        await self.session.commit()
        await self.session.refresh(recurrence)

        logger.info(f"Recurrence deactivated: id={recurrence_id}")

        return recurrence

    async def delete_recurrence(
        self,
        recurrence_id: str
    ) -> bool:
        """
        Delete a recurrence record.

        Args:
            recurrence_id: Recurrence UUID

        Returns:
            True if deleted, False if not found
        """
        recurrence = await self.get_by_id(recurrence_id)
        if not recurrence:
            return False

        await self.session.delete(recurrence)
        await self.session.commit()

        logger.info(f"Recurrence deleted: id={recurrence_id}")

        return True


# ============================================================================
# Factory Function
# ============================================================================

def create_recurrence_repository(session: AsyncSession) -> RecurrenceRepository:
    """
    Factory function to create RecurrenceRepository instance.

    Args:
        session: SQLAlchemy async session

    Returns:
        RecurrenceRepository: Configured instance
    """
    return RecurrenceRepository(session)
