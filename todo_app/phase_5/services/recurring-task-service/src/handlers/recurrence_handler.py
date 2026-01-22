"""
T114-T116: RecurrenceHandler - Business logic for creating next task occurrences

Consumes task.completed events and auto-generates next occurrence for recurring tasks.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import calendar

from repositories.event_log_repository import EventLogRepository


logger = logging.getLogger(__name__)


class RecurrenceCalculator:
    """
    Calculate next occurrence dates for recurring tasks.

    Reused from backend implementation - lightweight calculation logic.
    """

    def calculate_next_daily(
        self,
        current_date: datetime,
        interval: int = 1
    ) -> datetime:
        """
        Calculate next daily occurrence.

        Args:
            current_date: Current task due date
            interval: Number of days between occurrences (e.g., 2 = every 2 days)

        Returns:
            Next occurrence datetime
        """
        return current_date + timedelta(days=interval)

    def calculate_next_weekly(
        self,
        current_date: datetime,
        interval: int = 1,
        days_of_week: Optional[list[int]] = None
    ) -> datetime:
        """
        Calculate next weekly occurrence.

        Args:
            current_date: Current task due date
            interval: Number of weeks between occurrences
            days_of_week: List of weekdays (0=Monday, 6=Sunday)

        Returns:
            Next occurrence datetime
        """
        if not days_of_week:
            # Default to same day of week, N weeks later
            return current_date + timedelta(weeks=interval)

        # Find next occurrence from days_of_week
        current_weekday = current_date.weekday()
        days_ahead = None

        # Sort days_of_week to find next occurrence
        sorted_days = sorted(days_of_week)

        for day in sorted_days:
            if day > current_weekday:
                days_ahead = day - current_weekday
                break

        # If no future day this week, wrap to first day next week
        if days_ahead is None:
            days_ahead = (7 - current_weekday) + sorted_days[0]

        return current_date + timedelta(days=days_ahead)

    def calculate_next_monthly(
        self,
        current_date: datetime,
        interval: int = 1,
        day_of_month: int = 1
    ) -> datetime:
        """
        Calculate next monthly occurrence with edge case handling.

        Handles edge case: January 31 → February 28/29 (last day of month).

        Args:
            current_date: Current task due date
            interval: Number of months between occurrences
            day_of_month: Target day of month (1-31)

        Returns:
            Next occurrence datetime
        """
        # Calculate target month/year
        next_month = current_date.month + interval
        next_year = current_date.year

        while next_month > 12:
            next_month -= 12
            next_year += 1

        # Handle edge case: day_of_month > days in next month
        days_in_next_month = calendar.monthrange(next_year, next_month)[1]
        actual_day = min(day_of_month, days_in_next_month)

        return current_date.replace(
            year=next_year,
            month=next_month,
            day=actual_day
        )

    def calculate_next_occurrence(
        self,
        current_date: datetime,
        pattern: str,
        interval: int,
        days_of_week: Optional[list[int]] = None,
        day_of_month: Optional[int] = None
    ) -> datetime:
        """
        Calculate next occurrence based on recurrence pattern.

        Args:
            current_date: Current task due date
            pattern: Recurrence pattern (daily/weekly/monthly)
            interval: Recurrence interval
            days_of_week: Days of week for weekly recurrence
            day_of_month: Day of month for monthly recurrence

        Returns:
            Next occurrence datetime

        Raises:
            ValueError: If pattern is invalid
        """
        if pattern == "daily":
            return self.calculate_next_daily(current_date, interval)
        elif pattern == "weekly":
            return self.calculate_next_weekly(current_date, interval, days_of_week)
        elif pattern == "monthly":
            return self.calculate_next_monthly(
                current_date,
                interval,
                day_of_month or current_date.day
            )
        else:
            raise ValueError(f"Invalid recurrence pattern: {pattern}")


class RecurrenceHandler:
    """
    T114-T116: Handler for task.completed events to create next occurrences.

    Responsibilities:
    - T115: Parse task.completed events and calculate next due date
    - T116: Create next task via backend API (Dapr service invocation)
    - Idempotency: Skip duplicate events using EventLogRepository
    """

    def __init__(
        self,
        task_api_client: Any,
        event_log_repo: EventLogRepository
    ):
        """
        Initialize RecurrenceHandler.

        Args:
            task_api_client: HTTP client for calling backend API
            event_log_repo: Repository for idempotency tracking
        """
        self.api_client = task_api_client
        self.event_log_repo = event_log_repo
        self.calculator = RecurrenceCalculator()

    async def handle_task_completed(self, event: Dict[str, Any]) -> None:
        """
        T115: Handle task.completed event and create next occurrence.

        Args:
            event: task.completed event payload
                {
                    "event_id": "uuid",
                    "event_type": "task.completed.v1",
                    "data": {
                        "task_id": "uuid",
                        "user_id": "uuid",
                        "completed_at": "2026-01-06T10:00:00Z",
                        "has_recurrence": true,
                        "recurrence_pattern": "daily",
                        "recurrence_interval": 1,
                        "original_task": {
                            "title": "Task Title",
                            "due_at": "2026-01-06T10:00:00Z",
                            ...
                        }
                    }
                }

        Raises:
            Exception: If API call fails (propagated for retry mechanism)
        """
        event_id = event.get("event_id")
        event_data = event.get("data", {})

        # Idempotency check: Skip if event already processed
        if await self.event_log_repo.has_processed(event_id):
            logger.info(
                f"Skipping duplicate event: event_id={event_id}"
            )
            return

        # Check if task has recurrence
        has_recurrence = event_data.get("has_recurrence", False)
        if not has_recurrence:
            logger.debug(
                f"Task has no recurrence, skipping: task_id={event_data.get('task_id')}"
            )
            return

        # Extract recurrence configuration
        recurrence_pattern = event_data.get("recurrence_pattern")
        recurrence_interval = event_data.get("recurrence_interval", 1)
        recurrence_days_of_week = event_data.get("recurrence_days_of_week")
        recurrence_day_of_month = event_data.get("recurrence_day_of_month")

        # Extract original task metadata
        original_task = event_data.get("original_task", {})
        original_due_at_str = original_task.get("due_at")

        if not original_due_at_str:
            logger.error(
                f"Missing due_at in original_task: event_id={event_id}"
            )
            return

        # Parse due date
        original_due_at = datetime.fromisoformat(
            original_due_at_str.replace("Z", "+00:00")
        )

        # Calculate next occurrence date
        try:
            next_due_at = self.calculator.calculate_next_occurrence(
                current_date=original_due_at,
                pattern=recurrence_pattern,
                interval=recurrence_interval,
                days_of_week=recurrence_days_of_week,
                day_of_month=recurrence_day_of_month
            )

            logger.info(
                f"Calculated next occurrence: task_id={event_data.get('task_id')}, "
                f"pattern={recurrence_pattern}, next_due_at={next_due_at.isoformat()}"
            )

        except ValueError as e:
            logger.error(
                f"Failed to calculate next occurrence: {str(e)}, event_id={event_id}"
            )
            return

        # Create next task occurrence
        await self.create_next_occurrence(
            user_id=event_data.get("user_id"),
            original_task=original_task,
            next_due_at=next_due_at,
            recurrence_pattern=recurrence_pattern,
            recurrence_interval=recurrence_interval,
            recurrence_days_of_week=recurrence_days_of_week,
            recurrence_day_of_month=recurrence_day_of_month
        )

        # Mark event as processed for idempotency
        await self.event_log_repo.mark_as_processed(
            event_id=event_id,
            event_type=event.get("event_type"),
            processed_at=datetime.now(timezone.utc)
        )

        logger.info(
            f"Next occurrence created successfully: original_task_id={event_data.get('task_id')}, "
            f"next_due_at={next_due_at.isoformat()}"
        )

    async def create_next_occurrence(
        self,
        user_id: str,
        original_task: Dict[str, Any],
        next_due_at: datetime,
        recurrence_pattern: str,
        recurrence_interval: int,
        recurrence_days_of_week: Optional[list[int]] = None,
        recurrence_day_of_month: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        T116: Create next task occurrence via backend API.

        Uses Dapr service invocation to call backend API: POST /{user_id}/tasks

        Args:
            user_id: User UUID
            original_task: Original task metadata (title, description, etc.)
            next_due_at: Calculated next due date/time
            recurrence_pattern: Recurrence pattern (daily/weekly/monthly)
            recurrence_interval: Recurrence interval
            recurrence_days_of_week: Days of week for weekly recurrence
            recurrence_day_of_month: Day of month for monthly recurrence

        Returns:
            Created task response from API

        Raises:
            Exception: If API call fails (propagated for retry)
        """
        # Build task creation payload
        task_payload = {
            "user_id": user_id,
            "title": original_task.get("title"),
            "description": original_task.get("description"),
            "priority": original_task.get("priority", "medium"),
            "tags": original_task.get("tags", []),
            "due_at": next_due_at.isoformat().replace("+00:00", "Z"),
            "has_recurrence": True,
            "recurrence_pattern": recurrence_pattern,
            "recurrence_interval": recurrence_interval,
        }

        # Add optional recurrence fields
        if recurrence_days_of_week:
            task_payload["recurrence_days_of_week"] = recurrence_days_of_week
        if recurrence_day_of_month:
            task_payload["recurrence_day_of_month"] = recurrence_day_of_month

        # Call backend API via Dapr service invocation
        try:
            created_task = await self.api_client.create_task(**task_payload)

            logger.info(
                f"Task created via API: new_task_id={created_task.get('id')}, "
                f"user_id={user_id}, due_at={next_due_at.isoformat()}"
            )

            return created_task

        except Exception as e:
            logger.error(
                f"Failed to create task via API: user_id={user_id}, error={str(e)}"
            )
            # Propagate exception for retry mechanism
            raise
