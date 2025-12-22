---
name: jwt-validation
description: JWT token validation patterns, signature verification, payload extraction, and error handling.
---

# JWT Validation

## Instructions

### When to Use

- Validating JWT tokens in API requests
- Extracting user information from tokens
- Implementing authentication middleware
- Handling token expiration
- Verifying token signatures
- Managing token security

## JWT Structure

A JWT consists of three parts separated by dots:

```
header.payload.signature
```

Example:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEyMywi ZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwiaWF0IjoxNzA0MDY3MjAwLCJleHAiOjE3MDQ2NzIwMDB9.signature_here
```

**Header:**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload:**
```json
{
  "sub": 123,
  "email": "user@example.com",
  "iat": 1704067200,
  "exp": 1704672000
}
```

**Signature:**
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret
)
```

## Python JWT Validation (FastAPI)

### Installation

```bash
uv add pyjwt[crypto]
```

### Basic JWT Utilities

```python
# app/auth/jwt.py
import jwt
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, ValidationError
import os

# Load secret from environment
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
if not SECRET_KEY:
    raise ValueError("BETTER_AUTH_SECRET environment variable not set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

class TokenPayload(BaseModel):
    """JWT token payload structure."""
    sub: int  # User ID
    email: str
    exp: int  # Expiration timestamp
    iat: int  # Issued at timestamp

    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.utcnow().timestamp() > self.exp

def create_access_token(user_id: int, email: str) -> str:
    """
    Create a JWT access token.

    Args:
        user_id: User ID
        email: User email

    Returns:
        JWT token string
    """
    now = datetime.utcnow()
    exp = now + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": user_id,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_access_token(token: str) -> Optional[TokenPayload]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        TokenPayload if valid, None if invalid or expired
    """
    try:
        # Decode and verify signature
        payload_dict = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "require_exp": True,
                "require_iat": True,
            }
        )

        # Validate payload structure with Pydantic
        payload = TokenPayload(**payload_dict)
        return payload

    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Token is invalid (wrong signature, malformed, etc.)
        return None
    except ValidationError:
        # Payload doesn't match expected structure
        return None
    except Exception:
        # Unexpected error
        return None
```

### FastAPI Authentication Dependency

```python
# app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.auth.jwt import decode_access_token, TokenPayload

# HTTP Bearer scheme for Authorization header
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenPayload:
    """
    Validate JWT token and return current user.

    Extracts token from Authorization: Bearer <token> header.

    Args:
        credentials: HTTP Bearer credentials from request

    Returns:
        Token payload with user information

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[TokenPayload]:
    """
    Optional authentication - returns None if no token provided.

    Use this for endpoints that work with or without authentication.
    """
    if credentials is None:
        return None

    token = credentials.credentials
    return decode_access_token(token)
```

### Protected Routes

```python
# app/api/routes/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.auth.jwt import TokenPayload
from app.schemas.task import TaskCreate, TaskResponse
from app.services.task_service import TaskService

router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    user_id: int,
    task_data: TaskCreate,
    current_user: TokenPayload = Depends(get_current_user),  # Requires auth
    task_service: TaskService = Depends()
) -> TaskResponse:
    """
    Create a new task.

    Requires authentication. User can only create tasks for themselves.
    """
    # Verify user_id matches authenticated user
    if current_user.sub != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's tasks"
        )

    task = await task_service.create_task(user_id, task_data)
    return TaskResponse.model_validate(task)

@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    user_id: int,
    current_user: TokenPayload = Depends(get_current_user),
    task_service: TaskService = Depends()
) -> List[TaskResponse]:
    """List tasks for authenticated user."""
    # User isolation - verify access
    if current_user.sub != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's tasks"
        )

    tasks = await task_service.get_tasks(user_id)
    return [TaskResponse.model_validate(task) for task in tasks]
```

## Error Handling

### Comprehensive Error Messages

```python
# app/auth/jwt.py
from enum import Enum

class TokenError(Enum):
    """Token validation error types."""
    EXPIRED = "Token has expired"
    INVALID_SIGNATURE = "Invalid token signature"
    MALFORMED = "Token is malformed"
    MISSING_CLAIMS = "Token missing required claims"
    INVALID_STRUCTURE = "Token payload has invalid structure"

def decode_access_token_detailed(
    token: str
) -> tuple[Optional[TokenPayload], Optional[TokenError]]:
    """
    Decode token with detailed error information.

    Returns:
        Tuple of (payload, error)
        - If successful: (payload, None)
        - If failed: (None, error_type)
    """
    try:
        payload_dict = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
            }
        )

        payload = TokenPayload(**payload_dict)
        return payload, None

    except jwt.ExpiredSignatureError:
        return None, TokenError.EXPIRED

    except jwt.InvalidSignatureError:
        return None, TokenError.INVALID_SIGNATURE

    except jwt.DecodeError:
        return None, TokenError.MALFORMED

    except jwt.MissingRequiredClaimError:
        return None, TokenError.MISSING_CLAIMS

    except ValidationError:
        return None, TokenError.INVALID_STRUCTURE

    except Exception:
        return None, TokenError.MALFORMED
```

## Token Refresh Pattern

### Refresh Token Implementation

```python
# app/auth/jwt.py
REFRESH_TOKEN_EXPIRE_DAYS = 30

def create_refresh_token(user_id: int) -> str:
    """Create a refresh token with longer expiration."""
    now = datetime.utcnow()
    exp = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": user_id,
        "type": "refresh",  # Mark as refresh token
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_refresh_token(token: str) -> Optional[int]:
    """
    Decode refresh token and return user ID.

    Returns:
        User ID if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            return None

        return payload.get("sub")

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

# app/api/routes/auth.py
@router.post("/refresh")
async def refresh_access_token(
    refresh_token: str,
    user_service: UserService = Depends()
) -> dict:
    """
    Get new access token using refresh token.
    """
    user_id = decode_refresh_token(refresh_token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Get user from database
    user = await user_service.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # Create new access token
    access_token = create_access_token(user.id, user.email)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
```

## Security Best Practices

### 1. Secret Management

```python
# ✅ Good: Load from environment
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
if not SECRET_KEY:
    raise ValueError("Secret key not set")

# ❌ Bad: Hardcoded secret
SECRET_KEY = "my-secret-key-123"
```

### 2. Signature Verification

```python
# ✅ Good: Always verify signature
payload = jwt.decode(
    token,
    SECRET_KEY,
    algorithms=[ALGORITHM],
    options={"verify_signature": True}
)

# ❌ Bad: Skip verification (NEVER DO THIS)
payload = jwt.decode(
    token,
    options={"verify_signature": False}
)
```

### 3. Token Expiration

```python
# ✅ Good: Set reasonable expiration
ACCESS_TOKEN_EXPIRE_DAYS = 7

# ❌ Bad: No expiration or very long
ACCESS_TOKEN_EXPIRE_DAYS = 365
```

### 4. User Isolation

```python
# ✅ Good: Always verify user_id matches token
if current_user.sub != user_id:
    raise HTTPException(status_code=403)

# ❌ Bad: Trust user_id from path without verification
tasks = await get_tasks(user_id)  # Anyone can access any user's data!
```

## Testing JWT Validation

```python
# tests/test_jwt.py
import pytest
from datetime import datetime, timedelta
import jwt

from app.auth.jwt import (
    create_access_token,
    decode_access_token,
    SECRET_KEY,
    ALGORITHM
)

def test_create_and_decode_token():
    """Test creating and decoding valid token."""
    token = create_access_token(user_id=1, email="user@example.com")
    payload = decode_access_token(token)

    assert payload is not None
    assert payload.sub == 1
    assert payload.email == "user@example.com"

def test_expired_token():
    """Test that expired tokens are rejected."""
    # Create expired token
    exp = datetime.utcnow() - timedelta(days=1)  # 1 day ago
    payload_dict = {
        "sub": 1,
        "email": "user@example.com",
        "iat": int(datetime.utcnow().timestamp()),
        "exp": int(exp.timestamp()),
    }

    expired_token = jwt.encode(payload_dict, SECRET_KEY, algorithm=ALGORITHM)

    # Verify it's rejected
    payload = decode_access_token(expired_token)
    assert payload is None

def test_invalid_signature():
    """Test that tokens with wrong signature are rejected."""
    # Create token with different secret
    wrong_token = jwt.encode(
        {"sub": 1, "email": "user@example.com"},
        "wrong-secret",
        algorithm=ALGORITHM
    )

    # Verify it's rejected
    payload = decode_access_token(wrong_token)
    assert payload is None

def test_malformed_token():
    """Test that malformed tokens are rejected."""
    malformed_token = "not.a.valid.jwt.token"

    payload = decode_access_token(malformed_token)
    assert payload is None

def test_protected_endpoint(client, auth_headers):
    """Test accessing protected endpoint with valid token."""
    response = client.get("/api/1/tasks", headers=auth_headers)
    assert response.status_code == 200

def test_protected_endpoint_without_token(client):
    """Test that protected endpoint requires authentication."""
    response = client.get("/api/1/tasks")
    assert response.status_code == 401
```

## Integration with auth-specialist Subagent

This skill is primarily used by:
- **auth-specialist** - For implementing JWT validation
- **backend-api-dev** - For protecting API routes

### Key Principles

1. **Always Verify Signature** - Never skip signature verification
2. **Check Expiration** - Validate exp claim
3. **User Isolation** - Verify user_id matches token sub
4. **Secure Secrets** - Load from environment, never hardcode
5. **Error Handling** - Return 401 for invalid/expired tokens
6. **Token Structure** - Validate payload with Pydantic models
