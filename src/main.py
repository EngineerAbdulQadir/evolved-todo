"""
Main entry point for Evolved Todo CLI application (T018).

This module initializes the Typer CLI app and registers all commands.
"""

import typer
from rich.console import Console

from src.dependencies import get_task_service

# Initialize CLI app
app = typer.Typer(
    name="todo",
    help="Evolved Todo - A spec-driven CLI todo application",
    add_completion=False,
)

# Initialize console for rich output
console = Console()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version and exit"),
) -> None:
    """Evolved Todo - A spec-driven CLI todo application."""
    if version:
        from src import __version__

        console.print(f"Evolved Todo version {__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        console.print("Use --help for usage information")
        raise typer.Exit()


# Register CLI commands (imported here to avoid circular dependency)
from src.cli.commands import (  # noqa: E402
    app as commands_app,
)

app.add_typer(commands_app, name="", add_help_option=False)


def run_interactive() -> None:
    """Run the menu-driven interactive mode."""
    import sys

    from rich.prompt import Confirm, IntPrompt, Prompt
    from rich.table import Table

    # Get task service
    _task_service = get_task_service()

    def show_welcome() -> None:
        """Display welcome banner."""
        console.print("\n[bold cyan]Welcome to the TODO Application![/bold cyan]")
        console.print(
            "[yellow]All data is stored in memory and will be lost when you exit.[/yellow]\n"
        )

    def show_menu() -> None:
        """Display the main menu."""
        menu_table = Table(show_header=False, box=None, padding=(0, 2))
        menu_table.add_column("Option", style="cyan bold")
        menu_table.add_column("Description", style="white")

        menu_table.add_row("1)", "Add Task")
        menu_table.add_row("2)", "List Tasks")
        menu_table.add_row("3)", "Update Task")
        menu_table.add_row("4)", "Delete Task")
        menu_table.add_row("5)", "Complete/Uncomplete Task")
        menu_table.add_row("6)", "Exit")

        console.print("=" * 60)
        console.print("[bold]TODO Application - Interactive Console[/bold]")
        console.print("=" * 60)
        console.print(menu_table)
        console.print("=" * 60)

    def menu_add_task() -> None:
        """Menu option 1: Add a new task."""
        from datetime import date, time

        from src.cli.formatters import format_error
        from src.models.priority import Priority
        from src.models.recurrence import RecurrencePattern

        console.print("\n[bold cyan]--- Add New Task ---[/bold cyan]")

        # Get title (required)
        title = Prompt.ask("[bold]Title (required)[/bold]")
        if not title.strip():
            format_error("Title cannot be empty")
            return

        # Get description (optional)
        desc_input = Prompt.ask("Description (optional, press Enter to skip)", default="")
        desc: str | None = desc_input if desc_input.strip() else None

        # Get priority (optional)
        priority_input = Prompt.ask("Priority (high/medium/low, press Enter to skip)", default="")
        priority_enum = None
        if priority_input.strip():
            priority_lower = priority_input.lower()
            if priority_lower == "high":
                priority_enum = Priority.HIGH
            elif priority_lower == "medium":
                priority_enum = Priority.MEDIUM
            elif priority_lower == "low":
                priority_enum = Priority.LOW
            else:
                format_error("Invalid priority. Skipping.")

        # Get tags (optional)
        tags_input = Prompt.ask("Tags (comma-separated, press Enter to skip)", default="")
        tags_list = None
        if tags_input.strip():
            tags_list = [tag.strip() for tag in tags_input.split(",") if tag.strip()]

        # Get due date (optional)
        due_date_input = Prompt.ask("Due date (YYYY-MM-DD, press Enter to skip)", default="")
        due_date_obj = None
        if due_date_input.strip():
            try:
                date_parts = due_date_input.split("-")
                due_date_obj = date(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
            except (ValueError, IndexError):
                format_error("Invalid date format. Skipping due date.")

        # Get due time (optional, only if due date is set)
        due_time_obj = None
        if due_date_obj:
            due_time_input = Prompt.ask("Due time (HH:MM, press Enter to skip)", default="")
            if due_time_input.strip():
                try:
                    time_parts = due_time_input.split(":")
                    due_time_obj = time(int(time_parts[0]), int(time_parts[1]))
                except (ValueError, IndexError):
                    format_error("Invalid time format. Skipping due time.")

        # Get recurrence (optional, only if due date is set)
        recurrence_pattern = RecurrencePattern.NONE
        recurrence_day = None
        if due_date_obj:
            recur_input = Prompt.ask(
                "Recurrence (daily/weekly/monthly, press Enter to skip)", default=""
            )
            if recur_input.strip():
                recur_lower = recur_input.lower()
                if recur_lower == "daily":
                    recurrence_pattern = RecurrencePattern.DAILY
                elif recur_lower == "weekly":
                    recurrence_pattern = RecurrencePattern.WEEKLY
                    recur_day_input = Prompt.ask("Recurrence day (1-7 for Mon-Sun)")
                    try:
                        recurrence_day = int(recur_day_input)
                    except ValueError:
                        format_error("Invalid recurrence day. Skipping recurrence.")
                        recurrence_pattern = RecurrencePattern.NONE
                elif recur_lower == "monthly":
                    recurrence_pattern = RecurrencePattern.MONTHLY
                    recur_day_input = Prompt.ask("Recurrence day (1-31)")
                    try:
                        recurrence_day = int(recur_day_input)
                    except ValueError:
                        format_error("Invalid recurrence day. Skipping recurrence.")
                        recurrence_pattern = RecurrencePattern.NONE

        try:
            task = _task_service.add(
                title=title,
                description=desc,
                priority=priority_enum,
                tags=tags_list,
                due_date=due_date_obj,
                due_time=due_time_obj,
                recurrence=recurrence_pattern,
                recurrence_day=recurrence_day,
            )
            console.print(f"[green]✓ Task created: {task.title} (ID: {task.id})[/green]\n")
        except (ValueError, Exception) as e:
            format_error(str(e))

    def menu_list_tasks() -> None:
        """Menu option 2: List all tasks with advanced filtering and sorting."""
        from src.cli.formatters import format_task_list
        from src.models.priority import Priority
        from src.services.search_service import SearchService
        from src.services.sort_service import SortService

        console.print("\n[bold cyan]--- List Tasks ---[/bold cyan]")
        console.print("[dim]Press Enter to skip filters and use defaults[/dim]\n")

        # Get all tasks
        tasks = _task_service.all()
        total_count = len(tasks)

        # Initialize services
        search_service = SearchService()
        sort_service = SortService()

        # Filter by status (all/complete/incomplete)
        status_input = Prompt.ask(
            "Show (all/complete/incomplete)",
            choices=["all", "complete", "incomplete", ""],
            default="",
        )
        status_filter = None if status_input in ("", "all") else status_input

        # Filter by priority
        priority_input = Prompt.ask(
            "Filter by priority (high/medium/low, Enter to skip)", default=""
        )
        priority_filter = None
        if priority_input.strip():
            priority_lower = priority_input.lower()
            if priority_lower == "high":
                priority_filter = Priority.HIGH
            elif priority_lower == "medium":
                priority_filter = Priority.MEDIUM
            elif priority_lower == "low":
                priority_filter = Priority.LOW

        # Filter by tag
        tag_input = Prompt.ask("Filter by tag (Enter to skip)", default="")
        tag_filter = tag_input if tag_input.strip() else None

        # Search by keyword
        keyword_input = Prompt.ask("Search keyword (Enter to skip)", default="")
        keyword_filter = keyword_input if keyword_input.strip() else None

        # Apply search and filters
        tasks = search_service.search_and_filter(
            tasks,
            keyword=keyword_filter,
            status=status_filter,
            priority=priority_filter,
            tag=tag_filter,
        )

        # Sort options
        sort_input = Prompt.ask(
            "Sort by (id/title/priority/due-date/created, Enter for id)",
            choices=["", "id", "title", "priority", "due-date", "created"],
            default="",
        )
        sort_by = sort_input if sort_input.strip() else "id"

        # Sort order
        desc_input = Prompt.ask(
            "Sort order (asc/desc, Enter for asc)", choices=["", "asc", "desc"], default=""
        )
        descending = desc_input == "desc"

        # Apply sorting
        try:
            tasks = sort_service.sort_tasks(tasks, sort_by=sort_by, descending=descending)
        except ValueError as e:
            from src.cli.formatters import format_error

            format_error(str(e))
            return

        # Display results
        console.print()
        if len(tasks) < total_count:
            console.print(f"[dim]Showing {len(tasks)} of {total_count} tasks[/dim]")
        format_task_list(tasks)
        console.print()

    def menu_update_task() -> None:
        """Menu option 3: Update a task with all advanced options."""
        from datetime import date, time

        from src.cli.formatters import format_error
        from src.models.priority import Priority
        from src.models.recurrence import RecurrencePattern
        from src.services.task_service import TaskService

        console.print("\n[bold cyan]--- Update Task ---[/bold cyan]")

        # Get task ID
        try:
            task_id = IntPrompt.ask("Task ID to update")
            task = _task_service.get(task_id)
        except ValueError:
            format_error("Invalid task ID")
            return
        except Exception as e:
            format_error(str(e))
            return

        console.print(f"\nCurrent: [cyan]{task.title}[/cyan]")
        console.print("[dim]Press Enter to keep current value[/dim]\n")

        # Update title
        title_input = Prompt.ask("New title (Enter to keep)", default="")
        title: str | None = title_input if title_input.strip() else None

        # Update description
        desc_input = Prompt.ask("New description (Enter to keep)", default="")
        desc: str | None = desc_input if desc_input.strip() else None

        # Update priority
        priority_val = Prompt.ask("New priority (high/medium/low/none, Enter to keep)", default="")
        priority_enum = TaskService._UNSET
        if priority_val.strip():
            priority_lower = priority_val.lower()
            if priority_lower == "none":
                priority_enum = None
            elif priority_lower == "high":
                priority_enum = Priority.HIGH
            elif priority_lower == "medium":
                priority_enum = Priority.MEDIUM
            elif priority_lower == "low":
                priority_enum = Priority.LOW

        # Update tags - add tags
        add_tags_input = Prompt.ask("Add tags (comma-separated, Enter to skip)", default="")
        add_tags_list = None
        if add_tags_input.strip():
            add_tags_list = [tag.strip() for tag in add_tags_input.split(",") if tag.strip()]

        # Update tags - remove tags
        remove_tags_input = Prompt.ask("Remove tags (comma-separated, Enter to skip)", default="")
        remove_tags_list = None
        if remove_tags_input.strip():
            remove_tags_list = [tag.strip() for tag in remove_tags_input.split(",") if tag.strip()]

        # Update due date
        due_date_val = Prompt.ask("New due date (YYYY-MM-DD or 'none', Enter to keep)", default="")
        due_date_obj = TaskService._UNSET
        if due_date_val.strip():
            if due_date_val.lower() == "none":
                due_date_obj = None
            else:
                try:
                    date_parts = due_date_val.split("-")
                    due_date_obj = date(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
                except (ValueError, IndexError):
                    format_error("Invalid date format. Skipping.")
                    due_date_obj = TaskService._UNSET

        # Update due time
        due_time_val = Prompt.ask("New due time (HH:MM or 'none', Enter to keep)", default="")
        due_time_obj = TaskService._UNSET
        if due_time_val.strip():
            if due_time_val.lower() == "none":
                due_time_obj = None
            else:
                try:
                    time_parts = due_time_val.split(":")
                    due_time_obj = time(int(time_parts[0]), int(time_parts[1]))
                except (ValueError, IndexError):
                    format_error("Invalid time format. Skipping.")
                    due_time_obj = TaskService._UNSET

        # Update recurrence pattern
        recur_val = Prompt.ask(
            "New recurrence (daily/weekly/monthly/none, Enter to keep)", default=""
        )
        recurrence_obj = TaskService._UNSET
        recurrence_day_obj = TaskService._UNSET
        if recur_val.strip():
            recur_lower = recur_val.lower()
            if recur_lower == "none":
                recurrence_obj = RecurrencePattern.NONE
                recurrence_day_obj = None
            elif recur_lower == "daily":
                recurrence_obj = RecurrencePattern.DAILY
                recurrence_day_obj = None
            elif recur_lower == "weekly":
                recurrence_obj = RecurrencePattern.WEEKLY
                recur_day_input = Prompt.ask("Recurrence day (1-7 for Mon-Sun)")
                try:
                    recurrence_day_obj = int(recur_day_input)
                except ValueError:
                    format_error("Invalid recurrence day. Skipping recurrence.")
                    recurrence_obj = TaskService._UNSET
                    recurrence_day_obj = TaskService._UNSET
            elif recur_lower == "monthly":
                recurrence_obj = RecurrencePattern.MONTHLY
                recur_day_input = Prompt.ask("Recurrence day (1-31)")
                try:
                    recurrence_day_obj = int(recur_day_input)
                except ValueError:
                    format_error("Invalid recurrence day. Skipping recurrence.")
                    recurrence_obj = TaskService._UNSET
                    recurrence_day_obj = TaskService._UNSET

        try:
            updated_task = _task_service.update(
                task_id=task_id,
                title=title,
                description=desc,
                priority=priority_enum,
                add_tags=add_tags_list,
                remove_tags=remove_tags_list,
                due_date=due_date_obj,
                due_time=due_time_obj,
                recurrence=recurrence_obj,
                recurrence_day=recurrence_day_obj,
            )
            console.print(f"[green]✓ Task updated: {updated_task.title}[/green]\n")
        except Exception as e:
            format_error(str(e))

    def menu_delete_task() -> None:
        """Menu option 4: Delete a task."""
        from src.cli.formatters import format_error

        console.print("\n[bold cyan]--- Delete Task ---[/bold cyan]")

        try:
            task_id = IntPrompt.ask("Task ID to delete")
            task = _task_service.get(task_id)

            confirm = Confirm.ask(f"Delete task #{task_id}: '{task.title}'?", default=False)
            if confirm:
                _task_service.delete(task_id)
                console.print(f"[green]✓ Task #{task_id} deleted[/green]\n")
            else:
                console.print("[yellow]Deletion cancelled[/yellow]\n")
        except ValueError:
            format_error("Invalid task ID")
        except Exception as e:
            format_error(str(e))

    def menu_complete_task() -> None:
        """Menu option 5: Toggle task completion."""
        from src.cli.formatters import format_error

        console.print("\n[bold cyan]--- Complete/Uncomplete Task ---[/bold cyan]")

        try:
            task_id = IntPrompt.ask("Task ID to toggle")
            task = _task_service.toggle_complete(task_id)

            status = "completed" if task.is_complete else "marked incomplete"
            console.print(f"[green]✓ Task #{task_id} {status}[/green]\n")
        except ValueError:
            format_error("Invalid task ID")
        except Exception as e:
            format_error(str(e))

    # Show welcome screen
    show_welcome()

    # Main menu loop
    while True:
        try:
            show_menu()
            choice = Prompt.ask("\nEnter choice (1-6)", choices=["1", "2", "3", "4", "5", "6"])

            if choice == "1":
                menu_add_task()
            elif choice == "2":
                menu_list_tasks()
            elif choice == "3":
                menu_update_task()
            elif choice == "4":
                menu_delete_task()
            elif choice == "5":
                menu_complete_task()
            elif choice == "6":
                console.print("\n[yellow]Goodbye![/yellow]\n")
                sys.exit(0)

        except KeyboardInterrupt:
            console.print("\n[yellow]Use option 6 to exit[/yellow]")
            continue
        except EOFError:
            console.print("\n[yellow]Goodbye![/yellow]\n")
            sys.exit(0)


if __name__ == "__main__":
    # Run interactive mode when executed directly
    run_interactive()
else:
    # Used as a module by the CLI
    pass
