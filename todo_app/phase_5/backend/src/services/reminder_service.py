"""
ReminderService - Business logic for creating and managing reminders

Handles:
- Creating reminders with validation
- Validating ISO 8601 duration formats
- Validating notification channels
- Retrieving reminders for tasks

Part of TDD Green Phase for User Story 2.
"""

import logging
from datetime import timedelta
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from models.task_reminder import TaskReminder
from repositories.reminder_repository import ReminderRepository


logger = logging.getLogger(__name__)


# Valid notification channels
VALID_CHANNELS = {"email", "push"}


class ReminderService:
    """
    Business logic layer for reminder management.

    Responsibilities:
    - Create reminders with validation
    - Validate remind_before ISO 8601 duration format
    - Validate notification channels
    - Get reminders for a task
    """

    def __init__(self, db_session: AsyncSession):
        """
        Initialize ReminderService.

        Args:
            db_session: SQLAlchemy async session
        """
        self.repository = ReminderRepository(db_session)

    async def create_reminder(
        self,
        task_id: str,
        user_id: str,
        remind_before: str,
        channels: List[str]
    ) -> TaskReminder:
        """
        Create a reminder for a task with validation.

        Args:
            task_id: Task UUID
            user_id: User UUID
            remind_before: ISO 8601 duration (PT1H, P1D, P1W)
            channels: List of notification channels (email, push)

        Returns:
            TaskReminder: Created reminder object

        Raises:
            ValueError: If validation fails
        """
        # Validate inputs
        self.validate_remind_before(remind_before)
        self.validate_channels(channels)

        # Deduplicate channels
        unique_channels = list(set(channels))

        # Create reminder via repository
        reminder = await self.repository.create(
            task_id=task_id,
            user_id=user_id,
            remind_before=remind_before,
            channels=unique_channels
        )

        logger.info(
            f"Reminder created: reminder_id={reminder.id}, task_id={task_id}, "
            f"remind_before={remind_before}"
        )

        return reminder

    async def get_reminders_for_task(
        self,
        task_id: str
    ) -> List[TaskReminder]:
        """
        Get all reminders for a specific task.

        Args:
            task_id: Task UUID

        Returns:
            List[TaskReminder]: List of reminders
        """
        return await self.repository.get_by_task_id(task_id)

    def validate_remind_before(self, remind_before: str) -> None:
        """
        Validate remind_before is a valid ISO 8601 duration.

        Supported formats:
        - PT1H, PT2H, etc. (hours)
        - P1D, P2D, etc. (days)
        - P1W, P2W, etc. (weeks)

        Args:
            remind_before: ISO 8601 duration string

        Raises:
            ValueError: If format is invalid or empty
        """
        if not remind_before:
            raise ValueError("remind_before cannot be empty")

        # Try to parse the duration
        try:
            self.validate_iso8601_duration(remind_before)
        except ValueError as e:
            raise ValueError(f"Invalid ISO 8601 duration format: {remind_before}") from e

    def validate_iso8601_duration(self, duration_str: str) -> None:
        """
        Validate ISO 8601 duration format.

        Args:
            duration_str: ISO 8601 duration (PT1H, P1D, P1W)

        Raises:
            ValueError: If format is invalid
        """
        if not duration_str:
            raise ValueError("Duration cannot be empty")

        if not duration_str.startswith('P'):
            raise ValueError(f"Invalid ISO 8601 duration (must start with 'P'): {duration_str}")

        # Remove 'P' prefix
        duration_body = duration_str[1:]

        # Time duration (PT1H, PT2H)
        if duration_body.startswith('T'):
            time_part = duration_body[1:]  # Remove 'T'
            if not time_part.endswith('H'):
                raise ValueError(f"Invalid time duration (must end with 'H'): {duration_str}")
            try:
                hours = int(time_part[:-1])
                if hours <= 0:
                    raise ValueError(f"Duration must be positive: {duration_str}")
            except ValueError:
                raise ValueError(f"Invalid hour value in duration: {duration_str}")

        # Date duration (P1D, P1W)
        else:
            if duration_body.endswith('D'):
                try:
                    days = int(duration_body[:-1])
                    if days <= 0:
                        raise ValueError(f"Duration must be positive: {duration_str}")
                except ValueError:
                    raise ValueError(f"Invalid day value in duration: {duration_str}")
            elif duration_body.endswith('W'):
                try:
                    weeks = int(duration_body[:-1])
                    if weeks <= 0:
                        raise ValueError(f"Duration must be positive: {duration_str}")
                except ValueError:
                    raise ValueError(f"Invalid week value in duration: {duration_str}")
            else:
                raise ValueError(
                    f"Invalid date duration (must end with 'D' or 'W'): {duration_str}"
                )

    def validate_channels(self, channels: List[str]) -> None:
        """
        Validate notification channels.

        Args:
            channels: List of channel names

        Raises:
            ValueError: If channels are invalid or empty
        """
        if not channels:
            raise ValueError("At least one channel required")

        for channel in channels:
            if channel not in VALID_CHANNELS:
                raise ValueError(
                    f"Invalid channel: {channel}. "
                    f"Valid channels: {', '.join(VALID_CHANNELS)}"
                )


# ============================================================================
# Factory Function
# ============================================================================

def create_reminder_service(db_session: AsyncSession) -> ReminderService:
    """
    Factory function to create ReminderService instance.

    Args:
        db_session: SQLAlchemy async session

    Returns:
        ReminderService: Configured instance
    """
    return ReminderService(db_session)
