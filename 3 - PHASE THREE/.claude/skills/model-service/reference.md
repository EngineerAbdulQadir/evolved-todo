# Model & Service Layer - Extended Reference

## Table of Contents

1. [Dataclass Patterns](#dataclass-patterns)
2. [Validation Strategies](#validation-strategies)
3. [Service Layer Architecture](#service-layer-architecture)
4. [Repository Pattern](#repository-pattern)
5. [Dependency Injection](#dependency-injection)
6. [Common Mistakes](#common-mistakes)
7. [Best Practices](#best-practices)

---

## Dataclass Patterns

### Why Dataclasses?

Python 3.7+ dataclasses provide:
- Automatic `__init__`, `__repr__`, `__eq__` generation
- Type hints enforcement
- Immutability support with `frozen=True`
- Default values with `field(default_factory=...)`

### Basic Dataclass

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Task:
    """Immutable task representation."""

    id: int
    title: str
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
```

### Field Types and Defaults

```python
from dataclasses import dataclass, field
from typing import Set, List, Optional

@dataclass
class Task:
    # Required fields (no default)
    id: int
    title: str

    # Optional with None default
    description: Optional[str] = None

    # Mutable defaults require field(default_factory=...)
    tags: Set[str] = field(default_factory=set)

    # Immutable defaults can be inline
    is_complete: bool = False
    priority: Priority = Priority.MEDIUM
```

**CRITICAL**: Never use mutable defaults directly:
```python
# L WRONG - All instances share the same list!
tags: List[str] = []

#  CORRECT - Each instance gets a new list
tags: List[str] = field(default_factory=list)
```

### Post-Init Validation

Use `__post_init__` to validate after initialization:

```python
@dataclass
class Task:
    title: str
    priority: Priority

    def __post_init__(self) -> None:
        """Validate after all fields are set."""
        self._validate_title()
        self._validate_priority()

    def _validate_title(self) -> None:
        if not self.title or not self.title.strip():
            raise ValidationError("Title cannot be empty")
        if len(self.title) > 200:
            raise ValidationError("Title too long")

    def _validate_priority(self) -> None:
        if not isinstance(self.priority, Priority):
            raise ValidationError(f"Invalid priority: {self.priority}")
```

### Frozen (Immutable) Dataclasses

```python
@dataclass(frozen=True)
class Task:
    """Immutable task - cannot modify after creation."""

    id: int
    title: str
    is_complete: bool = False

    def complete(self) -> "Task":
        """Return new Task with is_complete=True."""
        return Task(
            id=self.id,
            title=self.title,
            is_complete=True
        )
```

Benefits:
- Thread-safe
- Hashable (can use in sets/dict keys)
- Prevents accidental mutation

Tradeoffs:
- Cannot modify fields directly
- Must create new instances for changes
- Slightly more memory overhead

### Computed Properties

```python
from datetime import datetime, timedelta

@dataclass
class Task:
    due_date: Optional[datetime] = None

    @property
    def is_overdue(self) -> bool:
        """Computed property, not stored."""
        if not self.due_date:
            return False
        return datetime.now() > self.due_date

    @property
    def days_until_due(self) -> Optional[int]:
        """Calculate days remaining."""
        if not self.due_date:
            return None
        delta = self.due_date - datetime.now()
        return delta.days
```

---

## Validation Strategies

### Strategy 1: Fail Fast (Recommended)

Validate immediately in `__post_init__`:

```python
@dataclass
class Task:
    title: str

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValidationError("Title required")
```

**Pros**:
- Catches errors immediately
- Invalid objects never exist
- Easy to debug

**Cons**:
- Cannot create invalid objects for testing
- Less flexible

### Strategy 2: Lazy Validation

Validate on-demand with explicit method:

```python
@dataclass
class Task:
    title: str

    def validate(self) -> None:
        """Call explicitly to validate."""
        if not self.title.strip():
            raise ValidationError("Title required")
```

**Pros**:
- Can create invalid objects for testing
- Flexible

**Cons**:
- Easy to forget to call
- Invalid objects can propagate

### Strategy 3: Validation Decorators

```python
from typing import Callable

def validate_field(validator: Callable[[str], bool], message: str):
    """Decorator for field validation."""
    def decorator(func):
        def wrapper(self):
            value = func(self)
            if not validator(value):
                raise ValidationError(message)
            return value
        return wrapper
    return decorator

@dataclass
class Task:
    title: str

    @validate_field(lambda s: len(s) > 0, "Title required")
    def _title(self) -> str:
        return self.title
```

### Complex Validation Rules

```python
from datetime import datetime
from typing import Optional

@dataclass
class Task:
    title: str
    due_date: Optional[datetime] = None
    reminder_date: Optional[datetime] = None

    def __post_init__(self) -> None:
        self._validate_dates()

    def _validate_dates(self) -> None:
        """Cross-field validation."""
        # Reminder must be before due date
        if self.reminder_date and self.due_date:
            if self.reminder_date >= self.due_date:
                raise ValidationError(
                    "Reminder must be before due date"
                )

        # Due date cannot be in the past
        if self.due_date:
            if self.due_date < datetime.now():
                raise ValidationError(
                    "Due date cannot be in the past"
                )
```

---

## Service Layer Architecture

### Why Service Layer?

The service layer:
- Encapsulates business logic
- Orchestrates between models and storage
- Provides transaction boundaries
- Simplifies testing (mock storage, not business logic)

### Service Responsibilities

```python
class TaskService:
    """
    Responsibilities:
    1. Orchestrate business operations
    2. Enforce business rules
    3. Coordinate between storage and models
    4. Return domain models, not primitives
    """

    def __init__(self, store: TaskStore, id_gen: IdGenerator) -> None:
        self._store = store
        self._id_gen = id_gen

    def add(self, title: str, description: Optional[str] = None) -> Task:
        """Business logic: Create task."""
        # 1. Generate ID (business rule)
        task_id = self._id_gen.next()

        # 2. Create model (validates)
        task = Task(
            id=task_id,
            title=title,
            description=description
        )

        # 3. Persist
        self._store.save(task)

        # 4. Return domain model
        return task
```

### Service Patterns

**Pattern 1: Finder Methods**

```python
class TaskService:
    def find_by_tag(self, tag: str) -> List[Task]:
        """Find tasks with specific tag."""
        all_tasks = self._store.all()
        return [t for t in all_tasks if tag in t.tags]

    def find_overdue(self) -> List[Task]:
        """Find tasks past due date."""
        all_tasks = self._store.all()
        now = datetime.now()
        return [
            t for t in all_tasks
            if t.due_date and t.due_date < now and not t.is_complete
        ]
```

**Pattern 2: Command Methods**

```python
class TaskService:
    def complete_task(self, task_id: int) -> Task:
        """Mark task as complete (command)."""
        task = self.get(task_id)
        task.is_complete = True
        task.completed_at = datetime.now()
        self._store.save(task)
        return task

    def bulk_delete(self, task_ids: List[int]) -> int:
        """Delete multiple tasks (returns count)."""
        count = 0
        for task_id in task_ids:
            try:
                self.delete(task_id)
                count += 1
            except TaskNotFoundError:
                pass  # Skip missing tasks
        return count
```

**Pattern 3: Transaction-Like Operations**

```python
class TaskService:
    def duplicate_task(self, task_id: int) -> Task:
        """Create copy of existing task."""
        # 1. Get original
        original = self.get(task_id)

        # 2. Create new with same attributes
        duplicate = self.add(
            title=f"{original.title} (copy)",
            description=original.description,
            priority=original.priority,
            tags=original.tags.copy(),  # Copy mutable fields
        )

        return duplicate
```

---

## Repository Pattern

### What is Repository Pattern?

A repository:
- Abstracts data persistence
- Provides collection-like interface
- Hides storage implementation details
- Makes testing easier (swap real for in-memory)

### Repository Interface

```python
from abc import ABC, abstractmethod
from typing import List, Optional

class TaskRepository(ABC):
    """Abstract repository interface."""

    @abstractmethod
    def save(self, task: Task) -> None:
        """Save or update task."""
        pass

    @abstractmethod
    def get(self, task_id: int) -> Optional[Task]:
        """Get task by ID."""
        pass

    @abstractmethod
    def all(self) -> List[Task]:
        """Get all tasks."""
        pass

    @abstractmethod
    def delete(self, task_id: int) -> None:
        """Delete task."""
        pass
```

### In-Memory Implementation

```python
class InMemoryTaskRepository(TaskRepository):
    """In-memory storage for testing and Phase 1."""

    def __init__(self) -> None:
        self._tasks: Dict[int, Task] = {}

    def save(self, task: Task) -> None:
        self._tasks[task.id] = task

    def get(self, task_id: int) -> Optional[Task]:
        return self._tasks.get(task_id)

    def all(self) -> List[Task]:
        return list(self._tasks.values())

    def delete(self, task_id: int) -> None:
        self._tasks.pop(task_id, None)
```

### File-Based Implementation (Future)

```python
import json
from pathlib import Path

class FileTaskRepository(TaskRepository):
    """JSON file storage."""

    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path
        self._tasks: Dict[int, Task] = self._load()

    def save(self, task: Task) -> None:
        self._tasks[task.id] = task
        self._persist()

    def _load(self) -> Dict[int, Task]:
        """Load from JSON file."""
        if not self._file_path.exists():
            return {}

        with open(self._file_path) as f:
            data = json.load(f)

        return {
            int(k): Task(**v)
            for k, v in data.items()
        }

    def _persist(self) -> None:
        """Save to JSON file."""
        data = {
            str(task.id): asdict(task)
            for task in self._tasks.values()
        }

        with open(self._file_path, 'w') as f:
            json.dump(data, f, indent=2)
```

---

## Dependency Injection

### Why Dependency Injection?

- Testability (inject mocks)
- Flexibility (swap implementations)
- Explicit dependencies
- No global state

### Constructor Injection (Recommended)

```python
class TaskService:
    """All dependencies injected via constructor."""

    def __init__(
        self,
        repository: TaskRepository,
        id_generator: IdGenerator,
        clock: Clock = SystemClock(),  # Optional with default
    ) -> None:
        self._repo = repository
        self._id_gen = id_generator
        self._clock = clock
```

### Manual Wiring (Simple)

```python
# src/main.py
def create_task_service() -> TaskService:
    """Factory function for service creation."""
    repository = InMemoryTaskRepository()
    id_generator = SequentialIdGenerator()

    return TaskService(
        repository=repository,
        id_generator=id_generator,
    )

# Usage
task_service = create_task_service()
```

### Testing with DI

```python
# tests/unit/test_task_service.py
def test_add_task():
    # Inject test doubles
    mock_repo = InMemoryTaskRepository()
    mock_id_gen = FakeIdGenerator(start=1)

    service = TaskService(
        repository=mock_repo,
        id_generator=mock_id_gen,
    )

    task = service.add(title="Test task")

    assert task.id == 1
    assert task.title == "Test task"
```

---

## Common Mistakes

### L Mistake 1: Business Logic in Models

```python
# L BAD - Business logic in model
@dataclass
class Task:
    tags: Set[str]

    def add_tag(self, tag: str) -> None:
        """Don't put business rules in models!"""
        # What if we need to validate tag against a service?
        # What if we need to log tag additions?
        self.tags.add(tag)
```

```python
#  GOOD - Business logic in service
class TaskService:
    def add_tag(self, task_id: int, tag: str) -> Task:
        """Business logic belongs in service."""
        task = self.get(task_id)

        # Validate tag
        if len(tag) > 20:
            raise ValidationError("Tag too long")

        # Add tag
        task.tags.add(tag)

        # Persist
        self._store.save(task)

        return task
```

### L Mistake 2: Service Knows About Storage Details

```python
# L BAD - Service knows about dict storage
class TaskService:
    def __init__(self):
        self._tasks = {}  # Service shouldn't own storage!

    def add(self, title: str) -> Task:
        task = Task(id=len(self._tasks) + 1, title=title)
        self._tasks[task.id] = task  # Direct storage access
        return task
```

```python
#  GOOD - Service uses repository abstraction
class TaskService:
    def __init__(self, repository: TaskRepository, id_gen: IdGenerator):
        self._repo = repository  # Abstraction
        self._id_gen = id_gen

    def add(self, title: str) -> Task:
        task = Task(id=self._id_gen.next(), title=title)
        self._repo.save(task)  # Interface, not implementation
        return task
```

### L Mistake 3: Returning Primitives Instead of Models

```python
# L BAD - Returns dict instead of model
class TaskService:
    def get(self, task_id: int) -> Dict[str, Any]:
        task = self._store.get(task_id)
        return {
            "id": task.id,
            "title": task.title,
            # Loses type safety!
        }
```

```python
#  GOOD - Returns domain model
class TaskService:
    def get(self, task_id: int) -> Task:
        task = self._store.get(task_id)
        if not task:
            raise TaskNotFoundError(f"Task #{task_id} not found")
        return task  # Type-safe model
```

### L Mistake 4: Mutable Default Arguments

```python
# L BAD - Mutable default shared across all calls
def add(self, title: str, tags: Set[str] = set()) -> Task:
    # All calls share the same set!
    pass
```

```python
#  GOOD - None as sentinel, create new in function
def add(self, title: str, tags: Optional[Set[str]] = None) -> Task:
    tags = tags or set()  # New set each time
    # ...
```

---

## Best Practices

### 1. Keep Models Dumb

Models should:
- Store data
- Validate themselves
- Provide computed properties
- NOT contain business logic

### 2. Keep Services Focused

One service per aggregate root:
- `TaskService` - Task operations
- `RecurrenceService` - Recurrence patterns
- `SearchService` - Search operations

Avoid "god services" that do everything.

### 3. Use Type Hints Everywhere

```python
from typing import List, Optional, Set

def add(
    self,
    title: str,
    description: Optional[str] = None,
    tags: Optional[Set[str]] = None,
) -> Task:
    """Type hints on all parameters and return."""
    pass
```

### 4. Validate Early

Validate in model's `__post_init__`:
```python
@dataclass
class Task:
    title: str

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValidationError("Title required")
```

### 5. Test Models and Services Separately

```python
# Unit test model validation
def test_task_title_validation():
    with pytest.raises(ValidationError):
        Task(id=1, title="")

# Unit test service logic
def test_task_service_add(mock_store):
    service = TaskService(store=mock_store, id_gen=FakeIdGen())
    task = service.add(title="Test")
    assert task.id == 1
```

### 6. Use Custom Exceptions

```python
# Custom exceptions hierarchy
class TodoAppError(Exception):
    """Base exception."""

class ValidationError(TodoAppError):
    """Input validation failed."""

class TaskNotFoundError(TodoAppError):
    """Task doesn't exist."""
```

### 7. Document Public APIs

```python
def add(self, title: str, description: Optional[str] = None) -> Task:
    """
    Create a new task.

    Args:
        title: Task title (1-200 characters, required)
        description: Optional description (max 1000 characters)

    Returns:
        Created Task instance with generated ID

    Raises:
        ValidationError: If title is empty or too long
    """
    pass
```

---

## Resources

- [PEP 557  Data Classes](https://peps.python.org/pep-0557/)
- [Domain-Driven Design](https://www.domainlanguage.com/ddd/)
- [Martin Fowler - Service Layer](https://martinfowler.com/eaaCatalog/serviceLayer.html)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
