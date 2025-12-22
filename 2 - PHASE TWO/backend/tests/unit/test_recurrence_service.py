"""
Unit tests for RecurrenceService (T188).

Tests the calculation of next occurrence dates for recurring tasks.
"""

from datetime import date, time
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import RecurrencePattern
from app.services.recurrence_service import RecurrenceService


@pytest.fixture
def recurrence_service():
    """Create RecurrenceService instance for testing."""
    return RecurrenceService()


class TestCalculateNextOccurrence:
    """Test next occurrence calculation for different recurrence patterns."""

    def test_daily_recurrence(self, recurrence_service):
        """Test daily recurrence returns tomorrow."""
        current = date(2025, 12, 14)
        next_date = recurrence_service.calculate_next_occurrence(
            current, RecurrencePattern.DAILY
        )
        assert next_date == date(2025, 12, 15)

    def test_weekly_recurrence_same_day(self, recurrence_service):
        """Test weekly recurrence on same weekday goes to next week."""
        # Monday, Dec 15, 2025
        current = date(2025, 12, 15)
        # Recur on Monday (1)
        next_date = recurrence_service.calculate_next_occurrence(
            current, RecurrencePattern.WEEKLY, recurrence_day=1
        )
        # Should be next Monday
        assert next_date == date(2025, 12, 22)

    def test_weekly_recurrence_different_day(self, recurrence_service):
        """Test weekly recurrence advances to target weekday."""
        # Monday, Dec 15, 2025
        current = date(2025, 12, 15)
        # Recur on Friday (5)
        next_date = recurrence_service.calculate_next_occurrence(
            current, RecurrencePattern.WEEKLY, recurrence_day=5
        )
        # Should be this Friday
        assert next_date == date(2025, 12, 19)

    def test_monthly_recurrence_same_month(self, recurrence_service):
        """Test monthly recurrence stays in current month if day hasn't passed."""
        # Dec 10, 2025
        current = date(2025, 12, 10)
        # Recur on 15th
        next_date = recurrence_service.calculate_next_occurrence(
            current, RecurrencePattern.MONTHLY, recurrence_day=15
        )
        # Should be Dec 15
        assert next_date == date(2025, 12, 15)

    def test_monthly_recurrence_next_month(self, recurrence_service):
        """Test monthly recurrence moves to next month if day has passed."""
        # Dec 20, 2025
        current = date(2025, 12, 20)
        # Recur on 15th
        next_date = recurrence_service.calculate_next_occurrence(
            current, RecurrencePattern.MONTHLY, recurrence_day=15
        )
        # Should be Jan 15, 2026
        assert next_date == date(2026, 1, 15)

    def test_monthly_recurrence_month_boundary(self, recurrence_service):
        """Test monthly recurrence handles months with fewer days."""
        # Jan 31, 2025
        current = date(2025, 1, 31)
        # Recur on 31st
        next_date = recurrence_service.calculate_next_occurrence(
            current, RecurrencePattern.MONTHLY, recurrence_day=31
        )
        # Feb only has 28 days in 2025, should cap to Feb 28
        assert next_date == date(2025, 2, 28)

    def test_monthly_recurrence_year_boundary(self, recurrence_service):
        """Test monthly recurrence crosses year boundary."""
        # Dec 15, 2025
        current = date(2025, 12, 31)
        # Recur on 15th
        next_date = recurrence_service.calculate_next_occurrence(
            current, RecurrencePattern.MONTHLY, recurrence_day=15
        )
        # Should be Jan 15, 2026
        assert next_date == date(2026, 1, 15)

    def test_none_pattern_raises_error(self, recurrence_service):
        """Test that NONE pattern raises ValueError."""
        with pytest.raises(ValueError, match="Cannot calculate next occurrence for NONE pattern"):
            recurrence_service.calculate_next_occurrence(
                date(2025, 12, 14), RecurrencePattern.NONE
            )

    def test_weekly_without_recurrence_day_raises_error(self, recurrence_service):
        """Test weekly recurrence without recurrence_day raises ValueError."""
        with pytest.raises(ValueError, match="Weekly recurrence requires recurrence_day"):
            recurrence_service.calculate_next_occurrence(
                date(2025, 12, 14), RecurrencePattern.WEEKLY
            )

    def test_monthly_without_recurrence_day_raises_error(self, recurrence_service):
        """Test monthly recurrence without recurrence_day raises ValueError."""
        with pytest.raises(ValueError, match="Monthly recurrence requires recurrence_day"):
            recurrence_service.calculate_next_occurrence(
                date(2025, 12, 14), RecurrencePattern.MONTHLY
            )

    def test_unknown_pattern_raises_error(self, recurrence_service):
        """Test unknown recurrence pattern raises ValueError."""
        # Create an invalid pattern by directly using a string
        with pytest.raises(ValueError, match="Unknown recurrence pattern"):
            recurrence_service.calculate_next_occurrence(
                date(2025, 12, 14), "INVALID_PATTERN"  # type: ignore
            )


class TestCreateNextInstance:
    """Test creation of next task instance for recurring tasks."""

    @pytest.mark.asyncio
    async def test_create_next_instance_with_due_date(self, test_db: AsyncSession, recurrence_service):
        """Test creating next instance for recurring task with due date."""
        from app.models.task import Task

        # Create a recurring task
        task = Task(
            user_id="test-user-123",
            title="Weekly Report",
            description="Submit weekly report",
            priority="medium",
            tags=["work", "report"],
            due_date=date(2025, 12, 15),  # Monday
            due_time=time(10, 0),
            recurrence=RecurrencePattern.WEEKLY,
            recurrence_day=7,  # Sunday
            is_complete=True,
        )

        test_db.add(task)
        await test_db.commit()

        # Create next instance
        next_task = await recurrence_service.create_next_instance(test_db, task)

        assert next_task is not None
        assert next_task.title == "Weekly Report"
        assert next_task.description == "Submit weekly report"
        assert next_task.priority == "medium"
        assert next_task.tags == ["work", "report"]
        assert next_task.due_date == date(2025, 12, 21)  # Next Sunday
        assert next_task.due_time == time(10, 0)
        assert next_task.recurrence == RecurrencePattern.WEEKLY
        assert next_task.recurrence_day == 7
        assert next_task.is_complete is False
        assert next_task.user_id == "test-user-123"

    @pytest.mark.asyncio
    async def test_create_next_instance_without_due_date(self, test_db: AsyncSession, recurrence_service):
        """Test creating next instance for recurring task without due date."""
        from app.models.task import Task
        from datetime import timedelta

        # Create a recurring task without due date
        task = Task(
            user_id="test-user-123",
            title="Daily Standup",
            recurrence=RecurrencePattern.DAILY,
            is_complete=True,
        )

        test_db.add(task)
        await test_db.commit()

        # Create next instance
        next_task = await recurrence_service.create_next_instance(test_db, task)

        assert next_task is not None
        assert next_task.title == "Daily Standup"
        # Should use today + 1 day
        assert next_task.due_date == date.today() + timedelta(days=1)
        assert next_task.recurrence == RecurrencePattern.DAILY
        assert next_task.is_complete is False

    @pytest.mark.asyncio
    async def test_create_next_instance_none_pattern(self, test_db: AsyncSession, recurrence_service):
        """Test that non-recurring tasks return None."""
        from app.models.task import Task

        # Create a non-recurring task
        task = Task(
            user_id="test-user-123",
            title="One-time Task",
            recurrence=RecurrencePattern.NONE,
            is_complete=True,
        )

        test_db.add(task)
        await test_db.commit()

        # Should return None for non-recurring tasks
        next_task = await recurrence_service.create_next_instance(test_db, task)

        assert next_task is None

    @pytest.mark.asyncio
    async def test_create_next_instance_no_recurrence(self, test_db: AsyncSession, recurrence_service):
        """Test that tasks without recurrence field return None."""
        from app.models.task import Task

        # Create a task without recurrence
        task = Task(
            user_id="test-user-123",
            title="Simple Task",
            is_complete=True,
        )

        test_db.add(task)
        await test_db.commit()

        # Should return None
        next_task = await recurrence_service.create_next_instance(test_db, task)

        assert next_task is None
