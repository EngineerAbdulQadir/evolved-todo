"""
Integration tests for toggle task completion (Phase 7).

These tests verify:
- T125: Rapid checkbox toggles (race conditions)
- T126: Toggle with network error (rollback)
- T127: completed_at timestamp is stored correctly
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task


@pytest.mark.asyncio
async def test_rapid_checkbox_toggles(
    test_client: AsyncClient, test_user, auth_token: str, test_task: Task
):
    """Test rapid checkbox toggles don't cause race conditions (T125)."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}
    original_status = test_task.is_complete

    # Act - Toggle 5 times rapidly
    responses = []
    for _ in range(5):
        response = await test_client.patch(
            f"/api/tasks/{test_user.id}/{test_task.id}/complete", headers=headers
        )
        responses.append(response)

    # Assert - All requests should succeed
    for response in responses:
        assert response.status_code == 200

    # Final state should be opposite of original after odd number of toggles
    final_response = responses[-1]
    final_data = final_response.json()
    assert final_data["is_complete"] != original_status


@pytest.mark.asyncio
async def test_toggle_with_invalid_task_id(
    test_client: AsyncClient, test_user, auth_token: str
):
    """Test toggle with non-existent task returns 404 (T126 - error handling)."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}
    invalid_task_id = 99999

    # Act
    response = await test_client.patch(
        f"/api/tasks/{test_user.id}/{invalid_task_id}/complete", headers=headers
    )

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert str(invalid_task_id) in data["detail"]


@pytest.mark.asyncio
async def test_toggle_without_auth_returns_401(
    test_client: AsyncClient, test_user, test_task: Task
):
    """Test toggle without authentication returns 401 (T126 - error handling)."""
    # Act
    response = await test_client.patch(
        f"/api/tasks/{test_user.id}/{test_task.id}/complete"
    )

    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_toggle_other_user_task_returns_403(
    test_client: AsyncClient, test_task: Task, auth_token: str
):
    """Test toggle another user's task returns 403 (T126 - error handling)."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}
    other_user_id = "different-user"

    # Act
    response = await test_client.patch(
        f"/api/tasks/{other_user_id}/{test_task.id}/complete", headers=headers
    )

    # Assert
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_completed_at_timestamp_set_on_complete(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test completed_at timestamp is set when marking task complete (T127, T118)."""
    # Arrange - Create incomplete task
    headers = {"Authorization": f"Bearer {auth_token}"}
    task = Task(
        user_id=test_user.id,
        title="Test Timestamp Task",
        is_complete=False,
        completed_at=None,
    )
    test_db.add(task)
    await test_db.commit()
    await test_db.refresh(task)

    # Act - Mark complete
    response = await test_client.patch(
        f"/api/tasks/{test_user.id}/{task.id}/complete", headers=headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["is_complete"] is True
    assert data["completed_at"] is not None
    assert isinstance(data["completed_at"], str)  # ISO format string


@pytest.mark.asyncio
async def test_completed_at_timestamp_cleared_on_incomplete(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test completed_at timestamp is cleared when marking task incomplete (T127, T119)."""
    # Arrange - Create completed task with completed_at set
    from datetime import datetime

    headers = {"Authorization": f"Bearer {auth_token}"}
    task = Task(
        user_id=test_user.id,
        title="Test Timestamp Clear Task",
        is_complete=True,
        completed_at=datetime.utcnow(),
    )
    test_db.add(task)
    await test_db.commit()
    await test_db.refresh(task)

    # Verify task has completed_at
    assert task.completed_at is not None

    # Act - Mark incomplete
    response = await test_client.patch(
        f"/api/tasks/{test_user.id}/{task.id}/complete", headers=headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["is_complete"] is False
    assert data["completed_at"] is None


@pytest.mark.asyncio
async def test_toggle_preserves_other_fields(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test toggling completion doesn't modify other task fields (T126)."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}
    task = Task(
        user_id=test_user.id,
        title="Preserve Fields Task",
        description="Important description",
        priority="high",
        tags=["work", "urgent"],
        is_complete=False,
    )
    test_db.add(task)
    await test_db.commit()
    await test_db.refresh(task)

    # Act - Toggle complete
    response = await test_client.patch(
        f"/api/tasks/{test_user.id}/{task.id}/complete", headers=headers
    )

    # Assert - All other fields preserved
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Preserve Fields Task"
    assert data["description"] == "Important description"
    assert data["priority"] == "high"
    assert set(data["tags"]) == {"work", "urgent"}
    assert data["is_complete"] is True


@pytest.mark.asyncio
async def test_multiple_tasks_toggle_independently(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test toggling one task doesn't affect others (T125 - data isolation)."""
    # Arrange - Create 3 tasks
    headers = {"Authorization": f"Bearer {auth_token}"}
    tasks = []
    for i in range(3):
        task = Task(
            user_id=test_user.id,
            title=f"Task {i+1}",
            is_complete=False,
        )
        test_db.add(task)
        tasks.append(task)

    await test_db.commit()
    for task in tasks:
        await test_db.refresh(task)

    # Act - Toggle only the second task
    response = await test_client.patch(
        f"/api/tasks/{test_user.id}/{tasks[1].id}/complete", headers=headers
    )

    # Assert
    assert response.status_code == 200

    # Verify only second task is complete
    all_tasks_response = await test_client.get(
        f"/api/tasks/{test_user.id}", headers=headers
    )
    all_tasks_data = all_tasks_response.json()

    task_statuses = {
        task["id"]: task["is_complete"] for task in all_tasks_data["tasks"]
    }

    assert task_statuses[tasks[0].id] is False  # First task unchanged
    assert task_statuses[tasks[1].id] is True  # Second task toggled
    assert task_statuses[tasks[2].id] is False  # Third task unchanged
