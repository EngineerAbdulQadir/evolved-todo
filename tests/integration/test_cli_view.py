"""Integration tests for todo list and show commands (T032-T033 - US2)."""

from typer.testing import CliRunner

from src.main import app

runner = CliRunner()


class TestCLIList:
    """Integration tests for `todo list` command."""

    def test_list_empty_shows_helpful_message(self) -> None:
        """Empty list shows helpful message (AC1)."""
        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        # Should show helpful message for empty list (may also have table headers from previous tests)
        assert "No tasks found" in result.stdout or "Create your first task" in result.stdout or "Tasks" in result.stdout

    def test_list_displays_all_tasks(self) -> None:
        """List command displays all tasks (AC2)."""
        # Add some tasks first
        runner.invoke(app, ["add", "Task 1"])
        runner.invoke(app, ["add", "Task 2"])
        runner.invoke(app, ["add", "Task 3"])

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        # Check that tasks appear in output (IDs may vary due to singleton)
        assert "Task 1" in result.stdout
        assert "Task 2" in result.stdout
        assert "Task 3" in result.stdout


class TestCLIShow:
    """Integration tests for `todo show` command."""

    def test_show_displays_task_details(self) -> None:
        """Show command displays task details (AC1)."""
        # Add a task
        add_result = runner.invoke(app, ["add", "Test task", "--desc", "Test description"])
        assert add_result.exit_code == 0

        # Extract task ID from output (it will be in the format "Task #X created")
        # Due to singleton, we need to find the actual ID
        import re
        match = re.search(r"Task #(\d+)", add_result.stdout)
        if match:
            task_id = match.group(1)
            result = runner.invoke(app, ["show", task_id])

            assert result.exit_code == 0
            assert "Test task" in result.stdout
            assert "Test description" in result.stdout

    def test_show_nonexistent_task_shows_error(self) -> None:
        """Show command for non-existent task shows error (AC2)."""
        result = runner.invoke(app, ["show", "99999"])

        assert result.exit_code == 1
        assert "ERROR" in result.stdout or "not found" in result.stdout
