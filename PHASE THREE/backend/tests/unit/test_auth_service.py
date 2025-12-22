"""
Unit tests for the authentication service.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import auth_service
from app.schemas.auth import UserCreate, UserLogin
from app.models.user import User


@pytest.mark.asyncio
async def test_get_user_by_id(test_db: AsyncSession):
    """Tests retrieving a user by their ID."""
    # First, create a user to retrieve
    user_data = UserCreate(email="test@example.com", password="password", name="Test User")
    created_user = await auth_service.create_user(test_db, user_data)

    retrieved_user = await auth_service.get_user_by_id(test_db, created_user.id)

    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.email == created_user.email


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(test_db: AsyncSession):
    """Tests that get_user_by_id returns None for a non-existent user."""
    retrieved_user = await auth_service.get_user_by_id(test_db, "non_existent_id")
    assert retrieved_user is None


@pytest.mark.asyncio
async def test_create_user_already_exists(test_db: AsyncSession):
    """Tests that creating a user with an existing email raises a ValueError."""
    user_data = UserCreate(email="test@example.com", password="password", name="Test User")
    await auth_service.create_user(test_db, user_data)

    with pytest.raises(ValueError, match="Email already registered"):
        await auth_service.create_user(test_db, user_data)


@pytest.mark.asyncio
async def test_authenticate_user_success(test_db: AsyncSession):
    """Tests successful user authentication."""
    user_data = UserCreate(email="test@example.com", password="password", name="Test User")
    await auth_service.create_user(test_db, user_data)

    login_data = UserLogin(email="test@example.com", password="password")
    authenticated_user, token = await auth_service.authenticate_user(test_db, login_data)

    assert authenticated_user is not None
    assert token is not None
    assert authenticated_user.email == login_data.email


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(test_db: AsyncSession):
    """Tests that authentication fails with a wrong password."""
    user_data = UserCreate(email="test@example.com", password="password", name="Test User")
    await auth_service.create_user(test_db, user_data)

    login_data = UserLogin(email="test@example.com", password="wrong_password")
    result = await auth_service.authenticate_user(test_db, login_data)

    assert result is None


@pytest.mark.asyncio
async def test_authenticate_user_not_found(test_db: AsyncSession):
    """Tests that authentication fails for a non-existent user."""
    login_data = UserLogin(email="nonexistent@example.com", password="password")
    result = await auth_service.authenticate_user(test_db, login_data)

    assert result is None

@pytest.mark.asyncio
async def test_authenticate_user_no_password_account(test_db: AsyncSession):
    """Tests that authentication fails for a user with no password account."""
    user_data = UserCreate(email="test@example.com", password="password", name="Test User")
    user = await auth_service.create_user(test_db, user_data)

    # Manually delete the account to simulate a user with no password
    from app.models.user import Account
    from sqlmodel import select
    result = await test_db.execute(select(Account).where(Account.user_id == user.id))
    account = result.scalar_one()
    await test_db.delete(account)
    await test_db.commit()

    login_data = UserLogin(email="test@example.com", password="password")
    result = await auth_service.authenticate_user(test_db, login_data)

    assert result is None
