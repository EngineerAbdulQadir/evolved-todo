"""
Output formatters for CLI commands using Rich library.

Tasks: T026, T029, T031, T039, T043, T056, T063, T070, T071, T077
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.models.task import Task

console = Console()


def format_task_added(task: Task) -> None:
    """
    Display success message when task is added (T026 - US1).

    Args:
        task: The newly created task
    """
    message = f"[OK] Task #{task.id} created: {task.title}"
    console.print(f"[green]{message}[/green]")


def format_error(message: str) -> None:
    """
    Display error message (T026 - US1).

    Args:
        message: Error message to display
    """
    console.print(f"[red][ERROR] {message}[/red]")


def format_task_list(
    tasks: list[Task],
    total_count: int | None = None,
    sort_by: str = "id",
    descending: bool = False,
) -> None:
    """
    Display list of tasks in table format (T029, T056, T063, T069, T077 - US2, US6, US7, US8, US9).

    Args:
        tasks: List of tasks to display
        total_count: Total count before filtering (optional, for "Showing X of Y")
        sort_by: Current sort field (optional, for display indicator)
        descending: Current sort direction (optional, for display indicator)
    """
    if not tasks:
        format_empty_list()
        return

    # Show filtered count and sort order
    title = "Tasks"
    if total_count is not None and total_count > len(tasks):
        title = f"Tasks (Showing {len(tasks)} of {total_count})"

    # Add sort indicator (T077)
    sort_direction = "↓" if descending else "↑"
    if sort_by and sort_by != "id":  # Only show for non-default sorts
        title += f" [sorted by {sort_by} {sort_direction}]"

    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", width=6)
    table.add_column("Status", width=8)
    table.add_column("Priority", width=8)
    table.add_column("Title", style="white", width=12, no_wrap=False)
    table.add_column("Due Date", width=18)
    table.add_column("Tags", style="blue", width=8)
    table.add_column("Description", style="dim")

    for task in tasks:
        status = "[green][X][/green]" if task.is_complete else "[ ]"

        # Format priority with color
        if task.priority:
            if task.priority.value == "high":
                priority_display = "[red]HIGH[/red]"
            elif task.priority.value == "medium":
                priority_display = "[yellow]MED[/yellow]"
            else:  # low
                priority_display = "[dim]LOW[/dim]"
        else:
            priority_display = "-"

        # Format due date with overdue indicator
        if task.due_date:
            from src.models.priority import DueStatus

            due_display = task.display_due
            # Shorten format for table: "Dec 15, 2025" -> "Dec 15"
            if " at " in due_display:
                date_part, time_part = due_display.split(" at ")
                # Remove year from date for compact display
                date_short = ", ".join(date_part.split(", ")[:-1])
                due_display = f"{date_short} {time_part}"
            else:
                # Remove year for compact display
                due_display = ", ".join(due_display.split(", ")[:-1])

            # Add overdue indicator
            if task.due_status == DueStatus.OVERDUE:
                due_display = f"[red]⚠ {due_display}[/red]"
            elif task.due_status == DueStatus.DUE_TODAY:
                due_display = f"[yellow]● {due_display}[/yellow]"
            else:  # UPCOMING
                due_display = f"[dim]{due_display}[/dim]"
        else:
            due_display = "-"

        title_text = task.title
        tags_display = ", ".join(task.tags) if task.tags else "-"
        description = task.description or ""

        table.add_row(
            str(task.id),
            status,
            priority_display,
            title_text,
            due_display,
            tags_display[:30] + "..." if len(tags_display) > 30 else tags_display,
            description[:40] + "..." if len(description) > 40 else description,
        )

    console.print(table)


def format_empty_list() -> None:
    """Display message when task list is empty (T031 - US2)."""
    message = "No tasks found. Create your first task with 'todo add <title>'"
    console.print(f"[yellow]{message}[/yellow]")


def format_task_detail(task: Task) -> None:
    """
    Display detailed view of a single task (T033, T069 - US2, US8).

    Args:
        task: Task to display
    """
    status = "[X] Complete" if task.is_complete else "[ ] Incomplete"
    status_color = "green" if task.is_complete else "yellow"

    lines = [
        f"[bold]Task #{task.id}[/bold]",
        f"Status: [{status_color}]{status}[/{status_color}]",
        f"Title: {task.title}",
    ]

    if task.description:
        lines.append(f"Description: {task.description}")

    if task.priority:
        lines.append(f"Priority: {task.priority.value}")

    if task.tags:
        lines.append(f"Tags: {', '.join(task.tags)}")

    # Always show due date field (T069)
    lines.append(f"Due: {task.display_due}")

    lines.append(f"Created: {task.created_at.strftime('%b %d, %Y at %I:%M %p')}")

    panel = Panel("\n".join(lines), title="Task Details", border_style="blue")
    console.print(panel)


def format_task_updated(task: Task) -> None:
    """
    Display success message when task is updated (T039 - US3).

    Args:
        task: The updated task
    """
    message = f"[OK] Task #{task.id} updated: {task.title}"
    console.print(f"[green]{message}[/green]")


def format_task_completed(task: Task) -> None:
    """
    Display success message when task is marked complete (T043 - US4).

    Args:
        task: The completed/uncompleted task
    """
    if task.is_complete:
        message = f"[OK] Task #{task.id} marked as complete"
        console.print(f"[green]{message}[/green]")
    else:
        message = f"[OK] Task #{task.id} marked as incomplete"
        console.print(f"[yellow]{message}[/yellow]")


def format_task_deleted(task_id: int) -> None:
    """
    Display success message when task is deleted.

    Args:
        task_id: ID of deleted task
    """
    message = f"[OK] Task #{task_id} deleted"
    console.print(f"[green]{message}[/green]")
