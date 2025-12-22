# Testing Patterns - Complete Examples

## Example 1: Complete Unit Test Suite for Task Model

### Test File Structure

```python
# tests/unit/models/test_task.py
"""
Complete unit tests for Task model.

Tests cover:
- Valid task creation
- Validation rules (title, description, tags)
- Edge cases and boundaries
- Default values
"""

import pytest
from datetime import datetime
from src.models.task import Task
from src.models.priority import Priority
from src.models.exceptions import ValidationError


class TestTaskCreation:
    """Test task initialization and defaults."""

    def test_create_task_with_required_fields_only(self) -> None:
        """Create task with only required fields."""
        task = Task(id=1, title="Buy groceries")

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description is None
        assert task.is_complete is False
        assert task.priority == Priority.MEDIUM
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.tags, set)
        assert len(task.tags) == 0

    def test_create_task_with_all_fields(self) -> None:
        """Create task with all optional fields."""
        created = datetime(2024, 1, 1, 12, 0, 0)
        tags = {"work", "urgent"}

        task = Task(
            id=42,
            title="Important meeting",
            description="Discuss Q4 roadmap",
            is_complete=True,
            created_at=created,
            priority=Priority.HIGH,
            tags=tags
        )

        assert task.id == 42
        assert task.title == "Important meeting"
        assert task.description == "Discuss Q4 roadmap"
        assert task.is_complete is True
        assert task.created_at == created
        assert task.priority == Priority.HIGH
        assert task.tags == tags


class TestTaskTitleValidation:
    """Test title field validation rules."""

    def test_empty_title_raises_validation_error(self) -> None:
        """Empty string title should raise ValidationError."""
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            Task(id=1, title="")

    def test_whitespace_only_title_raises_error(self) -> None:
        """Whitespace-only title should raise ValidationError."""
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            Task(id=1, title="   ")

        with pytest.raises(ValidationError, match="Title cannot be empty"):
            Task(id=1, title="\t\n  ")

    def test_title_exactly_max_length_succeeds(self) -> None:
        """Title with exactly 200 characters should succeed."""
        max_title = "x" * 200
        task = Task(id=1, title=max_title)

        assert len(task.title) == 200
        assert task.title == max_title

    def test_title_exceeds_max_length_raises_error(self) -> None:
        """Title with 201+ characters should raise ValidationError."""
        long_title = "x" * 201

        with pytest.raises(ValidationError, match="cannot exceed 200 characters"):
            Task(id=1, title=long_title)

    @pytest.mark.parametrize("length", [1, 50, 100, 199, 200])
    def test_valid_title_lengths(self, length: int) -> None:
        """Test various valid title lengths."""
        title = "x" * length
        task = Task(id=1, title=title)

        assert len(task.title) == length


class TestTaskDescriptionValidation:
    """Test description field validation rules."""

    def test_none_description_is_valid(self) -> None:
        """None description should be allowed."""
        task = Task(id=1, title="Valid")

        assert task.description is None

    def test_empty_description_is_valid(self) -> None:
        """Empty string description should be allowed."""
        task = Task(id=1, title="Valid", description="")

        assert task.description == ""

    def test_description_exactly_max_length_succeeds(self) -> None:
        """Description with exactly 1000 characters should succeed."""
        max_desc = "x" * 1000
        task = Task(id=1, title="Valid", description=max_desc)

        assert len(task.description) == 1000

    def test_description_exceeds_max_length_raises_error(self) -> None:
        """Description with 1001+ characters should raise ValidationError."""
        long_desc = "x" * 1001

        with pytest.raises(ValidationError, match="cannot exceed 1000 characters"):
            Task(id=1, title="Valid", description=long_desc)


class TestTaskTagValidation:
    """Test tag validation rules."""

    def test_empty_tags_set_is_valid(self) -> None:
        """Empty tags set should be allowed."""
        task = Task(id=1, title="Valid", tags=set())

        assert len(task.tags) == 0

    def test_valid_tag_formats(self) -> None:
        """Test valid tag formats."""
        valid_tags = {
            "work",
            "urgent",
            "project-2024",
            "sprint_3",
            "Q4",
            "alpha123"
        }

        task = Task(id=1, title="Valid", tags=valid_tags)

        assert task.tags == valid_tags

    def test_tag_exceeds_max_length_raises_error(self) -> None:
        """Tag exceeding 20 characters should raise ValidationError."""
        long_tag = "x" * 21

        with pytest.raises(ValidationError, match="exceeds 20 characters"):
            Task(id=1, title="Valid", tags={long_tag})

    @pytest.mark.parametrize("invalid_tag", [
        "tag with spaces",
        "tag@special",
        "tag#hashtag",
        "tag!exclaim",
        "tag.period",
    ])
    def test_invalid_tag_characters_raise_error(self, invalid_tag: str) -> None:
        """Tags with invalid characters should raise ValidationError."""
        with pytest.raises(ValidationError, match="invalid characters"):
            Task(id=1, title="Valid", tags={invalid_tag})
```

---

## Example 2: Complete Service Layer Tests with Fixtures

```python
# tests/unit/services/test_task_service.py
"""
Complete unit tests for TaskService.

Tests cover:
- CRUD operations (Create, Read, Update, Delete)
- Business logic validation
- Error handling
- Edge cases
"""

import pytest
from src.models.task import Task
from src.models.priority import Priority
from src.models.exceptions import TaskNotFoundError, ValidationError
from src.services.task_service import TaskService
from src.storage.in_memory_store import InMemoryTaskStore
from src.lib.id_generator import SequentialIdGenerator


# Fixtures in conftest.py or local

@pytest.fixture
def task_store() -> InMemoryTaskStore:
    """Create fresh in-memory store for each test."""
    return InMemoryTaskStore()


@pytest.fixture
def id_generator() -> SequentialIdGenerator:
    """Create ID generator starting at 1."""
    return SequentialIdGenerator(start=1)


@pytest.fixture
def task_service(
    task_store: InMemoryTaskStore,
    id_generator: SequentialIdGenerator
) -> TaskService:
    """Create configured TaskService."""
    return TaskService(store=task_store, id_gen=id_generator)


class TestTaskServiceAdd:
    """Test add() method."""

    def test_add_task_with_title_only(self, task_service: TaskService) -> None:
        """Add task with only title generates ID and stores it."""
        task = task_service.add(title="Buy groceries")

        assert isinstance(task, Task)
        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description is None
        assert not task.is_complete

    def test_add_task_with_all_parameters(self, task_service: TaskService) -> None:
        """Add task with all parameters."""
        task = task_service.add(
            title="Important meeting",
            description="Discuss Q4 roadmap",
            priority=Priority.HIGH,
            tags={"work", "urgent"}
        )

        assert task.id == 1
        assert task.title == "Important meeting"
        assert task.description == "Discuss Q4 roadmap"
        assert task.priority == Priority.HIGH
        assert task.tags == {"work", "urgent"}

    def test_add_multiple_tasks_increments_id(self, task_service: TaskService) -> None:
        """Adding multiple tasks increments ID sequentially."""
        task1 = task_service.add(title="Task 1")
        task2 = task_service.add(title="Task 2")
        task3 = task_service.add(title="Task 3")

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    def test_add_task_with_invalid_title_raises_error(
        self,
        task_service: TaskService
    ) -> None:
        """Add with invalid title raises ValidationError."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            task_service.add(title="")


class TestTaskServiceGet:
    """Test get() method."""

    def test_get_existing_task_returns_it(self, task_service: TaskService) -> None:
        """Get existing task by ID returns the task."""
        created = task_service.add(title="Test task")
        retrieved = task_service.get(created.id)

        assert retrieved.id == created.id
        assert retrieved.title == created.title

    def test_get_nonexistent_task_raises_error(
        self,
        task_service: TaskService
    ) -> None:
        """Get non-existent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError, match="Task #999 not found"):
            task_service.get(999)

    def test_get_after_delete_raises_error(self, task_service: TaskService) -> None:
        """Get task after deletion raises TaskNotFoundError."""
        task = task_service.add(title="To delete")
        task_service.delete(task.id)

        with pytest.raises(TaskNotFoundError):
            task_service.get(task.id)


class TestTaskServiceAll:
    """Test all() method."""

    def test_all_returns_empty_list_initially(self, task_service: TaskService) -> None:
        """All() returns empty list when no tasks exist."""
        tasks = task_service.all()

        assert tasks == []

    def test_all_returns_all_tasks(self, task_service: TaskService) -> None:
        """All() returns all added tasks."""
        task_service.add(title="Task 1")
        task_service.add(title="Task 2")
        task_service.add(title="Task 3")

        tasks = task_service.all()

        assert len(tasks) == 3

    def test_all_returns_tasks_sorted_by_id(self, task_service: TaskService) -> None:
        """All() returns tasks sorted by ID in ascending order."""
        task_service.add(title="First")
        task_service.add(title="Second")
        task_service.add(title="Third")

        tasks = task_service.all()

        assert [t.id for t in tasks] == [1, 2, 3]
        assert [t.title for t in tasks] == ["First", "Second", "Third"]


class TestTaskServiceUpdate:
    """Test update() method."""

    def test_update_task_title(self, task_service: TaskService) -> None:
        """Update changes title while preserving other fields."""
        task = task_service.add(title="Original", description="Original desc")

        updated = task_service.update(task.id, title="Updated")

        assert updated.id == task.id
        assert updated.title == "Updated"
        assert updated.description == "Original desc"

    def test_update_task_description(self, task_service: TaskService) -> None:
        """Update changes description while preserving title."""
        task = task_service.add(title="Original", description="Original desc")

        updated = task_service.update(task.id, description="New desc")

        assert updated.title == "Original"
        assert updated.description == "New desc"

    def test_update_nonexistent_task_raises_error(
        self,
        task_service: TaskService
    ) -> None:
        """Update non-existent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            task_service.update(999, title="New title")

    def test_update_with_invalid_data_raises_error(
        self,
        task_service: TaskService
    ) -> None:
        """Update with invalid data raises ValidationError."""
        task = task_service.add(title="Original")

        with pytest.raises(ValidationError):
            task_service.update(task.id, title="")


class TestTaskServiceDelete:
    """Test delete() method."""

    def test_delete_existing_task_removes_it(
        self,
        task_service: TaskService
    ) -> None:
        """Delete removes task from storage."""
        task = task_service.add(title="To delete")

        task_service.delete(task.id)

        with pytest.raises(TaskNotFoundError):
            task_service.get(task.id)

    def test_delete_nonexistent_task_raises_error(
        self,
        task_service: TaskService
    ) -> None:
        """Delete non-existent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            task_service.delete(999)

    def test_delete_reduces_all_count(self, task_service: TaskService) -> None:
        """Delete reduces count returned by all()."""
        task_service.add(title="Task 1")
        task_service.add(title="Task 2")
        task_to_delete = task_service.add(title="Task 3")

        assert len(task_service.all()) == 3

        task_service.delete(task_to_delete.id)

        assert len(task_service.all()) == 2


class TestTaskServiceToggleComplete:
    """Test toggle_complete() method."""

    def test_toggle_incomplete_to_complete(self, task_service: TaskService) -> None:
        """Toggle changes incomplete task to complete."""
        task = task_service.add(title="Task")
        assert not task.is_complete

        toggled = task_service.toggle_complete(task.id)

        assert toggled.is_complete

    def test_toggle_complete_to_incomplete(self, task_service: TaskService) -> None:
        """Toggle changes complete task to incomplete."""
        task = task_service.add(title="Task")
        task_service.toggle_complete(task.id)

        toggled_again = task_service.toggle_complete(task.id)

        assert not toggled_again.is_complete

    def test_toggle_nonexistent_task_raises_error(
        self,
        task_service: TaskService
    ) -> None:
        """Toggle non-existent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            task_service.toggle_complete(999)
```

---

## Example 3: Integration Tests for CLI Commands

```python
# tests/integration/test_cli_commands.py
"""
Integration tests for CLI commands using CliRunner.

Tests full command flow from user input to output.
"""

import pytest
from typer.testing import CliRunner
from src.main import app

runner = CliRunner()


class TestAddCommand:
    """Test 'todo add' command."""

    def test_add_task_success(self) -> None:
        """Add task with valid title succeeds."""
        result = runner.invoke(app, ["add", "Buy milk"])

        assert result.exit_code == 0
        assert "created" in result.stdout.lower()
        assert "Buy milk" in result.stdout

    def test_add_task_with_description(self) -> None:
        """Add task with --desc option succeeds."""
        result = runner.invoke(app, [
            "add",
            "Buy milk",
            "--desc", "From grocery store"
        ])

        assert result.exit_code == 0
        assert "created" in result.stdout.lower()

    def test_add_task_with_priority(self) -> None:
        """Add task with --priority option succeeds."""
        result = runner.invoke(app, [
            "add",
            "Important task",
            "--priority", "high"
        ])

        assert result.exit_code == 0
        assert "created" in result.stdout.lower()

    def test_add_task_empty_title_fails(self) -> None:
        """Add with empty title returns error code."""
        result = runner.invoke(app, ["add", ""])

        assert result.exit_code == 1
        assert "error" in result.stdout.lower()


class TestListCommand:
    """Test 'todo list' command."""

    def test_list_empty_tasks(self) -> None:
        """List with no tasks shows appropriate message."""
        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        # Check for empty state message

    def test_list_shows_added_tasks(self) -> None:
        """List shows tasks after adding them."""
        # Add tasks
        runner.invoke(app, ["add", "Task 1"])
        runner.invoke(app, ["add", "Task 2"])

        # List tasks
        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "Task 1" in result.stdout
        assert "Task 2" in result.stdout


class TestCompleteCommand:
    """Test 'todo complete' command."""

    def test_complete_existing_task(self) -> None:
        """Complete marks task as done."""
        # Add task
        add_result = runner.invoke(app, ["add", "Task to complete"])
        assert add_result.exit_code == 0

        # Complete task (assuming ID 1)
        complete_result = runner.invoke(app, ["complete", "1"])

        assert complete_result.exit_code == 0
        assert "completed" in complete_result.stdout.lower()

    def test_complete_nonexistent_task_fails(self) -> None:
        """Complete non-existent task returns error."""
        result = runner.invoke(app, ["complete", "999"])

        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()
```

---

## Example 4: Parametrized Tests for Multiple Scenarios

```python
# tests/unit/test_validation_rules.py
"""
Parametrized tests for validation rules.
"""

import pytest
from src.models.task import Task
from src.models.exceptions import ValidationError


class TestTitleValidationParametrized:
    """Parametrized tests for title validation."""

    @pytest.mark.parametrize("title,should_pass", [
        ("Valid title", True),
        ("x" * 200, True),  # Max length
        ("x" * 201, False),  # Over max
        ("", False),  # Empty
        ("   ", False),  # Whitespace
        ("a", True),  # Min length
    ])
    def test_title_validation(self, title: str, should_pass: bool) -> None:
        """Test various title inputs."""
        if should_pass:
            task = Task(id=1, title=title)
            assert task.title == title
        else:
            with pytest.raises(ValidationError):
                Task(id=1, title=title)


class TestTagValidationParametrized:
    """Parametrized tests for tag validation."""

    @pytest.mark.parametrize("tag,should_pass,reason", [
        pytest.param("valid", True, id="simple_tag"),
        pytest.param("valid-tag", True, id="hyphen_allowed"),
        pytest.param("valid_tag", True, id="underscore_allowed"),
        pytest.param("tag123", True, id="numbers_allowed"),
        pytest.param("x" * 20, True, id="max_length"),
        pytest.param("x" * 21, False, id="exceeds_max_length"),
        pytest.param("tag with space", False, id="space_not_allowed"),
        pytest.param("tag@special", False, id="special_char_not_allowed"),
    ])
    def test_tag_validation(self, tag: str, should_pass: bool, reason: str) -> None:
        """Test various tag formats."""
        if should_pass:
            task = Task(id=1, title="Test", tags={tag})
            assert tag in task.tags
        else:
            with pytest.raises(ValidationError):
                Task(id=1, title="Test", tags={tag})
```

---

## Example 5: Fixture Factories and Advanced Patterns

```python
# tests/conftest.py
"""
Shared fixtures for all tests.
"""

import pytest
from typing import Callable
from src.models.task import Task
from src.models.priority import Priority
from src.services.task_service import TaskService
from src.storage.in_memory_store import InMemoryTaskStore
from src.lib.id_generator import SequentialIdGenerator


@pytest.fixture
def task_store() -> InMemoryTaskStore:
    """Fresh in-memory store."""
    return InMemoryTaskStore()


@pytest.fixture
def id_gen() -> SequentialIdGenerator:
    """ID generator starting at 1."""
    return SequentialIdGenerator(start=1)


@pytest.fixture
def task_service(task_store, id_gen) -> TaskService:
    """Configured task service."""
    return TaskService(store=task_store, id_gen=id_gen)


@pytest.fixture
def make_task() -> Callable:
    """Factory to create custom tasks."""
    def _make(
        id: int = 1,
        title: str = "Test task",
        **kwargs
    ) -> Task:
        return Task(id=id, title=title, **kwargs)
    return _make


@pytest.fixture
def sample_tasks(make_task) -> list[Task]:
    """Create sample tasks for testing."""
    return [
        make_task(id=1, title="Task A", priority=Priority.HIGH),
        make_task(id=2, title="Task B", priority=Priority.MEDIUM, is_complete=True),
        make_task(id=3, title="Task C", priority=Priority.LOW),
    ]


# Usage in tests
def test_with_factory(make_task):
    """Use factory to create custom tasks."""
    urgent_task = make_task(
        id=42,
        title="Urgent",
        priority=Priority.HIGH,
        tags={"urgent", "work"}
    )

    assert urgent_task.id == 42
    assert urgent_task.priority == Priority.HIGH


def test_with_sample_tasks(sample_tasks):
    """Use pre-created sample tasks."""
    assert len(sample_tasks) == 3
    assert sample_tasks[0].priority == Priority.HIGH
    assert sample_tasks[1].is_complete
```

---

## Summary of Testing Patterns Demonstrated

1. **AAA Pattern**: Arrange-Act-Assert structure in all tests
2. **Fixtures**: Reusable test setup with pytest fixtures
3. **Parametrization**: Test multiple scenarios efficiently
4. **Exception Testing**: Verify errors are raised correctly
5. **CLI Testing**: Integration tests with CliRunner
6. **Fixture Factories**: Create custom test data on demand
7. **Test Organization**: Logical grouping in test classes
8. **Edge Cases**: Boundary testing (min/max lengths)
9. **Error Paths**: Testing failure scenarios
10. **Integration Tests**: Full command flow testing
