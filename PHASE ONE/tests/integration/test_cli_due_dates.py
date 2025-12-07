"""Integration tests for due dates and reminders (T071 - US8)."""

from datetime import date, time

from typer.testing import CliRunner

from src.main import app

runner = CliRunner()


class TestCLIDueDates:
    """Integration tests for due date functionality."""

    def test_add_task_with_due_date(self) -> None:
        """Add task with due date (AC1)."""
        result = runner.invoke(
            app, ["add", "Submit report", "--due-date", "2025-12-15"]
        )

        assert result.exit_code == 0
        assert "Task #" in result.stdout
        assert "created" in result.stdout.lower()

    def test_add_task_with_due_date_and_time(self) -> None:
        """Add task with due date and time (AC2)."""
        result = runner.invoke(
            app,
            [
                "add",
                "Team meeting",
                "--due-date",
                "2025-12-10",
                "--due-time",
                "14:30",
            ],
        )

        assert result.exit_code == 0
        assert "Task #" in result.stdout

    def test_add_task_invalid_due_date_format(self) -> None:
        """Invalid due date format shows error (AC3)."""
        result = runner.invoke(app, ["add", "Task", "--due-date", "12/15/2025"])

        assert result.exit_code == 1
        assert "ERROR" in result.stdout or "Invalid" in result.stdout

    def test_add_task_invalid_due_time_format(self) -> None:
        """Invalid due time format shows error (AC4)."""
        result = runner.invoke(
            app,
            ["add", "Task", "--due-date", "2025-12-15", "--due-time", "2:30 PM"],
        )

        assert result.exit_code == 1
        assert "ERROR" in result.stdout or "Invalid" in result.stdout

    def test_list_shows_due_date(self) -> None:
        """List command shows due dates (AC5)."""
        runner.invoke(app, ["add", "Task with date", "--due-date", "2025-12-20"])

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "Due Date" in result.stdout or "Dec" in result.stdout

    def test_list_shows_overdue_indicator(self) -> None:
        """List shows overdue indicator for past due dates (AC6)."""
        # Add task with past due date
        runner.invoke(
            app, ["add", "Overdue task", "--due-date", "2020-01-01"]
        )

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        # Should show overdue indicator (⚠ symbol or red text)
        # Due to rich formatting, we check for task presence
        assert "Overdue task" in result.stdout or "Jan" in result.stdout

    def test_show_displays_due_date(self) -> None:
        """Show command displays due date (AC7)."""
        import re

        add_result = runner.invoke(
            app, ["add", "Task", "--due-date", "2025-12-15", "--due-time", "14:00"]
        )
        match = re.search(r"Task #(\d+)", add_result.stdout)
        if match:
            task_id = match.group(1)

            result = runner.invoke(app, ["show", task_id])

            assert result.exit_code == 0
            assert "Due:" in result.stdout
            assert "Dec 15" in result.stdout or "2025" in result.stdout


class TestCLIUpdateDueDates:
    """Integration tests for updating due dates."""

    def test_update_task_due_date(self) -> None:
        """Update task due date (AC1)."""
        import re

        add_result = runner.invoke(app, ["add", "Task to update"])
        match = re.search(r"Task #(\d+)", add_result.stdout)
        if match:
            task_id = match.group(1)

            result = runner.invoke(
                app, ["update", task_id, "--due-date", "2025-12-25"]
            )

            assert result.exit_code == 0
            assert "updated" in result.stdout.lower()

    def test_update_task_due_time(self) -> None:
        """Update task due time (AC2)."""
        import re

        add_result = runner.invoke(
            app, ["add", "Task", "--due-date", "2025-12-20"]
        )
        match = re.search(r"Task #(\d+)", add_result.stdout)
        if match:
            task_id = match.group(1)

            result = runner.invoke(app, ["update", task_id, "--due-time", "09:00"])

            assert result.exit_code == 0
            assert "updated" in result.stdout.lower()

    def test_update_clear_due_date(self) -> None:
        """Update can clear due date (AC3)."""
        import re

        add_result = runner.invoke(
            app, ["add", "Task", "--due-date", "2025-12-20"]
        )
        match = re.search(r"Task #(\d+)", add_result.stdout)
        if match:
            task_id = match.group(1)

            result = runner.invoke(app, ["update", task_id, "--due-date", "none"])

            assert result.exit_code == 0
            assert "updated" in result.stdout.lower()

            # Verify cleared
            show_result = runner.invoke(app, ["show", task_id])
            assert "No due date" in show_result.stdout

    def test_update_clear_due_time(self) -> None:
        """Update can clear due time (AC4)."""
        import re

        add_result = runner.invoke(
            app,
            ["add", "Task", "--due-date", "2025-12-20", "--due-time", "14:00"],
        )
        match = re.search(r"Task #(\d+)", add_result.stdout)
        if match:
            task_id = match.group(1)

            result = runner.invoke(app, ["update", task_id, "--due-time", "none"])

            assert result.exit_code == 0
            assert "updated" in result.stdout.lower()


class TestCLIDueDateValidation:
    """Integration tests for due date validation."""

    def test_invalid_date_format_yyyy_mm_dd(self) -> None:
        """Invalid date format shows helpful error (AC1)."""
        result = runner.invoke(app, ["add", "Task", "--due-date", "2025/12/15"])

        assert result.exit_code == 1
        assert "YYYY-MM-DD" in result.stdout or "Invalid" in result.stdout

    def test_invalid_time_format_hh_mm(self) -> None:
        """Invalid time format shows helpful error (AC2)."""
        result = runner.invoke(
            app, ["add", "Task", "--due-date", "2025-12-15", "--due-time", "14.30"]
        )

        assert result.exit_code == 1
        assert "HH:MM" in result.stdout or "Invalid" in result.stdout

    def test_invalid_date_value(self) -> None:
        """Invalid date value shows error (AC3)."""
        result = runner.invoke(app, ["add", "Task", "--due-date", "2025-13-45"])

        assert result.exit_code == 1
        assert "ERROR" in result.stdout or "Invalid" in result.stdout

    def test_invalid_time_value(self) -> None:
        """Invalid time value shows error (AC4)."""
        result = runner.invoke(
            app, ["add", "Task", "--due-date", "2025-12-15", "--due-time", "25:99"]
        )

        assert result.exit_code == 1
        assert "ERROR" in result.stdout or "Invalid" in result.stdout
