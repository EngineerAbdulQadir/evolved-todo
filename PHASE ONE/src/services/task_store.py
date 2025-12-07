"""In-memory task storage implementation (T016)."""

from abc import ABC, abstractmethod

from src.models.exceptions import TaskNotFoundError
from src.models.task import Task


class TaskStore(ABC):
    """Abstract base for task storage."""

    @abstractmethod
    def add(self, task: Task) -> Task:
        """
        Store a new task.

        Args:
            task: Task to store

        Returns:
            The stored task

        Raises:
            ValueError: If task with same ID already exists
        """
        ...

    @abstractmethod
    def get(self, task_id: int) -> Task:
        """
        Retrieve task by ID.

        Args:
            task_id: ID of task to retrieve

        Returns:
            Task with matching ID

        Raises:
            TaskNotFoundError: If task not found
        """
        ...

    @abstractmethod
    def update(self, task: Task) -> Task:
        """
        Update existing task.

        Args:
            task: Task with updated values

        Returns:
            The updated task

        Raises:
            TaskNotFoundError: If task not found
        """
        ...

    @abstractmethod
    def delete(self, task_id: int) -> None:
        """
        Remove task by ID.

        Args:
            task_id: ID of task to remove

        Raises:
            TaskNotFoundError: If task not found
        """
        ...

    @abstractmethod
    def all(self) -> list[Task]:
        """
        Get all tasks.

        Returns:
            List of all tasks (may be empty)
        """
        ...

    @abstractmethod
    def count(self) -> int:
        """
        Get total task count.

        Returns:
            Number of tasks in store
        """
        ...


class InMemoryTaskStore(TaskStore):
    """In-memory task storage using dictionary (T016)."""

    def __init__(self) -> None:
        """Initialize empty task store."""
        self._tasks: dict[int, Task] = {}

    def add(self, task: Task) -> Task:
        """Store a new task."""
        if task.id in self._tasks:
            raise ValueError(f"Task with ID {task.id} already exists")
        self._tasks[task.id] = task
        return task

    def get(self, task_id: int) -> Task:
        """Retrieve task by ID."""
        if task_id not in self._tasks:
            raise TaskNotFoundError(f"Task with ID {task_id} not found")
        return self._tasks[task_id]

    def update(self, task: Task) -> Task:
        """Update existing task."""
        if task.id not in self._tasks:
            raise TaskNotFoundError(f"Task with ID {task.id} not found")
        self._tasks[task.id] = task
        return task

    def delete(self, task_id: int) -> None:
        """Remove task by ID."""
        if task_id not in self._tasks:
            raise TaskNotFoundError(f"Task with ID {task_id} not found")
        del self._tasks[task_id]

    def all(self) -> list[Task]:
        """Get all tasks sorted by ID."""
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def count(self) -> int:
        """Get total task count."""
        return len(self._tasks)
