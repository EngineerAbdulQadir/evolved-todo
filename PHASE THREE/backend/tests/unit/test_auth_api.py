import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from app.api.auth import register, login, get_me
from app.schemas.auth import UserCreate, UserLogin


@pytest.mark.asyncio
async def test_register_success():
    """Test successful user registration."""
    mock_db = AsyncMock()

    # Mock user data - need to ensure it passes validation
    user_create_data = UserCreate(
        email="test@example.com",
        password="password123",
        name="Test User"
    )

    # Mock user object - need to include all required fields for UserResponse
    mock_user = MagicMock()
    mock_user.id = "user_123"
    mock_user.email = "test@example.com"
    mock_user.email_verified = False
    mock_user.name = "Test User"
    mock_user.image = None
    mock_user.hashed_password = "hashed_password"
    mock_user.created_at = datetime.utcnow()
    mock_user.updated_at = datetime.utcnow()

    # Mock auth service
    with patch('app.api.auth.auth_service.create_user', return_value=mock_user):
        with patch('app.api.auth.auth_service.create_access_token',
                   return_value=("mock_token", "2023-12-31T23:59:59")):
            with patch('app.api.auth.auth_service.ACCESS_TOKEN_EXPIRE_DAYS', 30):
                result = await register(user_create_data, mock_db)

                assert result.access_token == "mock_token"
                assert result.token_type == "bearer"
                assert result.user.email == "test@example.com"
                assert result.user.name == "Test User"


@pytest.mark.asyncio
async def test_register_duplicate_email():
    """Test registration with duplicate email."""
    mock_db = AsyncMock()
    
    user_create_data = UserCreate(
        email="test@example.com",
        password="password123"
    )
    
    # Mock auth service to raise ValueError for duplicate email
    with patch('app.api.auth.auth_service.create_user', side_effect=ValueError("Email already registered")):
        with pytest.raises(HTTPException) as exc_info:
            await register(user_create_data, mock_db)
            
            assert exc_info.value.status_code == 400
            assert "Email already registered" in exc_info.value.detail


@pytest.mark.asyncio
async def test_login_success():
    """Test successful user login."""
    mock_db = AsyncMock()

    login_data = UserLogin(
        email="test@example.com",
        password="password123"
    )

    # Mock user object with all required fields
    mock_user = MagicMock()
    mock_user.id = "user_123"
    mock_user.email = "test@example.com"
    mock_user.email_verified = False
    mock_user.name = "Test User"
    mock_user.image = None
    mock_user.hashed_password = "hashed_password"
    mock_user.created_at = datetime.utcnow()
    mock_user.updated_at = datetime.utcnow()

    # Mock auth service
    with patch('app.api.auth.auth_service.authenticate_user',
               return_value=(mock_user, "mock_token")):
        with patch('app.api.auth.auth_service.ACCESS_TOKEN_EXPIRE_DAYS', 30):
            result = await login(login_data, mock_db)

            assert result.access_token == "mock_token"
            assert result.token_type == "bearer"
            assert result.user.email == "test@example.com"


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    mock_db = AsyncMock()
    
    login_data = UserLogin(
        email="test@example.com",
        password="wrongpassword"
    )
    
    # Mock auth service to return None for invalid credentials
    with patch('app.api.auth.auth_service.authenticate_user', return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            await login(login_data, mock_db)
            
            assert exc_info.value.status_code == 401
            assert "Invalid email or password" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_me_success():
    """Test getting current user profile."""
    mock_db = AsyncMock()
    user_id = "user_123"

    # Mock user object with all required fields
    mock_user = MagicMock()
    mock_user.id = user_id
    mock_user.email = "test@example.com"
    mock_user.email_verified = False
    mock_user.name = "Test User"
    mock_user.image = None
    mock_user.hashed_password = "hashed_password"
    mock_user.created_at = datetime.utcnow()
    mock_user.updated_at = datetime.utcnow()

    # Mock auth service
    with patch('app.api.auth.auth_service.get_user_by_id', return_value=mock_user):
        result = await get_me(mock_db, user_id)

        assert result.id == user_id
        assert result.email == "test@example.com"
        assert result.name == "Test User"


@pytest.mark.asyncio
async def test_get_me_user_not_found():
    """Test getting profile for non-existent user."""
    mock_db = AsyncMock()
    user_id = "user_123"
    
    # Mock auth service to return None for non-existent user
    with patch('app.api.auth.auth_service.get_user_by_id', return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            await get_me(mock_db, user_id)
            
            assert exc_info.value.status_code == 404
            assert "User not found" in exc_info.value.detail