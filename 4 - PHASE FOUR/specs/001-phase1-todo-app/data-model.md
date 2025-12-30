# Data Model: Phase 1 Complete Todo App

**Date**: 2025-12-06 | **Plan**: [plan.md](./plan.md)

This document defines the complete data model for all 10 Phase 1 features.

---

## Entity: Task

The central entity representing a todo item with all attributes from Basic, Intermediate, and Advanced features.

### Attributes

| Attribute | Type | Required | Default | Constraints | Feature |
|-----------|------|----------|---------|-------------|---------|
| `id` | `int` | Auto | - | Unique, positive, immutable | 001 |
| `title` | `str` | Yes | - | 1-200 chars, non-whitespace | 001 |
| `description` | `str \| None` | No | `None` | Max 1000 chars | 001 |
| `is_complete` | `bool` | Auto | `False` | - | 004 |
| `created_at` | `datetime` | Auto | Now | Immutable | 001 |
| `priority` | `Priority \| None` | No | `None` | Enum value | 006 |
| `tags` | `list[str]` | No | `[]` | 0-10 tags, each max 50 chars | 006 |
| `due_date` | `date \| None` | No | `None` | Valid date | 010 |
| `due_time` | `time \| None` | No | `None` | Valid time | 010 |
| `recurrence` | `RecurrencePattern \| None` | No | `None` | Enum value | 009 |
| `recurrence_day` | `int \| None` | No | `None` | 1-7 (weekly) or 1-31 (monthly) | 009 |

### Computed Properties

| Property | Type | Description | Feature |
|----------|------|-------------|---------|
| `is_overdue` | `bool` | `True` if due date passed and not complete | 010 |
| `due_status` | `DueStatus` | Overdue/DueToday/Upcoming/NoDueDate | 010 |
| `has_recurrence` | `bool` | `True` if recurrence pattern is set | 009 |
| `display_due` | `str` | Formatted due date/time string | 010 |

### Implementation

```python
from dataclasses import dataclass, field
from datetime import datetime, date, time
from enum import Enum
from typing import Self


class Priority(Enum):
    """Task priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecurrencePattern(Enum):
    """Task recurrence patterns."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class DueStatus(Enum):
    """Task due date status."""
    OVERDUE = "overdue"
    DUE_TODAY = "due_today"
    UPCOMING = "upcoming"
    NO_DUE_DATE = "no_due_date"


@dataclass
class Task:
    """
    Represents a todo item with all Phase 1 attributes.

    Attributes:
        id: Unique identifier (auto-generated, immutable)
        title: Task name (required, 1-200 chars)
        description: Additional details (optional, max 1000 chars)
        is_complete: Completion status (default False)
        created_at: Creation timestamp (auto-set, immutable)
        priority: Priority level (high/medium/low)
        tags: Category labels (0-10 tags, each max 50 chars)
        due_date: Deadline date (optional)
        due_time: Deadline time (optional)
        recurrence: Recurrence pattern (daily/weekly/monthly)
        recurrence_day: Day for weekly (1-7) or monthly (1-31) recurrence
    """

    # Core attributes (Basic Level - Features 001-005)
    id: int
    title: str
    description: str | None = None
    is_complete: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    # Organization attributes (Intermediate Level - Feature 006)
    priority: Priority | None = None
    tags: list[str] = field(default_factory=list)

    # Scheduling attributes (Advanced Level - Features 009, 010)
    due_date: date | None = None
    due_time: time | None = None
    recurrence: RecurrencePattern | None = None
    recurrence_day: int | None = None

    def __post_init__(self) -> None:
        """Validate task attributes after initialization."""
        self._validate_title()
        self._validate_description()
        self._validate_tags()
        self._validate_recurrence()

    def _validate_title(self) -> None:
        """Ensure title is valid."""
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty or whitespace")
        if len(self.title) > 200:
            raise ValueError("Title cannot exceed 200 characters")

    def _validate_description(self) -> None:
        """Ensure description is valid if provided."""
        if self.description is not None and len(self.description) > 1000:
            raise ValueError("Description cannot exceed 1000 characters")

    def _validate_tags(self) -> None:
        """Ensure tags are valid."""
        if len(self.tags) > 10:
            raise ValueError("Cannot have more than 10 tags")
        for tag in self.tags:
            if len(tag) > 50:
                raise ValueError(f"Tag '{tag}' exceeds 50 character limit")

    def _validate_recurrence(self) -> None:
        """Ensure recurrence settings are valid."""
        if self.recurrence == RecurrencePattern.WEEKLY:
            if self.recurrence_day is None or not (1 <= self.recurrence_day <= 7):
                raise ValueError("Weekly recurrence requires day 1-7 (Mon-Sun)")
        elif self.recurrence == RecurrencePattern.MONTHLY:
            if self.recurrence_day is None or not (1 <= self.recurrence_day <= 31):
                raise ValueError("Monthly recurrence requires day 1-31")

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue (past due date and incomplete)."""
        if self.is_complete or self.due_date is None:
            return False
        today = date.today()
        if self.due_time:
            # Compare date and time
            now = datetime.now()
            due_datetime = datetime.combine(self.due_date, self.due_time)
            return now > due_datetime
        return today > self.due_date

    @property
    def due_status(self) -> DueStatus:
        """Get the due date status category."""
        if self.due_date is None:
            return DueStatus.NO_DUE_DATE
        if self.is_complete:
            return DueStatus.NO_DUE_DATE  # Completed tasks aren't "overdue"
        today = date.today()
        if self.due_date < today:
            return DueStatus.OVERDUE
        if self.due_date == today:
            return DueStatus.DUE_TODAY
        return DueStatus.UPCOMING

    @property
    def has_recurrence(self) -> bool:
        """Check if task has recurrence enabled."""
        return (
            self.recurrence is not None
            and self.recurrence != RecurrencePattern.NONE
        )

    @property
    def display_due(self) -> str:
        """Format due date/time for display."""
        if self.due_date is None:
            return "No due date"
        date_str = self.due_date.strftime("%b %d, %Y")  # e.g., "Dec 15, 2025"
        if self.due_time:
            time_str = self.due_time.strftime("%I:%M %p")  # e.g., "2:00 PM"
            return f"{date_str} at {time_str}"
        return date_str

    def copy_for_recurrence(self, new_id: int, new_due_date: date) -> Self:
        """
        Create a new task instance for recurring task.

        Args:
            new_id: ID for the new occurrence
            new_due_date: Due date for the new occurrence

        Returns:
            New Task instance with reset completion status
        """
        return Task(
            id=new_id,
            title=self.title,
            description=self.description,
            is_complete=False,  # Reset for new occurrence
            created_at=datetime.now(),
            priority=self.priority,
            tags=self.tags.copy(),
            due_date=new_due_date,
            due_time=self.due_time,
            recurrence=self.recurrence,
            recurrence_day=self.recurrence_day,
        )
```

---

## Entity: TaskStore

In-memory storage for tasks with CRUD operations.

### Interface

```python
from abc import ABC, abstractmethod


class TaskStore(ABC):
    """Abstract base for task storage."""

    @abstractmethod
    def add(self, task: Task) -> Task:
        """Store a new task."""
        ...

    @abstractmethod
    def get(self, task_id: int) -> Task:
        """Retrieve task by ID. Raises TaskNotFoundError if not found."""
        ...

    @abstractmethod
    def update(self, task: Task) -> Task:
        """Update existing task. Raises TaskNotFoundError if not found."""
        ...

    @abstractmethod
    def delete(self, task_id: int) -> None:
        """Remove task by ID. Raises TaskNotFoundError if not found."""
        ...

    @abstractmethod
    def all(self) -> list[Task]:
        """Get all tasks."""
        ...

    @abstractmethod
    def count(self) -> int:
        """Get total task count."""
        ...
```

### Implementation (In-Memory)

```python
class InMemoryTaskStore(TaskStore):
    """In-memory task storage using dictionary."""

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}

    def add(self, task: Task) -> Task:
        if task.id in self._tasks:
            raise ValueError(f"Task with ID {task.id} already exists")
        self._tasks[task.id] = task
        return task

    def get(self, task_id: int) -> Task:
        if task_id not in self._tasks:
            raise TaskNotFoundError(f"Task with ID {task_id} not found")
        return self._tasks[task_id]

    def update(self, task: Task) -> Task:
        if task.id not in self._tasks:
            raise TaskNotFoundError(f"Task with ID {task.id} not found")
        self._tasks[task.id] = task
        return task

    def delete(self, task_id: int) -> None:
        if task_id not in self._tasks:
            raise TaskNotFoundError(f"Task with ID {task_id} not found")
        del self._tasks[task_id]

    def all(self) -> list[Task]:
        return list(self._tasks.values())

    def count(self) -> int:
        return len(self._tasks)
```

---

## Enumerations

### Priority

```python
class Priority(Enum):
    """Task priority levels for Feature 006."""
    HIGH = "high"      # Most important, needs immediate attention
    MEDIUM = "medium"  # Normal importance (default for display)
    LOW = "low"        # Can be deferred, low urgency
```

### RecurrencePattern

```python
class RecurrencePattern(Enum):
    """Task recurrence patterns for Feature 009."""
    NONE = "none"        # One-time task (no recurrence)
    DAILY = "daily"      # Repeat every day
    WEEKLY = "weekly"    # Repeat on specific day of week
    MONTHLY = "monthly"  # Repeat on specific day of month
```

### DueStatus

```python
class DueStatus(Enum):
    """Task due date status for Feature 010."""
    OVERDUE = "overdue"        # Due date passed, task incomplete
    DUE_TODAY = "due_today"    # Due date is today
    UPCOMING = "upcoming"      # Due date in future
    NO_DUE_DATE = "no_due_date"  # No deadline set
```

---

## Exceptions

```python
class TodoAppError(Exception):
    """Base exception for all Todo App errors."""
    pass


class TaskNotFoundError(TodoAppError):
    """Raised when task ID does not exist in storage."""
    pass


class ValidationError(TodoAppError):
    """Raised when input validation fails."""
    pass


class InvalidTitleError(ValidationError):
    """Raised when task title is invalid (empty, too long)."""
    pass


class InvalidDescriptionError(ValidationError):
    """Raised when description exceeds length limit."""
    pass


class InvalidPriorityError(ValidationError):
    """Raised when priority value is not high/medium/low."""
    pass


class InvalidTagError(ValidationError):
    """Raised when tag is invalid (too long, too many tags)."""
    pass


class InvalidDateError(ValidationError):
    """Raised when date parsing fails."""
    pass


class InvalidTimeError(ValidationError):
    """Raised when time parsing fails."""
    pass


class InvalidRecurrenceError(ValidationError):
    """Raised when recurrence settings are invalid."""
    pass
```

---

## Validation Rules Summary

| Field | Rule | Error |
|-------|------|-------|
| `title` | Non-empty, non-whitespace | InvalidTitleError |
| `title` | Max 200 chars | InvalidTitleError |
| `description` | Max 1000 chars (if provided) | InvalidDescriptionError |
| `priority` | Must be high/medium/low | InvalidPriorityError |
| `tags` | Max 10 tags | InvalidTagError |
| `tags` | Each tag max 50 chars | InvalidTagError |
| `tags` | Alphanumeric, hyphens, underscores | InvalidTagError |
| `due_date` | Valid date format | InvalidDateError |
| `due_time` | Valid time format | InvalidTimeError |
| `recurrence_day` | 1-7 for weekly | InvalidRecurrenceError |
| `recurrence_day` | 1-31 for monthly | InvalidRecurrenceError |

---

## State Transitions

### Task Completion

```
┌──────────┐    complete()    ┌──────────┐
│INCOMPLETE├─────────────────►│ COMPLETE │
└──────────┘                  └──────────┘
      ▲                            │
      │      uncomplete()          │
      └────────────────────────────┘
```

### Recurring Task Lifecycle

```
┌──────────────┐  complete()   ┌──────────────┐  create_next()  ┌──────────────┐
│  Incomplete  ├──────────────►│   Complete   ├────────────────►│  New Task    │
│  Recurring   │               │   Recurring  │                 │  Incomplete  │
└──────────────┘               └──────────────┘                 └──────────────┘
```

### Due Status Transitions (Time-Based)

```
                        time passes
┌───────────┐  ─────────────────────►  ┌──────────┐  ────────►  ┌─────────┐
│  UPCOMING │                          │ DUE_TODAY│             │ OVERDUE │
└───────────┘                          └──────────┘             └─────────┘
                                            │
                                            │ complete()
                                            ▼
                                       ┌───────────┐
                                       │ NO_DUE_DATE│
                                       └───────────┘
```

---

## Relationships

```
Task
├── Priority (enum, 0..1)
├── Tags (list[str], 0..10)
├── RecurrencePattern (enum, 0..1)
└── DueStatus (computed, always present)

TaskStore
└── contains: Task (0..*)
```

---

## Index Strategy (In-Memory)

For Phase 1, all lookups use the dictionary key (task ID). For filter/search operations, we iterate over all tasks. This is acceptable for up to 10,000 tasks.

Future optimization (Phase 2+):
- Index by priority for fast priority filtering
- Index by tag for fast tag filtering
- Index by due_date for fast date sorting/filtering
