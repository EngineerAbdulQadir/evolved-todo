"""Unit tests for TaskService validation logic."""

import pytest
from datetime import date, time
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.task import TaskCreate, TaskUpdate
from app.models.task import Priority, RecurrencePattern
from app.services.task_service import create_task, update_task, toggle_task_complete, get_task_by_id


class TestTaskCreateValidation:
    """Test TaskCreate schema validation."""

    def test_valid_minimal_task(self):
        """Test creating task with only required field (title)."""
        task_data = TaskCreate(title="Test Task")

        assert task_data.title == "Test Task"
        assert task_data.description is None
        assert task_data.priority is None
        assert task_data.tags == []
        assert task_data.due_date is None
        assert task_data.due_time is None

    def test_valid_full_task(self):
        """Test creating task with all fields."""
        task_data = TaskCreate(
            title="Full Task",
            description="Complete description",
            priority=Priority.HIGH,
            tags=["work", "urgent"],
            due_date=date(2025, 12, 31),
            due_time=time(23, 59, 0),
        )

        assert task_data.title == "Full Task"
        assert task_data.description == "Complete description"
        assert task_data.priority == Priority.HIGH
        assert task_data.tags == ["work", "urgent"]
        assert task_data.due_date == date(2025, 12, 31)
        assert task_data.due_time == time(23, 59, 0)

    def test_title_required(self):
        """Test that title is required."""
        with pytest.raises(ValueError):
            TaskCreate()  # type: ignore

    def test_title_cannot_be_empty_string(self):
        """Test that title cannot be empty string."""
        with pytest.raises(ValueError, match="at least 1 character"):
            TaskCreate(title="")

    def test_title_max_length_200(self):
        """Test that title cannot exceed 200 characters."""
        with pytest.raises(ValueError, match="at most 200 character"):
            TaskCreate(title="a" * 201)

    def test_title_exactly_200_chars(self):
        """Test that title can be exactly 200 characters."""
        task_data = TaskCreate(title="a" * 200)
        assert len(task_data.title) == 200

    def test_description_max_length_1000(self):
        """Test that description cannot exceed 1000 characters."""
        with pytest.raises(ValueError, match="at most 1000 character"):
            TaskCreate(title="Test", description="a" * 1001)

    def test_description_exactly_1000_chars(self):
        """Test that description can be exactly 1000 characters."""
        task_data = TaskCreate(title="Test", description="a" * 1000)
        assert len(task_data.description) == 1000  # type: ignore

    def test_description_optional(self):
        """Test that description is optional."""
        task_data = TaskCreate(title="Test")
        assert task_data.description is None

    def test_priority_valid_values(self):
        """Test valid priority values."""
        for priority in [Priority.LOW, Priority.MEDIUM, Priority.HIGH]:
            task_data = TaskCreate(title="Test", priority=priority)
            assert task_data.priority == priority

    def test_priority_invalid_value(self):
        """Test that invalid priority is rejected."""
        with pytest.raises(ValueError):
            TaskCreate(title="Test", priority="invalid")  # type: ignore

    def test_priority_optional(self):
        """Test that priority is optional."""
        task_data = TaskCreate(title="Test")
        assert task_data.priority is None

    def test_tags_as_list(self):
        """Test that tags are stored as list."""
        task_data = TaskCreate(title="Test", tags=["tag1", "tag2"])
        assert task_data.tags == ["tag1", "tag2"]
        assert isinstance(task_data.tags, list)

    def test_tags_max_10_items(self):
        """Test that tags cannot exceed 10 items."""
        with pytest.raises(ValueError):
            TaskCreate(title="Test", tags=[f"tag{i}" for i in range(11)])

    def test_tags_exactly_10_items(self):
        """Test that tags can be exactly 10 items."""
        tags = [f"tag{i}" for i in range(10)]
        task_data = TaskCreate(title="Test", tags=tags)
        assert len(task_data.tags) == 10

    def test_tags_empty_list(self):
        """Test that tags can be empty list."""
        task_data = TaskCreate(title="Test", tags=[])
        assert task_data.tags == []

    def test_tags_default_empty_list(self):
        """Test that tags default to empty list."""
        task_data = TaskCreate(title="Test")
        assert task_data.tags == []

    def test_due_date_valid(self):
        """Test valid due_date."""
        task_data = TaskCreate(title="Test", due_date=date(2025, 12, 31))
        assert task_data.due_date == date(2025, 12, 31)

    def test_due_date_optional(self):
        """Test that due_date is optional."""
        task_data = TaskCreate(title="Test")
        assert task_data.due_date is None

    def test_due_time_valid(self):
        """Test valid due_time."""
        task_data = TaskCreate(
            title="Test", due_date=date(2025, 12, 31), due_time=time(14, 30, 0)
        )
        assert task_data.due_time == time(14, 30, 0)

    def test_due_time_optional(self):
        """Test that due_time is optional."""
        task_data = TaskCreate(title="Test", due_date=date(2025, 12, 31))
        assert task_data.due_time is None


class TestTaskUpdateValidation:
    """Test TaskUpdate schema validation."""

    def test_all_fields_optional(self):
        """Test that all fields are optional in TaskUpdate."""
        task_data = TaskUpdate()
        assert task_data.title is None
        assert task_data.description is None
        assert task_data.priority is None
        assert task_data.tags is None
        assert task_data.is_complete is None

    def test_partial_update_title_only(self):
        """Test updating only title."""
        task_data = TaskUpdate(title="Updated Title")
        assert task_data.title == "Updated Title"
        assert task_data.description is None

    def test_partial_update_priority_only(self):
        """Test updating only priority."""
        task_data = TaskUpdate(priority=Priority.HIGH)
        assert task_data.priority == Priority.HIGH
        assert task_data.title is None

    def test_partial_update_is_complete(self):
        """Test updating completion status."""
        task_data = TaskUpdate(is_complete=True)
        assert task_data.is_complete is True

    def test_title_min_length_when_provided(self):
        """Test that title must have at least 1 char when provided."""
        with pytest.raises(ValueError, match="at least 1 character"):
            TaskUpdate(title="")

    def test_title_max_length_when_provided(self):
        """Test that title cannot exceed 200 chars when provided."""
        with pytest.raises(ValueError, match="at most 200 character"):
            TaskUpdate(title="a" * 201)

    def test_description_max_length_when_provided(self):
        """Test that description cannot exceed 1000 chars when provided."""
        with pytest.raises(ValueError, match="at most 1000 character"):
            TaskUpdate(description="a" * 1001)

    def test_tags_max_10_when_provided(self):
        """Test that tags cannot exceed 10 items when provided."""
        with pytest.raises(ValueError):
            TaskUpdate(tags=[f"tag{i}" for i in range(11)])

    def test_priority_valid_when_provided(self):
        """Test that priority must be valid when provided."""
        with pytest.raises(ValueError):
            TaskUpdate(priority="invalid")  # type: ignore


class TestBusinessLogicValidation:
    """Test business logic validation rules."""

    def test_due_time_without_due_date_rejected(self):
        """Test that due_time requires due_date (business rule)."""
        # This validation should happen in the service layer
        # Creating the schema is allowed, but service should reject it
        task_data = TaskCreate(title="Test", due_time=time(14, 30, 0))

        # Schema allows it (no built-in cross-field validation)
        assert task_data.due_time == time(14, 30, 0)
        assert task_data.due_date is None

        # But service layer should validate and reject this combination
        # (tested in integration tests)

    def test_due_date_with_time(self):
        """Test valid combination of due_date and due_time."""
        task_data = TaskCreate(
            title="Test", due_date=date(2025, 12, 31), due_time=time(14, 30, 0)
        )

        assert task_data.due_date == date(2025, 12, 31)
        assert task_data.due_time == time(14, 30, 0)

    def test_due_date_without_time(self):
        """Test valid due_date without time."""
        task_data = TaskCreate(title="Test", due_date=date(2025, 12, 31))

        assert task_data.due_date == date(2025, 12, 31)
        assert task_data.due_time is None


class TestTaskDataTypes:
    """Test correct data types for task fields."""

    def test_title_must_be_string(self):
        """Test that title must be string."""
        with pytest.raises(ValueError):
            TaskCreate(title=123)  # type: ignore

    def test_description_must_be_string(self):
        """Test that description must be string."""
        with pytest.raises(ValueError):
            TaskCreate(title="Test", description=123)  # type: ignore

    def test_tags_must_be_list_of_strings(self):
        """Test that tags must be list of strings."""
        with pytest.raises(ValueError):
            TaskCreate(title="Test", tags=["tag1", 123])  # type: ignore

    def test_is_complete_coerces_to_boolean(self):
        """Test that is_complete coerces string to boolean."""
        # Pydantic coerces truthy strings to boolean
        task_data = TaskUpdate(is_complete="true")  # type: ignore
        assert task_data.is_complete is True

    def test_due_date_parses_string(self):
        """Test that due_date parses ISO date string."""
        # Pydantic parses ISO date strings
        task_data = TaskCreate(title="Test", due_date="2025-12-31")  # type: ignore
        assert task_data.due_date == date(2025, 12, 31)

    def test_due_time_parses_string(self):
        """Test that due_time parses ISO time string."""
        # Pydantic parses ISO time strings
        task_data = TaskCreate(
            title="Test",
            due_date=date(2025, 12, 31),
            due_time="14:30:00",  # type: ignore
        )
        assert task_data.due_time == time(14, 30, 0)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_unicode_in_title(self):
        """Test that unicode characters work in title."""
        task_data = TaskCreate(title="Task 📝 with emojis 🎯")
        assert "📝" in task_data.title
        assert "🎯" in task_data.title

    def test_unicode_in_description(self):
        """Test that unicode characters work in description."""
        task_data = TaskCreate(title="Test", description="Description with émojis 🚀")
        assert "🚀" in task_data.description  # type: ignore

    def test_special_characters_in_title(self):
        """Test special characters in title."""
        task_data = TaskCreate(title="Task: with special-chars! @#$%")
        assert task_data.title == "Task: with special-chars! @#$%"

    def test_newlines_in_description(self):
        """Test multiline description."""
        description = "Line 1\nLine 2\nLine 3"
        task_data = TaskCreate(title="Test", description=description)
        assert task_data.description == description

    def test_empty_tag_in_list(self):
        """Test that empty strings in tags are allowed (but not recommended)."""
        # Pydantic allows it, but we may want to filter empty strings
        task_data = TaskCreate(title="Test", tags=["tag1", "", "tag2"])
        assert task_data.tags == ["tag1", "", "tag2"]

    def test_duplicate_tags(self):
        """Test that duplicate tags are allowed (not automatically deduplicated)."""
        task_data = TaskCreate(title="Test", tags=["work", "work", "urgent"])
        assert task_data.tags == ["work", "work", "urgent"]

    def test_whitespace_title_allowed_by_schema(self):
        """Test that whitespace-only title passes schema validation."""
        # Schema allows it, but application should trim before saving
        task_data = TaskCreate(title="   ")
        assert task_data.title == "   "

    def test_past_due_date(self):
        """Test that past due dates are allowed (no date validation)."""
        task_data = TaskCreate(title="Test", due_date=date(2020, 1, 1))
        assert task_data.due_date == date(2020, 1, 1)

    def test_future_due_date(self):
        """Test that future due dates are allowed."""
        task_data = TaskCreate(title="Test", due_date=date(2099, 12, 31))
        assert task_data.due_date == date(2099, 12, 31)


@pytest.mark.asyncio
async def test_create_task_due_time_without_due_date_raises_error(test_db: AsyncSession):
    """Test creating task with due_time but no due_date raises ValueError."""
    task_data = TaskCreate(title="Test Task", due_time=time(10, 0))
    with pytest.raises(ValueError, match="Due time requires a due date"):
        await create_task(test_db, "test_user_id", task_data)


@pytest.mark.asyncio
async def test_create_task_invalid_weekly_recurrence_day_raises_error(test_db: AsyncSession):
    """Test creating weekly recurring task with invalid recurrence_day raises ValueError."""
    task_data = TaskCreate(
        title="Weekly Task",
        recurrence=RecurrencePattern.WEEKLY,
        recurrence_day=8,  # Invalid day
    )
    with pytest.raises(ValueError, match="Weekly recurrence requires day 1-7"):
        await create_task(test_db, "test_user_id", task_data)


@pytest.mark.asyncio
async def test_create_task_invalid_monthly_recurrence_day_raises_error(test_db: AsyncSession):
    """Test creating monthly recurring task with invalid recurrence_day raises ValidationError."""
    with pytest.raises(Exception):  # Will catch the pydantic validation error during TaskCreate instantiation
        TaskCreate(
            title="Monthly Task",
            recurrence=RecurrencePattern.MONTHLY,
            recurrence_day=32,  # Invalid day
        )


@pytest.mark.asyncio
async def test_update_task_not_found_returns_none(test_db: AsyncSession):
    """Test updating a non-existent task returns None."""
    result = await update_task(test_db, 999, "test_user_id", TaskUpdate(title="Non-existent"))
    assert result is None


@pytest.mark.asyncio
async def test_update_task_due_time_without_due_date_raises_error(test_db: AsyncSession, test_task):
    """Test updating task to have due_time but no due_date raises ValueError."""
    update_data = TaskUpdate(due_time=time(10, 0), due_date=None)
    with pytest.raises(ValueError, match="Due time requires a due date"):
        await update_task(test_db, test_task.id, test_task.user_id, update_data)


@pytest.mark.asyncio
async def test_toggle_task_complete_not_found_returns_none(test_db: AsyncSession):
    """Test toggling completion of a non-existent task returns None."""
    result = await toggle_task_complete(test_db, 999, "test_user_id")
    assert result is None

