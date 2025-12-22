"""Integration tests for recurring tasks CLI (T084 - US10)."""

from datetime import date

from typer.testing import CliRunner

from src.main import app

runner = CliRunner()


class TestCLIRecurringTasksAdd:
    """Test adding recurring tasks via CLI."""

    def test_add_daily_recurring_task(self) -> None:
        """Add task with daily recurrence (AC1)."""
        result = runner.invoke(
            app,
            [
                "add",
                "Daily standup",
                "--due-date",
                "2025-12-10",
                "--due-time",
                "09:00",
                "--recur",
                "daily",
            ],
        )

        assert result.exit_code == 0
        assert "Daily standup" in result.stdout
        assert "created" in result.stdout.lower()

    def test_add_weekly_recurring_task(self) -> None:
        """Add task with weekly recurrence (AC2)."""
        result = runner.invoke(
            app,
            [
                "add",
                "Weekly team meeting",
                "--due-date",
                "2025-12-12",
                "--recur",
                "weekly",
                "--recur-day",
                "5",  # Friday
            ],
        )

        assert result.exit_code == 0
        assert "Weekly team meeting" in result.stdout

    def test_add_monthly_recurring_task(self) -> None:
        """Add task with monthly recurrence (AC3)."""
        result = runner.invoke(
            app,
            [
                "add",
                "Monthly report",
                "--due-date",
                "2025-12-01",
                "--recur",
                "monthly",
                "--recur-day",
                "1",
            ],
        )

        assert result.exit_code == 0
        assert "Monthly report" in result.stdout

    def test_add_recurring_without_due_date_fails(self) -> None:
        """Recurring task without due date fails (AC4)."""
        result = runner.invoke(
            app,
            ["add", "Recurring task", "--recur", "daily"],
        )

        assert result.exit_code == 1
        assert "Recurring tasks require a --due-date" in result.stdout

    def test_add_weekly_without_recur_day_fails(self) -> None:
        """Weekly recurrence without recur_day fails (AC5)."""
        result = runner.invoke(
            app,
            ["add", "Weekly task", "--due-date", "2025-12-10", "--recur", "weekly"],
        )

        assert result.exit_code == 1
        assert "Weekly recurrence requires --recur-day" in result.stdout

    def test_add_monthly_without_recur_day_fails(self) -> None:
        """Monthly recurrence without recur_day fails (AC6)."""
        result = runner.invoke(
            app,
            ["add", "Monthly task", "--due-date", "2025-12-10", "--recur", "monthly"],
        )

        assert result.exit_code == 1
        assert "Monthly recurrence requires --recur-day" in result.stdout


class TestCLIRecurringTasksUpdate:
    """Test updating recurring tasks via CLI."""

    def test_update_task_to_weekly_recurring(self) -> None:
        """Update non-recurring task to weekly recurrence (AC7)."""
        # Add non-recurring task
        add_result = runner.invoke(
            app,
            ["add", "Task to update", "--due-date", "2025-12-10"],
        )
        assert add_result.exit_code == 0

        # Update to weekly recurrence
        result = runner.invoke(
            app,
            ["update", "1", "--recur", "weekly", "--recur-day", "3"],  # Wednesday
        )

        assert result.exit_code == 0
        assert "updated" in result.stdout.lower()

    def test_update_clear_recurrence(self) -> None:
        """Clear recurrence from recurring task (AC8)."""
        # Add recurring task
        add_result = runner.invoke(
            app,
            [
                "add",
                "Recurring task",
                "--due-date",
                "2025-12-10",
                "--recur",
                "daily",
            ],
        )
        assert add_result.exit_code == 0

        # Clear recurrence
        result = runner.invoke(
            app,
            ["update", "1", "--recur", "none"],
        )

        assert result.exit_code == 0


class TestCLIRecurringTasksComplete:
    """Test completing recurring tasks via CLI."""

    def test_complete_daily_recurring_creates_new_task(self) -> None:
        """Completing daily recurring task creates new task for next day (AC9)."""
        # Add daily recurring task
        add_result = runner.invoke(
            app,
            [
                "add",
                "DailyEx",  # Shorter name to avoid truncation
                "--due-date",
                "2025-12-10",
                "--recur",
                "daily",
            ],
        )
        assert add_result.exit_code == 0
        # Extract task ID from output
        import re

        match = re.search(r"#(\d+)", add_result.stdout)
        assert match is not None
        task_id = int(match.group(1))

        # Complete the task
        complete_result = runner.invoke(app, ["complete", str(task_id)])
        assert complete_result.exit_code == 0

        # List tasks - should show both completed original and new incomplete task
        list_result = runner.invoke(app, ["list"])
        assert list_result.exit_code == 0
        # Should have DailyEx somewhere in output (appears twice: completed and new)
        assert "DailyEx" in list_result.stdout
        # Should have both [X] (completed) and [ ] (new incomplete)
        assert "[X]" in list_result.stdout
        assert "[ ]" in list_result.stdout
        # Should show Dec 11 (next day) for new task
        assert "Dec 11" in list_result.stdout

    def test_complete_weekly_recurring_creates_new_task(self) -> None:
        """Completing weekly recurring task creates new task for next week (AC10)."""
        # Add weekly recurring task (Friday)
        add_result = runner.invoke(
            app,
            [
                "add",
                "WeeklyRev",  # Shorter name
                "--due-date",
                "2025-12-12",  # Friday
                "--recur",
                "weekly",
                "--recur-day",
                "5",  # Friday
            ],
        )
        assert add_result.exit_code == 0

        import re

        match = re.search(r"#(\d+)", add_result.stdout)
        assert match is not None
        task_id = int(match.group(1))

        # Complete the task
        complete_result = runner.invoke(app, ["complete", str(task_id)])
        assert complete_result.exit_code == 0

        # List should show both completed and new task
        list_result = runner.invoke(app, ["list"])
        assert list_result.exit_code == 0
        # Should have Weekly somewhere (title may be truncated)
        assert "Weekly" in list_result.stdout
        # Should show Dec 19 (next Friday) for new task
        assert "Dec 19" in list_result.stdout

    def test_complete_monthly_recurring_creates_new_task(self) -> None:
        """Completing monthly recurring task creates new task for next month (AC11)."""
        # Add monthly recurring task
        add_result = runner.invoke(
            app,
            [
                "add",
                "Monthly report",
                "--due-date",
                "2025-12-01",
                "--recur",
                "monthly",
                "--recur-day",
                "1",
            ],
        )
        assert add_result.exit_code == 0

        # Complete the task
        complete_result = runner.invoke(app, ["complete", "1"])
        assert complete_result.exit_code == 0

        # New task should exist
        list_result = runner.invoke(app, ["list"])
        assert list_result.exit_code == 0
        assert "2" in list_result.stdout

    def test_complete_non_recurring_does_not_create_new_task(self) -> None:
        """Completing non-recurring task does not create new task (AC12)."""
        # Add non-recurring task
        add_result = runner.invoke(
            app,
            ["add", "One-time task", "--due-date", "2025-12-10"],
        )
        assert add_result.exit_code == 0

        # Complete the task
        complete_result = runner.invoke(app, ["complete", "1"])
        assert complete_result.exit_code == 0

        # List should only show task 1 (no task 2)
        list_result = runner.invoke(app, ["list"])
        assert list_result.exit_code == 0
        # Should NOT have task 2
        lines = [line for line in list_result.stdout.split("\n") if line.strip()]
        id_2_count = sum(1 for line in lines if line.strip().startswith("2"))
        assert id_2_count == 0
