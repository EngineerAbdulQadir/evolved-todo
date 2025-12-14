"""Integration tests for authentication endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_registration_success(test_client: AsyncClient, test_db: AsyncSession):
    """Test successful user registration."""
    # Arrange
    registration_data = {
        "name": "New User",
        "email": "newuser@example.com",
        "password": "SecurePass123!",
    }

    # Act
    response = await test_client.post("/api/auth/register", json=registration_data)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert "user" in data
    assert "access_token" in data
    assert data["access_token"]  # Token should not be empty
    assert data["user"]["email"] == registration_data["email"]
    assert data["user"]["name"] == registration_data["name"]
    assert "password" not in data["user"]  # Password should not be returned


@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_registration_duplicate_email(
    test_client: AsyncClient, test_user: User
):
    """Test registration with duplicate email fails."""
    # Arrange
    registration_data = {
        "name": "Another User",
        "email": test_user.email,  # Duplicate email
        "password": "SecurePass123!",
    }

    # Act
    response = await test_client.post("/api/auth/register", json=registration_data)

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already registered" in data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_registration_invalid_email(test_client: AsyncClient):
    """Test registration with invalid email format fails."""
    # Arrange
    registration_data = {
        "name": "New User",
        "email": "invalid-email",  # Invalid email format
        "password": "SecurePass123!",
    }

    # Act
    response = await test_client.post("/api/auth/register", json=registration_data)

    # Assert
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_login_success(test_client: AsyncClient, test_user: User):
    """Test successful user login."""
    # Note: test_user fixture doesn't set password, so we need to register first
    registration_data = {
        "name": "Login Test User",
        "email": "logintest@example.com",
        "password": "SecurePass123!",
    }
    await test_client.post("/api/auth/register", json=registration_data)

    # Act - Now login with that user
    login_data = {
        "email": "logintest@example.com",
        "password": "SecurePass123!",
    }
    response = await test_client.post("/api/auth/login", json=login_data)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "user" in data
    assert data["user"]["email"] == login_data["email"]
    assert len(data["access_token"]) > 0  # Token should not be empty


@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_login_wrong_password(test_client: AsyncClient):
    """Test login with wrong password fails."""
    # Arrange - Register a user first
    registration_data = {
        "name": "Test User",
        "email": "wrongpass@example.com",
        "password": "CorrectPass123!",
    }
    await test_client.post("/api/auth/register", json=registration_data)

    # Act - Login with wrong password
    login_data = {
        "email": "wrongpass@example.com",
        "password": "WrongPassword123!",
    }
    response = await test_client.post("/api/auth/login", json=login_data)

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_login_nonexistent_user(test_client: AsyncClient):
    """Test login with non-existent user fails."""
    # Arrange
    login_data = {
        "email": "nonexistent@example.com",
        "password": "SomePassword123!",
    }

    # Act
    response = await test_client.post("/api/auth/login", json=login_data)

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_current_user_authenticated(test_client: AsyncClient, auth_token: str):
    """Test getting current user with valid token."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Act
    response = await test_client.get("/api/auth/me", headers=headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "id" in data
    assert "name" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_current_user_no_token(test_client: AsyncClient):
    """Test getting current user without token fails."""
    # Act
    response = await test_client.get("/api/auth/me")

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_current_user_invalid_token(test_client: AsyncClient):
    """Test getting current user with invalid token fails."""
    # Arrange
    headers = {"Authorization": "Bearer invalid-token-here"}

    # Act
    response = await test_client.get("/api/auth/me", headers=headers)

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_current_user_not_found(test_client: AsyncClient):
    """Test getting current user fails if user ID in token does not exist."""
    # Arrange: Create a token for a non-existent user ID
    from app.services.auth_service import create_access_token
    non_existent_user_id = "non-existent-user-123"
    token, _ = create_access_token(non_existent_user_id, "nonexistent@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Act
    response = await test_client.get("/api/auth/me", headers=headers)

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "User not found" in data["detail"]
