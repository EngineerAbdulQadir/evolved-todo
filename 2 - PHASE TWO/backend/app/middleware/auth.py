"""
JWT authentication middleware and dependencies.

This module provides JWT token validation and user authentication
for protected API endpoints.
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.settings import settings

# JWT configuration from settings
BETTER_AUTH_SECRET = settings.better_auth_secret
JWT_ALGORITHM = "HS256"

security = HTTPBearer()


class TokenPayload(BaseModel):
    """JWT token payload structure."""

    sub: str  # Subject (user_id)
    email: str
    exp: int  # Expiration timestamp
    iat: int  # Issued at timestamp


def decode_jwt_token(token: str) -> TokenPayload:
    """
    Decode and validate JWT token.

    Args:
        token: JWT token string

    Returns:
        TokenPayload with user information

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
        return TokenPayload(**payload)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenPayload:
    """
    Dependency to extract and validate current user from JWT token.

    Usage:
        @app.get("/protected")
        async def protected_route(user: TokenPayload = Depends(get_current_user)):
            return {"user_id": user.sub}

    Args:
        credentials: HTTP Authorization header with Bearer token

    Returns:
        TokenPayload with authenticated user information

    Raises:
        HTTPException: If token is missing, invalid, or expired (401)
    """
    token = credentials.credentials
    return decode_jwt_token(token)


async def get_current_user_id(
    user: TokenPayload = Depends(get_current_user),
) -> str:
    """
    Dependency to extract just the user_id from JWT token.

    Args:
        user: Token payload from get_current_user

    Returns:
        User ID string
    """
    return user.sub


def validate_user_ownership(user_id_from_path: str, current_user_id: str) -> None:
    """
    Validate that the user_id in the path matches the authenticated user.

    This prevents users from accessing other users' data.

    Args:
        user_id_from_path: User ID from URL path parameter
        current_user_id: Authenticated user ID from JWT token

    Raises:
        HTTPException: If user IDs don't match (403 Forbidden)
    """
    if user_id_from_path != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own data",
        )
