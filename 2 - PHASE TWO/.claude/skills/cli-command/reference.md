# CLI Command Reference

## Typer Framework Deep Dive

### Command Registration Patterns

```python
import typer
from typing import Optional, List
from enum import Enum

app = typer.Typer(
    name="todo",
    help="A powerful CLI todo application",
    add_completion=True,
)

# Subcommand groups
task_app = typer.Typer(help="Task management commands")
app.add_typer(task_app, name="task")

@task_app.command("add")
def add_task(...):
    """Add a new task."""
    pass
```

### Argument vs Option Guidelines

**Arguments** (Positional):
- Required values
- Natural order
- Examples: task_id, title

**Options** (Flags):
- Optional values
- Named parameters
- Examples: --priority, --tags, --force

### Rich Console Patterns

```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress

console = Console()

# Colored output
console.print("[green]Success![/green]")
console.print("[red]Error:[/red] Something failed")
console.print("[yellow]Warning:[/yellow] Be careful")

# Tables
table = Table(title="Tasks")
table.add_column("ID", style="cyan")
table.add_column("Title")
console.print(table)

# Panels
panel = Panel("Important message", title="Notice")
console.print(panel)

# Progress bars
with Progress() as progress:
    task = progress.add_task("Processing...", total=100)
    # ... do work ...
    progress.update(task, advance=10)
```

### Exit Codes Standard

- 0: Success
- 1: General error
- 2: Misuse of command
- 126: Command cannot execute
- 127: Command not found
- 130: Ctrl+C interrupt

### Command Help Best Practices

```python
@app.command()
def add(
    title: str = typer.Argument(..., help="Task title (1-200 characters)"),
    priority: Optional[str] = typer.Option(
        None,
        "--priority", "-p",
        help="Priority level: low, medium, high"
    ),
) -> None:
    """
    Create a new task with title and optional attributes.

    Examples:

      Create simple task:
      $ todo add "Buy milk"

      Create with priority:
      $ todo add "Important task" --priority high

      Create with all options:
      $ todo add "Complex task" -p high --tags work,urgent --due 2025-12-31
    """
    pass
```

## CLI Testing Strategies

### Using CliRunner

```python
from typer.testing import CliRunner
from src.main import app

runner = CliRunner()

def test_add_command():
    result = runner.invoke(app, ["add", "Buy milk"])
    assert result.exit_code == 0
    assert "created" in result.stdout.lower()

def test_add_with_options():
    result = runner.invoke(app, [
        "add", "Task",
        "--priority", "high",
        "--tags", "work,urgent"
    ])
    assert result.exit_code == 0
```

### Testing Error Cases

```python
def test_add_empty_title():
    result = runner.invoke(app, ["add", ""])
    assert result.exit_code == 1
    assert "error" in result.stdout.lower()

def test_invalid_priority():
    result = runner.invoke(app, ["add", "Task", "--priority", "invalid"])
    assert result.exit_code == 1
    assert "invalid priority" in result.stdout.lower()
```

## Advanced Patterns

### Confirmation Prompts

```python
def delete_task(
    task_id: int,
    force: bool = typer.Option(False, "--force", "-f")
) -> None:
    """Delete task with confirmation."""
    if not force:
        confirmed = typer.confirm(f"Delete task #{task_id}?")
        if not confirmed:
            console.print("Cancelled")
            raise typer.Abort()

    # Proceed with deletion
    service.delete(task_id)
```

### Interactive Prompts

```python
def interactive_add() -> None:
    """Add task interactively."""
    title = typer.prompt("Task title")
    priority = typer.prompt(
        "Priority",
        type=typer.Choice(["low", "medium", "high"]),
        default="medium"
    )
    task = service.add(title, priority=Priority(priority))
    console.print(f"Created task #{task.id}")
```

### File Path Handling

```python
from pathlib import Path

def import_tasks(
    file: Path = typer.Argument(..., exists=True, dir_okay=False)
) -> None:
    """Import tasks from JSON file."""
    if not file.suffix == ".json":
        console.print("[red]Error:[/red] File must be .json")
        raise typer.Exit(code=1)

    with open(file) as f:
        data = json.load(f)
    # ... process data ...
```

## Error Handling Best Practices

### User-Friendly Error Messages

```python
try:
    task = service.get(task_id)
except TaskNotFoundError:
    console.print(f"[red]Error:[/red] Task #{task_id} not found")
    console.print("[yellow]Hint:[/yellow] Use 'todo list' to see all tasks")
    raise typer.Exit(code=1)
except ValidationError as e:
    console.print(f"[red]Validation Error:[/red] {e}")
    console.print("[yellow]Hint:[/yellow] Check input format")
    raise typer.Exit(code=1)
```

### Context Managers for Cleanup

```python
from contextlib import contextmanager

@contextmanager
def error_handler():
    """Handle errors gracefully."""
    try:
        yield
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
        raise typer.Abort()
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise typer.Exit(code=2)

@app.command()
def risky_command():
    """Command with error handling."""
    with error_handler():
        # Command logic
        pass
```

## Resources

- Typer Documentation: https://typer.tiangolo.com/
- Rich Documentation: https://rich.readthedocs.io/
- Click (Typer's foundation): https://click.palletsprojects.com/
