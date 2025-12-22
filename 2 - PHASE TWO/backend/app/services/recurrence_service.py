"""
Recurrence service for calculating next occurrence dates and creating task instances.

This module provides functions for handling recurring tasks including:
- Calculating next occurrence dates (daily, weekly, monthly)
- Creating new task instances when recurring tasks are completed
"""

from datetime import date, datetime, timedelta
from typing import Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.task import Task, RecurrencePattern


class RecurrenceService:
    """
    Service for managing recurring tasks.

    Handles calculation of next occurrence dates and creation of new
    task instances when recurring tasks are marked complete.
    """

    def calculate_next_occurrence(
        self,
        current_date: date,
        pattern: RecurrencePattern,
        recurrence_day: Optional[int] = None,
    ) -> date:
        """
        Calculate the next occurrence date for a recurring task (T193).

        Args:
            current_date: The current due date of the task
            pattern: Recurrence pattern (DAILY, WEEKLY, MONTHLY)
            recurrence_day: Day for weekly (1-7 Mon-Sun) or monthly (1-31) recurrence

        Returns:
            Next occurrence date

        Raises:
            ValueError: If pattern requires recurrence_day but it's not provided
        """
        if pattern == RecurrencePattern.NONE:
            raise ValueError("Cannot calculate next occurrence for NONE pattern")

        if pattern == RecurrencePattern.DAILY:
            return self._next_daily(current_date)
        elif pattern == RecurrencePattern.WEEKLY:
            if recurrence_day is None:
                raise ValueError("Weekly recurrence requires recurrence_day (1-7)")
            return self._next_weekly(current_date, recurrence_day)
        elif pattern == RecurrencePattern.MONTHLY:
            if recurrence_day is None:
                raise ValueError("Monthly recurrence requires recurrence_day (1-31)")
            return self._next_monthly(current_date, recurrence_day)
        else:
            raise ValueError(f"Unknown recurrence pattern: {pattern}")

    async def create_next_instance(
        self,
        db: AsyncSession,
        completed_task: Task,
    ) -> Optional[Task]:
        """
        Create next instance of a recurring task (T191, T194).

        When a recurring task is marked complete, this creates a new task
        with the same properties but updated due date.

        Args:
            db: Database session
            completed_task: The task that was just completed

        Returns:
            New task instance if task is recurring, None otherwise
        """
        # Only create next instance if task has recurrence pattern
        if not completed_task.recurrence or completed_task.recurrence == RecurrencePattern.NONE:
            return None

        # Calculate next due date
        if completed_task.due_date:
            next_date = self.calculate_next_occurrence(
                completed_task.due_date,
                completed_task.recurrence,
                completed_task.recurrence_day,
            )
        else:
            # If no due date, use tomorrow for daily, or current date + interval
            today = date.today()
            next_date = self.calculate_next_occurrence(
                today,
                completed_task.recurrence,
                completed_task.recurrence_day,
            )

        # Create new task instance (T194 - copy task fields)
        new_task = Task(
            user_id=completed_task.user_id,
            title=completed_task.title,
            description=completed_task.description,
            priority=completed_task.priority,
            tags=completed_task.tags.copy() if completed_task.tags else [],
            due_date=next_date,
            due_time=completed_task.due_time,
            recurrence=completed_task.recurrence,
            recurrence_day=completed_task.recurrence_day,
            is_complete=False,  # New instance starts incomplete
        )

        db.add(new_task)
        await db.commit()
        await db.refresh(new_task)

        return new_task

    def _next_daily(self, current_date: date) -> date:
        """Calculate next daily occurrence (tomorrow)."""
        return current_date + timedelta(days=1)

    def _next_weekly(self, current_date: date, target_weekday: int) -> date:
        """
        Calculate next weekly occurrence on specified weekday.

        Args:
            current_date: Current date
            target_weekday: Target weekday (1=Monday, 7=Sunday)

        Returns:
            Next occurrence of the target weekday
        """
        # Convert target_weekday (1-7) to Python weekday (0-6)
        # Our system: 1=Mon, 2=Tue, ..., 7=Sun
        # Python: 0=Mon, 1=Tue, ..., 6=Sun
        target_py_weekday = (target_weekday - 1) % 7

        # Calculate days until next occurrence
        current_py_weekday = current_date.weekday()
        days_ahead = (target_py_weekday - current_py_weekday + 7) % 7
        if days_ahead == 0:
            days_ahead = 7

        return current_date + timedelta(days=days_ahead)

    def _next_monthly(self, current_date: date, target_day: int) -> date:
        """
        Calculate next monthly occurrence on specified day.

        Args:
            current_date: Current date
            target_day: Target day of month (1-31)

        Returns:
            Next occurrence of the target day

        Handles month boundaries (e.g., if target is 31 but next month has 30 days,
        uses the last day of that month).
        """
        # First, check if we can stay in the current month
        # (i.e., the target day hasn't arrived yet this month)
        if current_date.day < target_day:
            # Try to use current month with target day
            try_current = self._safe_date(current_date.year, current_date.month, target_day)
            # Check if safe_date didn't cap the day (month has enough days)
            # OR if it did cap but we're still before that capped day
            if try_current.day == target_day or current_date.day < try_current.day:
                return try_current

        # Otherwise, move to next month
        if current_date.month == 12:
            next_year = current_date.year + 1
            next_month = 1
        else:
            next_year = current_date.year
            next_month = current_date.month + 1

        return self._safe_date(next_year, next_month, target_day)

    def _safe_date(self, year: int, month: int, day: int) -> date:
        """
        Create a date, adjusting day to month's last day if needed.

        Args:
            year: Year
            month: Month (1-12)
            day: Day (1-31)

        Returns:
            Valid date, using last day of month if day exceeds month length
        """
        # Get the last day of the month
        next_month_first = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
        last_day = (next_month_first - timedelta(days=1)).day

        # Use the minimum of target day and last day of month
        actual_day = min(day, last_day)

        return date(year, month, actual_day)
