"""Unit tests for TaskService (T019, T027, T034, T040, T045)."""

import pytest

from src.models.exceptions import TaskNotFoundError
from src.services.task_service import TaskService


class TestTaskServiceAdd:
    """Tests for TaskService.add() - US1 (T019)."""

    def test_add_task_with_title_only(self, task_service: TaskService) -> None:
        """User can create task with just a title (AC1)."""
        task = task_service.add(title="Buy milk")

        assert task.id == 1
        assert task.title == "Buy milk"
        assert task.description is None
        assert task.is_complete is False

    def test_add_task_with_title_and_description(
        self, task_service: TaskService
    ) -> None:
        """User can create task with title and description (AC2)."""
        task = task_service.add(
            title="Prepare presentation",
            description="Include Q3 revenue charts and roadmap",
        )

        assert task.id == 1
        assert task.title == "Prepare presentation"
        assert task.description == "Include Q3 revenue charts and roadmap"
        assert task.is_complete is False

    def test_add_multiple_tasks_generates_unique_ids(
        self, task_service: TaskService
    ) -> None:
        """System assigns unique IDs to each task (AC3)."""
        task1 = task_service.add(title="First task")
        task2 = task_service.add(title="Second task")
        task3 = task_service.add(title="Third task")

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3
        assert task1.id != task2.id != task3.id

    def test_add_task_sets_created_at_timestamp(
        self, task_service: TaskService
    ) -> None:
        """System sets creation timestamp automatically (AC4)."""
        task = task_service.add(title="Test task")

        assert task.created_at is not None
        assert str(task.created_at).startswith("2025")  # Rough validation

    def test_add_task_appears_in_all_list(self, task_service: TaskService) -> None:
        """Task is immediately available after creation (AC5)."""
        task = task_service.add(title="Buy groceries")
        all_tasks = task_service.all()

        assert len(all_tasks) == 1
        assert all_tasks[0].id == task.id
        assert all_tasks[0].title == "Buy groceries"

    def test_add_task_with_unicode_characters(
        self, task_service: TaskService
    ) -> None:
        """System preserves unicode characters in title and description (AC6)."""
        task = task_service.add(title="Email 📧 mom", description="About 🎂 party")

        assert task.title == "Email 📧 mom"
        assert task.description == "About 🎂 party"

    def test_add_task_with_special_characters(
        self, task_service: TaskService
    ) -> None:
        """System handles special characters correctly (AC7)."""
        task = task_service.add(
            title='Task with "quotes" and \\backslash',
            description="Line 1\\nLine 2\\tTabbed",
        )

        assert '"quotes"' in task.title
        assert "\\backslash" in task.title


class TestTaskServiceGet:
    """Tests for TaskService.get() - US2 (T027)."""

    def test_get_existing_task_by_id(self, task_service: TaskService) -> None:
        """Can retrieve task by ID (AC1)."""
        created_task = task_service.add(title="Test task")
        retrieved_task = task_service.get(created_task.id)

        assert retrieved_task.id == created_task.id
        assert retrieved_task.title == created_task.title

    def test_get_nonexistent_task_raises_error(
        self, task_service: TaskService
    ) -> None:
        """Attempting to get non-existent task raises TaskNotFoundError (AC2)."""
        with pytest.raises(TaskNotFoundError, match="Task with ID 999 not found"):
            task_service.get(999)


class TestTaskServiceAll:
    """Tests for TaskService.all() - US2 (T027)."""

    def test_all_returns_empty_list_when_no_tasks(
        self, task_service: TaskService
    ) -> None:
        """Returns empty list when no tasks exist (AC1)."""
        tasks = task_service.all()

        assert tasks == []
        assert len(tasks) == 0

    def test_all_returns_all_tasks_sorted_by_id(
        self, task_service: TaskService
    ) -> None:
        """Returns all tasks sorted by ID (AC2)."""
        task1 = task_service.add(title="First")
        task2 = task_service.add(title="Second")
        task3 = task_service.add(title="Third")

        tasks = task_service.all()

        assert len(tasks) == 3
        assert tasks[0].id == task1.id
        assert tasks[1].id == task2.id
        assert tasks[2].id == task3.id
        assert [t.id for t in tasks] == [1, 2, 3]
