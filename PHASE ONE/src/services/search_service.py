"""Search and filter service for tasks (T058-T062 - US7)."""

from src.models.priority import Priority
from src.models.task import Task


class SearchService:
    """
    Service for searching and filtering tasks.

    Provides keyword search and multi-criteria filtering (status, priority, tags).
    """

    def search_by_keyword(self, tasks: list[Task], keyword: str) -> list[Task]:
        """
        Search tasks by keyword in title and description (T058).

        Args:
            tasks: List of tasks to search
            keyword: Search term (case-insensitive)

        Returns:
            List of tasks matching the keyword
        """
        if not keyword:
            return tasks

        keyword_lower = keyword.lower()
        return [
            task
            for task in tasks
            if keyword_lower in task.title.lower()
            or (task.description and keyword_lower in task.description.lower())
        ]

    def filter_tasks(
        self,
        tasks: list[Task],
        status: str | None = None,
        priority: Priority | None = None,
        tag: str | None = None,
    ) -> list[Task]:
        """
        Filter tasks by status, priority, and/or tag (T059, T062).

        Uses AND logic: tasks must match ALL provided criteria.

        Args:
            tasks: List of tasks to filter
            status: Filter by status ("complete", "incomplete", or None for all)
            priority: Filter by priority (Priority enum or None for all)
            tag: Filter by tag (must contain this tag, or None for all)

        Returns:
            List of tasks matching all provided filters
        """
        filtered = tasks

        # Filter by status
        if status == "complete":
            filtered = [t for t in filtered if t.is_complete]
        elif status == "incomplete":
            filtered = [t for t in filtered if not t.is_complete]

        # Filter by priority
        if priority is not None:
            filtered = [t for t in filtered if t.priority == priority]

        # Filter by tag
        if tag is not None:
            filtered = [t for t in filtered if tag in t.tags]

        return filtered

    def search_and_filter(
        self,
        tasks: list[Task],
        keyword: str | None = None,
        status: str | None = None,
        priority: Priority | None = None,
        tag: str | None = None,
    ) -> list[Task]:
        """
        Combined search and filter operation (T062).

        First applies keyword search, then applies all filters with AND logic.

        Args:
            tasks: List of tasks to search and filter
            keyword: Search term (case-insensitive, optional)
            status: Filter by status ("complete", "incomplete", optional)
            priority: Filter by priority (Priority enum, optional)
            tag: Filter by tag (must contain this tag, optional)

        Returns:
            List of tasks matching search and all filters
        """
        # First search by keyword
        if keyword:
            tasks = self.search_by_keyword(tasks, keyword)

        # Then apply filters
        tasks = self.filter_tasks(tasks, status=status, priority=priority, tag=tag)

        return tasks
