"""
Authentication API endpoints.

This module provides REST API endpoints for user registration and login.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.middleware.auth import get_current_user_id
from app.schemas.auth import AuthResponse, TokenResponse, UserCreate, UserLogin, UserResponse
from app.services import auth_service


router = APIRouter(tags=["authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email and password",
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_session),
) -> TokenResponse:
    """
    Register a new user account.

    Args:
        user_data: User registration data (email, password, optional name)
        db: Database session

    Returns:
        TokenResponse with JWT token and user information

    Raises:
        HTTPException 400: If email is already registered
        HTTPException 422: If validation fails
    """
    try:
        # Create user
        user = await auth_service.create_user(db, user_data)

        # Generate JWT token
        token, expires_at = auth_service.create_access_token(user.id, user.email)

        # Calculate expiration in seconds
        expires_in = auth_service.ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=expires_in,
            user=UserResponse.model_validate(user),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user with email and password, receive JWT token",
)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_session),
) -> TokenResponse:
    """
    Authenticate user and return JWT token.

    Args:
        login_data: Login credentials (email, password)
        db: Database session

    Returns:
        TokenResponse with JWT token and user information

    Raises:
        HTTPException 401: If credentials are invalid
    """
    result = await auth_service.authenticate_user(db, login_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user, token = result

    # Calculate expiration in seconds
    expires_in = auth_service.ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in,
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get authenticated user's profile information",
)
async def get_me(
    db: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
) -> UserResponse:
    """
    Get current authenticated user's information.

    Args:
        db: Database session
        user_id: Current user ID from JWT token

    Returns:
        UserResponse with user profile data

    Raises:
        HTTPException 401: If token is invalid
        HTTPException 404: If user not found
    """
    user = await auth_service.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(user)
