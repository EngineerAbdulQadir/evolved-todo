---
name: cli-command
description: Create CLI commands using Typer framework with Rich formatting, proper error handling, and user-friendly output. Use when implementing CLI tasks (T024, T030, T036, T042, etc.).
---

# CLI Command

## Instructions

Follow these steps when creating CLI commands:

### Command Structure

All CLI commands follow this pattern:

```python
import typer
from typing import Optional
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def command_name(
    arg1: str = typer.Argument(..., help="Description"),
    option1: Optional[str] = typer.Option(None, "--opt", help="Description"),
) -> None:
    """Command description for help text."""
    try:
        # 1. Validate inputs
        # 2. Call service layer
        # 3. Format output with rich
        # 4. Handle errors gracefully
        pass
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
```

## CLI Command Checklist

- [ ] **Import statements**: typer, Optional, rich.console
- [ ] **Type hints**: All parameters and return types annotated
- [ ] **Docstring**: Clear description shown in `--help`
- [ ] **Argument/Option help**: Every parameter has help text
- [ ] **Service layer call**: No business logic in CLI, delegate to services
- [ ] **Rich formatting**: Use rich for colored output, tables, panels
- [ ] **Error handling**: Try/except with user-friendly messages
- [ ] **Exit codes**: 0 for success, 1 for errors
- [ ] **Integration test**: Test in `tests/integration/test_cli_*.py`

## Examples

### Example 1: Add Command (T024)
```python
@app.command("add")
def add_task(
    title: str = typer.Argument(..., help="Task title (1-200 chars)"),
    desc: Optional[str] = typer.Option(None, "--desc", "-d", help="Task description"),
) -> None:
    """Create a new task."""
    try:
        task = task_service.add(title=title, description=desc)
        console.print(f"[green]✓[/green] Task #{task.id} created: {task.title}")
    except ValidationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
```

### Example 2: List Command (T030)
```python
@app.command("list")
def list_tasks() -> None:
    """Display all tasks."""
    tasks = task_service.all()
    if not tasks:
        console.print("[yellow]No tasks found.[/yellow]")
        return

    # Use rich Table for formatting
    from rich.table import Table
    table = Table(title="Tasks")
    table.add_column("ID", style="cyan")
    table.add_column("Status")
    table.add_column("Title")

    for task in tasks:
        status = "[green]✓[/green]" if task.is_complete else "[ ]"
        table.add_row(str(task.id), status, task.title)

    console.print(table)
```

### Example 3: Update Command (T036)
```python
@app.command("update")
def update_task(
    task_id: int = typer.Argument(..., help="Task ID"),
    title: Optional[str] = typer.Option(None, "--title", help="New title"),
    desc: Optional[str] = typer.Option(None, "--desc", help="New description"),
) -> None:
    """Update task fields."""
    if not title and not desc:
        console.print("[yellow]Warning:[/yellow] No fields to update")
        return

    try:
        task = task_service.update(task_id, title=title, description=desc)
        console.print(f"[green]✓[/green] Task #{task_id} updated")
    except TaskNotFoundError:
        console.print(f"[red]Error:[/red] Task #{task_id} not found")
        raise typer.Exit(code=1)
```

### Example 4: Testing CLI Commands

```python
# tests/integration/test_cli_add.py
from typer.testing import CliRunner
from src.main import app

runner = CliRunner()

def test_add_task_success():
    result = runner.invoke(app, ["add", "Buy milk", "--desc", "From store"])
    assert result.exit_code == 0
    assert "created" in result.stdout.lower()

def test_add_task_validation_error():
    result = runner.invoke(app, ["add", ""])  # Empty title
    assert result.exit_code == 1
    assert "error" in result.stdout.lower()
```

## Integration with Subagents

- **ux-advocate**: Review command UX after implementation
- **doc-curator**: Verify help text and documentation
- **test-guardian**: Ensure integration test coverage
