# Research: Phase 1 Complete Todo App

**Date**: 2025-12-06 | **Plan**: [plan.md](./plan.md)

This document resolves all technical decisions and unknowns identified during planning.

---

## 1. CLI Framework Selection

### Decision: `typer`

### Rationale
- **Type-safe**: Built on type hints, aligns with mypy strict mode
- **Auto-documentation**: Generates help text from function signatures
- **Minimal boilerplate**: Decorators handle argument parsing
- **Modern Python**: Designed for Python 3.6+, works great with 3.13
- **Built on Click**: Stable foundation with extensive community support

### Alternatives Considered

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| `argparse` | Standard library, no deps | Verbose, manual help text | Too much boilerplate |
| `click` | Mature, flexible | More verbose than Typer | Typer wraps Click with better DX |
| `fire` | Zero config | Less control over help/validation | Insufficient validation control |

### Best Practices
```python
import typer

app = typer.Typer(help="Evolved Todo - Phase 1 CLI")

@app.command()
def add(
    title: str = typer.Argument(..., help="Task title"),
    description: str = typer.Option(None, "--desc", "-d", help="Task description"),
    priority: str = typer.Option("medium", "--priority", "-p", help="Priority level"),
) -> None:
    """Add a new task."""
    ...
```

---

## 2. Date/Time Parsing

### Decision: `python-dateutil`

### Rationale
- **Natural language**: Parses "tomorrow", "next Monday", "Dec 15"
- **Robust**: Handles edge cases (leap years, timezones)
- **Well-maintained**: Active development, wide adoption
- **Lightweight**: Single dependency, no heavy stack

### Alternatives Considered

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| `datetime` only | Standard library | No natural language parsing | Doesn't meet FR-004 |
| `arrow` | Nice API | Heavier dependency | Overkill for our needs |
| `pendulum` | Excellent TZ handling | Heavier dependency | Complexity not needed |

### Best Practices
```python
from dateutil import parser
from datetime import date, time

def parse_due_date(input_str: str) -> date:
    """Parse natural language or ISO date string."""
    parsed = parser.parse(input_str, fuzzy=True)
    return parsed.date()

def parse_due_time(input_str: str) -> time:
    """Parse time string (HH:MM or 2:00 PM)."""
    parsed = parser.parse(input_str)
    return parsed.time()
```

---

## 3. Output Formatting

### Decision: `rich` (optional enhancement)

### Rationale
- **Visual indicators**: Colors for overdue (red), priority levels
- **Tables**: Clean task list display
- **Emojis**: Works cross-platform for indicators
- **Graceful degradation**: Falls back to plain text if terminal doesn't support

### Alternatives Considered

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| Plain `print()` | No dependencies | Limited formatting | Meets minimum but poor UX |
| `tabulate` | Good tables | No colors | Missing visual priority cues |
| `colorama` | Cross-platform colors | No tables | Would need combination |

### Best Practices
```python
from rich.console import Console
from rich.table import Table

console = Console()

def display_tasks(tasks: list[Task]) -> None:
    table = Table(title="Tasks")
    table.add_column("ID", style="cyan")
    table.add_column("Status")
    table.add_column("Title")
    table.add_column("Priority")
    table.add_column("Due")

    for task in tasks:
        status = "[green]✓[/]" if task.is_complete else "[ ]"
        priority_style = {
            Priority.HIGH: "[red]HIGH[/]",
            Priority.MEDIUM: "[yellow]MED[/]",
            Priority.LOW: "[blue]LOW[/]",
        }.get(task.priority, "")
        table.add_row(str(task.id), status, task.title, priority_style, ...)

    console.print(table)
```

---

## 4. ID Generation Strategy

### Decision: Sequential integer with in-memory counter

### Rationale
- **Simple**: Incrementing integer from 1
- **Predictable**: Users can reference tasks by number easily
- **No external deps**: Pure Python implementation
- **No ID reuse**: Deleted IDs remain unused (per spec)

### Implementation
```python
class IdGenerator:
    """Generates sequential unique IDs."""

    def __init__(self, start: int = 1) -> None:
        self._next_id = start

    def next_id(self) -> int:
        """Return next available ID and increment counter."""
        current = self._next_id
        self._next_id += 1
        return current
```

---

## 5. In-Memory Storage Pattern

### Decision: Dictionary-based storage with TaskService

### Rationale
- **O(1) lookup**: Dictionary by ID for fast retrieval
- **Simple iteration**: `.values()` for list operations
- **No persistence**: Aligns with Phase 1 constraints
- **Service pattern**: Encapsulates storage from CLI

### Implementation
```python
class TaskService:
    """Manages task storage and CRUD operations."""

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._id_gen = IdGenerator()

    def add(self, title: str, description: str | None = None, ...) -> Task:
        task = Task(
            id=self._id_gen.next_id(),
            title=title,
            description=description,
            ...
        )
        self._tasks[task.id] = task
        return task

    def get(self, task_id: int) -> Task:
        if task_id not in self._tasks:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return self._tasks[task_id]

    def all(self) -> list[Task]:
        return list(self._tasks.values())
```

---

## 6. Recurrence Edge Cases

### Decision: Smart date adjustment for edge cases

### Rationale
- **Monthly on 31st**: Roll to last day of month (28/29/30)
- **Weekly**: Always same day of week
- **Create on complete**: New occurrence created immediately

### Implementation
```python
from calendar import monthrange

def calculate_next_occurrence(task: Task) -> date:
    """Calculate next due date for recurring task."""
    today = date.today()

    match task.recurrence:
        case RecurrencePattern.DAILY:
            return today + timedelta(days=1)

        case RecurrencePattern.WEEKLY:
            # Same day next week
            days_ahead = (task.recurrence_day - today.weekday() + 7) % 7
            return today + timedelta(days=days_ahead or 7)

        case RecurrencePattern.MONTHLY:
            # Same day next month, adjusted for month length
            next_month = today.month % 12 + 1
            next_year = today.year + (1 if next_month == 1 else 0)
            max_day = monthrange(next_year, next_month)[1]
            target_day = min(task.recurrence_day, max_day)
            return date(next_year, next_month, target_day)
```

---

## 7. Search Implementation

### Decision: Case-insensitive substring matching

### Rationale
- **Simple**: Python's `in` operator with `.lower()`
- **Fast enough**: O(n) is acceptable for 1000 tasks
- **User-friendly**: No regex knowledge needed

### Implementation
```python
def search_tasks(tasks: list[Task], keyword: str) -> list[Task]:
    """Search tasks by keyword in title or description."""
    keyword_lower = keyword.lower()
    return [
        task for task in tasks
        if keyword_lower in task.title.lower()
        or (task.description and keyword_lower in task.description.lower())
    ]
```

---

## 8. Filter Logic

### Decision: AND logic for multiple filters

### Rationale
- **Consistent**: Matches user mental model ("show incomplete AND high priority")
- **Progressive narrowing**: Each filter reduces results
- **Composable**: Filters chain cleanly

### Implementation
```python
def filter_tasks(
    tasks: list[Task],
    status: str | None = None,
    priority: str | None = None,
    tag: str | None = None,
    due_status: str | None = None,
) -> list[Task]:
    """Filter tasks by multiple criteria (AND logic)."""
    result = tasks

    if status == "complete":
        result = [t for t in result if t.is_complete]
    elif status == "incomplete":
        result = [t for t in result if not t.is_complete]

    if priority:
        result = [t for t in result if t.priority == Priority(priority)]

    if tag:
        result = [t for t in result if tag.lower() in [t.lower() for t in t.tags]]

    if due_status:
        result = [t for t in result if t.due_status == DueStatus(due_status)]

    return result
```

---

## 9. Sort Implementation

### Decision: Stable sort with key functions

### Rationale
- **Python built-in**: `sorted()` with `key` parameter
- **Stable**: Preserves relative order for equal values
- **Null handling**: None values sorted to end

### Implementation
```python
def sort_tasks(
    tasks: list[Task],
    sort_by: str = "id",
    descending: bool = False,
) -> list[Task]:
    """Sort tasks by specified criterion."""
    key_funcs = {
        "id": lambda t: t.id,
        "priority": lambda t: (
            {"high": 0, "medium": 1, "low": 2}.get(
                t.priority.value if t.priority else "medium", 1
            )
        ),
        "title": lambda t: t.title.lower(),
        "due": lambda t: (
            t.due_date if t.due_date else date.max  # None sorts to end
        ),
    }

    key_func = key_funcs.get(sort_by, key_funcs["id"])
    return sorted(tasks, key=key_func, reverse=descending)
```

---

## 10. Error Handling Strategy

### Decision: Custom exception hierarchy

### Rationale
- **Specific**: Different exceptions for different error types
- **Informative**: Include context in error messages
- **CLI-friendly**: Catch at CLI layer, display user-friendly messages

### Implementation
```python
class TodoAppError(Exception):
    """Base exception for Todo App."""
    pass

class TaskNotFoundError(TodoAppError):
    """Raised when task ID does not exist."""
    pass

class ValidationError(TodoAppError):
    """Raised when input validation fails."""
    pass

class InvalidDateError(ValidationError):
    """Raised when date parsing fails."""
    pass

class InvalidPriorityError(ValidationError):
    """Raised when priority value is invalid."""
    pass
```

---

## 11. Testing Strategy

### Decision: Pytest with fixtures and parametrization

### Rationale
- **Constitution mandated**: pytest required
- **Fixtures**: Reusable test data setup
- **Parametrize**: Test multiple inputs efficiently
- **Coverage**: pytest-cov for >90% target

### Best Practices
```python
import pytest
from src.models.task import Task
from src.services.task_service import TaskService

@pytest.fixture
def task_service() -> TaskService:
    """Provide clean TaskService for each test."""
    return TaskService()

@pytest.fixture
def sample_task(task_service: TaskService) -> Task:
    """Provide a sample task for testing."""
    return task_service.add(title="Test Task", description="Test description")

@pytest.mark.parametrize("title,expected_valid", [
    ("Valid title", True),
    ("", False),
    ("   ", False),
    ("A" * 200, True),
    ("A" * 201, False),
])
def test_title_validation(title: str, expected_valid: bool) -> None:
    ...
```

---

## Summary

All technical unknowns resolved. Ready for Phase 1 (data model and contracts).

| Area | Decision | Confidence |
|------|----------|------------|
| CLI Framework | typer | High |
| Date Parsing | python-dateutil | High |
| Output Formatting | rich | Medium (optional) |
| ID Generation | Sequential integer | High |
| Storage | Dictionary in TaskService | High |
| Recurrence | Smart date adjustment | High |
| Search | Case-insensitive substring | High |
| Filters | AND logic | High |
| Sort | Stable sort with key funcs | High |
| Errors | Custom exception hierarchy | High |
| Testing | pytest + fixtures | High |
