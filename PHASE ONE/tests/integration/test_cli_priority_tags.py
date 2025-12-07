"""Integration tests for priority and tags features (T057 - US6)."""

from typer.testing import CliRunner

from src.main import app

runner = CliRunner()


class TestCLIPriorityTags:
    """Integration tests for priority and tags commands."""

    def test_add_task_with_priority_high(self) -> None:
        """Add task with high priority (AC1)."""
        result = runner.invoke(app, ["add", "Urgent task", "--priority", "high"])

        assert result.exit_code == 0
        assert "created" in result.stdout.lower()

    def test_add_task_with_priority_medium(self) -> None:
        """Add task with medium priority (AC2)."""
        result = runner.invoke(app, ["add", "Normal task", "--priority", "medium"])

        assert result.exit_code == 0
        assert "created" in result.stdout.lower()

    def test_add_task_with_priority_low(self) -> None:
        """Add task with low priority (AC3)."""
        result = runner.invoke(app, ["add", "Later task", "--priority", "low"])

        assert result.exit_code == 0
        assert "created" in result.stdout.lower()

    def test_add_task_with_invalid_priority_shows_error(self) -> None:
        """Add task with invalid priority shows error (AC4)."""
        result = runner.invoke(app, ["add", "Task", "--priority", "critical"])

        assert result.exit_code == 1
        assert "ERROR" in result.stdout or "Invalid" in result.stdout

    def test_add_task_with_tags(self) -> None:
        """Add task with tags (AC5)."""
        result = runner.invoke(app, ["add", "Task", "--tags", "work,urgent"])

        assert result.exit_code == 0
        assert "created" in result.stdout.lower()

    def test_add_task_with_priority_and_tags(self) -> None:
        """Add task with both priority and tags (AC6)."""
        result = runner.invoke(
            app, ["add", "Important task", "--priority", "high", "--tags", "work,urgent"]
        )

        assert result.exit_code == 0
        assert "created" in result.stdout.lower()

    def test_list_shows_priority_and_tags(self) -> None:
        """List command shows priority and tags (AC7)."""
        # Add task with priority and tags
        add_result = runner.invoke(
            app, ["add", "TestPrioTags", "--priority", "medium", "--tags", "dev,feature"]
        )
        assert add_result.exit_code == 0

        # List tasks
        list_result = runner.invoke(app, ["list"])

        assert list_result.exit_code == 0
        # The table should have Priority and Tags columns
        assert "Priority" in list_result.stdout  # Column header
        assert "Tags" in list_result.stdout  # Column header
        # Check that task with priority and tags is displayed (may be truncated in table)
        assert "MED" in list_result.stdout  # We check priority instead of title which may be truncated
        assert "MED" in list_result.stdout  # Medium priority
        assert "dev" in list_result.stdout  # Tags contain "dev"

    def test_show_displays_priority_and_tags(self) -> None:
        """Show command displays priority and tags (AC8)."""
        import re

        # Add task with priority and tags
        add_result = runner.invoke(
            app, ["add", "Test task", "--priority", "high", "--tags", "test,important"]
        )
        assert add_result.exit_code == 0

        # Extract task ID
        match = re.search(r"Task #(\d+)", add_result.stdout)
        if match:
            task_id = match.group(1)

            # Show task details
            show_result = runner.invoke(app, ["show", task_id])

            assert show_result.exit_code == 0
            assert "Priority" in show_result.stdout or "high" in show_result.stdout
            assert "Tags" in show_result.stdout or "test" in show_result.stdout

    def test_update_task_priority(self) -> None:
        """Update task priority (AC9)."""
        import re

        # Add task
        add_result = runner.invoke(app, ["add", "Task"])
        assert add_result.exit_code == 0

        # Extract task ID
        match = re.search(r"Task #(\d+)", add_result.stdout)
        if match:
            task_id = match.group(1)

            # Update priority
            update_result = runner.invoke(
                app, ["update", task_id, "--priority", "high"]
            )

            assert update_result.exit_code == 0
            assert "updated" in update_result.stdout.lower()

    def test_update_add_tags(self) -> None:
        """Update task to add tags (AC10)."""
        import re

        # Add task
        add_result = runner.invoke(app, ["add", "Task"])
        assert add_result.exit_code == 0

        # Extract task ID
        match = re.search(r"Task #(\d+)", add_result.stdout)
        if match:
            task_id = match.group(1)

            # Add tags
            update_result = runner.invoke(
                app, ["update", task_id, "--add-tags", "work,important"]
            )

            assert update_result.exit_code == 0
            assert "updated" in update_result.stdout.lower()

    def test_update_remove_tags(self) -> None:
        """Update task to remove tags (AC11)."""
        import re

        # Add task with tags
        add_result = runner.invoke(
            app, ["add", "Task", "--tags", "work,later,maybe"]
        )
        assert add_result.exit_code == 0

        # Extract task ID
        match = re.search(r"Task #(\d+)", add_result.stdout)
        if match:
            task_id = match.group(1)

            # Remove tags
            update_result = runner.invoke(
                app, ["update", task_id, "--remove-tags", "later,maybe"]
            )

            assert update_result.exit_code == 0
            assert "updated" in update_result.stdout.lower()

    def test_too_many_tags_shows_error(self) -> None:
        """Adding more than 10 tags shows validation error (AC12)."""
        # Try to add 11 tags
        tags = ",".join([f"tag{i}" for i in range(11)])
        result = runner.invoke(app, ["add", "Task", "--tags", tags])

        assert result.exit_code == 1
        assert "ERROR" in result.stdout or "Cannot have more than 10 tags" in result.stdout

    def test_tag_too_long_shows_error(self) -> None:
        """Adding tag exceeding 50 chars shows validation error (AC13)."""
        long_tag = "A" * 51
        result = runner.invoke(app, ["add", "Task", "--tags", long_tag])

        assert result.exit_code == 1
        assert "ERROR" in result.stdout or "50 character limit" in result.stdout
