"""
Integration tests for task sorting (Phase 11).

Tests for:
- T174: Sort query params
- T176-T179: Sort implementation
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime

from app.models.task import Task


@pytest.mark.asyncio
async def test_sort_by_created_at_desc(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test sorting by creation date descending (T174, T177-T179)."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create tasks with different timestamps
    task1 = Task(user_id=test_user.id, title="First Task", created_at=datetime(2024, 1, 1))
    task2 = Task(user_id=test_user.id, title="Second Task", created_at=datetime(2024, 1, 2))
    task3 = Task(user_id=test_user.id, title="Third Task", created_at=datetime(2024, 1, 3))
    test_db.add_all([task1, task2, task3])
    await test_db.commit()

    # Sort by created_at descending (newest first)
    response = await test_client.get(
        f"/api/tasks/{test_user.id}?sort_by=created_at&sort_order=desc",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["tasks"][0]["title"] == "Third Task"
    assert data["tasks"][1]["title"] == "Second Task"
    assert data["tasks"][2]["title"] == "First Task"


@pytest.mark.asyncio
async def test_sort_by_created_at_asc(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test sorting by creation date ascending (T179)."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create tasks
    task1 = Task(user_id=test_user.id, title="First Task", created_at=datetime(2024, 1, 1))
    task2 = Task(user_id=test_user.id, title="Second Task", created_at=datetime(2024, 1, 2))
    test_db.add_all([task1, task2])
    await test_db.commit()

    # Sort by created_at ascending (oldest first)
    response = await test_client.get(
        f"/api/tasks/{test_user.id}?sort_by=created_at&sort_order=asc",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tasks"][0]["title"] == "First Task"
    assert data["tasks"][1]["title"] == "Second Task"


@pytest.mark.asyncio
async def test_sort_by_due_date(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test sorting by due date (T178)."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create tasks with different due dates
    task1 = Task(user_id=test_user.id, title="Due Tomorrow", due_date=date(2024, 1, 2))
    task2 = Task(user_id=test_user.id, title="Due Today", due_date=date(2024, 1, 1))
    task3 = Task(user_id=test_user.id, title="No Due Date", due_date=None)
    test_db.add_all([task1, task2, task3])
    await test_db.commit()

    # Sort by due_date ascending (NULL values sort first in SQL)
    response = await test_client.get(
        f"/api/tasks/{test_user.id}?sort_by=due_date&sort_order=asc",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    # Verify tasks are sorted (NULL first, then by date)
    titles = [task["title"] for task in data["tasks"]]
    assert "Due Today" in titles
    assert "Due Tomorrow" in titles
    # Verify the two tasks with dates are in correct order
    dated_tasks = [t for t in data["tasks"] if t["due_date"] is not None]
    assert dated_tasks[0]["title"] == "Due Today"
    assert dated_tasks[1]["title"] == "Due Tomorrow"


@pytest.mark.asyncio
async def test_sort_by_priority(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test sorting by priority (T178)."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create tasks with different priorities
    task1 = Task(user_id=test_user.id, title="Low Priority", priority="low")
    task2 = Task(user_id=test_user.id, title="High Priority", priority="high")
    task3 = Task(user_id=test_user.id, title="Medium Priority", priority="medium")
    test_db.add_all([task1, task2, task3])
    await test_db.commit()

    # Sort by priority descending
    response = await test_client.get(
        f"/api/tasks/{test_user.id}?sort_by=priority&sort_order=desc",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    # Note: Alphabetically desc means "medium" > "low" > "high"
    assert data["tasks"][0]["priority"] == "medium"


@pytest.mark.asyncio
async def test_sort_by_title(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test sorting by title (T178)."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create tasks with different titles
    task1 = Task(user_id=test_user.id, title="Zebra Task")
    task2 = Task(user_id=test_user.id, title="Apple Task")
    task3 = Task(user_id=test_user.id, title="Banana Task")
    test_db.add_all([task1, task2, task3])
    await test_db.commit()

    # Sort by title ascending (A-Z)
    response = await test_client.get(
        f"/api/tasks/{test_user.id}?sort_by=title&sort_order=asc",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tasks"][0]["title"] == "Apple Task"
    assert data["tasks"][1]["title"] == "Banana Task"
    assert data["tasks"][2]["title"] == "Zebra Task"


@pytest.mark.asyncio
async def test_sort_by_completed_status(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test sorting by completion status (T178)."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create tasks with different completion statuses
    task1 = Task(user_id=test_user.id, title="Completed Task", is_complete=True)
    task2 = Task(user_id=test_user.id, title="Pending Task", is_complete=False)
    test_db.add_all([task1, task2])
    await test_db.commit()

    # Sort by completed ascending (pending first)
    response = await test_client.get(
        f"/api/tasks/{test_user.id}?sort_by=completed&sort_order=asc",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tasks"][0]["title"] == "Pending Task"
    assert data["tasks"][1]["title"] == "Completed Task"


@pytest.mark.asyncio
async def test_sort_with_filters(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test combining sort with filters (T185)."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create varied tasks
    task1 = Task(
        user_id=test_user.id,
        title="A Task",
        priority="high",
        is_complete=False,
    )
    task2 = Task(
        user_id=test_user.id,
        title="B Task",
        priority="high",
        is_complete=False,
    )
    task3 = Task(
        user_id=test_user.id,
        title="C Task",
        priority="low",
        is_complete=False,
    )
    test_db.add_all([task1, task2, task3])
    await test_db.commit()

    # Filter by priority=high and sort by title ascending
    response = await test_client.get(
        f"/api/tasks/{test_user.id}?priority=high&sort_by=title&sort_order=asc",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["tasks"][0]["title"] == "A Task"
    assert data["tasks"][1]["title"] == "B Task"


@pytest.mark.asyncio
async def test_default_sort_order(
    test_client: AsyncClient, test_user, auth_token: str, test_db: AsyncSession
):
    """Test default sort order is created_at desc."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create tasks
    task1 = Task(user_id=test_user.id, title="First Task", created_at=datetime(2024, 1, 1))
    task2 = Task(user_id=test_user.id, title="Second Task", created_at=datetime(2024, 1, 2))
    test_db.add_all([task1, task2])
    await test_db.commit()

    # No sort params - should default to created_at desc
    response = await test_client.get(
        f"/api/tasks/{test_user.id}",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tasks"][0]["title"] == "Second Task"  # Newer first
    assert data["tasks"][1]["title"] == "First Task"
