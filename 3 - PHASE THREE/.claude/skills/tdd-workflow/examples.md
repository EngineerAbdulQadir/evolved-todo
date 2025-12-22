# TDD Workflow Examples

## Example 1: Implementing TaskService.add() (T019-T020)

### Red Phase: Write Failing Test

```python
# tests/unit/test_task_service.py
import pytest
from src.services.task_service import TaskService
from src.models.task import Task

class TestTaskServiceAdd:
    def test_add_task_creates_task_with_id(self, task_service):
        """Adding a task should return Task with sequential ID."""
        # Arrange
        title = "Buy groceries"
        description = "Milk, eggs, bread"

        # Act
        task = task_service.add(title=title, description=description)

        # Assert
        assert isinstance(task, Task)
        assert task.id == 1
        assert task.title == title
        assert task.description == description
        assert not task.is_complete
```

**Run test:**
```bash
$ uv run pytest tests/unit/test_task_service.py::TestTaskServiceAdd::test_add_task_creates_task_with_id -v

FAILED tests/unit/test_task_service.py::TestTaskServiceAdd::test_add_task_creates_task_with_id
AttributeError: 'TaskService' object has no attribute 'add'
```

✅ **Test fails as expected** (method doesn't exist yet)

**Commit:**
```bash
git add tests/unit/test_task_service.py
git commit -m "test(task-service): add failing test for task creation"
```

### Green Phase: Make Test Pass

```python
# src/services/task_service.py
from typing import Optional
from src.models.task import Task
from src.services.task_store import TaskStore
from src.lib.id_generator import IdGenerator

class TaskService:
    def __init__(self, store: TaskStore, id_gen: IdGenerator) -> None:
        self._store = store
        self._id_gen = id_gen

    def add(self, title: str, description: Optional[str] = None) -> Task:
        """Create a new task."""
        task = Task(
            id=self._id_gen.next(),
            title=title,
            description=description,
        )
        self._store.save(task)
        return task
```

**Run test:**
```bash
$ uv run pytest tests/unit/test_task_service.py::TestTaskServiceAdd::test_add_task_creates_task_with_id -v

PASSED tests/unit/test_task_service.py::TestTaskServiceAdd::test_add_task_creates_task_with_id ✓
```

✅ **Test passes**

**Commit:**
```bash
git add src/services/task_service.py
git commit -m "feat(task-service): implement task creation with ID generation"
```

### Refactor Phase: Improve Quality

**Run quality checks:**
```bash
$ uv run mypy --strict src/
Success: no issues found in 15 source files

$ uv run ruff check src/ tests/
All checks passed!

$ uv run pytest
======================== 12 passed in 0.45s ========================
```

✅ **All quality gates pass** - No refactoring needed

---

## Example 2: Implementing Task Title Validation (T021-T022)

### Red Phase: Write Multiple Failing Tests

```python
# tests/unit/test_models.py
import pytest
from src.models.task import Task
from src.models.exceptions import ValidationError

class TestTaskTitleValidation:
    def test_valid_title_accepted(self):
        """Valid title (1-200 chars) should be accepted."""
        task = Task(id=1, title="Buy milk")
        assert task.title == "Buy milk"

    def test_empty_title_rejected(self):
        """Empty title should raise ValidationError."""
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            Task(id=1, title="")

    def test_whitespace_title_rejected(self):
        """Whitespace-only title should raise ValidationError."""
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            Task(id=1, title="   ")

    def test_title_max_length_200_accepted(self):
        """Title with exactly 200 chars should be accepted."""
        title = "x" * 200
        task = Task(id=1, title=title)
        assert len(task.title) == 200

    def test_title_exceeds_200_rejected(self):
        """Title exceeding 200 chars should raise ValidationError."""
        title = "x" * 201
        with pytest.raises(ValidationError, match="cannot exceed 200 characters"):
            Task(id=1, title=title)
```

**Run tests:**
```bash
$ uv run pytest tests/unit/test_models.py::TestTaskTitleValidation -v

FAILED test_empty_title_rejected - No validation implemented
FAILED test_whitespace_title_rejected - No validation implemented
PASSED test_valid_title_accepted ✓
PASSED test_title_max_length_200_accepted ✓
FAILED test_title_exceeds_200_rejected - No validation implemented

3 passed, 2 failed in 0.12s
```

✅ **Some tests fail** (validation not implemented)

**Commit:**
```bash
git add tests/unit/test_models.py
git commit -m "test(models): add failing tests for title validation"
```

### Green Phase: Implement Validation

```python
# src/models/task.py
from dataclasses import dataclass
from typing import Optional
from src.models.exceptions import ValidationError

@dataclass
class Task:
    id: int
    title: str
    description: Optional[str] = None
    is_complete: bool = False

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        self._validate_title()

    def _validate_title(self) -> None:
        """Validate title: 1-200 chars, non-empty."""
        if not self.title or not self.title.strip():
            raise ValidationError("Title cannot be empty")
        if len(self.title) > 200:
            raise ValidationError("Title cannot exceed 200 characters")
```

**Run tests:**
```bash
$ uv run pytest tests/unit/test_models.py::TestTaskTitleValidation -v

PASSED test_empty_title_rejected ✓
PASSED test_whitespace_title_rejected ✓
PASSED test_valid_title_accepted ✓
PASSED test_title_max_length_200_accepted ✓
PASSED test_title_exceeds_200_rejected ✓

5 passed in 0.08s
```

✅ **All tests pass**

**Commit:**
```bash
git add src/models/task.py
git commit -m "feat(models): implement title validation (1-200 chars)"
```

### Refactor Phase: Type Safety

**Run mypy:**
```bash
$ uv run mypy --strict src/

src/models/task.py:15: error: Missing return type annotation for __post_init__
```

**Fix type error:**
```python
def __post_init__(self) -> None:  # Add return type
    """Validate fields after initialization."""
    self._validate_title()
```

**Re-run checks:**
```bash
$ uv run mypy --strict src/
Success: no issues found ✓

$ uv run pytest
======================== 18 passed in 0.52s ======================== ✓
```

**Commit:**
```bash
git add src/models/task.py
git commit -m "refactor(models): add missing type annotations"
```

---

## Example 3: Full Feature Implementation (US1 - Add Task)

### Complete TDD Cycle for Phase 3

**T019-T023: Models + Services (5 tasks)**

```bash
# 1. Red: Write all tests
git commit -m "test(models): add failing tests for Task validation"
git commit -m "test(task-service): add failing tests for add() method"

# 2. Green: Implement minimal code
git commit -m "feat(models): implement Task with validation"
git commit -m "feat(task-service): implement add() method"

# 3. Refactor: Quality checks
uv run mypy --strict src/
uv run ruff check --fix src/ tests/
uv run pytest --cov=src --cov-fail-under=90
git commit -m "refactor: improve type safety and code style"
```

**T024-T026: CLI (3 tasks)**

```bash
# 1. Red: Write integration test
git commit -m "test(cli): add failing test for add command"

# 2. Green: Implement CLI command
git commit -m "feat(cli): implement add command with --desc option"

# 3. Refactor: UX improvements
git commit -m "refactor(cli): improve error messages and formatting"
```

**Phase completion check:**
```bash
$ uv run pytest -v
======================== 35 passed in 1.23s ========================

$ uv run pytest --cov=src --cov-fail-under=90
---------- coverage: 94% -----------

$ uv run mypy --strict src/
Success: no issues found

$ uv run ruff check src/ tests/
All checks passed!
```

✅ **Phase 3 complete** - Ready to move to Phase 4

---

## Example 4: Handling Test Failures During Development

### Scenario: Implementing due date parsing

**Red phase test:**
```python
def test_parse_relative_due_date():
    """Parse 'tomorrow' should return next day."""
    result = parse_due_date("tomorrow")
    expected = datetime.now().date() + timedelta(days=1)
    assert result == expected
```

**First implementation attempt:**
```python
def parse_due_date(date_str: str) -> date:
    """Parse natural language dates."""
    if date_str == "tomorrow":
        return datetime.now().date() + timedelta(days=1)
    raise ValueError(f"Unknown date format: {date_str}")
```

**Run test:**
```bash
$ uv run pytest tests/unit/test_date_parser.py::test_parse_relative_due_date -v

FAILED - AssertionError: 2025-12-07 != 2025-12-08
```

❌ **Test fails** - Off-by-one error at midnight

**Debug and fix:**
```python
def parse_due_date(date_str: str) -> date:
    """Parse natural language dates."""
    today = datetime.now().date()  # Calculate once
    if date_str == "tomorrow":
        return today + timedelta(days=1)
    raise ValueError(f"Unknown date format: {date_str}")
```

**Re-run test:**
```bash
$ uv run pytest tests/unit/test_date_parser.py::test_parse_relative_due_date -v

PASSED ✓
```

✅ **Test passes** after fix

---

## Time Tracking Example

Track time spent in each TDD phase:

```bash
# Start timer for Red phase
$ time uv run pytest tests/unit/test_task_service.py -v
# 0m 0.124s - Write tests

# Start timer for Green phase
$ time uv run pytest tests/unit/test_task_service.py -v
# 0m 0.089s - Implement code

# Start timer for Refactor phase
$ time uv run mypy --strict src/ && uv run ruff check src/
# 0m 0.512s - Quality checks
```

**Goal**: Minimize time in each phase for faster iteration
