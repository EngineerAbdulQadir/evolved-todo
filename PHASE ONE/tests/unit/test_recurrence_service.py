"""Unit tests for RecurrenceService (T081 - US10)."""

from datetime import date

import pytest

from src.models.recurrence import RecurrencePattern
from src.services.recurrence_service import RecurrenceService


class TestRecurrenceServiceDaily:
    """Test daily recurrence calculations."""

    def test_next_daily_occurrence(self) -> None:
        """Daily recurrence returns next day (AC1)."""
        service = RecurrenceService()
        current = date(2025, 12, 10)

        result = service.calculate_next_occurrence(current, RecurrencePattern.DAILY)

        assert result == date(2025, 12, 11)

    def test_next_daily_month_boundary(self) -> None:
        """Daily recurrence handles month boundary (AC1)."""
        service = RecurrenceService()
        current = date(2025, 12, 31)

        result = service.calculate_next_occurrence(current, RecurrencePattern.DAILY)

        assert result == date(2026, 1, 1)


class TestRecurrenceServiceWeekly:
    """Test weekly recurrence calculations."""

    def test_next_weekly_same_weekday(self) -> None:
        """Weekly recurrence on same weekday goes to next week (AC2)."""
        service = RecurrenceService()
        # 2025-12-10 is Wednesday (weekday 3)
        current = date(2025, 12, 10)

        result = service.calculate_next_occurrence(
            current, RecurrencePattern.WEEKLY, recurrence_day=3
        )

        # Next Wednesday is 2025-12-17
        assert result == date(2025, 12, 17)

    def test_next_weekly_future_weekday_same_week(self) -> None:
        """Weekly recurrence to future weekday in same week (AC2)."""
        service = RecurrenceService()
        # 2025-12-10 is Wednesday (weekday 3)
        current = date(2025, 12, 10)

        # Next Friday (weekday 5)
        result = service.calculate_next_occurrence(
            current, RecurrencePattern.WEEKLY, recurrence_day=5
        )

        assert result == date(2025, 12, 12)

    def test_next_weekly_past_weekday_next_week(self) -> None:
        """Weekly recurrence to past weekday goes to next week (AC2)."""
        service = RecurrenceService()
        # 2025-12-10 is Wednesday (weekday 3)
        current = date(2025, 12, 10)

        # Monday (weekday 1) - already passed this week
        result = service.calculate_next_occurrence(
            current, RecurrencePattern.WEEKLY, recurrence_day=1
        )

        assert result == date(2025, 12, 15)

    def test_next_weekly_sunday(self) -> None:
        """Weekly recurrence handles Sunday (weekday 7) (AC2)."""
        service = RecurrenceService()
        # 2025-12-10 is Wednesday
        current = date(2025, 12, 10)

        # Next Sunday (weekday 7)
        result = service.calculate_next_occurrence(
            current, RecurrencePattern.WEEKLY, recurrence_day=7
        )

        assert result == date(2025, 12, 14)

    def test_weekly_requires_recurrence_day(self) -> None:
        """Weekly recurrence raises error without recurrence_day (AC2)."""
        service = RecurrenceService()
        current = date(2025, 12, 10)

        with pytest.raises(ValueError, match="Weekly recurrence requires recurrence_day"):
            service.calculate_next_occurrence(current, RecurrencePattern.WEEKLY)


class TestRecurrenceServiceMonthly:
    """Test monthly recurrence calculations."""

    def test_next_monthly_future_day_same_month(self) -> None:
        """Monthly recurrence to future day in same month (AC3)."""
        service = RecurrenceService()
        # 2025-12-10, target is day 20
        current = date(2025, 12, 10)

        result = service.calculate_next_occurrence(
            current, RecurrencePattern.MONTHLY, recurrence_day=20
        )

        assert result == date(2025, 12, 20)

    def test_next_monthly_past_day_next_month(self) -> None:
        """Monthly recurrence to past day goes to next month (AC3)."""
        service = RecurrenceService()
        # 2025-12-15, target is day 10 (already passed)
        current = date(2025, 12, 15)

        result = service.calculate_next_occurrence(
            current, RecurrencePattern.MONTHLY, recurrence_day=10
        )

        assert result == date(2026, 1, 10)

    def test_next_monthly_year_boundary(self) -> None:
        """Monthly recurrence handles year boundary (AC3)."""
        service = RecurrenceService()
        # 2025-12-20, target is day 15 (already passed in Dec)
        current = date(2025, 12, 20)

        result = service.calculate_next_occurrence(
            current, RecurrencePattern.MONTHLY, recurrence_day=15
        )

        assert result == date(2026, 1, 15)

    def test_next_monthly_day_31_in_30_day_month(self) -> None:
        """Monthly recurrence day 31 in 30-day month uses day 30 (AC3)."""
        service = RecurrenceService()
        # 2025-12-15, target is day 31
        # December has 31 days, so next occurrence should be Dec 31 (same month)
        current = date(2025, 12, 15)

        result = service.calculate_next_occurrence(
            current, RecurrencePattern.MONTHLY, recurrence_day=31
        )

        # Should be Dec 31 (current month, since we haven't passed day 31 yet)
        assert result == date(2025, 12, 31)

        # From Dec 31, next occurrence should be Jan 31
        current2 = date(2025, 12, 31)
        result2 = service.calculate_next_occurrence(
            current2, RecurrencePattern.MONTHLY, recurrence_day=31
        )

        assert result2 == date(2026, 1, 31)

        # From Jan 20, next occurrence should be Jan 31 (same month)
        current3 = date(2026, 1, 20)
        result3 = service.calculate_next_occurrence(
            current3, RecurrencePattern.MONTHLY, recurrence_day=31
        )

        assert result3 == date(2026, 1, 31)

        # From Jan 31, next is February which has only 28 days
        current4 = date(2026, 1, 31)
        result4 = service.calculate_next_occurrence(
            current4, RecurrencePattern.MONTHLY, recurrence_day=31
        )

        # February 2026 has 28 days, so should use Feb 28
        assert result4 == date(2026, 2, 28)

    def test_next_monthly_day_31_in_february_leap_year(self) -> None:
        """Monthly recurrence day 31 in February leap year uses day 29 (AC3)."""
        service = RecurrenceService()
        # 2024 is a leap year, January 20
        current = date(2024, 1, 20)

        result = service.calculate_next_occurrence(
            current, RecurrencePattern.MONTHLY, recurrence_day=31
        )

        # Should be Jan 31
        assert result == date(2024, 1, 31)

        # From Jan 31, next occurrence should be Feb 29 (leap year)
        current2 = date(2024, 1, 31)
        result2 = service.calculate_next_occurrence(
            current2, RecurrencePattern.MONTHLY, recurrence_day=31
        )

        assert result2 == date(2024, 2, 29)

    def test_monthly_requires_recurrence_day(self) -> None:
        """Monthly recurrence raises error without recurrence_day (AC3)."""
        service = RecurrenceService()
        current = date(2025, 12, 10)

        with pytest.raises(
            ValueError, match="Monthly recurrence requires recurrence_day"
        ):
            service.calculate_next_occurrence(current, RecurrencePattern.MONTHLY)


class TestRecurrenceServiceErrors:
    """Test error handling in RecurrenceService."""

    def test_none_pattern_raises_error(self) -> None:
        """NONE pattern raises error (AC4)."""
        service = RecurrenceService()
        current = date(2025, 12, 10)

        with pytest.raises(
            ValueError, match="Cannot calculate next occurrence for NONE pattern"
        ):
            service.calculate_next_occurrence(current, RecurrencePattern.NONE)


class TestRecurrenceServiceEdgeCases:
    """Test edge cases for RecurrenceService."""

    def test_safe_date_handles_invalid_day(self) -> None:
        """_safe_date caps day at month's last day (AC3)."""
        service = RecurrenceService()

        # Day 31 in April (30 days)
        result = service._safe_date(2025, 4, 31)
        assert result == date(2025, 4, 30)

        # Day 31 in February (28 days)
        result2 = service._safe_date(2025, 2, 31)
        assert result2 == date(2025, 2, 28)

        # Day 31 in February leap year (29 days)
        result3 = service._safe_date(2024, 2, 31)
        assert result3 == date(2024, 2, 29)

    def test_monthly_recurrence_consistent_day(self) -> None:
        """Monthly recurrence maintains consistent day across months (AC3)."""
        service = RecurrenceService()

        # Start on day 15
        current = date(2025, 1, 15)

        # Next 12 months should all be day 15
        for month in range(2, 13):
            result = service.calculate_next_occurrence(
                current, RecurrencePattern.MONTHLY, recurrence_day=15
            )
            assert result.day == 15
            assert result.month == month
            current = result
