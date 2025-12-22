---
name: testing-patterns
description: Write comprehensive unit and integration tests using pytest with fixtures, parametrization, and >90% coverage. Use for all test tasks (T019, T021, T025, etc.).
---

# Testing Patterns

## Instructions

Follow these patterns when writing tests:

### Test Structure

```
tests/
├── unit/           # Fast, isolated tests
│   ├── test_models.py
│   ├── test_task_service.py
│   ├── test_search_service.py
│   └── test_date_parser.py
├── integration/    # CLI command tests
│   ├── test_cli_add.py
│   ├── test_cli_view.py
│   └── test_cli_update.py
└── conftest.py     # Shared fixtures
```

### Fixture Patterns (conftest.py)

## Examples

### Example 1: Shared Fixtures

```python
import pytest
from src.models.task import Task
from src.models.priority import Priority
from src.services.task_store import InMemoryTaskStore
from src.services.task_service import TaskService
from src.lib.id_generator import IdGenerator

@pytest.fixture
def task_store() -> InMemoryTaskStore:
    """Fresh in-memory store for each test."""
    return InMemoryTaskStore()

@pytest.fixture
def id_generator() -> IdGenerator:
    """ID generator starting at 1."""
    return IdGenerator()

@pytest.fixture
def task_service(task_store, id_generator) -> TaskService:
    """Configured task service."""
    return TaskService(store=task_store, id_gen=id_generator)

@pytest.fixture
def sample_task() -> Task:
    """Sample task for testing."""
    return Task(
        id=1,
        title="Buy groceries",
        description="Milk, eggs, bread",
        priority=Priority.HIGH,
        tags={"shopping", "urgent"},
    )

@pytest.fixture
def multiple_tasks() -> list[Task]:
    """Multiple tasks for testing."""
    return [
        Task(id=1, title="Task A", priority=Priority.HIGH),
        Task(id=2, title="Task B", priority=Priority.MEDIUM, is_complete=True),
        Task(id=3, title="Task C", priority=Priority.LOW),
    ]
```

## Unit Test Patterns

### Testing Models (Validation)

```python
# tests/unit/test_models.py
import pytest
from src.models.task import Task
from src.models.priority import Priority
from src.models.exceptions import ValidationError

class TestTaskValidation:
    """Test Task validation logic."""

    def test_valid_task_creation(self):
        """Valid task should initialize successfully."""
        task = Task(id=1, title="Valid title", description="Valid description")
        assert task.id == 1
        assert task.title == "Valid title"
        assert not task.is_complete

    def test_empty_title_raises_error(self):
        """Empty title should raise ValidationError."""
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            Task(id=1, title="")

    def test_whitespace_title_raises_error(self):
        """Whitespace-only title should raise ValidationError."""
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            Task(id=1, title="   ")

    def test_title_exceeds_max_length(self):
        """Title >200 chars should raise ValidationError."""
        long_title = "x" * 201
        with pytest.raises(ValidationError, match="cannot exceed 200 characters"):
            Task(id=1, title=long_title)

    def test_description_exceeds_max_length(self):
        """Description >1000 chars should raise ValidationError."""
        long_desc = "x" * 1001
        with pytest.raises(ValidationError, match="cannot exceed 1000 characters"):
            Task(id=1, title="Valid", description=long_desc)

    def test_none_description_is_valid(self):
        """None description should be allowed."""
        task = Task(id=1, title="Valid")
        assert task.description is None

    @pytest.mark.parametrize("tag,should_pass", [
        ("valid-tag", True),
        ("valid_tag", True),
        ("tag123", True),
        ("tag with spaces", False),
        ("tag@special", False),
        ("x" * 21, False),  # >20 chars
    ])
    def test_tag_validation(self, tag, should_pass):
        """Test various tag formats."""
        if should_pass:
            task = Task(id=1, title="Valid", tags={tag})
            assert tag in task.tags
        else:
            with pytest.raises(ValidationError):
                Task(id=1, title="Valid", tags={tag})
```

### Testing Services (Business Logic)

```python
# tests/unit/test_task_service.py
import pytest
from src.services.task_service import TaskService
from src.models.priority import Priority
from src.models.exceptions import TaskNotFoundError, ValidationError

class TestTaskService:
    """Test TaskService business logic."""

    def test_add_task_success(self, task_service):
        """Adding valid task should return Task with ID."""
        task = task_service.add(title="New task", description="Details")

        assert task.id == 1
        assert task.title == "New task"
        assert task.description == "Details"
        assert not task.is_complete

    def test_add_multiple_tasks_increments_id(self, task_service):
        """Sequential adds should increment IDs."""
        task1 = task_service.add(title="Task 1")
        task2 = task_service.add(title="Task 2")

        assert task1.id == 1
        assert task2.id == 2

    def test_add_task_validation_error(self, task_service):
        """Adding invalid task should raise ValidationError."""
        with pytest.raises(ValidationError):
            task_service.add(title="")  # Empty title

    def test_get_existing_task(self, task_service):
        """Getting existing task should return it."""
        added = task_service.add(title="Task")
        retrieved = task_service.get(added.id)

        assert retrieved.id == added.id
        assert retrieved.title == added.title

    def test_get_nonexistent_task_raises_error(self, task_service):
        """Getting nonexistent task should raise TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError, match="Task #999 not found"):
            task_service.get(999)

    def test_all_returns_sorted_by_id(self, task_service):
        """All tasks should be sorted by ID."""
        task_service.add(title="Task 1")
        task_service.add(title="Task 2")
        task_service.add(title="Task 3")

        tasks = task_service.all()
        assert len(tasks) == 3
        assert [t.id for t in tasks] == [1, 2, 3]

    def test_update_partial_fields(self, task_service):
        """Update should only change provided fields."""
        task = task_service.add(title="Original", description="Original desc")

        updated = task_service.update(task.id, title="Updated")

        assert updated.title == "Updated"
        assert updated.description == "Original desc"  # Unchanged

    def test_delete_existing_task(self, task_service):
        """Deleting existing task should remove it."""
        task = task_service.add(title="To delete")
        task_service.delete(task.id)

        with pytest.raises(TaskNotFoundError):
            task_service.get(task.id)

    def test_toggle_complete(self, task_service):
        """Toggle should flip completion status."""
        task = task_service.add(title="Task")
        assert not task.is_complete

        task_service.toggle_complete(task.id)
        updated = task_service.get(task.id)
        assert updated.is_complete

        task_service.toggle_complete(task.id)
        updated_again = task_service.get(task.id)
        assert not updated_again.is_complete
```

## Integration Test Patterns (CLI)

```python
# tests/integration/test_cli_add.py
from typer.testing import CliRunner
from src.main import app

runner = CliRunner()

class TestAddCommand:
    """Test 'todo add' CLI command."""

    def test_add_task_with_title_only(self):
        """Add task with just title should succeed."""
        result = runner.invoke(app, ["add", "Buy milk"])

        assert result.exit_code == 0
        assert "created" in result.stdout.lower()
        assert "Buy milk" in result.stdout

    def test_add_task_with_description(self):
        """Add task with --desc option should succeed."""
        result = runner.invoke(app, ["add", "Buy milk", "--desc", "From store"])

        assert result.exit_code == 0
        assert "created" in result.stdout.lower()

    def test_add_task_empty_title_fails(self):
        """Empty title should fail with error message."""
        result = runner.invoke(app, ["add", ""])

        assert result.exit_code == 1
        assert "error" in result.stdout.lower()

    def test_add_task_with_priority(self):
        """Add task with --priority option should succeed."""
        result = runner.invoke(app, ["add", "Important task", "--priority", "high"])

        assert result.exit_code == 0
        assert "created" in result.stdout.lower()

    def test_add_task_with_tags(self):
        """Add task with --tags option should succeed."""
        result = runner.invoke(app, ["add", "Task", "--tags", "work,urgent"])

        assert result.exit_code == 0
        assert "created" in result.stdout.lower()
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_models.py

# Run specific test
uv run pytest tests/unit/test_models.py::test_valid_task_creation

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run with coverage threshold
uv run pytest --cov=src --cov-fail-under=90

# Run verbose
uv run pytest -v

# Run with print statements
uv run pytest -s
```

## Coverage Requirements

- **Overall**: >90% code coverage
- **Unit tests**: All business logic paths
- **Integration tests**: All CLI commands and options
- **Edge cases**: Validation errors, boundary conditions
- **Error paths**: Exception handling

## Integration with Subagents

- **test-guardian**: Verify test quality and TDD compliance after implementation
- **performance-optimizer**: Benchmark critical test operations
