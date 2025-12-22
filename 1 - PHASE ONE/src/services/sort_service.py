"""Sort service for tasks (T073-T074 - US9)."""

from src.models.task import Task


class SortService:
    """
    Service for sorting tasks by various criteria.

    Supports sorting by: id, title, priority, due_date, created_at.
    """

    def sort_tasks(
        self, tasks: list[Task], sort_by: str = "id", descending: bool = False
    ) -> list[Task]:
        """
        Sort tasks by specified criteria (T073-T074).

        Args:
            tasks: List of tasks to sort
            sort_by: Sort field ("id", "title", "priority", "due-date", "created")
            descending: Sort in descending order (default: ascending)

        Returns:
            Sorted list of tasks

        Raises:
            ValueError: If sort_by is invalid
        """
        if sort_by == "id":
            return self._sort_by_id(tasks, descending)
        elif sort_by == "title":
            return self._sort_by_title(tasks, descending)
        elif sort_by == "priority":
            return self._sort_by_priority(tasks, descending)
        elif sort_by == "due-date":
            return self._sort_by_due_date(tasks, descending)
        elif sort_by == "created":
            return self._sort_by_created(tasks, descending)
        else:
            raise ValueError(
                f"Invalid sort_by '{sort_by}'. Must be: id, title, priority, due-date, or created"
            )

    def _sort_by_id(self, tasks: list[Task], descending: bool) -> list[Task]:
        """Sort by task ID."""
        return sorted(tasks, key=lambda t: t.id, reverse=descending)

    def _sort_by_title(self, tasks: list[Task], descending: bool) -> list[Task]:
        """Sort by title (case-insensitive)."""
        return sorted(tasks, key=lambda t: t.title.lower(), reverse=descending)

    def _sort_by_priority(self, tasks: list[Task], descending: bool) -> list[Task]:
        """
        Sort by priority (high > medium > low > no priority).

        Tasks with no priority are placed last (or first if descending).
        """
        from src.models.priority import Priority

        def priority_key(task: Task) -> int:
            """Convert priority to sortable integer."""
            if task.priority is None:
                return -1  # No priority goes last in ascending
            elif task.priority == Priority.HIGH:
                return 3
            elif task.priority == Priority.MEDIUM:
                return 2
            else:  # task.priority == Priority.LOW
                return 1

        return sorted(tasks, key=priority_key, reverse=descending)

    def _sort_by_due_date(self, tasks: list[Task], descending: bool) -> list[Task]:
        """
        Sort by due date (earliest first in ascending).

        Tasks with no due date are placed last (or first if descending).
        """
        from datetime import datetime

        def due_date_key(task: Task) -> datetime:
            """Convert due date/time to sortable datetime."""
            if task.due_date is None:
                # Use max datetime for tasks without due date
                # In ascending: max goes last, in descending: max goes first
                return datetime.max

            # Combine date and time if available
            if task.due_time:
                return datetime.combine(task.due_date, task.due_time)
            else:
                # Use midnight for tasks with only date
                return datetime.combine(task.due_date, datetime.min.time())

        return sorted(tasks, key=due_date_key, reverse=descending)

    def _sort_by_created(self, tasks: list[Task], descending: bool) -> list[Task]:
        """Sort by creation date (newest first in descending)."""
        return sorted(tasks, key=lambda t: t.created_at, reverse=descending)
