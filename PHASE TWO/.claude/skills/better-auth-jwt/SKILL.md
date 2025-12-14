---
name: better-auth-jwt
description: Better Auth JWT integration, shared secret management, token validation, and authentication flows between Next.js and FastAPI.
---

# Better Auth JWT

## Instructions

### When to Use

- Implementing user registration and login flows
- Setting up JWT token generation and validation
- Configuring shared secrets between frontend and backend
- Implementing authentication middleware
- Handling Authorization headers
- Managing user sessions with JWT tokens

## Architecture Overview

```
┌─────────────────────────────────────────┐
│   Next.js Frontend (Better Auth)       │
│   - Registration/Login forms            │
│   - JWT token storage                   │
│   - Authorization header injection      │
└──────────────┬──────────────────────────┘
               │
               │ JWT Token (HS256)
               │ Authorization: Bearer <token>
               │
               ▼
┌─────────────────────────────────────────┐
│   FastAPI Backend                       │
│   - JWT token validation                │
│   - User extraction from token          │
│   - Protected route middleware          │
└─────────────────────────────────────────┘

Shared Secret: BETTER_AUTH_SECRET
Algorithm: HS256
Expiration: 7 days
```

## JWT Token Structure

```json
{
  "sub": 123,
  "email": "user@example.com",
  "iat": 1704067200,
  "exp": 1704672000
}
```

**Fields:**
- `sub` - Subject (user ID)
- `email` - User email address
- `iat` - Issued at (Unix timestamp)
- `exp` - Expiration time (Unix timestamp)

## Frontend: Better Auth Setup (Next.js)

### Installation

```bash
cd frontend
pnpm add better-auth
```

### Configuration

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"
import { nextCookies } from "better-auth/next-js"

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET!,
  database: {
    provider: "postgresql",
    url: process.env.DATABASE_URL!,
  },
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // Set to true in production
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
  },
  plugins: [nextCookies()],
})

export type Session = typeof auth.$Infer.Session
```

### Environment Variables

```bash
# .env.local (frontend)
BETTER_AUTH_SECRET="your-secret-key-min-32-chars"
DATABASE_URL="postgresql://user:pass@host/db"
BETTER_AUTH_URL="http://localhost:3000"
```

### Registration Component

```typescript
// app/(auth)/register/page.tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { signUp } from '@/lib/auth-client'

export default function RegisterPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    try {
      const { data, error } = await signUp.email({
        email,
        password,
        callbackURL: '/dashboard',
      })

      if (error) {
        setError(error.message)
        return
      }

      // Registration successful
      router.push('/dashboard')
    } catch (err) {
      setError('Registration failed. Please try again.')
    }
  }

  return (
    <div className="max-w-md mx-auto mt-8">
      <h1 className="text-2xl font-bold mb-4">Register</h1>

      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded mb-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm font-medium mb-1">
            Email
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full px-3 py-2 border rounded"
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium mb-1">
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            className="w-full px-3 py-2 border rounded"
          />
        </div>

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
        >
          Register
        </button>
      </form>
    </div>
  )
}
```

### Login Component

```typescript
// app/(auth)/login/page.tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { signIn } from '@/lib/auth-client'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    try {
      const { data, error } = await signIn.email({
        email,
        password,
        callbackURL: '/dashboard',
      })

      if (error) {
        setError(error.message)
        return
      }

      // Login successful
      router.push('/dashboard')
    } catch (err) {
      setError('Login failed. Please try again.')
    }
  }

  return (
    <div className="max-w-md mx-auto mt-8">
      <h1 className="text-2xl font-bold mb-4">Login</h1>

      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded mb-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm font-medium mb-1">
            Email
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full px-3 py-2 border rounded"
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium mb-1">
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full px-3 py-2 border rounded"
          />
        </div>

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
        >
          Login
        </button>
      </form>
    </div>
  )
}
```

### API Client with JWT

```typescript
// lib/api-client.ts
import axios from 'axios'

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add JWT token
apiClient.interceptors.request.use(
  async (config) => {
    // Get session from Better Auth
    const session = await fetch('/api/auth/session').then(res => res.json())

    if (session?.token) {
      config.headers.Authorization = `Bearer ${session.token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Redirect to login on unauthorized
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
```

## Backend: JWT Validation (FastAPI)

### Installation

```bash
cd backend
uv add pyjwt[crypto] python-dotenv
```

### Environment Variables

```python
# .env (backend)
BETTER_AUTH_SECRET="your-secret-key-min-32-chars"  # MUST match frontend
DATABASE_URL="postgresql+asyncpg://user:pass@host/db"
```

### JWT Utilities

```python
# app/auth/jwt.py
import jwt
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

SECRET_KEY = "your-secret-key-min-32-chars"  # Load from env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

class TokenPayload(BaseModel):
    """JWT token payload structure."""
    sub: int  # user_id
    email: str
    exp: int
    iat: int

def create_access_token(user_id: int, email: str) -> str:
    """Create a JWT access token."""
    iat = datetime.utcnow()
    exp = iat + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": user_id,
        "email": email,
        "iat": int(iat.timestamp()),
        "exp": int(exp.timestamp()),
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_access_token(token: str) -> Optional[TokenPayload]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Token is invalid
        return None
```

### Authentication Dependency

```python
# app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.auth.jwt import decode_access_token, TokenPayload

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenPayload:
    """
    Validate JWT token and return current user.

    Raises:
        HTTPException: If token is invalid or expired.
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
    """
    if credentials is None:
        return None

    token = credentials.credentials
    return decode_access_token(token)
```

### Protected Routes

```python
# app/api/routes/tasks.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.api.deps import get_current_user
from app.auth.jwt import TokenPayload
from app.schemas.task import TaskCreate, TaskResponse
from app.services.task_service import TaskService

router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    user_id: int,
    task_data: TaskCreate,
    current_user: TokenPayload = Depends(get_current_user),
    task_service: TaskService = Depends()
) -> TaskResponse:
    """Create a new task (requires authentication)."""

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
    """List all tasks for authenticated user."""

    # Verify user_id matches authenticated user
    if current_user.sub != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's tasks"
        )

    tasks = await task_service.get_tasks(user_id)
    return [TaskResponse.model_validate(task) for task in tasks]
```

## Security Best Practices

### 1. Secret Management

```python
# ✅ Good: Load from environment
import os
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
if not SECRET_KEY:
    raise ValueError("BETTER_AUTH_SECRET environment variable not set")

# ❌ Bad: Hardcoded secret
SECRET_KEY = "my-secret-key-123"
```

### 2. Token Expiration

```python
# ✅ Good: Short expiration with refresh tokens
ACCESS_TOKEN_EXPIRE_DAYS = 7

# ❌ Bad: No expiration or very long expiration
ACCESS_TOKEN_EXPIRE_DAYS = 365
```

### 3. HTTPS Only

```typescript
// ✅ Good: HTTPS in production
const auth = betterAuth({
  // ...
  advanced: {
    useSecureCookies: process.env.NODE_ENV === 'production',
  },
})
```

### 4. User Isolation

```python
# ✅ Good: Always verify user_id matches token
if current_user.sub != user_id:
    raise HTTPException(status_code=403, detail="Not authorized")

# ❌ Bad: Trust user_id from path without verification
tasks = await task_service.get_tasks(user_id)  # Anyone can access any user's tasks!
```

## Testing Authentication

```python
# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient

from app.auth.jwt import create_access_token

def test_protected_route_without_token(client: TestClient):
    """Test that protected routes require authentication."""
    response = client.get("/api/1/tasks")
    assert response.status_code == 401

def test_protected_route_with_valid_token(client: TestClient):
    """Test accessing protected route with valid token."""
    token = create_access_token(user_id=1, email="user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/1/tasks", headers=headers)
    assert response.status_code == 200

def test_protected_route_with_expired_token(client: TestClient):
    """Test that expired tokens are rejected."""
    # Create token that expired 1 day ago
    token = create_access_token(user_id=1, email="user@example.com")
    # Manually set expiration to past (for testing only)

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/1/tasks", headers=headers)
    assert response.status_code == 401
```

## Integration with auth-specialist Subagent

This skill is primarily used by:
- **auth-specialist** - For implementing authentication flows
- **backend-api-dev** - For JWT validation in API routes
- **frontend-react-dev** - For Better Auth integration

### Key Principles

1. **Shared Secret** - BETTER_AUTH_SECRET must match between frontend and backend
2. **Token Structure** - Consistent JWT payload structure (sub, email, iat, exp)
3. **User Isolation** - Always verify user_id matches token sub claim
4. **Secure Storage** - Never hardcode secrets, use environment variables
5. **Expiration** - Tokens expire after 7 days
6. **HTTPS Only** - Use secure cookies in production
