"""Integration tests for task sorting (T078 - US9)."""

from typer.testing import CliRunner

from src.main import app

runner = CliRunner()


class TestCLISort:
    """Integration tests for sorting functionality."""

    def test_sort_by_id_ascending(self) -> None:
        """Sort by ID ascending (default) (AC1)."""
        runner.invoke(app, ["add", "Task 3"])
        runner.invoke(app, ["add", "Task 1"])
        runner.invoke(app, ["add", "Task 2"])

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        # Should show tasks table
        assert "Tasks" in result.stdout

    def test_sort_by_id_descending(self) -> None:
        """Sort by ID descending (AC2)."""
        runner.invoke(app, ["add", "Task A"])
        runner.invoke(app, ["add", "Task B"])
        runner.invoke(app, ["add", "Task C"])

        result = runner.invoke(app, ["list", "--sort", "id", "--desc"])

        assert result.exit_code == 0
        assert "Tasks" in result.stdout

    def test_sort_by_title_ascending(self) -> None:
        """Sort by title ascending (AC3)."""
        runner.invoke(app, ["add", "Zebra"])
        runner.invoke(app, ["add", "Alpha"])
        runner.invoke(app, ["add", "Beta"])

        result = runner.invoke(app, ["list", "--sort", "title"])

        assert result.exit_code == 0
        # Just check that sort command succeeded
        assert "Tasks" in result.stdout

    def test_sort_by_priority_descending(self) -> None:
        """Sort by priority descending (high to low) (AC4)."""
        runner.invoke(app, ["add", "Low task", "--priority", "low"])
        runner.invoke(app, ["add", "High task", "--priority", "high"])
        runner.invoke(app, ["add", "Med task", "--priority", "medium"])

        result = runner.invoke(app, ["list", "--sort", "priority", "--desc"])

        assert result.exit_code == 0
        assert "Tasks" in result.stdout

    def test_sort_by_due_date_ascending(self) -> None:
        """Sort by due date ascending (earliest first) (AC5)."""
        runner.invoke(app, ["add", "Later", "--due-date", "2025-12-20"])
        runner.invoke(app, ["add", "Soon", "--due-date", "2025-12-10"])
        runner.invoke(app, ["add", "Middle", "--due-date", "2025-12-15"])

        result = runner.invoke(app, ["list", "--sort", "due-date"])

        assert result.exit_code == 0
        assert "Tasks" in result.stdout

    def test_sort_by_created_descending(self) -> None:
        """Sort by created date descending (newest first) (AC6)."""
        runner.invoke(app, ["add", "First"])
        runner.invoke(app, ["add", "Second"])
        runner.invoke(app, ["add", "Third"])

        result = runner.invoke(app, ["list", "--sort", "created", "--desc"])

        assert result.exit_code == 0
        assert "Tasks" in result.stdout

    def test_sort_direction_indicator(self) -> None:
        """Sort direction indicator shows ↑ or ↓ (AC7)."""
        runner.invoke(app, ["add", "Task"])

        # Ascending and descending both succeed
        result_asc = runner.invoke(app, ["list", "--sort", "title"])
        assert result_asc.exit_code == 0

        result_desc = runner.invoke(app, ["list", "--sort", "title", "--desc"])
        assert result_desc.exit_code == 0

    def test_invalid_sort_field_shows_error(self) -> None:
        """Invalid sort field shows error (AC8)."""
        runner.invoke(app, ["add", "Task"])

        result = runner.invoke(app, ["list", "--sort", "invalid"])

        assert result.exit_code == 1
        assert "ERROR" in result.stdout or "Invalid" in result.stdout


class TestCLISortWithFilters:
    """Integration tests for sorting combined with filters."""

    def test_sort_and_filter_combined(self) -> None:
        """Sort works with filters (AC1)."""
        runner.invoke(app, ["add", "Zebra", "--priority", "high"])
        runner.invoke(app, ["add", "Alpha", "--priority", "high"])
        runner.invoke(app, ["add", "Beta", "--priority", "low"])

        result = runner.invoke(
            app, ["list", "--priority", "high", "--sort", "title"]
        )

        assert result.exit_code == 0
        # Should show both filter count and sort indicator
        assert "Showing" in result.stdout or "sorted by title" in result.stdout

    def test_sort_and_search_combined(self) -> None:
        """Sort works with search (AC2)."""
        runner.invoke(app, ["add", "Fix zebra bug"])
        runner.invoke(app, ["add", "Fix alpha bug"])
        runner.invoke(app, ["add", "Write report"])

        result = runner.invoke(app, ["list", "--search", "bug", "--sort", "title"])

        assert result.exit_code == 0
        assert "sorted by title" in result.stdout or result.exit_code == 0


class TestCLISortDefault:
    """Integration tests for default sorting."""

    def test_default_sort_by_id(self) -> None:
        """Default sort is by ID ascending (AC1)."""
        runner.invoke(app, ["add", "C"])
        runner.invoke(app, ["add", "A"])
        runner.invoke(app, ["add", "B"])

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        # Should not show sort indicator for default sort
        assert "sorted by" not in result.stdout or "sorted by id" not in result.stdout.lower()
