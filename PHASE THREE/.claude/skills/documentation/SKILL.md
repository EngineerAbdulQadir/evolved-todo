---
name: documentation
description: Create comprehensive, accurate documentation for all code. Use when writing public functions, classes, modules, or CLI commands.
---

# Documentation

## Instructions

### When to Use

- Writing any public function, class, or module
- Before committing code
- Creating CLI commands
- Adding complex algorithms

## Examples

### Example 1: Function Docstring (Google Style)

```python
def add_task(
    title: str,
    description: Optional[str] = None,
    priority: Priority = Priority.MEDIUM,
) -> Task:
    """
    Create a new task with validation.

    Args:
        title: Task title (1-200 characters, non-empty)
        description: Optional task description (max 1000 chars)
        priority: Task priority level (default: MEDIUM)

    Returns:
        Created task with generated ID

    Raises:
        ValidationError: If title/description validation fails

    Examples:
        >>> task = add_task("Buy milk", "From store", Priority.HIGH)
        >>> task.title
        'Buy milk'

    See Also:
        - update_task(): Update existing task
        - delete_task(): Remove task
    """
    ...
```

### Classes

```python
class TaskService:
    """
    Business logic layer for task management.

    Handles task CRUD operations with validation and storage.

    Attributes:
        _store: In-memory storage for tasks
        _id_gen: Sequential ID generator

    Examples:
        >>> service = TaskService(store, id_gen)
        >>> task = service.add(title="Buy milk")
        >>> task.id
        1
    """

    def __init__(self, store: TaskStore, id_gen: IdGenerator) -> None:
        """
        Initialize task service.

        Args:
            store: Storage backend for tasks
            id_gen: ID generator for new tasks
        """
        self._store = store
        self._id_gen = id_gen
```

### Modules

```python
"""
Task management services.

This module provides business logic for task operations including
creation, updates, completion tracking, and deletion.

Core Classes:
    - TaskService: Main task management service
    - SearchService: Task search and filtering
    - SortService: Task sorting operations

Example:
    >>> from src.services.task_service import TaskService
    >>> service = TaskService(store, id_gen)
    >>> task = service.add(title="Buy milk")
"""
```

## README.md Structure

```markdown
# Project Name

Brief description (1-2 sentences)

## Features

- Feature 1
- Feature 2

## Installation

\`\`\`bash
# Steps to install
\`\`\`

## Quick Start

\`\`\`bash
# Basic usage examples
\`\`\`

## Documentation

- [Architecture](docs/architecture.md)
- [API Reference](docs/api.md)
- [Contributing](docs/contributing.md)

## License

MIT
```

## CLI Help Text

```python
@app.command("add")
def add_task(
    title: str = typer.Argument(
        ...,
        help="Task title (1-200 characters, non-empty)"
    ),
    desc: Optional[str] = typer.Option(
        None,
        "--desc", "-d",
        help="Optional task description (max 1000 chars)"
    ),
) -> None:
    """
    Create a new task.

    Examples:

        Create task with title only:
        $ todo add "Buy milk"

        Create task with description:
        $ todo add "Buy milk" --desc "From store on Main St"

        Create task with priority:
        $ todo add "Important task" --priority high
    """
    ...
```

## Integration with doc-curator Subagent

Invoke before committing:

```
Reviews:
- All public APIs have docstrings
- README is complete and accurate
- CLI help text is user-friendly
- Code examples work
- No outdated documentation
```
