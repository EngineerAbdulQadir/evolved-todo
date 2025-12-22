"""Integration tests for task endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, Priority


@pytest.mark.asyncio
async def test_get_user_tasks_empty(
    test_client: AsyncClient, test_user, auth_token: str
):
    """Test fetching tasks when user has no tasks."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Act
    response = await test_client.get(f"/api/tasks/{test_user.id}", headers=headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert "total" in data
    assert data["total"] == 0
    assert len(data["tasks"]) == 0


@pytest.mark.asyncio
async def test_get_user_tasks_with_tasks(
    test_client: AsyncClient, test_user, auth_token: str, multiple_tasks
):
    """Test fetching tasks when user has multiple tasks."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Act
    response = await test_client.get(f"/api/tasks/{test_user.id}", headers=headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert "total" in data
    assert data["total"] == 5
    assert len(data["tasks"]) == 5


@pytest.mark.asyncio
async def test_get_user_tasks_unauthorized(test_client: AsyncClient, test_user):
    """Test fetching tasks without authentication fails."""
    # Act
    response = await test_client.get(f"/api/tasks/{test_user.id}")

    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_user_tasks_wrong_user(
    test_client: AsyncClient, test_user, auth_token: str
):
    """Test fetching another user's tasks fails."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}
    other_user_id = "different-user-id"

    # Act
    response = await test_client.get(f"/api/tasks/{other_user_id}", headers=headers)

    # Assert
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_task_minimal(
    test_client: AsyncClient, test_user, auth_token: str
):
    """Test creating a task with minimal required fields."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}
    task_data = {
        "title": "Test Task",
    }

    # Act
    response = await test_client.post(
        f"/api/tasks/{test_user.id}", json=task_data, headers=headers
    )

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["user_id"] == test_user.id
    assert data["is_complete"] is False
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_create_task_full(
    test_client: AsyncClient, test_user, auth_token: str
):
    """Test creating a task with all fields."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}
    task_data = {
        "title": "Full Task",
        "description": "Complete task description",
        "priority": "high",
        "tags": ["work", "urgent"],
        "due_date": "2025-12-31",
        "due_time": "23:59:00",
    }

    # Act
    response = await test_client.post(
        f"/api/tasks/{test_user.id}", json=task_data, headers=headers
    )

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert data["priority"] == "high"
    assert len(data["tags"]) == 2
    assert data["due_date"] == "2025-12-31"


@pytest.mark.asyncio
async def test_update_task(
    test_client: AsyncClient, test_user, auth_token: str, test_task: Task
):
    """Test updating a task."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}
    update_data = {
        "title": "Updated Title",
        "priority": "high",
    }

    # Act
    response = await test_client.put(
        f"/api/tasks/{test_user.id}/{test_task.id}",
        json=update_data,
        headers=headers,
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["priority"] == "high"
    assert data["id"] == test_task.id


@pytest.mark.asyncio
async def test_update_nonexistent_task(
    test_client: AsyncClient, test_user, auth_token: str
):
    """Test updating a non-existent task returns 404."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}
    update_data = {"title": "Updated"}

    # Act
    response = await test_client.put(
        f"/api/tasks/{test_user.id}/99999",
        json=update_data,
        headers=headers,
    )

    # Assert
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_task(
    test_client: AsyncClient, test_user, auth_token: str, test_task: Task
):
    """Test deleting a task."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Act
    response = await test_client.delete(
        f"/api/tasks/{test_user.id}/{test_task.id}", headers=headers
    )

    # Assert
    assert response.status_code == 204

    # Verify task is deleted
    get_response = await test_client.get(
        f"/api/tasks/{test_user.id}", headers=headers
    )
    tasks = get_response.json()["tasks"]
    assert all(t["id"] != test_task.id for t in tasks)


@pytest.mark.asyncio
async def test_toggle_task_complete(
    test_client: AsyncClient, test_user, auth_token: str, test_task: Task
):
    """Test toggling task completion status."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}
    original_status = test_task.is_complete

    # Act
    response = await test_client.patch(
        f"/api/tasks/{test_user.id}/{test_task.id}/complete", headers=headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["is_complete"] != original_status


@pytest.mark.asyncio
async def test_create_task_validation_empty_title(
    test_client: AsyncClient, test_user, auth_token: str
):
    """Test creating task with empty title fails validation."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}
    task_data = {"title": ""}

    # Act
    response = await test_client.post(
        f"/api/tasks/{test_user.id}", json=task_data, headers=headers
    )

    # Assert
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_task_validation_due_time_without_date(
    test_client: AsyncClient, test_user, auth_token: str
):
    """Test creating task with due_time but no due_date fails."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}
    task_data = {
        "title": "Test Task",
        "due_time": "10:00:00",
    }

    # Act
    response = await test_client.post(
        f"/api/tasks/{test_user.id}", json=task_data, headers=headers
    )

    # Assert
    assert response.status_code == 400
    assert "due time requires a due date" in response.json()["detail"].lower()


# ==================== Recurring Tasks Tests (T189) ====================


@pytest.mark.asyncio
async def test_toggle_complete_daily_recurring_creates_next_instance(
    test_client: AsyncClient, test_db: AsyncSession, test_user, auth_token: str
):
    """Test marking daily recurring task complete creates next instance."""
    # Arrange
    from datetime import date
    from app.models.task import RecurrencePattern

    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create daily recurring task
    task_data = {
        "title": "Daily standup",
        "recurrence": "daily",
        "due_date": "2025-12-14",
    }

    create_response = await test_client.post(
        f"/api/tasks/{test_user.id}", json=task_data, headers=headers
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Act - Mark complete
    toggle_response = await test_client.patch(
        f"/api/tasks/{test_user.id}/{task_id}/complete", headers=headers
    )

    # Assert
    assert toggle_response.status_code == 200
    completed_task = toggle_response.json()
    assert completed_task["is_complete"] is True

    # Verify new instance was created
    tasks_response = await test_client.get(
        f"/api/tasks/{test_user.id}?completed=false", headers=headers
    )
    assert tasks_response.status_code == 200
    active_tasks = tasks_response.json()["tasks"]

    # Should have 1 new incomplete task
    assert len(active_tasks) == 1
    new_task = active_tasks[0]

    # Verify new task properties
    assert new_task["title"] == "Daily standup"
    assert new_task["recurrence"] == "daily"
    assert new_task["due_date"] == "2025-12-15"  # Tomorrow
    assert new_task["is_complete"] is False


@pytest.mark.asyncio
async def test_toggle_complete_weekly_recurring_creates_next_instance(
    test_client: AsyncClient, test_db: AsyncSession, test_user, auth_token: str
):
    """Test marking weekly recurring task complete creates next instance."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create weekly recurring task (every Monday)
    task_data = {
        "title": "Weekly team meeting",
        "recurrence": "weekly",
        "recurrence_day": 1,  # Monday
        "due_date": "2025-12-15",  # Monday
        "description": "Discuss sprint progress",
        "priority": "high",
        "tags": ["work", "meeting"],
    }

    create_response = await test_client.post(
        f"/api/tasks/{test_user.id}", json=task_data, headers=headers
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Act - Mark complete
    toggle_response = await test_client.patch(
        f"/api/tasks/{test_user.id}/{task_id}/complete", headers=headers
    )

    # Assert
    assert toggle_response.status_code == 200

    # Verify new instance was created
    tasks_response = await test_client.get(
        f"/api/tasks/{test_user.id}?completed=false", headers=headers
    )
    assert tasks_response.status_code == 200
    active_tasks = tasks_response.json()["tasks"]

    assert len(active_tasks) == 1
    new_task = active_tasks[0]

    # Verify properties copied (T194)
    assert new_task["title"] == "Weekly team meeting"
    assert new_task["description"] == "Discuss sprint progress"
    assert new_task["priority"] == "high"
    assert sorted(new_task["tags"]) == ["meeting", "work"]
    assert new_task["recurrence"] == "weekly"
    assert new_task["recurrence_day"] == 1
    assert new_task["due_date"] == "2025-12-22"  # Next Monday
    assert new_task["is_complete"] is False


@pytest.mark.asyncio
async def test_toggle_complete_monthly_recurring_creates_next_instance(
    test_client: AsyncClient, test_db: AsyncSession, test_user, auth_token: str
):
    """Test marking monthly recurring task complete creates next instance."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create monthly recurring task (15th of each month)
    task_data = {
        "title": "Monthly report",
        "recurrence": "monthly",
        "recurrence_day": 15,
        "due_date": "2025-12-15",
    }

    create_response = await test_client.post(
        f"/api/tasks/{test_user.id}", json=task_data, headers=headers
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Act - Mark complete
    toggle_response = await test_client.patch(
        f"/api/tasks/{test_user.id}/{task_id}/complete", headers=headers
    )

    # Assert
    assert toggle_response.status_code == 200

    # Verify new instance was created
    tasks_response = await test_client.get(
        f"/api/tasks/{test_user.id}?completed=false", headers=headers
    )
    assert tasks_response.status_code == 200
    active_tasks = tasks_response.json()["tasks"]

    assert len(active_tasks) == 1
    new_task = active_tasks[0]

    assert new_task["title"] == "Monthly report"
    assert new_task["recurrence"] == "monthly"
    assert new_task["recurrence_day"] == 15
    assert new_task["due_date"] == "2026-01-15"  # Next month
    assert new_task["is_complete"] is False


@pytest.mark.asyncio
async def test_toggle_complete_non_recurring_does_not_create_instance(
    test_client: AsyncClient, test_db: AsyncSession, test_user, auth_token: str
):
    """Test that non-recurring tasks don't create new instances."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}

    task_data = {"title": "One-time task", "recurrence": None}

    create_response = await test_client.post(
        f"/api/tasks/{test_user.id}", json=task_data, headers=headers
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Act - Mark complete
    toggle_response = await test_client.patch(
        f"/api/tasks/{test_user.id}/{task_id}/complete", headers=headers
    )

    # Assert
    assert toggle_response.status_code == 200

    # Verify NO new instance was created
    tasks_response = await test_client.get(
        f"/api/tasks/{test_user.id}?completed=false", headers=headers
    )
    assert tasks_response.status_code == 200
    active_tasks = tasks_response.json()["tasks"]

    # Should have NO incomplete tasks
    assert len(active_tasks) == 0


@pytest.mark.asyncio
async def test_toggle_complete_recurring_without_due_date(
    test_client: AsyncClient, test_db: AsyncSession, test_user, auth_token: str
):
    """Test recurring task without due date uses current date for calculation."""
    # Arrange
    from datetime import date, timedelta

    headers = {"Authorization": f"Bearer {auth_token}"}

    task_data = {
        "title": "Daily task without due date",
        "recurrence": "daily",
        # No due_date specified
    }

    create_response = await test_client.post(
        f"/api/tasks/{test_user.id}", json=task_data, headers=headers
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Act - Mark complete
    toggle_response = await test_client.patch(
        f"/api/tasks/{test_user.id}/{task_id}/complete", headers=headers
    )

    # Assert
    assert toggle_response.status_code == 200

    # Verify new instance was created with tomorrow's date
    tasks_response = await test_client.get(
        f"/api/tasks/{test_user.id}?completed=false", headers=headers
    )
    assert tasks_response.status_code == 200
    active_tasks = tasks_response.json()["tasks"]

    assert len(active_tasks) == 1
    new_task = active_tasks[0]

    # Should have due date set to tomorrow
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    assert new_task["due_date"] == tomorrow


@pytest.mark.asyncio
async def test_delete_recurring_task_stops_future_instances(
    test_client: AsyncClient, test_db: AsyncSession, test_user, auth_token: str
):
    """Test deleting recurring task prevents future instances (T202)."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create daily recurring task
    task_data = {
        "title": "Daily recurring task",
        "recurrence": "daily",
        "due_date": "2025-12-14",
    }

    create_response = await test_client.post(
        f"/api/tasks/{test_user.id}", json=task_data, headers=headers
    )
    assert create_response.status_code == 201
    original_task_id = create_response.json()["id"]

    # Complete the task to create next instance
    toggle_response = await test_client.patch(
        f"/api/tasks/{test_user.id}/{original_task_id}/complete", headers=headers
    )
    assert toggle_response.status_code == 200

    # Verify new instance was created
    tasks_response = await test_client.get(
        f"/api/tasks/{test_user.id}?completed=false", headers=headers
    )
    assert tasks_response.status_code == 200
    active_tasks = tasks_response.json()["tasks"]
    assert len(active_tasks) == 1
    new_instance_id = active_tasks[0]["id"]

    # Act - Delete the original completed task
    delete_original_response = await test_client.delete(
        f"/api/tasks/{test_user.id}/{original_task_id}", headers=headers
    )
    assert delete_original_response.status_code == 204

    # Verify new instance still exists (not cascade deleted)
    tasks_after_delete = await test_client.get(
        f"/api/tasks/{test_user.id}", headers=headers
    )
    assert tasks_after_delete.status_code == 200
    remaining_tasks = tasks_after_delete.json()["tasks"]
    assert len(remaining_tasks) == 1
    assert remaining_tasks[0]["id"] == new_instance_id

    # Delete the new instance
    delete_new_response = await test_client.delete(
        f"/api/tasks/{test_user.id}/{new_instance_id}", headers=headers
    )
    assert delete_new_response.status_code == 204

    # Assert - Verify no tasks remain and no new instances are created
    final_tasks_response = await test_client.get(
        f"/api/tasks/{test_user.id}", headers=headers
    )
    assert final_tasks_response.status_code == 200
    final_tasks = final_tasks_response.json()["tasks"]
    assert len(final_tasks) == 0  # All recurring instances deleted, no orphans


# Phase 13: Due Date Filtering Tests (T203)


@pytest.mark.asyncio
async def test_filter_overdue_tasks(
    test_client: AsyncClient, test_db: AsyncSession, test_user, auth_token: str
):
    """Test filtering tasks by overdue status (T203)."""
    from datetime import date, timedelta

    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    # Create overdue task
    overdue_task = {
        "title": "Overdue task",
        "due_date": yesterday.isoformat(),
    }
    await test_client.post(f"/api/tasks/{test_user.id}", json=overdue_task, headers=headers)

    # Create task due today
    today_task = {
        "title": "Task due today",
        "due_date": today.isoformat(),
    }
    await test_client.post(f"/api/tasks/{test_user.id}", json=today_task, headers=headers)

    # Create future task
    future_task = {
        "title": "Future task",
        "due_date": tomorrow.isoformat(),
    }
    await test_client.post(f"/api/tasks/{test_user.id}", json=future_task, headers=headers)

    # Act - Filter for overdue tasks
    response = await test_client.get(
        f"/api/tasks/{test_user.id}?due_date_filter=overdue", headers=headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["tasks"][0]["title"] == "Overdue task"


@pytest.mark.asyncio
async def test_filter_tasks_due_today(
    test_client: AsyncClient, test_db: AsyncSession, test_user, auth_token: str
):
    """Test filtering tasks due today (T203)."""
    from datetime import date, timedelta

    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    # Create tasks with different due dates
    await test_client.post(
        f"/api/tasks/{test_user.id}",
        json={"title": "Overdue", "due_date": yesterday.isoformat()},
        headers=headers,
    )
    await test_client.post(
        f"/api/tasks/{test_user.id}",
        json={"title": "Due today", "due_date": today.isoformat()},
        headers=headers,
    )
    await test_client.post(
        f"/api/tasks/{test_user.id}",
        json={"title": "Future", "due_date": tomorrow.isoformat()},
        headers=headers,
    )

    # Act
    response = await test_client.get(
        f"/api/tasks/{test_user.id}?due_date_filter=today", headers=headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["tasks"][0]["title"] == "Due today"


@pytest.mark.asyncio
async def test_filter_tasks_due_this_week(
    test_client: AsyncClient, test_db: AsyncSession, test_user, auth_token: str
):
    """Test filtering tasks due this week (T203)."""
    from datetime import date, timedelta

    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}
    today = date.today()
    in_3_days = today + timedelta(days=3)
    in_10_days = today + timedelta(days=10)

    # Create tasks with different due dates
    await test_client.post(
        f"/api/tasks/{test_user.id}",
        json={"title": "This week", "due_date": in_3_days.isoformat()},
        headers=headers,
    )
    await test_client.post(
        f"/api/tasks/{test_user.id}",
        json={"title": "Next week", "due_date": in_10_days.isoformat()},
        headers=headers,
    )

    # Act
    response = await test_client.get(
        f"/api/tasks/{test_user.id}?due_date_filter=this_week", headers=headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["tasks"][0]["title"] == "This week"
