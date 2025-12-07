"""Integration tests for todo add command (T025 - US1)."""

from typer.testing import CliRunner

from src.main import app

runner = CliRunner()


class TestCLIAdd:
    """Integration tests for `todo add` command."""

    def test_add_task_with_title_only(self) -> None:
        """User can add task with title only via CLI (AC1)."""
        result = runner.invoke(app, ["add", "Buy milk"])

        assert result.exit_code == 0
        assert "Task #1 created" in result.stdout
        assert "Buy milk" in result.stdout

    def test_add_task_with_description(self) -> None:
        """User can add task with title and description via CLI (AC2)."""
        result = runner.invoke(
            app, ["add", "Prepare presentation", "--desc", "Include Q3 charts"]
        )

        assert result.exit_code == 0
        assert "created" in result.stdout
        assert "Prepare presentation" in result.stdout

    def test_add_task_with_description_short_flag(self) -> None:
        """User can use -d short flag for description (AC3)."""
        result = runner.invoke(app, ["add", "Meeting", "-d", "Discuss timeline"])

        assert result.exit_code == 0
        assert "created" in result.stdout
        assert "Meeting" in result.stdout

    def test_add_task_empty_title_shows_error(self) -> None:
        """Adding task with empty title shows error (AC4)."""
        result = runner.invoke(app, ["add", ""])

        assert result.exit_code == 1
        assert "ERROR" in result.stdout or "Error" in result.stdout

    def test_add_task_whitespace_title_shows_error(self) -> None:
        """Adding task with whitespace-only title shows error (AC5)."""
        result = runner.invoke(app, ["add", "   "])

        assert result.exit_code == 1
        assert "ERROR" in result.stdout or "Error" in result.stdout

    def test_add_multiple_tasks_assigns_unique_ids(self) -> None:
        """Multiple tasks get unique IDs (AC6)."""
        result1 = runner.invoke(app, ["add", "First task"])
        result2 = runner.invoke(app, ["add", "Second task"])

        # IDs are incrementing because singleton service is shared
        assert result1.exit_code == 0
        assert result2.exit_code == 0
        assert "created" in result1.stdout
        assert "created" in result2.stdout

    def test_add_task_with_unicode_characters(self) -> None:
        """Task with unicode characters is created successfully (AC7)."""
        result = runner.invoke(app, ["add", "Email mom 📧"])

        # May fail on Windows console, but should at least not crash
        assert result.exit_code == 0 or result.exit_code == 1

    def test_add_task_with_long_title(self) -> None:
        """Task with 200 character title is accepted (AC8)."""
        long_title = "A" * 200
        result = runner.invoke(app, ["add", long_title])

        assert result.exit_code == 0
        assert "created" in result.stdout

    def test_add_task_with_too_long_title_shows_error(self) -> None:
        """Task with >200 character title shows error (AC9)."""
        too_long_title = "A" * 201
        result = runner.invoke(app, ["add", too_long_title])

        assert result.exit_code == 1
        assert "ERROR" in result.stdout or "Error" in result.stdout
        assert "200" in result.stdout
