# Model & Service Layer - Implementation Examples

## Example 1: Complete Task Model (T009-T015)

### Phase: RED - Write failing tests first

```python
# tests/unit/models/test_task.py
import pytest
from datetime import datetime
from src.models.task import Task
from src.models.priority import Priority
from src.models.exceptions import ValidationError


class TestTaskModel:
    """Test Task model validation and behavior."""

    def test_create_minimal_task(self) -> None:
        """Create task with only required fields."""
        task = Task(id=1, title="Buy groceries")

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description is None
        assert task.is_complete is False
        assert isinstance(task.created_at, datetime)

    def test_title_cannot_be_empty(self) -> None:
        """Title validation: cannot be empty or whitespace."""
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            Task(id=1, title="")

        with pytest.raises(ValidationError, match="Title cannot be empty"):
            Task(id=1, title="   ")

    def test_title_max_length_200(self) -> None:
        """Title validation: max 200 characters."""
        # Exactly 200 chars should succeed
        valid_title = "x" * 200
        task = Task(id=1, title=valid_title)
        assert len(task.title) == 200

        # 201 chars should fail
        invalid_title = "x" * 201
        with pytest.raises(ValidationError, match="cannot exceed 200"):
            Task(id=1, title=invalid_title)

    def test_description_max_length_1000(self) -> None:
        """Description validation: max 1000 characters."""
        valid_desc = "x" * 1000
        task = Task(id=1, title="Test", description=valid_desc)
        assert len(task.description) == 1000

        invalid_desc = "x" * 1001
        with pytest.raises(ValidationError, match="cannot exceed 1000"):
            Task(id=1, title="Test", description=invalid_desc)

    def test_tags_validation(self) -> None:
        """Tag validation: alphanumeric + hyphens, max 20 chars."""
        # Valid tags
        valid_tags = {"work", "urgent-task", "project_2024"}
        task = Task(id=1, title="Test", tags=valid_tags)
        assert task.tags == valid_tags

        # Tag too long
        with pytest.raises(ValidationError, match="exceeds 20 characters"):
            Task(id=1, title="Test", tags={"this_is_a_very_long_tag_name"})

        # Invalid characters
        with pytest.raises(ValidationError, match="invalid characters"):
            Task(id=1, title="Test", tags={"invalid@tag"})
```

### Phase: GREEN - Minimal implementation

```python
# src/models/exceptions.py
class TodoAppError(Exception):
    """Base exception for all app errors."""

class ValidationError(TodoAppError):
    """Raised when input validation fails."""

class TaskNotFoundError(TodoAppError):
    """Raised when task ID doesn't exist."""
```

```python
# src/models/priority.py
from enum import Enum

class Priority(Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
```

```python
# src/models/task.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Set
from src.models.exceptions import ValidationError
from src.models.priority import Priority


@dataclass
class Task:
    """Represents a single todo task."""

    id: int
    title: str
    description: Optional[str] = None
    is_complete: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    priority: Priority = Priority.MEDIUM
    tags: Set[str] = field(default_factory=set)
    due_date: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validate on initialization."""
        self._validate_title()
        self._validate_description()
        self._validate_tags()

    def _validate_title(self) -> None:
        """Title: 1-200 chars, non-empty."""
        if not self.title or not self.title.strip():
            raise ValidationError("Title cannot be empty")
        if len(self.title) > 200:
            raise ValidationError("Title cannot exceed 200 characters")

    def _validate_description(self) -> None:
        """Description: max 1000 chars if provided."""
        if self.description and len(self.description) > 1000:
            raise ValidationError("Description cannot exceed 1000 characters")

    def _validate_tags(self) -> None:
        """Tags: alphanumeric + hyphens/underscores, max 20 chars each."""
        for tag in self.tags:
            if len(tag) > 20:
                raise ValidationError(f"Tag '{tag}' exceeds 20 characters")
            if not tag.replace("-", "").replace("_", "").isalnum():
                raise ValidationError(f"Tag '{tag}' contains invalid characters")
```

### Phase: REFACTOR - Add type checking and docs

```bash
# Run quality checks
uv run mypy --strict src/models/
uv run ruff check src/models/ tests/unit/models/
uv run pytest tests/unit/models/ -v --cov=src/models
```

---

## Example 2: TaskService Implementation (T016-T020)

### Phase: RED - Service tests

```python
# tests/unit/services/test_task_service.py
import pytest
from src.models.task import Task
from src.models.priority import Priority
from src.models.exceptions import TaskNotFoundError, ValidationError
from src.services.task_service import TaskService
from src.storage.in_memory_store import InMemoryTaskStore
from src.lib.id_generator import SequentialIdGenerator


class TestTaskService:
    """Test TaskService business logic."""

    @pytest.fixture
    def task_service(self) -> TaskService:
        """Create service with in-memory storage."""
        store = InMemoryTaskStore()
        id_gen = SequentialIdGenerator()
        return TaskService(store=store, id_gen=id_gen)

    def test_add_task_creates_with_id(self, task_service: TaskService) -> None:
        """Add task generates ID and stores it."""
        task = task_service.add(title="Buy groceries")

        assert isinstance(task, Task)
        assert task.id == 1
        assert task.title == "Buy groceries"
        assert not task.is_complete

    def test_add_task_with_all_fields(self, task_service: TaskService) -> None:
        """Add task with optional fields."""
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

    def test_add_task_with_invalid_title_raises(
        self,
        task_service: TaskService
    ) -> None:
        """Add task validates title."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            task_service.add(title="")

    def test_get_task_by_id(self, task_service: TaskService) -> None:
        """Get existing task by ID."""
        created = task_service.add(title="Test task")
        retrieved = task_service.get(created.id)

        assert retrieved.id == created.id
        assert retrieved.title == created.title

    def test_get_nonexistent_task_raises(
        self,
        task_service: TaskService
    ) -> None:
        """Get non-existent task raises error."""
        with pytest.raises(TaskNotFoundError, match="Task #999 not found"):
            task_service.get(999)

    def test_all_returns_tasks_sorted_by_id(
        self,
        task_service: TaskService
    ) -> None:
        """All tasks returned sorted by ID."""
        task_service.add(title="Task 3")
        task_service.add(title="Task 1")
        task_service.add(title="Task 2")

        tasks = task_service.all()

        assert len(tasks) == 3
        assert tasks[0].id == 1
        assert tasks[1].id == 2
        assert tasks[2].id == 3

    def test_update_task_title(self, task_service: TaskService) -> None:
        """Update task title."""
        task = task_service.add(title="Original title")

        updated = task_service.update(
            task_id=task.id,
            title="Updated title"
        )

        assert updated.title == "Updated title"
        assert updated.id == task.id

    def test_update_nonexistent_task_raises(
        self,
        task_service: TaskService
    ) -> None:
        """Update non-existent task raises error."""
        with pytest.raises(TaskNotFoundError):
            task_service.update(task_id=999, title="New title")

    def test_delete_task(self, task_service: TaskService) -> None:
        """Delete task removes it from storage."""
        task = task_service.add(title="To delete")
        task_service.delete(task.id)

        with pytest.raises(TaskNotFoundError):
            task_service.get(task.id)

    def test_toggle_complete(self, task_service: TaskService) -> None:
        """Toggle task completion status."""
        task = task_service.add(title="Test task")
        assert not task.is_complete

        # Toggle to complete
        toggled = task_service.toggle_complete(task.id)
        assert toggled.is_complete

        # Toggle back to incomplete
        toggled_again = task_service.toggle_complete(task.id)
        assert not toggled_again.is_complete
```

### Phase: GREEN - Implement TaskService

```python
# src/lib/id_generator.py
from abc import ABC, abstractmethod


class IdGenerator(ABC):
    """Abstract ID generator."""

    @abstractmethod
    def next(self) -> int:
        """Generate next ID."""
        pass


class SequentialIdGenerator(IdGenerator):
    """Sequential integer ID generator."""

    def __init__(self, start: int = 1) -> None:
        self._current = start

    def next(self) -> int:
        """Return next sequential ID."""
        id_val = self._current
        self._current += 1
        return id_val
```

```python
# src/storage/in_memory_store.py
from typing import Dict, List, Optional
from src.models.task import Task


class InMemoryTaskStore:
    """In-memory task storage."""

    def __init__(self) -> None:
        self._tasks: Dict[int, Task] = {}

    def save(self, task: Task) -> None:
        """Save or update task."""
        self._tasks[task.id] = task

    def get(self, task_id: int) -> Optional[Task]:
        """Get task by ID."""
        return self._tasks.get(task_id)

    def all(self) -> List[Task]:
        """Get all tasks."""
        return list(self._tasks.values())

    def delete(self, task_id: int) -> None:
        """Delete task."""
        self._tasks.pop(task_id, None)
```

```python
# src/services/task_service.py
from typing import List, Optional, Set
from src.models.task import Task
from src.models.priority import Priority
from src.models.exceptions import TaskNotFoundError
from src.storage.in_memory_store import InMemoryTaskStore
from src.lib.id_generator import IdGenerator


class TaskService:
    """Business logic for task operations."""

    def __init__(
        self,
        store: InMemoryTaskStore,
        id_gen: IdGenerator
    ) -> None:
        self._store = store
        self._id_gen = id_gen

    def add(
        self,
        title: str,
        description: Optional[str] = None,
        priority: Priority = Priority.MEDIUM,
        tags: Optional[Set[str]] = None,
    ) -> Task:
        """
        Create a new task.

        Args:
            title: Task title (1-200 characters)
            description: Optional description (max 1000 characters)
            priority: Task priority (default: MEDIUM)
            tags: Optional set of tags

        Returns:
            Created Task instance with generated ID

        Raises:
            ValidationError: If title/description/tags invalid
        """
        task = Task(
            id=self._id_gen.next(),
            title=title,
            description=description,
            priority=priority,
            tags=tags or set(),
        )
        self._store.save(task)
        return task

    def get(self, task_id: int) -> Task:
        """
        Retrieve task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task instance

        Raises:
            TaskNotFoundError: If task doesn't exist
        """
        task = self._store.get(task_id)
        if not task:
            raise TaskNotFoundError(f"Task #{task_id} not found")
        return task

    def all(self) -> List[Task]:
        """
        Get all tasks sorted by ID.

        Returns:
            List of all tasks
        """
        return sorted(self._store.all(), key=lambda t: t.id)

    def update(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Task:
        """
        Update task fields (partial update).

        Args:
            task_id: Task ID
            title: New title (None = keep current)
            description: New description (None = keep current)

        Returns:
            Updated Task instance

        Raises:
            TaskNotFoundError: If task doesn't exist
            ValidationError: If new values invalid
        """
        task = self.get(task_id)

        updated = Task(
            id=task.id,
            title=title if title is not None else task.title,
            description=description if description is not None else task.description,
            is_complete=task.is_complete,
            created_at=task.created_at,
            priority=task.priority,
            tags=task.tags,
        )

        self._store.save(updated)
        return updated

    def delete(self, task_id: int) -> None:
        """
        Remove task from storage.

        Args:
            task_id: Task ID

        Raises:
            TaskNotFoundError: If task doesn't exist
        """
        task = self.get(task_id)  # Verify exists
        self._store.delete(task_id)

    def toggle_complete(self, task_id: int) -> Task:
        """
        Toggle task completion status.

        Args:
            task_id: Task ID

        Returns:
            Updated Task instance

        Raises:
            TaskNotFoundError: If task doesn't exist
        """
        task = self.get(task_id)
        task.is_complete = not task.is_complete
        self._store.save(task)
        return task
```

---

## Example 3: Integration Test with Full Flow

```python
# tests/integration/test_task_flow.py
"""
Integration test: Full task lifecycle.
"""
import pytest
from src.models.priority import Priority
from src.services.task_service import TaskService
from src.storage.in_memory_store import InMemoryTaskStore
from src.lib.id_generator import SequentialIdGenerator


def test_full_task_lifecycle():
    """Test complete task workflow from create to delete."""
    # Setup
    store = InMemoryTaskStore()
    id_gen = SequentialIdGenerator()
    service = TaskService(store=store, id_gen=id_gen)

    # 1. Create tasks
    task1 = service.add(
        title="Buy groceries",
        description="Milk, eggs, bread",
        priority=Priority.HIGH,
        tags={"shopping", "urgent"}
    )
    task2 = service.add(title="Read book")

    assert task1.id == 1
    assert task2.id == 2

    # 2. List all tasks
    all_tasks = service.all()
    assert len(all_tasks) == 2
    assert all_tasks[0].title == "Buy groceries"
    assert all_tasks[1].title == "Read book"

    # 3. Update task
    updated = service.update(
        task_id=task2.id,
        title="Read Python book",
        description="Clean Architecture by Robert Martin"
    )
    assert updated.title == "Read Python book"
    assert updated.description is not None

    # 4. Complete task
    completed = service.toggle_complete(task1.id)
    assert completed.is_complete

    # 5. Verify state
    retrieved = service.get(task1.id)
    assert retrieved.is_complete
    assert retrieved.title == "Buy groceries"

    # 6. Delete task
    service.delete(task2.id)

    # 7. Verify only one task remains
    remaining = service.all()
    assert len(remaining) == 1
    assert remaining[0].id == task1.id
```

---

## Example 4: Testing with Mock Dependencies

```python
# tests/unit/services/test_task_service_with_mocks.py
from unittest.mock import Mock
import pytest
from src.models.task import Task
from src.services.task_service import TaskService


def test_service_calls_store_save():
    """Verify service calls store.save() when adding task."""
    # Arrange: Create mocks
    mock_store = Mock()
    mock_id_gen = Mock()
    mock_id_gen.next.return_value = 42

    service = TaskService(store=mock_store, id_gen=mock_id_gen)

    # Act: Add task
    task = service.add(title="Test task")

    # Assert: Verify interactions
    mock_id_gen.next.assert_called_once()
    mock_store.save.assert_called_once()

    saved_task = mock_store.save.call_args[0][0]
    assert saved_task.id == 42
    assert saved_task.title == "Test task"


def test_service_uses_id_generator():
    """Verify service uses ID generator correctly."""
    mock_store = Mock()
    mock_id_gen = Mock()

    # Configure mock to return specific IDs
    mock_id_gen.next.side_effect = [1, 2, 3]

    service = TaskService(store=mock_store, id_gen=mock_id_gen)

    # Create three tasks
    task1 = service.add(title="Task 1")
    task2 = service.add(title="Task 2")
    task3 = service.add(title="Task 3")

    # Verify IDs
    assert task1.id == 1
    assert task2.id == 2
    assert task3.id == 3
    assert mock_id_gen.next.call_count == 3
```

---

## Example 5: Real-World Service Pattern

```python
# src/services/search_service.py
from typing import List, Set
from src.models.task import Task
from src.models.priority import Priority
from src.storage.in_memory_store import InMemoryTaskStore


class SearchService:
    """Search and filter tasks."""

    def __init__(self, store: InMemoryTaskStore) -> None:
        self._store = store

    def find_by_keyword(self, keyword: str) -> List[Task]:
        """
        Find tasks containing keyword in title or description.

        Args:
            keyword: Search term (case-insensitive)

        Returns:
            List of matching tasks
        """
        keyword_lower = keyword.lower()
        all_tasks = self._store.all()

        return [
            task for task in all_tasks
            if keyword_lower in task.title.lower() or
            (task.description and keyword_lower in task.description.lower())
        ]

    def find_by_tags(self, tags: Set[str]) -> List[Task]:
        """
        Find tasks with ANY of the specified tags.

        Args:
            tags: Set of tags to search for

        Returns:
            Tasks with at least one matching tag
        """
        all_tasks = self._store.all()
        return [
            task for task in all_tasks
            if task.tags & tags  # Set intersection
        ]

    def find_by_priority(self, priority: Priority) -> List[Task]:
        """Find tasks with specific priority."""
        all_tasks = self._store.all()
        return [task for task in all_tasks if task.priority == priority]

    def find_incomplete(self) -> List[Task]:
        """Find all incomplete tasks."""
        all_tasks = self._store.all()
        return [task for task in all_tasks if not task.is_complete]
```

```python
# tests/unit/services/test_search_service.py
import pytest
from src.models.priority import Priority
from src.services.search_service import SearchService
from src.services.task_service import TaskService
from src.storage.in_memory_store import InMemoryTaskStore
from src.lib.id_generator import SequentialIdGenerator


class TestSearchService:
    """Test search functionality."""

    @pytest.fixture
    def services(self):
        """Create search and task services."""
        store = InMemoryTaskStore()
        id_gen = SequentialIdGenerator()

        task_service = TaskService(store=store, id_gen=id_gen)
        search_service = SearchService(store=store)

        return task_service, search_service

    def test_find_by_keyword_in_title(self, services):
        """Search finds keyword in title."""
        task_svc, search_svc = services

        task_svc.add(title="Buy groceries")
        task_svc.add(title="Read book")
        task_svc.add(title="Buy concert tickets")

        results = search_svc.find_by_keyword("buy")

        assert len(results) == 2
        assert all("buy" in t.title.lower() for t in results)

    def test_find_by_tags(self, services):
        """Search finds tasks by tags."""
        task_svc, search_svc = services

        task_svc.add(title="Work task", tags={"work", "urgent"})
        task_svc.add(title="Personal task", tags={"personal"})
        task_svc.add(title="Another work task", tags={"work"})

        results = search_svc.find_by_tags({"work"})

        assert len(results) == 2

    def test_find_by_priority(self, services):
        """Search finds tasks by priority."""
        task_svc, search_svc = services

        task_svc.add(title="Task 1", priority=Priority.HIGH)
        task_svc.add(title="Task 2", priority=Priority.LOW)
        task_svc.add(title="Task 3", priority=Priority.HIGH)

        high_priority = search_svc.find_by_priority(Priority.HIGH)

        assert len(high_priority) == 2
        assert all(t.priority == Priority.HIGH for t in high_priority)
```

---

## Summary of Patterns Used

1. **Dataclass with Validation**: Task model validates in `__post_init__`
2. **Service Layer**: TaskService orchestrates business logic
3. **Repository Pattern**: InMemoryTaskStore abstracts storage
4. **Dependency Injection**: Services receive dependencies via constructor
5. **Custom Exceptions**: Specific exceptions for different error types
6. **Test Fixtures**: pytest fixtures for reusable test setup
7. **Parametrized Tests**: Test multiple scenarios efficiently
8. **Mock Objects**: Verify interactions without real dependencies
9. **Integration Tests**: Test full workflows end-to-end
10. **Domain Models**: Return Task objects, not primitives
