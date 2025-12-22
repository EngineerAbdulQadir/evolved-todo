"""Performance and data isolation tests."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, Priority


@pytest.mark.asyncio
async def test_dashboard_with_zero_tasks(
    test_client: AsyncClient, test_user, auth_token: str
):
    """Test dashboard performance with 0 tasks."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Act
    response = await test_client.get(f"/api/tasks/{test_user.id}", headers=headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["tasks"]) == 0


@pytest.mark.asyncio
async def test_dashboard_with_five_tasks(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test dashboard performance with 5 tasks."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create 5 tasks
    for i in range(5):
        task = Task(
            user_id=test_user.id,
            title=f"Task {i+1}",
            description=f"Description {i+1}",
            is_complete=i % 2 == 0,  # Alternate complete/incomplete
            priority=Priority.MEDIUM,
            tags=[f"tag{i+1}"],
        )
        test_db.add(task)
    await test_db.commit()

    # Act
    response = await test_client.get(f"/api/tasks/{test_user.id}", headers=headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["tasks"]) == 5

    # Verify all tasks are returned
    titles = {task["title"] for task in data["tasks"]}
    assert titles == {f"Task {i+1}" for i in range(5)}


@pytest.mark.asyncio
async def test_dashboard_with_fifty_tasks(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test dashboard performance with 50 tasks."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create 50 tasks
    priorities = [Priority.LOW, Priority.MEDIUM, Priority.HIGH]
    for i in range(50):
        task = Task(
            user_id=test_user.id,
            title=f"Task {i+1}",
            description=f"Description for task {i+1}",
            is_complete=i % 3 == 0,  # Every third task is complete
            priority=priorities[i % 3],
            tags=[f"category{i % 5}", f"tag{i % 10}"],  # Mix of tags
        )
        test_db.add(task)
    await test_db.commit()

    # Act
    response = await test_client.get(f"/api/tasks/{test_user.id}", headers=headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 50
    assert len(data["tasks"]) == 50

    # Verify data integrity
    for task in data["tasks"]:
        assert "id" in task
        assert "title" in task
        assert "description" in task
        assert "is_complete" in task
        assert "priority" in task
        assert "tags" in task
        assert isinstance(task["tags"], list)


@pytest.mark.asyncio
async def test_user_data_isolation(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test that users can only see their own tasks (data isolation)."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create tasks for test_user
    for i in range(3):
        task = Task(
            user_id=test_user.id,
            title=f"User A Task {i+1}",
            description="Belongs to User A",
            priority=Priority.MEDIUM,
        )
        test_db.add(task)

    # Create tasks for a different user
    other_user_id = "different-user-id-456"
    for i in range(5):
        task = Task(
            user_id=other_user_id,
            title=f"User B Task {i+1}",
            description="Belongs to User B",
            priority=Priority.HIGH,
        )
        test_db.add(task)

    await test_db.commit()

    # Act - User A fetches their tasks
    response = await test_client.get(f"/api/tasks/{test_user.id}", headers=headers)

    # Assert
    assert response.status_code == 200
    data = response.json()

    # User A should only see their 3 tasks
    assert data["total"] == 3
    assert len(data["tasks"]) == 3

    # Verify all tasks belong to User A
    for task in data["tasks"]:
        assert task["user_id"] == test_user.id
        assert "User A Task" in task["title"]
        assert task["description"] == "Belongs to User A"

    # Verify no User B tasks are returned
    for task in data["tasks"]:
        assert "User B Task" not in task["title"]


@pytest.mark.asyncio
async def test_user_cannot_access_other_user_tasks(
    test_client: AsyncClient, test_user, auth_token: str
):
    """Test that user cannot access another user's tasks via API."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}
    other_user_id = "different-user-id-789"

    # Act - Try to fetch another user's tasks
    response = await test_client.get(f"/api/tasks/{other_user_id}", headers=headers)

    # Assert - Should be forbidden
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data
    assert "access" in data["detail"].lower() or "forbidden" in data["detail"].lower()


@pytest.mark.asyncio
async def test_user_cannot_create_task_for_other_user(
    test_client: AsyncClient, test_user, auth_token: str
):
    """Test that user cannot create tasks for another user."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}
    other_user_id = "different-user-id-999"
    task_data = {"title": "Malicious Task"}

    # Act - Try to create task for another user
    response = await test_client.post(
        f"/api/tasks/{other_user_id}", json=task_data, headers=headers
    )

    # Assert - Should be forbidden
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_user_cannot_modify_other_user_task(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test that user cannot modify another user's tasks."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}
    other_user_id = "different-user-id-111"

    # Create a task belonging to another user
    other_task = Task(
        user_id=other_user_id,
        title="Other User Task",
        description="Belongs to someone else",
    )
    test_db.add(other_task)
    await test_db.commit()
    await test_db.refresh(other_task)

    # Act - Try to update another user's task
    update_data = {"title": "Hacked Task"}
    response = await test_client.put(
        f"/api/tasks/{test_user.id}/{other_task.id}",
        json=update_data,
        headers=headers,
    )

    # Assert - Should return 404 (task doesn't exist for this user)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_user_cannot_delete_other_user_task(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test that user cannot delete another user's tasks."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}
    other_user_id = "different-user-id-222"

    # Create a task belonging to another user
    other_task = Task(
        user_id=other_user_id, title="Protected Task", description="Cannot be deleted"
    )
    test_db.add(other_task)
    await test_db.commit()
    await test_db.refresh(other_task)

    # Act - Try to delete another user's task
    response = await test_client.delete(
        f"/api/tasks/{test_user.id}/{other_task.id}", headers=headers
    )

    # Assert - Should return 404 (task doesn't exist for this user)
    assert response.status_code == 404
