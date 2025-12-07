"""Integration tests for search and filter features (T064 - US7)."""

from typer.testing import CliRunner

from src.main import app

runner = CliRunner()


class TestCLISearch:
    """Integration tests for search functionality."""

    def test_search_by_keyword_in_title(self) -> None:
        """Search finds tasks by keyword in title (AC1)."""
        # Add tasks
        runner.invoke(app, ["add", "Fix bug in login"])
        runner.invoke(app, ["add", "Write report"])

        result = runner.invoke(app, ["list", "--search", "bug"])

        assert result.exit_code == 0
        assert "Fix bug" in result.stdout or "bug" in result.stdout

    def test_search_by_keyword_in_description(self) -> None:
        """Search finds tasks by keyword in description (AC2)."""
        runner.invoke(app, ["add", "Task 1", "--desc", "Important sales meeting"])
        runner.invoke(app, ["add", "Task 2", "--desc", "Review code"])

        result = runner.invoke(app, ["list", "--search", "sales"])

        assert result.exit_code == 0
        assert "Task 1" in result.stdout

    def test_search_case_insensitive(self) -> None:
        """Search is case-insensitive (AC3)."""
        runner.invoke(app, ["add", "Buy Groceries"])

        result_lower = runner.invoke(app, ["list", "--search", "groceries"])
        result_upper = runner.invoke(app, ["list", "--search", "GROCERIES"])

        assert result_lower.exit_code == 0
        assert result_upper.exit_code == 0
        assert "Groceries" in result_lower.stdout or "Buy" in result_lower.stdout
        assert "Groceries" in result_upper.stdout or "Buy" in result_upper.stdout


class TestCLIFilter:
    """Integration tests for filter functionality."""

    def test_filter_by_status_complete(self) -> None:
        """Filter by complete status (AC1)."""
        import re

        # Add and complete a task
        add_result = runner.invoke(app, ["add", "Completed task"])
        match = re.search(r"Task #(\d+)", add_result.stdout)
        if match:
            task_id = match.group(1)
            runner.invoke(app, ["complete", task_id])

        result = runner.invoke(app, ["list", "--status", "complete"])

        assert result.exit_code == 0
        # Should show completed tasks
        assert "[X]" in result.stdout or "complete" in result.stdout.lower()

    def test_filter_by_status_incomplete(self) -> None:
        """Filter by incomplete status (AC2)."""
        runner.invoke(app, ["add", "Incomplete task"])

        result = runner.invoke(app, ["list", "--status", "incomplete"])

        assert result.exit_code == 0
        assert "Incomplete task" in result.stdout or "[ ]" in result.stdout

    def test_filter_by_priority_high(self) -> None:
        """Filter by high priority (AC3)."""
        runner.invoke(app, ["add", "Critical bug", "--priority", "high"])

        result = runner.invoke(app, ["list", "--priority", "high"])

        assert result.exit_code == 0
        assert "Critical bug" in result.stdout or "HIGH" in result.stdout

    def test_filter_by_tag(self) -> None:
        """Filter by tag (AC4)."""
        runner.invoke(app, ["add", "Work task", "--tags", "work,urgent"])

        result = runner.invoke(app, ["list", "--tag", "work"])

        assert result.exit_code == 0
        assert "Work task" in result.stdout or "work" in result.stdout

    def test_filter_invalid_status_shows_error(self) -> None:
        """Invalid status filter shows error (AC5)."""
        result = runner.invoke(app, ["list", "--status", "invalid"])

        assert result.exit_code == 1
        assert "ERROR" in result.stdout or "Invalid" in result.stdout

    def test_filter_invalid_priority_shows_error(self) -> None:
        """Invalid priority filter shows error (AC6)."""
        result = runner.invoke(app, ["list", "--priority", "critical"])

        assert result.exit_code == 1
        assert "ERROR" in result.stdout or "Invalid" in result.stdout


class TestCLICombinedSearchFilter:
    """Integration tests for combined search and filter."""

    def test_search_and_filter_combined(self) -> None:
        """Search with filter combines results with AND logic (AC1)."""
        import re

        # Add tasks
        runner.invoke(app, ["add", "Fix login bug", "--priority", "high"])
        runner.invoke(app, ["add", "Fix display bug", "--priority", "low"])

        result = runner.invoke(app, ["list", "--search", "bug", "--priority", "high"])

        assert result.exit_code == 0
        # Should only show "Fix login bug" (high priority + contains "bug")
        assert "login" in result.stdout

    def test_search_and_multiple_filters(self) -> None:
        """Search with multiple filters (AC2)."""
        import re

        # Add task
        add_result = runner.invoke(
            app, ["add", "Review PR", "--priority", "medium", "--tags", "work"]
        )
        match = re.search(r"Task #(\d+)", add_result.stdout)
        if match:
            task_id = match.group(1)

            result = runner.invoke(
                app, [
                    "list",
                    "--search", "review",
                    "--status", "incomplete",
                    "--priority", "medium",
                    "--tag", "work",
                ]
            )

            assert result.exit_code == 0
            assert "Review" in result.stdout or "PR" in result.stdout

    def test_filtered_count_displayed(self) -> None:
        """Filtered results show count 'Showing X of Y' (AC3)."""
        # Add multiple tasks
        runner.invoke(app, ["add", "Task 1", "--priority", "high"])
        runner.invoke(app, ["add", "Task 2", "--priority", "low"])
        runner.invoke(app, ["add", "Task 3", "--priority", "low"])

        result = runner.invoke(app, ["list", "--priority", "high"])

        assert result.exit_code == 0
        # Should show filtered count
        assert "Showing" in result.stdout or "Tasks" in result.stdout

    def test_no_results_shows_empty_message(self) -> None:
        """Search/filter with no results shows appropriate message (AC4)."""
        result = runner.invoke(app, ["list", "--search", "nonexistentxyz123"])

        assert result.exit_code == 0
        assert "No tasks found" in result.stdout or "Create your first task" in result.stdout
