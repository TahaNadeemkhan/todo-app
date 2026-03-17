"""
T069-T071: Unit tests for RecurrenceCalculator
TDD Red Phase - These tests will FAIL until RecurrenceCalculator is implemented

Tests calculate_next_* methods for daily, weekly, and monthly recurrence patterns.
"""

import pytest
from datetime import datetime, timedelta


class TestRecurrenceCalculatorDaily:
    """T069: Unit tests for daily recurrence calculation."""

    def test_calculate_next_daily_simple(self):
        """Test daily recurrence with interval=1 (every day)."""
        from services.calculators.recurrence_calculator import RecurrenceCalculator

        calculator = RecurrenceCalculator()
        current_date = datetime(2026, 1, 5, 10, 0, 0)

        next_date = calculator.calculate_next_daily(
            current_date=current_date,
            interval=1
        )

        expected_date = datetime(2026, 1, 6, 10, 0, 0)
        assert next_date == expected_date

    def test_calculate_next_daily_with_interval(self):
        """Test daily recurrence with interval=3 (every 3 days)."""
        from services.calculators.recurrence_calculator import RecurrenceCalculator

        calculator = RecurrenceCalculator()
        current_date = datetime(2026, 1, 5, 10, 0, 0)

        next_date = calculator.calculate_next_daily(
            current_date=current_date,
            interval=3
        )

        expected_date = datetime(2026, 1, 8, 10, 0, 0)  # +3 days
        assert next_date == expected_date

    def test_calculate_next_daily_preserves_time(self):
        """Test that daily recurrence preserves time of day."""
        from services.calculators.recurrence_calculator import RecurrenceCalculator

        calculator = RecurrenceCalculator()
        current_date = datetime(2026, 1, 5, 14, 30, 0)  # 2:30 PM

        next_date = calculator.calculate_next_daily(
            current_date=current_date,
            interval=1
        )

        assert next_date.hour == 14
        assert next_date.minute == 30


class TestRecurrenceCalculatorWeekly:
    """T070: Unit tests for weekly recurrence calculation."""

    def test_calculate_next_weekly_same_day(self):
        """Test weekly recurrence with interval=1, same day of week."""
        from services.calculators.recurrence_calculator import RecurrenceCalculator

        calculator = RecurrenceCalculator()
        # Monday, January 5, 2026
        current_date = datetime(2026, 1, 5, 10, 0, 0)

        next_date = calculator.calculate_next_weekly(
            current_date=current_date,
            interval=1,
            days_of_week=[0]  # Monday (0 = Monday in Python)
        )

        # Next Monday (January 12, 2026)
        expected_date = datetime(2026, 1, 12, 10, 0, 0)
        assert next_date == expected_date

    def test_calculate_next_weekly_multiple_days(self):
        """Test weekly recurrence with multiple days of week."""
        from services.calculators.recurrence_calculator import RecurrenceCalculator

        calculator = RecurrenceCalculator()
        # Monday, January 5, 2026
        current_date = datetime(2026, 1, 5, 10, 0, 0)

        next_date = calculator.calculate_next_weekly(
            current_date=current_date,
            interval=1,
            days_of_week=[0, 3, 5]  # Monday, Thursday, Saturday
        )

        # Next occurrence is Thursday (January 8, 2026)
        expected_date = datetime(2026, 1, 8, 10, 0, 0)
        assert next_date == expected_date

    def test_calculate_next_weekly_wraps_to_next_week(self):
        """Test weekly recurrence wraps to next week if no more days in current week."""
        from services.calculators.recurrence_calculator import RecurrenceCalculator

        calculator = RecurrenceCalculator()
        # Saturday, January 10, 2026
        current_date = datetime(2026, 1, 10, 10, 0, 0)

        next_date = calculator.calculate_next_weekly(
            current_date=current_date,
            interval=1,
            days_of_week=[0, 3]  # Monday, Thursday
        )

        # Next occurrence is Monday (January 12, 2026)
        expected_date = datetime(2026, 1, 12, 10, 0, 0)
        assert next_date == expected_date

    def test_calculate_next_weekly_with_interval_2(self):
        """Test weekly recurrence with interval=2 (every 2 weeks)."""
        from services.calculators.recurrence_calculator import RecurrenceCalculator

        calculator = RecurrenceCalculator()
        # Monday, January 5, 2026
        current_date = datetime(2026, 1, 5, 10, 0, 0)

        next_date = calculator.calculate_next_weekly(
            current_date=current_date,
            interval=2,
            days_of_week=[0]  # Monday
        )

        # Next Monday is 2 weeks later (January 19, 2026)
        expected_date = datetime(2026, 1, 19, 10, 0, 0)
        assert next_date == expected_date


class TestRecurrenceCalculatorMonthly:
    """T071: Unit tests for monthly recurrence calculation with edge cases."""

    def test_calculate_next_monthly_simple(self):
        """Test monthly recurrence with interval=1, same day of month."""
        from services.calculators.recurrence_calculator import RecurrenceCalculator

        calculator = RecurrenceCalculator()
        # January 15, 2026
        current_date = datetime(2026, 1, 15, 10, 0, 0)

        next_date = calculator.calculate_next_monthly(
            current_date=current_date,
            interval=1,
            day_of_month=15
        )

        # February 15, 2026
        expected_date = datetime(2026, 2, 15, 10, 0, 0)
        assert next_date == expected_date

    def test_calculate_next_monthly_edge_case_31st(self):
        """
        T071: Test monthly recurrence handles 31st day edge case.

        Critical: If current month has 31 days but next month has fewer
        (e.g., January 31 → February), use last day of next month.
        """
        from services.calculators.recurrence_calculator import RecurrenceCalculator

        calculator = RecurrenceCalculator()
        # January 31, 2026
        current_date = datetime(2026, 1, 31, 10, 0, 0)

        next_date = calculator.calculate_next_monthly(
            current_date=current_date,
            interval=1,
            day_of_month=31
        )

        # February only has 28 days in 2026, so use February 28
        expected_date = datetime(2026, 2, 28, 10, 0, 0)
        assert next_date == expected_date

    def test_calculate_next_monthly_edge_case_31st_to_march(self):
        """Test monthly recurrence from February (28 days) to March (31 days)."""
        from services.calculators.recurrence_calculator import RecurrenceCalculator

        calculator = RecurrenceCalculator()
        # February 28, 2026 (last day of February)
        current_date = datetime(2026, 2, 28, 10, 0, 0)

        next_date = calculator.calculate_next_monthly(
            current_date=current_date,
            interval=1,
            day_of_month=31  # User wants 31st of every month
        )

        # March has 31 days, so use March 31
        expected_date = datetime(2026, 3, 31, 10, 0, 0)
        assert next_date == expected_date

    def test_calculate_next_monthly_with_interval_3(self):
        """Test monthly recurrence with interval=3 (every 3 months)."""
        from services.calculators.recurrence_calculator import RecurrenceCalculator

        calculator = RecurrenceCalculator()
        # January 15, 2026
        current_date = datetime(2026, 1, 15, 10, 0, 0)

        next_date = calculator.calculate_next_monthly(
            current_date=current_date,
            interval=3,
            day_of_month=15
        )

        # April 15, 2026 (3 months later)
        expected_date = datetime(2026, 4, 15, 10, 0, 0)
        assert next_date == expected_date

    def test_calculate_next_monthly_preserves_time(self):
        """Test that monthly recurrence preserves time of day."""
        from services.calculators.recurrence_calculator import RecurrenceCalculator

        calculator = RecurrenceCalculator()
        current_date = datetime(2026, 1, 15, 14, 30, 0)  # 2:30 PM

        next_date = calculator.calculate_next_monthly(
            current_date=current_date,
            interval=1,
            day_of_month=15
        )

        assert next_date.hour == 14
        assert next_date.minute == 30

    def test_calculate_next_monthly_february_leap_year(self):
        """Test monthly recurrence handles February in leap year."""
        from services.calculators.recurrence_calculator import RecurrenceCalculator

        calculator = RecurrenceCalculator()
        # January 31, 2024 (2024 is a leap year)
        current_date = datetime(2024, 1, 31, 10, 0, 0)

        next_date = calculator.calculate_next_monthly(
            current_date=current_date,
            interval=1,
            day_of_month=31
        )

        # February 2024 has 29 days (leap year), so use February 29
        expected_date = datetime(2024, 2, 29, 10, 0, 0)
        assert next_date == expected_date
