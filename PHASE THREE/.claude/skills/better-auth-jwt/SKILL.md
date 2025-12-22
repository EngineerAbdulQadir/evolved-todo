# Better Auth JWT Integration

**Skill**: better-auth-jwt
**Version**: 1.0.0
**Primary Users**: auth-specialist  
**Prerequisites**: Better Auth, JWT, FastAPI

## Purpose
Integrate Better Auth JWT authentication with shared secret management, token validation, and user isolation between Next.js frontend and FastAPI backend.

## Core Patterns

### JWT Token Validation
```python
import jwt
from fastapi import HTTPException, Header
from typing import Annotated

BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

async def verify_token(authorization: Annotated[str, Header()]) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid authorization header")
    
    token = authorization[7:]
    try:
        payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")
```

### FastAPI Dependency
```python
@app.post("/api/{user_id}/chat")
async def chat(
    user_id: str,
    token_user_id: str = Depends(verify_token)
):
    if user_id != token_user_id:
        raise HTTPException(403, "Access denied")
    # Process request
```

### Frontend Token Injection
```typescript
// frontend/lib/api-client.ts
const getAuthToken = () => {
  // Better Auth stores token in cookie/localStorage
  return localStorage.getItem('auth_token');
};

export async function sendChatMessage(message: string) {
  const token = getAuthToken();
  const response = await fetch('/api/user123/chat', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message })
  });
  return response.json();
}
```

### Shared Secret Configuration
```bash
# .env (both frontend and backend)
BETTER_AUTH_SECRET=your-32-character-hex-secret
```

## Best Practices
- BETTER_AUTH_SECRET must be identical in frontend and backend
- Always verify path parameter user_id matches JWT user_id
- Return 401 for invalid/expired tokens
- Return 403 for unauthorized access to resources
- Use HTTPS in production
- Token expiry: 7 days (configurable in Better Auth)

## User Data Isolation Pattern
```python
async def get_user_resource(user_id: str, resource_id: int, session: AsyncSession):
    result = await session.exec(
        select(Resource)
        .where(Resource.id == resource_id, Resource.user_id == user_id)
    )
    resource = result.first()
    if not resource:
        raise HTTPException(404, "Resource not found or access denied")
    return resource
```

## Related Skills
jwt-validation, security, fastapi-sqlmodel

See examples.md for complete authentication flows.
