---
name: error-handling
description: Implement robust error handling and exception management patterns. Use when implementing service methods, CLI commands, or parsing user data.
---

# Error Handling

## Instructions

### When to Use

- Implementing any service layer method
- Creating CLI commands with user input
- Parsing dates, tags, or other user data
- File I/O or external operations

## Exception Hierarchy

```python
# src/models/exceptions.py
class TodoAppError(Exception):
    """Base exception for all application errors."""
    pass

class ValidationError(TodoAppError):
    """Raised when input validation fails."""
    pass

class TaskNotFoundError(TodoAppError):
    """Raised when task ID doesn't exist."""
    pass

class StorageError(TodoAppError):
    """Raised on storage operation failure."""
    pass

class ParseError(TodoAppError):
    """Raised when parsing fails (dates, tags, etc.)."""
    pass
```

## Examples

### Error Handling Patterns

### 1. Service Layer (Business Logic)

```python
from src.models.exceptions import TaskNotFoundError, ValidationError

class TaskService:
    def update(self, task_id: int, **kwargs) -> Task:
        """Update task - raises specific exceptions."""
        # Validate first
        if not task_id or task_id < 1:
            raise ValidationError("Invalid task ID")

        # Check existence
        task = self._store.get(task_id)
        if not task:
            raise TaskNotFoundError(f"Task #{task_id} not found")

        # Business logic
        # ... update logic ...

        return updated_task
```

### 2. CLI Layer (User Interface)

```python
import typer
from rich.console import Console
from src.models.exceptions import TaskNotFoundError, ValidationError

console = Console()

@app.command("update")
def update_task(task_id: int, title: str = None) -> None:
    """Update task - handles exceptions gracefully."""
    try:
        task = task_service.update(task_id, title=title)
        console.print(f"[green]✓[/green] Task #{task_id} updated")

    except ValidationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)

    except TaskNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        console.print("[yellow]Hint:[/yellow] Use 'todo list' to see all tasks")
        raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise typer.Exit(code=2)
```

### 3. Parser/Validator Functions

```python
from datetime import datetime, date
from src.models.exceptions import ParseError

def parse_due_date(date_str: str) -> date:
    """
    Parse natural language date strings.

    Raises:
        ParseError: If date format is invalid
    """
    date_str = date_str.strip().lower()

    # Handle relative dates
    if date_str == "today":
        return datetime.now().date()

    if date_str == "tomorrow":
        return datetime.now().date() + timedelta(days=1)

    # Handle absolute dates
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        try:
            return datetime.strptime(date_str, "%m/%d/%Y").date()
        except ValueError:
            raise ParseError(
                f"Invalid date format: '{date_str}'. "
                f"Use 'today', 'tomorrow', or YYYY-MM-DD"
            )
```

## Error Message Guidelines

### DO: User-Friendly Messages

```python
# Good
raise ValidationError("Title cannot be empty")
raise ValidationError("Title must be between 1-200 characters")
raise TaskNotFoundError(f"Task #{task_id} not found")
raise ParseError("Invalid date format. Use 'today', 'tomorrow', or YYYY-MM-DD")
```

### DON'T: Technical Jargon

```python
# Bad
raise Exception("NoneType object has no attribute 'id'")
raise Exception("Index out of range")
raise Exception("Validation failed")
```

## Error Recovery Strategies

### 1. Retry with Exponential Backoff (for transient errors)

```python
import time
from typing import TypeVar, Callable

T = TypeVar('T')

def retry_on_error(
    func: Callable[[], T],
    max_attempts: int = 3,
    base_delay: float = 0.1
) -> T:
    """Retry function on failure with exponential backoff."""
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise

            delay = base_delay * (2 ** attempt)
            time.sleep(delay)

    raise RuntimeError("Unreachable")  # For type checker
```

### 2. Graceful Degradation

```python
def get_task_with_stats(task_id: int) -> dict:
    """Get task with statistics, gracefully handle stat failures."""
    try:
        task = task_service.get(task_id)
    except TaskNotFoundError:
        raise  # Don't catch this, let it propagate

    # Get optional stats (non-critical)
    stats = {}
    try:
        stats = compute_task_stats(task)
    except Exception as e:
        # Log error but don't fail the request
        logger.warning(f"Failed to compute stats: {e}")
        stats = {"error": "Stats unavailable"}

    return {
        "task": task,
        "stats": stats
    }
```

### 3. Context Managers for Cleanup

```python
from contextlib import contextmanager
from typing import Iterator

@contextmanager
def transaction() -> Iterator[None]:
    """Transaction context with rollback on error."""
    snapshot = store.create_snapshot()
    try:
        yield
    except Exception:
        store.restore_snapshot(snapshot)
        raise
```

## Logging Errors

```python
import logging

logger = logging.getLogger(__name__)

def risky_operation() -> None:
    """Operation that might fail - log errors."""
    try:
        # ... operation ...
        pass
    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in risky_operation: {e}")
        raise
```

## Testing Error Paths

```python
import pytest
from src.models.exceptions import ValidationError, TaskNotFoundError

def test_update_task_not_found():
    """Updating non-existent task should raise TaskNotFoundError."""
    with pytest.raises(TaskNotFoundError, match="Task #999 not found"):
        task_service.update(999, title="New title")

def test_empty_title_validation():
    """Empty title should raise ValidationError with helpful message."""
    with pytest.raises(ValidationError, match="Title cannot be empty"):
        task_service.add(title="")

def test_invalid_date_format():
    """Invalid date should raise ParseError with format hint."""
    with pytest.raises(ParseError, match="Invalid date format"):
        parse_due_date("not-a-date")
```

## Integration with security-sentinel Subagent

Invoke after implementing error handling:

```
Reviews for:
- Information leakage in error messages (no stack traces to users)
- Proper input sanitization before error messages
- No sensitive data in logs
- Appropriate error granularity (not too specific for attackers)
```

## See Also

- `templates/error-handler-template.py` - Error handling template
- `scripts/error-analyzer.py` - Analyze error patterns in codebase
- `reference.md` - Extended error handling patterns
