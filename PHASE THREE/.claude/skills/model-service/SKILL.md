---
name: model-service
description: Implement data models using dataclasses and service layer with business logic, validation, and dependency injection. Use for model tasks (T009-T015) and service tasks (T016-T082).
---

# Model & Service

## Instructions

Follow these patterns when implementing models and services:

### Architecture Layers

```
CLI Layer (commands.py)
    ↓
Service Layer (services/*.py) ← Business logic lives here
    ↓
Model Layer (models/*.py) ← Data structures + validation
    ↓
Storage Layer (task_store.py) ← In-memory storage
```

### Model Pattern (Dataclass)

## Examples

### Example 1: Task Model Implementation

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Set
from src.models.exceptions import ValidationError
from src.models.priority import Priority

@dataclass
class Task:
    """Represents a single todo task."""

    # Core attributes
    id: int
    title: str
    description: Optional[str] = None
    is_complete: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    # Extended attributes (add in later phases)
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
        """Tags: alphanumeric + hyphens, max 20 chars each."""
        for tag in self.tags:
            if len(tag) > 20:
                raise ValidationError(f"Tag '{tag}' exceeds 20 characters")
            if not tag.replace("-", "").replace("_", "").isalnum():
                raise ValidationError(f"Tag '{tag}' contains invalid characters")
```

## Service Pattern

```python
from typing import List, Optional
from src.models.task import Task
from src.models.priority import Priority
from src.models.exceptions import TaskNotFoundError, ValidationError
from src.services.task_store import TaskStore
from src.lib.id_generator import IdGenerator

class TaskService:
    """Business logic for task operations."""

    def __init__(self, store: TaskStore, id_gen: IdGenerator) -> None:
        self._store = store
        self._id_gen = id_gen

    def add(
        self,
        title: str,
        description: Optional[str] = None,
        priority: Priority = Priority.MEDIUM,
        tags: Optional[Set[str]] = None,
    ) -> Task:
        """Create a new task."""
        task = Task(
            id=self._id_gen.next(),
            title=title,
            description=description,
            priority=priority,
            tags=tags or set(),
        )
        # Task validates itself in __post_init__
        self._store.save(task)
        return task

    def get(self, task_id: int) -> Task:
        """Retrieve task by ID."""
        task = self._store.get(task_id)
        if not task:
            raise TaskNotFoundError(f"Task #{task_id} not found")
        return task

    def all(self) -> List[Task]:
        """Get all tasks sorted by ID."""
        return sorted(self._store.all(), key=lambda t: t.id)

    def update(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Task:
        """Update task fields (partial update)."""
        task = self.get(task_id)  # Raises TaskNotFoundError if missing

        # Create updated task (triggers validation)
        updated = Task(
            id=task.id,
            title=title if title is not None else task.title,
            description=description if description is not None else task.description,
            is_complete=task.is_complete,
            created_at=task.created_at,
        )

        self._store.save(updated)
        return updated

    def delete(self, task_id: int) -> None:
        """Remove task from storage."""
        task = self.get(task_id)  # Verify exists
        self._store.delete(task_id)

    def toggle_complete(self, task_id: int) -> Task:
        """Toggle completion status."""
        task = self.get(task_id)
        task.is_complete = not task.is_complete
        self._store.save(task)
        return task
```

## Storage Pattern (In-Memory)

```python
from typing import Dict, List, Optional
from src.models.task import Task

class InMemoryTaskStore:
    """In-memory storage for tasks."""

    def __init__(self) -> None:
        self._tasks: Dict[int, Task] = {}

    def save(self, task: Task) -> None:
        """Save or update task."""
        self._tasks[task.id] = task

    def get(self, task_id: int) -> Optional[Task]:
        """Retrieve task by ID."""
        return self._tasks.get(task_id)

    def all(self) -> List[Task]:
        """Get all tasks."""
        return list(self._tasks.values())

    def delete(self, task_id: int) -> None:
        """Remove task."""
        self._tasks.pop(task_id, None)
```

## Exception Hierarchy

```python
# src/models/exceptions.py
class TodoAppError(Exception):
    """Base exception for all app errors."""

class ValidationError(TodoAppError):
    """Raised when input validation fails."""

class TaskNotFoundError(TodoAppError):
    """Raised when task ID doesn't exist."""

class StorageError(TodoAppError):
    """Raised on storage operations failure."""
```

## Testing Checklist

- [ ] **Unit tests for models**: Validation logic, edge cases
- [ ] **Unit tests for services**: Business logic, error handling
- [ ] **Type hints**: All parameters and returns annotated
- [ ] **Docstrings**: Clear descriptions for all public methods
- [ ] **mypy strict**: No type errors
- [ ] **Coverage**: >90% for new code

## Integration with Subagents

- **type-enforcer**: Comprehensive type annotations
- **test-guardian**: Test quality and TDD compliance
- **style-guardian**: Code style and patterns
- **security-sentinel**: Input validation security
