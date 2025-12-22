"""Shared pytest fixtures for all tests."""

from datetime import date, datetime, time

import pytest

from src.lib.id_generator import IdGenerator
from src.models.task import Priority, RecurrencePattern, Task
from src.services.task_service import TaskService
from src.services.task_store import InMemoryTaskStore


@pytest.fixture
def id_generator() -> IdGenerator:
    """Provide a fresh ID generator for each test."""
    return IdGenerator()


@pytest.fixture
def task_store() -> InMemoryTaskStore:
    """Provide an empty in-memory task store for each test."""
    return InMemoryTaskStore()


@pytest.fixture
def task_service(
    task_store: InMemoryTaskStore, id_generator: IdGenerator
) -> TaskService:
    """Provide a task service with empty store for each test."""
    return TaskService(store=task_store, id_gen=id_generator)


@pytest.fixture
def sample_task() -> Task:
    """Provide a basic sample task for testing."""
    return Task(
        id=1,
        title="Buy groceries",
        description="Milk, eggs, bread",
        is_complete=False,
        created_at=datetime(2025, 12, 7, 10, 0, 0),
    )


@pytest.fixture
def sample_task_with_priority() -> Task:
    """Provide a sample task with priority for testing."""
    return Task(
        id=2,
        title="Fix bug in production",
        description="Critical bug affecting users",
        is_complete=False,
        created_at=datetime(2025, 12, 7, 11, 0, 0),
        priority=Priority.HIGH,
        tags=["bug", "urgent"],
    )


@pytest.fixture
def sample_task_with_due_date() -> Task:
    """Provide a sample task with due date for testing."""
    return Task(
        id=3,
        title="Submit report",
        description="Q4 financial report",
        is_complete=False,
        created_at=datetime(2025, 12, 7, 12, 0, 0),
        due_date=date(2025, 12, 15),
        due_time=time(17, 0, 0),
    )


@pytest.fixture
def sample_recurring_task() -> Task:
    """Provide a sample recurring task for testing."""
    return Task(
        id=4,
        title="Water plants",
        description="Weekly plant watering",
        is_complete=False,
        created_at=datetime(2025, 12, 7, 13, 0, 0),
        recurrence=RecurrencePattern.WEEKLY,
        recurrence_day=1,  # Monday
    )
