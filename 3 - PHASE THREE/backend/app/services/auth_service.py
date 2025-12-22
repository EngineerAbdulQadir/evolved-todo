"""
Authentication service with user management and JWT utilities.

This module provides functions for user registration, login,
password hashing, and JWT token generation.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import jwt
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.settings import settings
from app.models.user import Account, Session, User
from app.schemas.auth import UserCreate, UserLogin, UserResponse

# Authentication configuration from settings
BETTER_AUTH_SECRET = settings.better_auth_secret
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Args:
        password: Plain-text password

    Returns:
        Bcrypt password hash (as string)

    Note:
        Bcrypt has a 72-byte limit. Passwords are automatically truncated
        to 72 bytes before hashing to comply with this limitation.
    """
    # Truncate password to 72 bytes (bcrypt limitation)
    password_bytes = password.encode('utf-8')[:72]

    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return as string (bcrypt returns bytes)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain-text password to verify
        hashed_password: Bcrypt hash to compare against (as string)

    Returns:
        True if password matches, False otherwise

    Note:
        Password is truncated to 72 bytes to match the hashing behavior.
    """
    # Truncate password to 72 bytes (same as hash_password)
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')

    # Verify using bcrypt
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(user_id: str, email: str) -> tuple[str, datetime]:
    """
    Create JWT access token for authenticated user.

    Args:
        user_id: User's unique identifier
        email: User's email address

    Returns:
        Tuple of (JWT token string, expiration datetime)
    """
    expires_delta = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    expire = datetime.utcnow() + expires_delta

    to_encode = {
        "sub": user_id,  # Subject (user ID)
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    encoded_jwt = jwt.encode(
        to_encode,
        BETTER_AUTH_SECRET,
        algorithm=JWT_ALGORITHM,
    )

    return encoded_jwt, expire


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Retrieve user by email address.

    Args:
        db: Database session
        email: User's email address

    Returns:
        User object if found, None otherwise
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    """
    Retrieve user by ID.

    Args:
        db: Database session
        user_id: User's unique identifier

    Returns:
        User object if found, None otherwise
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """
    Create a new user account with hashed password.

    Args:
        db: Database session
        user_data: User registration data

    Returns:
        Created User object

    Raises:
        ValueError: If email already exists
    """
    # Check if user already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise ValueError("Email already registered")

    # Generate user ID
    user_id = f"user_{secrets.token_urlsafe(16)}"

    # Create user
    new_user = User(
        id=user_id,
        email=user_data.email,
        name=user_data.name,
        email_verified=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_user)

    # Flush to insert user first (ensures user exists before account insertion)
    await db.flush()

    # Create account with hashed password
    account_id = f"account_{secrets.token_urlsafe(16)}"
    new_account = Account(
        id=account_id,
        user_id=user_id,
        account_id=user_data.email,  # Email as account identifier
        provider_id="credential",  # Email/password provider
        password=hash_password(user_data.password),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_account)

    await db.commit()
    await db.refresh(new_user)

    return new_user


async def authenticate_user(
    db: AsyncSession, login_data: UserLogin
) -> Optional[tuple[User, str]]:
    """
    Authenticate user with email and password.

    Args:
        db: Database session
        login_data: Login credentials

    Returns:
        Tuple of (User, JWT token) if authentication successful, None otherwise
    """
    # Get user by email
    user = await get_user_by_email(db, login_data.email)
    if not user:
        return None

    # Get account with password
    result = await db.execute(
        select(Account).where(
            Account.user_id == user.id, Account.provider_id == "credential"
        )
    )
    account = result.scalar_one_or_none()

    if not account or not account.password:
        return None

    # Verify password
    if not verify_password(login_data.password, account.password):
        return None

    # Generate JWT token
    token, expires_at = create_access_token(user.id, user.email)

    # Create session
    session_id = f"session_{secrets.token_urlsafe(16)}"
    new_session = Session(
        id=session_id,
        user_id=user.id,
        session_token=token,
        expires_at=expires_at,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_session)
    await db.commit()

    return user, token
