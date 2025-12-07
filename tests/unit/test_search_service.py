"""Unit tests for SearchService (T060 - US7)."""

import pytest

from src.models.priority import Priority
from src.models.task import Task
from src.services.search_service import SearchService


@pytest.fixture
def search_service() -> SearchService:
    """Create a SearchService instance for testing."""
    return SearchService()


@pytest.fixture
def sample_tasks() -> list[Task]:
    """Create sample tasks for testing."""
    return [
        Task(
            id=1,
            title="Buy groceries",
            description="Milk, eggs, bread",
            is_complete=False,
            priority=Priority.MEDIUM,
            tags=["shopping", "urgent"],
        ),
        Task(
            id=2,
            title="Fix bug in login",
            description="Users can't log in",
            is_complete=False,
            priority=Priority.HIGH,
            tags=["work", "bug"],
        ),
        Task(
            id=3,
            title="Write report",
            description="Q4 sales report",
            is_complete=True,
            priority=Priority.LOW,
            tags=["work", "documentation"],
        ),
        Task(
            id=4,
            title="Call mom",
            description=None,
            is_complete=False,
            priority=None,
            tags=["personal"],
        ),
        Task(
            id=5,
            title="Review PR",
            description="Code review for feature branch",
            is_complete=True,
            priority=Priority.MEDIUM,
            tags=["work", "code-review"],
        ),
    ]


class TestSearchByKeyword:
    """Tests for keyword search functionality."""

    def test_search_title_match(
        self, search_service: SearchService, sample_tasks: list[Task]
    ) -> None:
        """Search finds tasks by title keyword (AC1)."""
        results = search_service.search_by_keyword(sample_tasks, "bug")

        assert len(results) == 1
        assert results[0].id == 2
        assert "bug" in results[0].title.lower()

    def test_search_description_match(
        self, search_service: SearchService, sample_tasks: list[Task]
    ) -> None:
        """Search finds tasks by description keyword (AC2)."""
        results = search_service.search_by_keyword(sample_tasks, "sales")

        assert len(results) == 1
        assert results[0].id == 3
        assert "sales" in results[0].description.lower()  # type: ignore

    def test_search_multiple_matches(
        self, search_service: SearchService, sample_tasks: list[Task]
    ) -> None:
        """Search finds multiple tasks matching keyword (AC3)."""
        # Search for "r" which appears in "groceries", "report", "PR", "review"
        results = search_service.search_by_keyword(sample_tasks, "r")

        # Should match multiple tasks containing "r" in title or description
        assert len(results) >= 3

    def test_search_case_insensitive(
        self, search_service: SearchService, sample_tasks: list[Task]
    ) -> None:
        """Search is case-insensitive (AC4)."""
        results_lower = search_service.search_by_keyword(sample_tasks, "buy")
        results_upper = search_service.search_by_keyword(sample_tasks, "BUY")
        results_mixed = search_service.search_by_keyword(sample_tasks, "Buy")

        assert len(results_lower) == len(results_upper) == len(results_mixed) == 1
        assert results_lower[0].id == 1

    def test_search_empty_keyword_returns_all(
        self, search_service: SearchService, sample_tasks: list[Task]
    ) -> None:
        """Search with empty keyword returns all tasks (AC5)."""
        results = search_service.search_by_keyword(sample_tasks, "")

        assert len(results) == len(sample_tasks)

    def test_search_no_match_returns_empty(
        self, search_service: SearchService, sample_tasks: list[Task]
    ) -> None:
        """Search with no matches returns empty list (AC6)."""
        results = search_service.search_by_keyword(sample_tasks, "xyz123notfound")

        assert len(results) == 0


class TestFilterTasks:
    """Tests for task filtering functionality."""

    def test_filter_by_status_complete(
        self, search_service: SearchService, sample_tasks: list[Task]
    ) -> None:
        """Filter by complete status (AC1)."""
        results = search_service.filter_tasks(sample_tasks, status="complete")

        assert len(results) == 2  # Tasks 3 and 5
        assert all(task.is_complete for task in results)

    def test_filter_by_status_incomplete(
        self, search_service: SearchService, sample_tasks: list[Task]
    ) -> None:
        """Filter by incomplete status (AC2)."""
        results = search_service.filter_tasks(sample_tasks, status="incomplete")

        assert len(results) == 3  # Tasks 1, 2, 4
        assert all(not task.is_complete for task in results)

    def test_filter_by_priority_high(
        self, search_service: SearchService, sample_tasks: list[Task]
    ) -> None:
        """Filter by high priority (AC3)."""
        results = search_service.filter_tasks(sample_tasks, priority=Priority.HIGH)

        assert len(results) == 1  # Task 2
        assert results[0].priority == Priority.HIGH

    def test_filter_by_priority_medium(
        self, search_service: SearchService, sample_tasks: list[Task]
    ) -> None:
        """Filter by medium priority (AC4)."""
        results = search_service.filter_tasks(sample_tasks, priority=Priority.MEDIUM)

        assert len(results) == 2  # Tasks 1 and 5
        assert all(task.priority == Priority.MEDIUM for task in results)

    def test_filter_by_tag(
        self, search_service: SearchService, sample_tasks: list[Task]
    ) -> None:
        """Filter by tag (AC5)."""
        results = search_service.filter_tasks(sample_tasks, tag="work")

        assert len(results) == 3  # Tasks 2, 3, 5
        assert all("work" in task.tags for task in results)

    def test_filter_combined_status_and_priority(
        self, search_service: SearchService, sample_tasks: list[Task]
    ) -> None:
        """Filter by multiple criteria uses AND logic (AC6)."""
        results = search_service.filter_tasks(
            sample_tasks, status="incomplete", priority=Priority.MEDIUM
        )

        assert len(results) == 1  # Only task 1
        assert results[0].id == 1
        assert not results[0].is_complete
        assert results[0].priority == Priority.MEDIUM

    def test_filter_combined_all_criteria(
        self, search_service: SearchService, sample_tasks: list[Task]
    ) -> None:
        """Filter by all criteria (status, priority, tag) (AC7)."""
        results = search_service.filter_tasks(
            sample_tasks, status="complete", priority=Priority.MEDIUM, tag="work"
        )

        assert len(results) == 1  # Only task 5
        assert results[0].id == 5
        assert results[0].is_complete
        assert results[0].priority == Priority.MEDIUM
        assert "work" in results[0].tags

    def test_filter_no_match_returns_empty(
        self, search_service: SearchService, sample_tasks: list[Task]
    ) -> None:
        """Filter with no matches returns empty list (AC8)."""
        results = search_service.filter_tasks(
            sample_tasks, status="complete", priority=Priority.HIGH
        )

        assert len(results) == 0  # No complete tasks with high priority


class TestSearchAndFilter:
    """Tests for combined search and filter operations."""

    def test_search_and_filter_combined(
        self, search_service: SearchService, sample_tasks: list[Task]
    ) -> None:
        """Combined search and filter (AC1)."""
        results = search_service.search_and_filter(
            sample_tasks, keyword="report", status="complete"
        )

        assert len(results) == 1
        assert results[0].id == 3
        assert "report" in results[0].title.lower()
        assert results[0].is_complete

    def test_search_and_filter_no_match(
        self, search_service: SearchService, sample_tasks: list[Task]
    ) -> None:
        """Combined search and filter with no match (AC2)."""
        results = search_service.search_and_filter(
            sample_tasks, keyword="xyz", status="complete"
        )

        assert len(results) == 0

    def test_search_and_filter_all_parameters(
        self, search_service: SearchService, sample_tasks: list[Task]
    ) -> None:
        """Combined search with all filter parameters (AC3)."""
        results = search_service.search_and_filter(
            sample_tasks,
            keyword="review",
            status="complete",
            priority=Priority.MEDIUM,
            tag="work",
        )

        assert len(results) == 1
        assert results[0].id == 5
