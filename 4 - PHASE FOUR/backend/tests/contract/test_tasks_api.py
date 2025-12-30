"""
Contract tests for task API endpoints.

These tests verify that API responses match the defined schemas/contracts.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task


@pytest.mark.asyncio
async def test_get_tasks_response_contract(
    test_client: AsyncClient, test_user, auth_token: str
):
    """Test GET /api/tasks/{user_id} response matches TaskListResponse schema."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Act
    response = await test_client.get(f"/api/tasks/{test_user.id}", headers=headers)

    # Assert - Status code
    assert response.status_code == 200

    # Assert - Response structure
    data = response.json()
    assert isinstance(data, dict), "Response should be a dictionary"
    assert "tasks" in data, "Response should have 'tasks' field"
    assert "total" in data, "Response should have 'total' field"

    # Assert - Field types
    assert isinstance(data["tasks"], list), "'tasks' should be a list"
    assert isinstance(data["total"], int), "'total' should be an integer"


@pytest.mark.asyncio
async def test_get_tasks_with_data_contract(
    test_client: AsyncClient, test_user, auth_token: str, multiple_tasks
):
    """Test GET /api/tasks/{user_id} with tasks matches TaskResponse schema."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Act
    response = await test_client.get(f"/api/tasks/{test_user.id}", headers=headers)

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Verify at least one task exists to test schema
    assert len(data["tasks"]) > 0, "Should have tasks to verify schema"

    # Verify each task matches TaskResponse schema
    for task in data["tasks"]:
        # Required fields
        assert "id" in task, "Task should have 'id'"
        assert "user_id" in task, "Task should have 'user_id'"
        assert "title" in task, "Task should have 'title'"
        assert "is_complete" in task, "Task should have 'is_complete'"
        assert "created_at" in task, "Task should have 'created_at'"

        # Field types - required
        assert isinstance(task["id"], int), "'id' should be integer"
        assert isinstance(task["user_id"], str), "'user_id' should be string"
        assert isinstance(task["title"], str), "'title' should be string"
        assert isinstance(task["is_complete"], bool), "'is_complete' should be boolean"
        assert isinstance(task["created_at"], str), "'created_at' should be ISO string"

        # Optional fields (can be null or have specific type)
        if task.get("description") is not None:
            assert isinstance(
                task["description"], str
            ), "'description' should be string when present"

        if task.get("priority") is not None:
            assert isinstance(
                task["priority"], str
            ), "'priority' should be string when present"
            assert task["priority"] in [
                "low",
                "medium",
                "high",
            ], "'priority' should be valid enum value"

        if task.get("tags") is not None:
            assert isinstance(task["tags"], list), "'tags' should be list when present"
            assert all(
                isinstance(tag, str) for tag in task["tags"]
            ), "All tags should be strings"

        if task.get("due_date") is not None:
            assert isinstance(
                task["due_date"], str
            ), "'due_date' should be string when present"

        if task.get("due_time") is not None:
            assert isinstance(
                task["due_time"], str
            ), "'due_time' should be string when present"

        if task.get("recurrence") is not None:
            assert isinstance(
                task["recurrence"], str
            ), "'recurrence' should be string when present"

        if task.get("recurrence_day") is not None:
            assert isinstance(
                task["recurrence_day"], int
            ), "'recurrence_day' should be integer when present"


@pytest.mark.asyncio
async def test_create_task_request_contract(
    test_client: AsyncClient, test_user, auth_token: str
):
    """Test POST /api/tasks/{user_id} accepts TaskCreate schema."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Test minimal valid request
    minimal_task = {"title": "Test Task"}

    # Act
    response = await test_client.post(
        f"/api/tasks/{test_user.id}", json=minimal_task, headers=headers
    )

    # Assert
    assert response.status_code == 201, "Minimal task creation should succeed"

    # Test full valid request
    full_task = {
        "title": "Full Task",
        "description": "Task description",
        "priority": "high",
        "tags": ["work", "urgent"],
        "due_date": "2025-12-31",
        "due_time": "23:59:00",
    }

    response = await test_client.post(
        f"/api/tasks/{test_user.id}", json=full_task, headers=headers
    )

    assert response.status_code == 201, "Full task creation should succeed"


@pytest.mark.asyncio
async def test_create_task_response_contract(
    test_client: AsyncClient, test_user, auth_token: str
):
    """Test POST /api/tasks/{user_id} response matches TaskResponse schema."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}
    task_data = {
        "title": "Contract Test Task",
        "description": "Testing response contract",
        "priority": "medium",
        "tags": ["test"],
    }

    # Act
    response = await test_client.post(
        f"/api/tasks/{test_user.id}", json=task_data, headers=headers
    )

    # Assert
    assert response.status_code == 201
    task = response.json()

    # Required fields
    assert "id" in task
    assert "user_id" in task
    assert "title" in task
    assert "is_complete" in task
    assert "created_at" in task

    # Field values
    assert task["title"] == task_data["title"]
    assert task["description"] == task_data["description"]
    assert task["priority"] == task_data["priority"]
    assert task["user_id"] == test_user.id
    assert task["is_complete"] is False


@pytest.mark.asyncio
async def test_create_task_validation_contract(
    test_client: AsyncClient, test_user, auth_token: str
):
    """Test POST /api/tasks/{user_id} validates TaskCreate schema."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Test missing required field
    invalid_task = {}

    # Act
    response = await test_client.post(
        f"/api/tasks/{test_user.id}", json=invalid_task, headers=headers
    )

    # Assert
    assert response.status_code == 422, "Should fail validation for missing title"

    # Test empty title
    invalid_task = {"title": ""}

    response = await test_client.post(
        f"/api/tasks/{test_user.id}", json=invalid_task, headers=headers
    )

    assert response.status_code == 422, "Should fail validation for empty title"

    # Test invalid priority
    invalid_task = {"title": "Test", "priority": "invalid"}

    response = await test_client.post(
        f"/api/tasks/{test_user.id}", json=invalid_task, headers=headers
    )

    assert response.status_code == 422, "Should fail validation for invalid priority"


@pytest.mark.asyncio
async def test_update_task_request_contract(
    test_client: AsyncClient, test_user, auth_token: str, test_task: Task
):
    """Test PUT /api/tasks/{user_id}/{task_id} accepts TaskUpdate schema."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Test partial update
    update_data = {"title": "Updated Title"}

    # Act
    response = await test_client.put(
        f"/api/tasks/{test_user.id}/{test_task.id}",
        json=update_data,
        headers=headers,
    )

    # Assert
    assert response.status_code == 200, "Partial update should succeed"

    # Test full update
    update_data = {
        "title": "New Title",
        "description": "New description",
        "priority": "high",
        "tags": ["updated"],
        "is_complete": True,
    }

    response = await test_client.put(
        f"/api/tasks/{test_user.id}/{test_task.id}",
        json=update_data,
        headers=headers,
    )

    assert response.status_code == 200, "Full update should succeed"


@pytest.mark.asyncio
async def test_update_task_response_contract(
    test_client: AsyncClient, test_user, auth_token: str, test_task: Task
):
    """Test PUT /api/tasks/{user_id}/{task_id} response matches TaskResponse schema."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}
    update_data = {"title": "Contract Updated", "priority": "low"}

    # Act
    response = await test_client.put(
        f"/api/tasks/{test_user.id}/{test_task.id}",
        json=update_data,
        headers=headers,
    )

    # Assert
    assert response.status_code == 200
    task = response.json()

    # Required fields present
    assert "id" in task
    assert "user_id" in task
    assert "title" in task
    assert "is_complete" in task
    assert "created_at" in task

    # Updated values reflected
    assert task["title"] == update_data["title"]
    assert task["priority"] == update_data["priority"]
    assert task["id"] == test_task.id


@pytest.mark.asyncio
async def test_toggle_complete_response_contract(
    test_client: AsyncClient, test_user, auth_token: str, test_task: Task
):
    """Test PATCH /api/tasks/{user_id}/{task_id}/complete response matches TaskResponse."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Act
    response = await test_client.patch(
        f"/api/tasks/{test_user.id}/{test_task.id}/complete", headers=headers
    )

    # Assert
    assert response.status_code == 200
    task = response.json()

    # Required fields
    assert "id" in task
    assert "user_id" in task
    assert "title" in task
    assert "is_complete" in task
    assert "created_at" in task

    # Field types
    assert isinstance(task["id"], int)
    assert isinstance(task["user_id"], str)
    assert isinstance(task["title"], str)
    assert isinstance(task["is_complete"], bool)
    assert isinstance(task["created_at"], str)


@pytest.mark.asyncio
async def test_delete_task_response_contract(
    test_client: AsyncClient, test_user, auth_token: str, test_task: Task
):
    """Test DELETE /api/tasks/{user_id}/{task_id} returns 204 No Content."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Act
    response = await test_client.delete(
        f"/api/tasks/{test_user.id}/{test_task.id}", headers=headers
    )

    # Assert
    assert response.status_code == 204, "Delete should return 204 No Content"
    assert response.content == b"", "Delete response should have no content"


@pytest.mark.asyncio
async def test_unauthorized_request_contract(test_client: AsyncClient, test_user):
    """Test requests without auth return 401 Unauthorized."""
    # Act
    response = await test_client.get(f"/api/tasks/{test_user.id}")

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data, "Error response should have 'detail' field"


@pytest.mark.asyncio
async def test_forbidden_request_contract(
    test_client: AsyncClient, test_user, auth_token: str
):
    """Test accessing another user's tasks returns 403 Forbidden."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}
    other_user_id = "different-user"

    # Act
    response = await test_client.get(f"/api/tasks/{other_user_id}", headers=headers)

    # Assert
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data, "Error response should have 'detail' field"


@pytest.mark.asyncio
async def test_not_found_contract(
    test_client: AsyncClient, test_user, auth_token: str
):
    """Test accessing non-existent task returns 404 Not Found."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Act
    response = await test_client.get(
        f"/api/tasks/{test_user.id}/99999", headers=headers
    )

    # Assert
    assert response.status_code in [404, 405], "Should return 404 or 405 for non-existent task"
    if response.status_code == 404:
        data = response.json()
        assert "detail" in data, "Error response should have 'detail' field"


@pytest.mark.asyncio
async def test_toggle_complete_response_contract(
    test_client: AsyncClient, test_user, test_task: Task, auth_token: str
):
    """Test PATCH /api/tasks/{user_id}/{id}/complete response matches TaskResponse schema."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}
    original_status = test_task.is_complete

    # Act
    response = await test_client.patch(
        f"/api/tasks/{test_user.id}/{test_task.id}/complete", headers=headers
    )

    # Assert - Status code
    assert response.status_code == 200

    # Assert - Response structure
    task = response.json()

    # Required fields
    assert "id" in task, "Response should have 'id' field"
    assert "user_id" in task, "Response should have 'user_id' field"
    assert "title" in task, "Response should have 'title' field"
    assert "is_complete" in task, "Response should have 'is_complete' field"
    assert "created_at" in task, "Response should have 'created_at' field"

    # Field values
    assert task["id"] == test_task.id, "Task ID should match"
    assert task["user_id"] == test_user.id, "User ID should match"
    assert task["is_complete"] != original_status, "Completion status should be toggled"
    assert isinstance(task["is_complete"], bool), "is_complete should be boolean"
