"""
Authentication request and response schemas.

This module defines Pydantic models for user registration,
login, and authentication responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """User registration request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ..., min_length=8, max_length=100, description="Password (min 8 characters)"
    )
    name: Optional[str] = Field(None, max_length=255, description="User display name")


class UserLogin(BaseModel):
    """User login request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """User information response (no sensitive data)."""

    id: str
    email: str
    email_verified: bool
    name: Optional[str] = None
    image: Optional[str] = None
    created_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user: UserResponse = Field(..., description="Authenticated user information")


class AuthResponse(BaseModel):
    """Authentication response with user and token."""

    user: UserResponse
    session: dict[str, str]  # Session information from Better Auth
