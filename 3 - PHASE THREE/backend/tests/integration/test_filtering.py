"""
Integration tests for task filtering and search (Phase 9 & 10).

Tests for:
- T145: Query param filtering
- T160: Search query param
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task


@pytest.mark.asyncio
async def test_filter_by_completed_status(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test filtering tasks by completion status (T145)."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create tasks with different completion statuses
    task1 = Task(user_id=test_user.id, title="Completed Task", is_complete=True)
    task2 = Task(user_id=test_user.id, title="Pending Task", is_complete=False)
    test_db.add_all([task1, task2])
    await test_db.commit()

    # Test filter for completed tasks
    response = await test_client.get(
        f"/api/tasks/{test_user.id}?completed=true", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["tasks"][0]["title"] == "Completed Task"

    # Test filter for pending tasks
    response = await test_client.get(
        f"/api/tasks/{test_user.id}?completed=false", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["tasks"][0]["title"] == "Pending Task"


@pytest.mark.asyncio
async def test_filter_by_priority(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test filtering tasks by priority (T145)."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create tasks with different priorities
    task1 = Task(user_id=test_user.id, title="High Priority", priority="high")
    task2 = Task(user_id=test_user.id, title="Medium Priority", priority="medium")
    task3 = Task(user_id=test_user.id, title="No Priority", priority=None)
    test_db.add_all([task1, task2, task3])
    await test_db.commit()

    # Test filter for high priority
    response = await test_client.get(
        f"/api/tasks/{test_user.id}?priority=high", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["tasks"][0]["title"] == "High Priority"


@pytest.mark.asyncio
async def test_filter_by_tag(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test filtering tasks by tag (T145)."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create tasks with different tags
    task1 = Task(user_id=test_user.id, title="Work Task", tags=["work", "urgent"])
    task2 = Task(user_id=test_user.id, title="Personal Task", tags=["personal"])
    task3 = Task(user_id=test_user.id, title="No Tags", tags=[])
    test_db.add_all([task1, task2, task3])
    await test_db.commit()

    # Test filter for "work" tag
    response = await test_client.get(
        f"/api/tasks/{test_user.id}?tag=work", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["tasks"][0]["title"] == "Work Task"


@pytest.mark.asyncio
async def test_multiple_filters_and_logic(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test combining multiple filters with AND logic (T145, T149)."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create varied tasks
    task1 = Task(
        user_id=test_user.id,
        title="Work High Pending",
        is_complete=False,
        priority="high",
        tags=["work"],
    )
    task2 = Task(
        user_id=test_user.id,
        title="Work High Complete",
        is_complete=True,
        priority="high",
        tags=["work"],
    )
    task3 = Task(
        user_id=test_user.id,
        title="Personal Low Pending",
        is_complete=False,
        priority="low",
        tags=["personal"],
    )
    test_db.add_all([task1, task2, task3])
    await test_db.commit()

    # Test combined filters (completed=false AND priority=high AND tag=work)
    response = await test_client.get(
        f"/api/tasks/{test_user.id}?completed=false&priority=high&tag=work",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["tasks"][0]["title"] == "Work High Pending"


@pytest.mark.asyncio
async def test_search_by_title(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test searching tasks by title (T160, T163)."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create tasks
    task1 = Task(user_id=test_user.id, title="Buy groceries", description="Milk and eggs")
    task2 = Task(user_id=test_user.id, title="Call dentist", description="Schedule appointment")
    test_db.add_all([task1, task2])
    await test_db.commit()

    # Search for "grocer" (substring of "groceries")
    response = await test_client.get(
        f"/api/tasks/{test_user.id}?search=grocer", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["tasks"][0]["title"] == "Buy groceries"


@pytest.mark.asyncio
async def test_search_by_description(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test searching tasks by description (T160, T164)."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create tasks
    task1 = Task(user_id=test_user.id, title="Shopping", description="Buy groceries from store")
    task2 = Task(user_id=test_user.id, title="Meeting", description="Team standup at 9am")
    test_db.add_all([task1, task2])
    await test_db.commit()

    # Search for "groceries" in description
    response = await test_client.get(
        f"/api/tasks/{test_user.id}?search=groceries", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["tasks"][0]["title"] == "Shopping"


@pytest.mark.asyncio
async def test_search_case_insensitive(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test case-insensitive search (T160, T163, T171)."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create task
    task = Task(user_id=test_user.id, title="Buy GROCERIES", description="milk")
    test_db.add(task)
    await test_db.commit()

    # Search with lowercase (substring of "GROCERIES")
    response = await test_client.get(
        f"/api/tasks/{test_user.id}?search=grocer", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1

    # Search with uppercase
    response = await test_client.get(
        f"/api/tasks/{test_user.id}?search=MILK", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1


@pytest.mark.asyncio
async def test_search_with_filters_combined(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test combining search with filters (T172)."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create tasks
    task1 = Task(
        user_id=test_user.id,
        title="Buy groceries",
        is_complete=False,
        priority="high",
        tags=["shopping"],
    )
    task2 = Task(
        user_id=test_user.id,
        title="Buy groceries online",
        is_complete=True,
        priority="low",
        tags=["shopping"],
    )
    test_db.add_all([task1, task2])
    await test_db.commit()

    # Search "grocer" (substring) with filter completed=false
    response = await test_client.get(
        f"/api/tasks/{test_user.id}?search=grocer&completed=false", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["tasks"][0]["is_complete"] is False


@pytest.mark.asyncio
async def test_no_results_returns_empty_list(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test that no matching results returns empty list (T169, T173)."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create task
    task = Task(user_id=test_user.id, title="Sample Task")
    test_db.add(task)
    await test_db.commit()

    # Search for non-existent term
    response = await test_client.get(
        f"/api/tasks/{test_user.id}?search=nonexistent", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["tasks"] == []
