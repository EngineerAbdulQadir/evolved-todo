"""
CLI command definitions using Typer.

Tasks: T024, T030, T033, T036, T042, T047, T048, T054, T055, T061, T069, T076,
T083
"""

from typing import Annotated

import typer

from src.cli.formatters import (
    format_error,
    format_task_added,
    format_task_detail,
    format_task_list,
)
from src.dependencies import get_task_service
from src.models.exceptions import TaskNotFoundError, ValidationError

app = typer.Typer()


@app.command("add")
def add_task(
    title: Annotated[str, typer.Argument(help="Task title (required)")],
    desc: Annotated[
        str | None, typer.Option("--desc", "-d", help="Task description (optional)")
    ] = None,
    priority: Annotated[
        str | None,
        typer.Option("--priority", "-p", help="Priority: high, medium, or low"),
    ] = None,
    tags: Annotated[
        str | None,
        typer.Option("--tags", "-t", help="Comma-separated tags (e.g., 'work,urgent')"),
    ] = None,
    due_date: Annotated[
        str | None,
        typer.Option("--due-date", help="Due date (YYYY-MM-DD format)"),
    ] = None,
    due_time: Annotated[
        str | None,
        typer.Option("--due-time", help="Due time (HH:MM format, 24-hour)"),
    ] = None,
    recur: Annotated[
        str | None,
        typer.Option("--recur", help="Recurrence: daily, weekly, or monthly"),
    ] = None,
    recur_day: Annotated[
        int | None,
        typer.Option(
            "--recur-day", help="Day for weekly (1-7 Mon-Sun) or monthly (1-31) recurrence"
        ),
    ] = None,
) -> None:
    """
    Create a new task with title, description, priority, tags, due date, and recurrence (T024, T054, T067, T083 - US1, US6, US8, US10).

    Examples:
        todo add "Buy milk"
        todo add "Prepare presentation" --desc "Include Q3 revenue charts"
        todo add "Meeting with team" -d "Discuss project timeline"
        todo add "Fix bug" --priority high --tags "work,urgent"
        todo add "Review PR" -p medium -t "code-review,team"
        todo add "Submit report" --due-date 2025-12-15
        todo add "Team meeting" --due-date 2025-12-10 --due-time 14:00
        todo add "Daily standup" --due-date 2025-12-10 --due-time 09:00 --recur daily
        todo add "Weekly review" --due-date 2025-12-12 --recur weekly --recur-day 5
        todo add "Monthly report" --due-date 2025-12-01 --recur monthly --recur-day 1
    """
    from datetime import date, time

    from src.models.priority import Priority
    from src.models.recurrence import RecurrencePattern

    try:
        # Parse priority
        priority_enum = None
        if priority:
            priority_lower = priority.lower()
            if priority_lower == "high":
                priority_enum = Priority.HIGH
            elif priority_lower == "medium":
                priority_enum = Priority.MEDIUM
            elif priority_lower == "low":
                priority_enum = Priority.LOW
            else:
                format_error(f"Invalid priority '{priority}'. Must be: high, medium, or low")
                raise typer.Exit(code=1)

        # Parse tags
        tags_list = None
        if tags:
            tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

        # Parse due date
        due_date_obj = None
        if due_date:
            try:
                year, month, day = map(int, due_date.split("-"))
                due_date_obj = date(year, month, day)
            except (ValueError, TypeError):
                format_error(
                    f"Invalid due date '{due_date}'. Use YYYY-MM-DD format (e.g., 2025-12-15)"
                )
                raise typer.Exit(code=1)

        # Parse due time
        due_time_obj = None
        if due_time:
            try:
                hour, minute = map(int, due_time.split(":"))
                due_time_obj = time(hour, minute)
            except (ValueError, TypeError):
                format_error(f"Invalid due time '{due_time}'. Use HH:MM format (e.g., 14:30)")
                raise typer.Exit(code=1)

        # Parse recurrence (T083)
        recurrence = RecurrencePattern.NONE
        recurrence_day_val = None

        if recur:
            recur_lower = recur.lower()
            if recur_lower == "daily":
                recurrence = RecurrencePattern.DAILY
            elif recur_lower == "weekly":
                recurrence = RecurrencePattern.WEEKLY
                if recur_day is None:
                    format_error("Weekly recurrence requires --recur-day (1-7 for Mon-Sun)")
                    raise typer.Exit(code=1)
                if not (1 <= recur_day <= 7):
                    format_error(
                        f"Invalid --recur-day '{recur_day}' for weekly. Must be 1-7 (Mon-Sun)"
                    )
                    raise typer.Exit(code=1)
                recurrence_day_val = recur_day
            elif recur_lower == "monthly":
                recurrence = RecurrencePattern.MONTHLY
                if recur_day is None:
                    format_error("Monthly recurrence requires --recur-day (1-31 for day of month)")
                    raise typer.Exit(code=1)
                if not (1 <= recur_day <= 31):
                    format_error(f"Invalid --recur-day '{recur_day}' for monthly. Must be 1-31")
                    raise typer.Exit(code=1)
                recurrence_day_val = recur_day
            else:
                format_error(f"Invalid recurrence '{recur}'. Must be: daily, weekly, or monthly")
                raise typer.Exit(code=1)

            # Recurrence requires a due date
            if due_date_obj is None:
                format_error("Recurring tasks require a --due-date")
                raise typer.Exit(code=1)

        task_service = get_task_service()
        task = task_service.add(
            title=title,
            description=desc,
            priority=priority_enum,
            tags=tags_list,
            due_date=due_date_obj,
            due_time=due_time_obj,
            recurrence=recurrence,
            recurrence_day=recurrence_day_val,
        )
        format_task_added(task)
    except (ValueError, ValidationError) as e:
        format_error(str(e))
        raise typer.Exit(code=1) from e


@app.command("list")
def list_tasks(
    search: Annotated[
        str | None,
        typer.Option("--search", "-s", help="Search keyword in title/description"),
    ] = None,
    status: Annotated[
        str | None,
        typer.Option("--status", help="Filter by status: complete or incomplete"),
    ] = None,
    priority: Annotated[
        str | None,
        typer.Option("--priority", "-p", help="Filter by priority: high, medium, or low"),
    ] = None,
    tag: Annotated[
        str | None,
        typer.Option("--tag", "-t", help="Filter by tag"),
    ] = None,
    sort: Annotated[
        str | None,
        typer.Option(
            "--sort",
            help="Sort by: id, title, priority, due-date, or created (default: id)",
        ),
    ] = None,
    desc: Annotated[
        bool,
        typer.Option("--desc", help="Sort in descending order"),
    ] = False,
) -> None:
    """
    Display all tasks with optional search, filters, and sorting (T030, T061, T076 - US2, US7, US9).

    Examples:
        todo list
        todo list --search bug
        todo list --status incomplete
        todo list --priority high
        todo list --tag work
        todo list --search login --status incomplete --priority high
        todo list --sort priority
        todo list --sort due-date --desc
        todo list --priority high --sort due-date
    """
    from src.models.priority import Priority
    from src.services.search_service import SearchService
    from src.services.sort_service import SortService

    task_service = get_task_service()
    all_tasks = task_service.all()
    tasks = all_tasks

    # Apply search and filters if provided
    if search or status or priority or tag:
        search_service = SearchService()

        # Parse priority
        priority_enum = None
        if priority:
            priority_lower = priority.lower()
            if priority_lower == "high":
                priority_enum = Priority.HIGH
            elif priority_lower == "medium":
                priority_enum = Priority.MEDIUM
            elif priority_lower == "low":
                priority_enum = Priority.LOW
            else:
                format_error(f"Invalid priority '{priority}'. Must be: high, medium, or low")
                raise typer.Exit(code=1)

        # Validate status
        if status and status not in ["complete", "incomplete"]:
            format_error(f"Invalid status '{status}'. Must be: complete or incomplete")
            raise typer.Exit(code=1)

        # Apply search and filter
        tasks = search_service.search_and_filter(
            all_tasks, keyword=search, status=status, priority=priority_enum, tag=tag
        )

    # Apply sorting if provided
    sort_by = sort or "id"  # Default to id
    try:
        sort_service = SortService()
        tasks = sort_service.sort_tasks(tasks, sort_by=sort_by, descending=desc)
    except ValueError as e:
        format_error(str(e))
        raise typer.Exit(code=1) from e

    # Show filtered count if filtering was applied
    if search or status or priority or tag:
        format_task_list(tasks, total_count=len(all_tasks), sort_by=sort_by, descending=desc)
    else:
        format_task_list(tasks, sort_by=sort_by, descending=desc)


@app.command("show")
def show_task(task_id: Annotated[int, typer.Argument(help="Task ID to display")]) -> None:
    """
    Display detailed information for a single task (T033 - US2).

    Examples:
        todo show 1
        todo show 42
    """
    try:
        task_service = get_task_service()
        task = task_service.get(task_id)
        format_task_detail(task)
    except TaskNotFoundError as e:
        format_error(str(e))
        raise typer.Exit(code=1) from e


@app.command("update")
def update_task(
    task_id: Annotated[int, typer.Argument(help="Task ID to update")],
    title: Annotated[str | None, typer.Option("--title", help="New title (optional)")] = None,
    desc: Annotated[str | None, typer.Option("--desc", help="New description (optional)")] = None,
    priority: Annotated[
        str | None,
        typer.Option("--priority", "-p", help="New priority: high, medium, or low"),
    ] = None,
    add_tags: Annotated[
        str | None,
        typer.Option("--add-tags", help="Comma-separated tags to add"),
    ] = None,
    remove_tags: Annotated[
        str | None,
        typer.Option("--remove-tags", help="Comma-separated tags to remove"),
    ] = None,
    due_date: Annotated[
        str | None,
        typer.Option("--due-date", help="Due date (YYYY-MM-DD format, or 'none' to clear)"),
    ] = None,
    due_time: Annotated[
        str | None,
        typer.Option("--due-time", help="Due time (HH:MM format, or 'none' to clear)"),
    ] = None,
    recur: Annotated[
        str | None,
        typer.Option("--recur", help="Recurrence: daily, weekly, monthly, or 'none' to clear"),
    ] = None,
    recur_day: Annotated[
        int | None,
        typer.Option(
            "--recur-day", help="Day for weekly (1-7) or monthly (1-31) recurrence, or 0 to clear"
        ),
    ] = None,
) -> None:
    """
    Update an existing task's title, description, priority, tags, due date, and/or recurrence (T036, T055, T068, T083 - US3, US6, US8, US10).

    Examples:
        todo update 1 --title "New title"
        todo update 1 --desc "New description"
        todo update 1 --priority high
        todo update 1 --add-tags "urgent,important"
        todo update 1 --remove-tags "later"
        todo update 1 --title "New" -p medium --add-tags "work"
        todo update 1 --due-date 2025-12-20
        todo update 1 --due-date 2025-12-20 --due-time 15:30
        todo update 1 --due-date none --due-time none
        todo update 1 --recur daily
        todo update 1 --recur weekly --recur-day 5
        todo update 1 --recur none
    """
    from datetime import date, time

    from src.cli.formatters import format_task_updated
    from src.models.priority import Priority

    if (
        title is None
        and desc is None
        and priority is None
        and add_tags is None
        and remove_tags is None
        and due_date is None
        and due_time is None
        and recur is None
        and recur_day is None
    ):
        format_error(
            "At least one of --title, --desc, --priority, --add-tags, --remove-tags, --due-date, --due-time, --recur, or --recur-day must be provided"
        )
        raise typer.Exit(code=1)

    try:
        from src.services.task_service import TaskService

        # Use sentinel to distinguish "not provided" from "None"
        UNSET = TaskService._UNSET

        # Parse priority
        priority_enum: Priority | None | object = UNSET
        if priority:
            priority_lower = priority.lower()
            if priority_lower == "high":
                priority_enum = Priority.HIGH
            elif priority_lower == "medium":
                priority_enum = Priority.MEDIUM
            elif priority_lower == "low":
                priority_enum = Priority.LOW
            else:
                format_error(f"Invalid priority '{priority}'. Must be: high, medium, or low")
                raise typer.Exit(code=1)

        # Parse add_tags
        add_tags_list = None
        if add_tags:
            add_tags_list = [tag.strip() for tag in add_tags.split(",") if tag.strip()]

        # Parse remove_tags
        remove_tags_list = None
        if remove_tags:
            remove_tags_list = [tag.strip() for tag in remove_tags.split(",") if tag.strip()]

        # Parse due date (support "none" to clear)
        due_date_obj: date | None | object = UNSET
        if due_date is not None:
            if due_date.lower() == "none":
                due_date_obj = None
            else:
                try:
                    year, month, day = map(int, due_date.split("-"))
                    due_date_obj = date(year, month, day)
                except (ValueError, TypeError):
                    format_error(
                        f"Invalid due date '{due_date}'. Use YYYY-MM-DD format or 'none' to clear"
                    )
                    raise typer.Exit(code=1)

        # Parse due time (support "none" to clear)
        due_time_obj: time | None | object = UNSET
        if due_time is not None:
            if due_time.lower() == "none":
                due_time_obj = None
            else:
                try:
                    hour, minute = map(int, due_time.split(":"))
                    due_time_obj = time(hour, minute)
                except (ValueError, TypeError):
                    format_error(
                        f"Invalid due time '{due_time}'. Use HH:MM format or 'none' to clear"
                    )
                    raise typer.Exit(code=1)

        # Parse recurrence (T083) (support "none" to clear)
        from src.models.recurrence import RecurrencePattern

        recurrence_obj: RecurrencePattern | None | object = UNSET
        recurrence_day_obj: int | None | object = UNSET

        if recur is not None:
            recur_lower = recur.lower()
            if recur_lower == "none":
                recurrence_obj = RecurrencePattern.NONE
                recurrence_day_obj = None
            elif recur_lower == "daily":
                recurrence_obj = RecurrencePattern.DAILY
                # Daily doesn't need recur_day, but keep current value if not explicitly set
            elif recur_lower == "weekly":
                recurrence_obj = RecurrencePattern.WEEKLY
                if recur_day is None:
                    format_error("Weekly recurrence requires --recur-day (1-7 for Mon-Sun)")
                    raise typer.Exit(code=1)
                if not (1 <= recur_day <= 7):
                    format_error(
                        f"Invalid --recur-day '{recur_day}' for weekly. Must be 1-7 (Mon-Sun)"
                    )
                    raise typer.Exit(code=1)
                recurrence_day_obj = recur_day
            elif recur_lower == "monthly":
                recurrence_obj = RecurrencePattern.MONTHLY
                if recur_day is None:
                    format_error("Monthly recurrence requires --recur-day (1-31 for day of month)")
                    raise typer.Exit(code=1)
                if not (1 <= recur_day <= 31):
                    format_error(f"Invalid --recur-day '{recur_day}' for monthly. Must be 1-31")
                    raise typer.Exit(code=1)
                recurrence_day_obj = recur_day
            else:
                format_error(
                    f"Invalid recurrence '{recur}'. Must be: daily, weekly, monthly, or none"
                )
                raise typer.Exit(code=1)
        elif recur_day is not None:
            # If only recur_day is provided (without recur), update the day
            if recur_day == 0:
                recurrence_day_obj = None
            elif 1 <= recur_day <= 31:
                recurrence_day_obj = recur_day
            else:
                format_error(f"Invalid --recur-day '{recur_day}'. Must be 0 to clear, or 1-31")
                raise typer.Exit(code=1)

        task_service = get_task_service()
        task = task_service.update(
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
        format_task_updated(task)
    except (TaskNotFoundError, ValueError, ValidationError) as e:
        format_error(str(e))
        raise typer.Exit(code=1) from e


@app.command("complete")
def complete_task(
    task_id: Annotated[int, typer.Argument(help="Task ID to mark complete/incomplete")],
) -> None:
    """
    Toggle task completion status (T042 - US4).

    Examples:
        todo complete 1
        todo complete 5
    """
    from src.cli.formatters import format_task_completed

    try:
        task_service = get_task_service()
        task = task_service.toggle_complete(task_id)
        format_task_completed(task)
    except TaskNotFoundError as e:
        format_error(str(e))
        raise typer.Exit(code=1) from e


@app.command("delete")
def delete_task(
    task_id: Annotated[int, typer.Argument(help="Task ID to delete")],
    force: Annotated[bool, typer.Option("--force", "-f", help="Skip confirmation prompt")] = False,
) -> None:
    """
    Delete a task from the list (T047 - US5).

    Examples:
        todo delete 1          # Prompts for confirmation
        todo delete 1 --force  # Deletes without confirmation
    """
    from src.cli.formatters import format_task_deleted

    try:
        task_service = get_task_service()

        # Get task first to show what will be deleted
        task = task_service.get(task_id)

        # Confirmation prompt unless --force
        if not force:
            import typer as typer_module

            confirm = typer_module.confirm(
                f"Delete task #{task_id}: '{task.title}'?", default=False
            )
            if not confirm:
                from rich.console import Console

                Console().print("[yellow]Deletion cancelled[/yellow]")
                raise typer.Exit(code=0)

        # Delete the task
        task_service.delete(task_id)
        format_task_deleted(task_id)

    except TaskNotFoundError as e:
        format_error(str(e))
        raise typer.Exit(code=1) from e
