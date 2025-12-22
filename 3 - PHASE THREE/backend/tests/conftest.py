"""Pytest configuration and fixtures for backend testing."""

import asyncio
from typing import AsyncGenerator, Generator
from datetime import datetime, date

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool, StaticPool
from sqlalchemy import create_engine

from app.core.database import get_session
from app.models.user import User, Account, Session
from app.models.task import Task, Priority, RecurrencePattern
from app.services.auth_service import create_access_token, hash_password
from sqlmodel import SQLModel

# Import app last to avoid naming conflicts
from app.main import app

# Import all models to ensure they're registered with SQLModel metadata
from app import models  # noqa: F401


# Test database URL (use in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create a test database engine."""
    # Import all model modules to register them with SQLModel metadata
    import app.models.user  # noqa: F401
    import app.models.task  # noqa: F401

    # Use StaticPool to share connection in memory
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Add exec() method for SQLModel compatibility
        if not hasattr(session, 'exec'):
            session.exec = session.execute
        yield session


@pytest_asyncio.fixture(scope="function")
async def session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Alias for test_db to support unit tests."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as db_session:
        # Add exec() method for SQLModel compatibility
        if not hasattr(db_session, 'exec'):
            db_session.exec = db_session.execute
        yield db_session


@pytest_asyncio.fixture(scope="function")
async def test_user(test_db: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        id="test-user-id-123",
        name="Test User",
        email="test@example.com",
        email_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_token(test_user: User) -> str:
    """Create a JWT token for the test user."""
    token, _ = create_access_token(test_user.id, test_user.email)
    return token


@pytest_asyncio.fixture(scope="function")
async def test_client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client with database override."""

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield test_db

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_task(test_db: AsyncSession, test_user: User) -> Task:
    """Create a test task."""
    task = Task(
        user_id=test_user.id,
        title="Test Task",
        description="This is a test task",
        priority=Priority.MEDIUM,
        tags=["test", "sample"],
        due_date=date(2025, 12, 31),
        is_complete=False,
    )
    test_db.add(task)
    await test_db.commit()
    await test_db.refresh(task)
    return task


@pytest_asyncio.fixture(scope="function")
async def multiple_tasks(test_db: AsyncSession, test_user: User) -> list[Task]:
    """Create multiple test tasks."""
    tasks = [
        Task(
            user_id=test_user.id,
            title=f"Task {i}",
            description=f"Description {i}",
            priority=Priority.HIGH if i % 3 == 0 else Priority.MEDIUM,
            tags=[f"tag{i}"],
            is_complete=i % 2 == 0,
        )
        for i in range(1, 6)
    ]
    for task in tasks:
        test_db.add(task)
    await test_db.commit()
    for task in tasks:
        await test_db.refresh(task)
    return tasks
