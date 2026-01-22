"""
T076-T079: RecurrenceCalculator - Calculate next occurrence dates for recurring tasks

Implements date calculation logic for daily, weekly, and monthly recurrence patterns.
Handles edge cases like February 31st → February 28/29.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
import calendar


logger = logging.getLogger(__name__)


class RecurrenceCalculator:
    """
    Calculator for recurring task next occurrence dates.

    Supports:
    - T077: Daily recurrence with interval
    - T078: Weekly recurrence with days_of_week
    - T079: Monthly recurrence with day_of_month (handles 31st edge case)
    """

    def calculate_next_daily(
        self,
        current_date: datetime,
        interval: int = 1
    ) -> datetime:
        """
        T077: Calculate next occurrence for daily recurrence.

        Args:
            current_date: Current/completed task due date
            interval: Number of days between occurrences (default: 1)

        Returns:
            Next occurrence date (time preserved)

        Example:
            current_date = 2026-01-05 10:00
            interval = 3
            → returns 2026-01-08 10:00
        """
        next_date = current_date + timedelta(days=interval)

        logger.debug(
            f"Daily recurrence calculated: current={current_date}, "
            f"interval={interval}, next={next_date}"
        )

        return next_date

    def calculate_next_weekly(
        self,
        current_date: datetime,
        interval: int = 1,
        days_of_week: Optional[List[int]] = None
    ) -> datetime:
        """
        T078: Calculate next occurrence for weekly recurrence.

        Args:
            current_date: Current/completed task due date
            interval: Number of weeks between occurrences (default: 1)
            days_of_week: List of weekdays (0=Monday, 6=Sunday)

        Returns:
            Next occurrence date on the specified day of week

        Example:
            current_date = 2026-01-05 (Monday) 10:00
            days_of_week = [0, 3, 5]  # Monday, Thursday, Saturday
            → returns 2026-01-08 (Thursday) 10:00 (next day in same week)

            current_date = 2026-01-10 (Saturday) 10:00
            days_of_week = [0, 3]  # Monday, Thursday
            → returns 2026-01-12 (Monday) 10:00 (wraps to next week)
        """
        if not days_of_week:
            # Default to same day next week
            days_of_week = [current_date.weekday()]

        # Sort days for consistent iteration
        days_of_week_sorted = sorted(days_of_week)

        current_weekday = current_date.weekday()

        # Find next day in current week
        next_day_in_week = None
        for day in days_of_week_sorted:
            if day > current_weekday:
                next_day_in_week = day
                break

        if next_day_in_week is not None:
            # Next occurrence is in same week
            days_ahead = next_day_in_week - current_weekday
            next_date = current_date + timedelta(days=days_ahead)
        else:
            # No more days in current week, go to first day of next interval week
            first_day = days_of_week_sorted[0]
            days_until_end_of_week = 6 - current_weekday  # Days to Saturday
            days_to_next_week_start = 1  # Sunday
            days_to_target_day = first_day  # Monday = 0, Tuesday = 1, etc.

            # Add interval weeks
            total_days = days_until_end_of_week + days_to_next_week_start + days_to_target_day
            total_days += (interval - 1) * 7  # Additional weeks for interval > 1

            next_date = current_date + timedelta(days=total_days)

        logger.debug(
            f"Weekly recurrence calculated: current={current_date}, "
            f"interval={interval}, days_of_week={days_of_week}, next={next_date}"
        )

        return next_date

    def calculate_next_monthly(
        self,
        current_date: datetime,
        interval: int = 1,
        day_of_month: int = 1
    ) -> datetime:
        """
        T079: Calculate next occurrence for monthly recurrence.

        CRITICAL: Handles edge case where day_of_month > days in next month.
        Example: January 31 → February 28/29 (uses last day of month)

        Args:
            current_date: Current/completed task due date
            interval: Number of months between occurrences (default: 1)
            day_of_month: Target day of month (1-31)

        Returns:
            Next occurrence date on the specified day of month

        Example:
            current_date = 2026-01-31 10:00
            day_of_month = 31
            → returns 2026-02-28 10:00 (February has only 28 days)

            current_date = 2026-02-28 10:00
            day_of_month = 31
            → returns 2026-03-31 10:00 (March has 31 days)
        """
        # Calculate next month
        next_month = current_date.month + interval
        next_year = current_date.year

        # Handle year wraparound
        while next_month > 12:
            next_month -= 12
            next_year += 1

        # Get number of days in next month
        days_in_next_month = calendar.monthrange(next_year, next_month)[1]

        # Use min(day_of_month, days_in_next_month) to handle 31st → Feb edge case
        actual_day = min(day_of_month, days_in_next_month)

        # Create next date with preserved time
        next_date = current_date.replace(
            year=next_year,
            month=next_month,
            day=actual_day
        )

        logger.debug(
            f"Monthly recurrence calculated: current={current_date}, "
            f"interval={interval}, day_of_month={day_of_month}, "
            f"actual_day={actual_day}, next={next_date}"
        )

        if actual_day != day_of_month:
            logger.info(
                f"Monthly recurrence edge case: day_of_month={day_of_month} "
                f"adjusted to {actual_day} (month has only {days_in_next_month} days)"
            )

        return next_date

    def calculate_next_occurrence(
        self,
        current_date: datetime,
        pattern: str,
        interval: int = 1,
        days_of_week: Optional[List[int]] = None,
        day_of_month: Optional[int] = None
    ) -> datetime:
        """
        Unified method to calculate next occurrence for any recurrence pattern.

        Args:
            current_date: Current/completed task due date
            pattern: Recurrence pattern ("daily", "weekly", "monthly")
            interval: Recurrence interval
            days_of_week: Days of week for weekly recurrence (0=Monday)
            day_of_month: Day of month for monthly recurrence (1-31)

        Returns:
            Next occurrence date

        Raises:
            ValueError: If pattern is invalid or required parameters missing
        """
        if pattern == "daily":
            return self.calculate_next_daily(current_date, interval)

        elif pattern == "weekly":
            if not days_of_week:
                raise ValueError("days_of_week required for weekly recurrence")
            return self.calculate_next_weekly(current_date, interval, days_of_week)

        elif pattern == "monthly":
            if not day_of_month:
                raise ValueError("day_of_month required for monthly recurrence")
            return self.calculate_next_monthly(current_date, interval, day_of_month)

        else:
            raise ValueError(f"Invalid recurrence pattern: {pattern}")


# ============================================================================
# Factory Function
# ============================================================================

def create_recurrence_calculator() -> RecurrenceCalculator:
    """
    Factory function to create RecurrenceCalculator instance.

    Returns:
        RecurrenceCalculator: New instance
    """
    return RecurrenceCalculator()
