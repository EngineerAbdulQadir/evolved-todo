"""Unit tests for Task model validation (T021, T052)."""

from datetime import date, datetime

import pytest

from src.models.priority import DueStatus
from src.models.task import RecurrencePattern, Task


class TestTaskTitleValidation:
    """Tests for Task title validation (T021 - US1)."""

    def test_valid_title_creates_task(self) -> None:
        """Task with valid title creates successfully (AC1)."""
        task = Task(id=1, title="Buy milk")

        assert task.title == "Buy milk"

    def test_empty_title_raises_error(self) -> None:
        """Empty title raises ValueError (AC2)."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Task(id=1, title="")

    def test_whitespace_only_title_raises_error(self) -> None:
        """Whitespace-only title raises ValueError (AC3)."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Task(id=1, title="   ")

    def test_title_max_length_200_chars(self) -> None:
        """Title with exactly 200 characters is valid (AC4)."""
        long_title = "A" * 200
        task = Task(id=1, title=long_title)

        assert len(task.title) == 200
        assert task.title == long_title

    def test_title_over_200_chars_raises_error(self) -> None:
        """Title exceeding 200 characters raises ValueError (AC5)."""
        too_long_title = "A" * 201
        with pytest.raises(ValueError, match="Title cannot exceed 200 characters"):
            Task(id=1, title=too_long_title)


class TestTaskDescriptionValidation:
    """Tests for Task description validation (T021 - US1)."""

    def test_none_description_is_valid(self) -> None:
        """Task with no description (None) is valid (AC1)."""
        task = Task(id=1, title="Task", description=None)

        assert task.description is None

    def test_empty_string_description_is_valid(self) -> None:
        """Task with empty string description is valid (AC2)."""
        task = Task(id=1, title="Task", description="")

        assert task.description == ""

    def test_description_max_length_1000_chars(self) -> None:
        """Description with exactly 1000 characters is valid (AC3)."""
        long_desc = "B" * 1000
        task = Task(id=1, title="Task", description=long_desc)

        assert len(task.description) == 1000
        assert task.description == long_desc

    def test_description_over_1000_chars_raises_error(self) -> None:
        """Description exceeding 1000 characters raises ValueError (AC4)."""
        too_long_desc = "B" * 1001
        with pytest.raises(
            ValueError, match="Description cannot exceed 1000 characters"
        ):
            Task(id=1, title="Task", description=too_long_desc)


class TestTaskDefaultValues:
    """Tests for Task default values."""

    def test_is_complete_defaults_to_false(self) -> None:
        """New task has is_complete=False by default (AC1)."""
        task = Task(id=1, title="Task")

        assert task.is_complete is False

    def test_created_at_auto_set_on_creation(self) -> None:
        """New task has created_at automatically set (AC2)."""
        task = Task(id=1, title="Task")

        assert task.created_at is not None
        assert isinstance(task.created_at, datetime)

    def test_priority_defaults_to_none(self) -> None:
        """New task has priority=None by default (AC3)."""
        task = Task(id=1, title="Task")

        assert task.priority is None

    def test_tags_defaults_to_empty_list(self) -> None:
        """New task has empty tags list by default (AC4)."""
        task = Task(id=1, title="Task")

        assert task.tags == []
        assert isinstance(task.tags, list)


class TestTaskComputedProperties:
    """Tests for Task computed properties."""

    def test_is_overdue_false_when_no_due_date(self) -> None:
        """Task with no due date is not overdue (AC1)."""
        task = Task(id=1, title="Task")

        assert task.is_overdue is False

    def test_is_overdue_false_when_complete(self) -> None:
        """Completed task is not overdue even if past due (AC2)."""
        task = Task(
            id=1, title="Task", is_complete=True, due_date=date(2025, 1, 1)
        )  # Past date

        assert task.is_overdue is False

    def test_due_status_no_due_date(self) -> None:
        """Task with no due date has NO_DUE_DATE status (AC3)."""
        task = Task(id=1, title="Task")

        assert task.due_status == DueStatus.NO_DUE_DATE

    def test_has_recurrence_false_when_none(self) -> None:
        """Task with no recurrence has has_recurrence=False (AC4)."""
        task = Task(id=1, title="Task")

        assert task.has_recurrence is False

    def test_has_recurrence_true_when_set(self) -> None:
        """Task with recurrence pattern has has_recurrence=True (AC5)."""
        task = Task(
            id=1, title="Task", recurrence=RecurrencePattern.DAILY
        )

        assert task.has_recurrence is True

    def test_display_due_no_due_date(self) -> None:
        """Task with no due date displays 'No due date' (AC6)."""
        task = Task(id=1, title="Task")

        assert task.display_due == "No due date"


class TestTaskTagsValidation:
    """Tests for Task tags validation (T052 - US6)."""

    def test_valid_tags_list(self) -> None:
        """Task with valid tags creates successfully (AC1)."""
        task = Task(id=1, title="Task", tags=["work", "urgent"])

        assert task.tags == ["work", "urgent"]

    def test_max_10_tags_allowed(self) -> None:
        """Task with exactly 10 tags is valid (AC2)."""
        tags = [f"tag{i}" for i in range(10)]
        task = Task(id=1, title="Task", tags=tags)

        assert len(task.tags) == 10

    def test_over_10_tags_raises_error(self) -> None:
        """Task with more than 10 tags raises ValueError (AC3)."""
        tags = [f"tag{i}" for i in range(11)]
        with pytest.raises(ValueError, match="Cannot have more than 10 tags"):
            Task(id=1, title="Task", tags=tags)

    def test_tag_max_length_50_chars(self) -> None:
        """Tag with exactly 50 characters is valid (AC4)."""
        long_tag = "A" * 50
        task = Task(id=1, title="Task", tags=[long_tag])

        assert len(task.tags[0]) == 50

    def test_tag_over_50_chars_raises_error(self) -> None:
        """Tag exceeding 50 characters raises ValueError (AC5)."""
        too_long_tag = "A" * 51
        with pytest.raises(ValueError, match="exceeds 50 character limit"):
            Task(id=1, title="Task", tags=[too_long_tag])


class TestTaskRecurrenceValidation:
    """Tests for Task recurrence validation."""

    def test_weekly_recurrence_requires_day_1_to_7(self) -> None:
        """Weekly recurrence with day 1-7 is valid (AC1)."""
        task = Task(
            id=1,
            title="Task",
            recurrence=RecurrencePattern.WEEKLY,
            recurrence_day=1,  # Monday
        )

        assert task.recurrence == RecurrencePattern.WEEKLY
        assert task.recurrence_day == 1

    def test_weekly_recurrence_invalid_day_raises_error(self) -> None:
        """Weekly recurrence with invalid day raises ValueError (AC2)."""
        with pytest.raises(ValueError, match="Weekly recurrence requires day 1-7"):
            Task(
                id=1,
                title="Task",
                recurrence=RecurrencePattern.WEEKLY,
                recurrence_day=8,  # Invalid
            )

    def test_monthly_recurrence_requires_day_1_to_31(self) -> None:
        """Monthly recurrence with day 1-31 is valid (AC3)."""
        task = Task(
            id=1,
            title="Task",
            recurrence=RecurrencePattern.MONTHLY,
            recurrence_day=15,
        )

        assert task.recurrence == RecurrencePattern.MONTHLY
        assert task.recurrence_day == 15

    def test_monthly_recurrence_invalid_day_raises_error(self) -> None:
        """Monthly recurrence with invalid day raises ValueError (AC4)."""
        with pytest.raises(ValueError, match="Monthly recurrence requires day 1-31"):
            Task(
                id=1,
                title="Task",
                recurrence=RecurrencePattern.MONTHLY,
                recurrence_day=32,  # Invalid
            )
