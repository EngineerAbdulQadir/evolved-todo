"""
User model for authentication and multi-user data isolation.

This module defines the User database model using SQLModel ORM
with Better Auth integration.
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """
    User model for authentication and session management.

    Attributes:
        id: Primary key (auto-generated UUID from Better Auth)
        email: User's email address (unique)
        email_verified: Whether email has been verified
        name: User's display name (optional)
        image: Profile image URL (optional)
        created_at: Timestamp when user was created
        updated_at: Timestamp when user was last updated
    """

    __tablename__ = "user"  # Better Auth expects 'user' table name

    id: str = Field(primary_key=True, max_length=255)
    email: str = Field(unique=True, index=True, max_length=255)
    email_verified: bool = Field(default=False)
    name: Optional[str] = Field(default=None, max_length=255)
    image: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Account(SQLModel, table=True):
    """
    Account model for Better Auth credential storage.

    Better Auth uses this table to store password hashes and
    authentication credentials.
    """

    __tablename__ = "account"

    id: str = Field(primary_key=True, max_length=255)
    user_id: str = Field(foreign_key="user.id", index=True, max_length=255)
    account_id: str = Field(max_length=255)
    provider_id: str = Field(max_length=255)
    access_token: Optional[str] = Field(default=None)
    refresh_token: Optional[str] = Field(default=None)
    id_token: Optional[str] = Field(default=None)
    access_token_expires_at: Optional[datetime] = Field(default=None)
    refresh_token_expires_at: Optional[datetime] = Field(default=None)
    scope: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None, max_length=500)  # Hashed password
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Session(SQLModel, table=True):
    """
    Session model for Better Auth session management.

    Stores active user sessions with JWT tokens.
    """

    __tablename__ = "session"

    id: str = Field(primary_key=True, max_length=255)
    user_id: str = Field(foreign_key="user.id", index=True, max_length=255)
    session_token: str = Field(unique=True, max_length=500)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
