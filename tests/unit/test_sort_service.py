"""Unit tests for SortService (T075 - US9)."""

from datetime import date, datetime, time

import pytest

from src.models.priority import Priority
from src.models.task import Task
from src.services.sort_service import SortService


@pytest.fixture
def sort_service() -> SortService:
    """Create a SortService instance for testing."""
    return SortService()


@pytest.fixture
def sample_tasks() -> list[Task]:
    """Create sample tasks for testing."""
    return [
        Task(
            id=3,
            title="Zebra task",
            priority=Priority.LOW,
            due_date=date(2025, 12, 20),
            created_at=datetime(2025, 12, 1, 10, 0),
        ),
        Task(
            id=1,
            title="Alpha task",
            priority=Priority.HIGH,
            due_date=date(2025, 12, 10),
            created_at=datetime(2025, 12, 1, 9, 0),
        ),
        Task(
            id=2,
            title="Beta task",
            priority=Priority.MEDIUM,
            due_date=date(2025, 12, 15),
            created_at=datetime(2025, 12, 1, 11, 0),
        ),
        Task(
            id=4,
            title="Gamma task",
            priority=None,
            due_date=None,
            created_at=datetime(2025, 12, 1, 8, 0),
        ),
    ]


class TestSortById:
    """Tests for sorting by ID."""

    def test_sort_by_id_ascending(
        self, sort_service: SortService, sample_tasks: list[Task]
    ) -> None:
        """Sort by ID ascending (AC1)."""
        result = sort_service.sort_tasks(sample_tasks, sort_by="id", descending=False)

        assert [t.id for t in result] == [1, 2, 3, 4]

    def test_sort_by_id_descending(
        self, sort_service: SortService, sample_tasks: list[Task]
    ) -> None:
        """Sort by ID descending (AC2)."""
        result = sort_service.sort_tasks(sample_tasks, sort_by="id", descending=True)

        assert [t.id for t in result] == [4, 3, 2, 1]


class TestSortByTitle:
    """Tests for sorting by title."""

    def test_sort_by_title_ascending(
        self, sort_service: SortService, sample_tasks: list[Task]
    ) -> None:
        """Sort by title ascending (AC1)."""
        result = sort_service.sort_tasks(sample_tasks, sort_by="title", descending=False)

        assert [t.title for t in result] == [
            "Alpha task",
            "Beta task",
            "Gamma task",
            "Zebra task",
        ]

    def test_sort_by_title_descending(
        self, sort_service: SortService, sample_tasks: list[Task]
    ) -> None:
        """Sort by title descending (AC2)."""
        result = sort_service.sort_tasks(sample_tasks, sort_by="title", descending=True)

        assert [t.title for t in result] == [
            "Zebra task",
            "Gamma task",
            "Beta task",
            "Alpha task",
        ]

    def test_sort_by_title_case_insensitive(
        self, sort_service: SortService
    ) -> None:
        """Sort by title is case-insensitive (AC3)."""
        tasks = [
            Task(id=1, title="ZEBRA"),
            Task(id=2, title="alpha"),
            Task(id=3, title="Beta"),
        ]

        result = sort_service.sort_tasks(tasks, sort_by="title", descending=False)

        assert [t.title for t in result] == ["alpha", "Beta", "ZEBRA"]


class TestSortByPriority:
    """Tests for sorting by priority."""

    def test_sort_by_priority_ascending(
        self, sort_service: SortService, sample_tasks: list[Task]
    ) -> None:
        """Sort by priority ascending (low to high) (AC1)."""
        result = sort_service.sort_tasks(
            sample_tasks, sort_by="priority", descending=False
        )

        # Ascending: no priority (-1) < low (1) < medium (2) < high (3)
        priorities = [t.priority for t in result]
        assert priorities == [None, Priority.LOW, Priority.MEDIUM, Priority.HIGH]

    def test_sort_by_priority_descending(
        self, sort_service: SortService, sample_tasks: list[Task]
    ) -> None:
        """Sort by priority descending (high to low) (AC2)."""
        result = sort_service.sort_tasks(
            sample_tasks, sort_by="priority", descending=True
        )

        # Descending: high (3) > medium (2) > low (1) > no priority (-1)
        priorities = [t.priority for t in result]
        assert priorities == [Priority.HIGH, Priority.MEDIUM, Priority.LOW, None]

    def test_sort_by_priority_none_last_ascending(
        self, sort_service: SortService
    ) -> None:
        """Tasks with no priority come last in ascending sort (AC3)."""
        tasks = [
            Task(id=1, title="High", priority=Priority.HIGH),
            Task(id=2, title="None", priority=None),
            Task(id=3, title="Low", priority=Priority.LOW),
        ]

        result = sort_service.sort_tasks(tasks, sort_by="priority", descending=False)

        assert [t.title for t in result] == ["None", "Low", "High"]


class TestSortByDueDate:
    """Tests for sorting by due date."""

    def test_sort_by_due_date_ascending(
        self, sort_service: SortService, sample_tasks: list[Task]
    ) -> None:
        """Sort by due date ascending (earliest first) (AC1)."""
        result = sort_service.sort_tasks(
            sample_tasks, sort_by="due-date", descending=False
        )

        due_dates = [t.due_date for t in result]
        assert due_dates == [
            date(2025, 12, 10),
            date(2025, 12, 15),
            date(2025, 12, 20),
            None,
        ]

    def test_sort_by_due_date_descending(
        self, sort_service: SortService, sample_tasks: list[Task]
    ) -> None:
        """Sort by due date descending (latest first) (AC2)."""
        result = sort_service.sort_tasks(
            sample_tasks, sort_by="due-date", descending=True
        )

        due_dates = [t.due_date for t in result]
        assert due_dates == [
            None,
            date(2025, 12, 20),
            date(2025, 12, 15),
            date(2025, 12, 10),
        ]

    def test_sort_by_due_date_with_time(self, sort_service: SortService) -> None:
        """Sort by due date considers time (AC3)."""
        tasks = [
            Task(
                id=1, title="T1", due_date=date(2025, 12, 15), due_time=time(14, 0)
            ),
            Task(
                id=2, title="T2", due_date=date(2025, 12, 15), due_time=time(9, 0)
            ),
            Task(id=3, title="T3", due_date=date(2025, 12, 15), due_time=None),
        ]

        result = sort_service.sort_tasks(tasks, sort_by="due-date", descending=False)

        # T3 (midnight) < T2 (9:00) < T1 (14:00)
        assert [t.title for t in result] == ["T3", "T2", "T1"]

    def test_sort_by_due_date_none_last_ascending(
        self, sort_service: SortService
    ) -> None:
        """Tasks with no due date come last in ascending sort (AC4)."""
        tasks = [
            Task(id=1, title="Soon", due_date=date(2025, 12, 10)),
            Task(id=2, title="None", due_date=None),
            Task(id=3, title="Later", due_date=date(2025, 12, 20)),
        ]

        result = sort_service.sort_tasks(tasks, sort_by="due-date", descending=False)

        assert [t.title for t in result] == ["Soon", "Later", "None"]


class TestSortByCreated:
    """Tests for sorting by creation date."""

    def test_sort_by_created_ascending(
        self, sort_service: SortService, sample_tasks: list[Task]
    ) -> None:
        """Sort by created date ascending (oldest first) (AC1)."""
        result = sort_service.sort_tasks(
            sample_tasks, sort_by="created", descending=False
        )

        created_times = [t.created_at for t in result]
        assert created_times == [
            datetime(2025, 12, 1, 8, 0),  # Gamma
            datetime(2025, 12, 1, 9, 0),  # Alpha
            datetime(2025, 12, 1, 10, 0),  # Zebra
            datetime(2025, 12, 1, 11, 0),  # Beta
        ]

    def test_sort_by_created_descending(
        self, sort_service: SortService, sample_tasks: list[Task]
    ) -> None:
        """Sort by created date descending (newest first) (AC2)."""
        result = sort_service.sort_tasks(
            sample_tasks, sort_by="created", descending=True
        )

        created_times = [t.created_at for t in result]
        assert created_times == [
            datetime(2025, 12, 1, 11, 0),  # Beta
            datetime(2025, 12, 1, 10, 0),  # Zebra
            datetime(2025, 12, 1, 9, 0),  # Alpha
            datetime(2025, 12, 1, 8, 0),  # Gamma
        ]


class TestSortValidation:
    """Tests for sort validation."""

    def test_invalid_sort_by_raises_error(
        self, sort_service: SortService, sample_tasks: list[Task]
    ) -> None:
        """Invalid sort_by raises ValueError (AC1)."""
        with pytest.raises(ValueError) as exc_info:
            sort_service.sort_tasks(sample_tasks, sort_by="invalid")

        assert "Invalid sort_by" in str(exc_info.value)
        assert "invalid" in str(exc_info.value)
