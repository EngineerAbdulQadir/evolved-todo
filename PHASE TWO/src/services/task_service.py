"""Task service with business logic and CRUD operations (T017)."""

from __future__ import annotations

from datetime import date, time

from src.lib.id_generator import IdGenerator
from src.models.priority import Priority
from src.models.recurrence import RecurrencePattern
from src.models.task import Task
from src.services.task_store import TaskStore


class TaskService:
    """
    Task service with business logic for managing tasks.

    Provides high-level operations for creating, reading, updating,
    and deleting tasks with automatic ID generation.
    """

    def __init__(self, store: TaskStore, id_gen: IdGenerator) -> None:
        """
        Initialize task service.

        Args:
            store: Task storage backend
            id_gen: ID generator for new tasks
        """
        self._store = store
        self._id_gen = id_gen

    def add(
        self,
        title: str,
        description: str | None = None,
        priority: Priority | None = None,
        tags: list[str] | None = None,
        due_date: date | None = None,
        due_time: time | None = None,
        recurrence: RecurrencePattern | None = None,
        recurrence_day: int | None = None,
    ) -> Task:
        """
        Create and store a new task (T017, T053, T066, T083).

        Args:
            title: Task title (required, 1-200 chars)
            description: Task description (optional, max 1000 chars)
            priority: Task priority (optional, high/medium/low)
            tags: List of tags (optional, max 10 tags, each max 50 chars)
            due_date: Due date (optional)
            due_time: Due time (optional)
            recurrence: Recurrence pattern (optional, daily/weekly/monthly)
            recurrence_day: Day for weekly (1-7) or monthly (1-31) recurrence (optional)

        Returns:
            Created task with auto-generated ID

        Raises:
            ValueError: If validation fails
        """
        task_id = self._id_gen.next()
        task = Task(
            id=task_id,
            title=title,
            description=description,
            priority=priority,
            tags=tags if tags is not None else [],
            due_date=due_date,
            due_time=due_time,
            recurrence=recurrence or RecurrencePattern.NONE,
            recurrence_day=recurrence_day,
        )
        return self._store.add(task)

    def get(self, task_id: int) -> Task:
        """
        Retrieve task by ID (T017).

        Args:
            task_id: ID of task to retrieve

        Returns:
            Task with matching ID

        Raises:
            TaskNotFoundError: If task not found
        """
        return self._store.get(task_id)

    def all(self) -> list[Task]:
        """
        Get all tasks sorted by ID (T017).

        Returns:
            List of all tasks (may be empty)
        """
        return self._store.all()

    # Sentinel value to distinguish "not provided" from "None (clear value)"
    _UNSET = object()

    def update(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        priority: Priority | None | object = _UNSET,
        add_tags: list[str] | None = None,
        remove_tags: list[str] | None = None,
        due_date: date | None | object = _UNSET,
        due_time: time | None | object = _UNSET,
        recurrence: RecurrencePattern | None | object = _UNSET,
        recurrence_day: int | None | object = _UNSET,
    ) -> Task:
        """
        Update an existing task (T035, T055, T066, T083 - US3, US6, US8, US10).

        Args:
            task_id: ID of task to update
            title: New title (optional)
            description: New description (optional)
            priority: New priority (optional, pass None to clear)
            add_tags: Tags to add (optional)
            remove_tags: Tags to remove (optional)
            due_date: New due date (optional, pass None to clear)
            due_time: New due time (optional, pass None to clear)
            recurrence: New recurrence pattern (optional, pass RecurrencePattern.NONE to clear)
            recurrence_day: New recurrence day (optional, pass None to clear)

        Returns:
            Updated task

        Raises:
            TaskNotFoundError: If task not found
            ValueError: If validation fails
        """
        UNSET = TaskService._UNSET

        # Get existing task
        task = self._store.get(task_id)

        # Update fields if provided
        if title is not None:
            task.title = title
            task._validate_title()  # Re-validate

        if description is not None:
            task.description = description
            task._validate_description()  # Re-validate

        if priority is not UNSET and priority is not None:
            task.priority = priority  # type: ignore[assignment]
            # Validation happens in __post_init__ but not called again
            # Priority enum validation is implicit (type safety)

        # Handle tag additions
        if add_tags:
            for tag in add_tags:
                if tag not in task.tags:
                    task.tags.append(tag)
            task._validate_tags()  # Re-validate

        # Handle tag removals
        if remove_tags:
            for tag in remove_tags:
                if tag in task.tags:
                    task.tags.remove(tag)

        # Update due date if provided
        if due_date is not UNSET:
            task.due_date = due_date  # type: ignore[assignment]

        # Update due time if provided
        if due_time is not UNSET:
            task.due_time = due_time  # type: ignore[assignment]

        # Update recurrence pattern if provided (T083)
        if recurrence is not UNSET:
            task.recurrence = recurrence  # type: ignore[assignment]

        # Update recurrence day if provided (T083)
        if recurrence_day is not UNSET:
            task.recurrence_day = recurrence_day  # type: ignore[assignment]

        # Store updated task
        return self._store.update(task)

    def toggle_complete(self, task_id: int) -> Task:
        """
        Toggle task completion status (T041 - US4, T082 - US10).

        For recurring tasks: When marked complete, creates a new task with the next
        occurrence date and marks the original as complete.

        Args:
            task_id: ID of task to toggle

        Returns:
            Updated task (or new task if recurring)

        Raises:
            TaskNotFoundError: If task not found
        """
        from src.models.recurrence import RecurrencePattern
        from src.services.recurrence_service import RecurrenceService

        task = self._store.get(task_id)

        # If toggling from incomplete to complete and task has recurrence
        if (
            not task.is_complete
            and task.recurrence != RecurrencePattern.NONE
            and task.due_date is not None
        ):
            # Mark current task as complete
            task.is_complete = True
            self._store.update(task)

            # Calculate next occurrence
            recurrence_service = RecurrenceService()
            # Type narrowing: we know recurrence is not None due to != NONE check
            assert task.recurrence is not None
            next_due_date = recurrence_service.calculate_next_occurrence(
                task.due_date, task.recurrence, task.recurrence_day
            )

            # Create new task with next occurrence
            new_task = Task(
                id=self._id_gen.next(),
                title=task.title,
                description=task.description,
                priority=task.priority,
                tags=task.tags.copy(),
                due_date=next_due_date,
                due_time=task.due_time,
                recurrence=task.recurrence,
                recurrence_day=task.recurrence_day,
            )
            return self._store.add(new_task)
        else:
            # Normal toggle (no recurrence or toggling back to incomplete)
            task.is_complete = not task.is_complete
            return self._store.update(task)

    def delete(self, task_id: int) -> None:
        """
        Delete a task (T046 - US5).

        Args:
            task_id: ID of task to delete

        Raises:
            TaskNotFoundError: If task not found
        """
        self._store.delete(task_id)
