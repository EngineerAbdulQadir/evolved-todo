# Authentication Flow: Phase 2 - Full-Stack Web Application

**Branch**: `002-phase2-web-app` | **Date**: 2025-12-10 | **Plan**: [../plan.md](../plan.md)

---

## Overview

Phase 2 uses **Better Auth** (Next.js) for user authentication and **JWT tokens** for API authorization. Both frontend (Better Auth) and backend (FastAPI) share the same secret key to verify tokens.

**Authentication Method**: JWT (JSON Web Tokens)
**Token Lifetime**: 7 days
**Token Algorithm**: HS256 (HMAC with SHA-256)
**Shared Secret**: `BETTER_AUTH_SECRET` (min 32 characters)

---

## Architecture

```
┌─────────────┐          ┌──────────────┐          ┌─────────────┐
│   Browser   │          │  Next.js     │          │  FastAPI    │
│  (Frontend) │          │ (Better Auth)│          │  (Backend)  │
└──────┬──────┘          └──────┬───────┘          └──────┬──────┘
       │                        │                         │
       │  1. Register/Login     │                         │
       ├───────────────────────>│                         │
       │                        │                         │
       │  2. JWT Token          │                         │
       │<───────────────────────┤                         │
       │                        │                         │
       │  3. API Request        │                         │
       │   (with JWT in header) │                         │
       ├─────────────────────────────────────────────────>│
       │                        │                         │
       │                        │  4. Validate JWT        │
       │                        │     (shared secret)     │
       │                        │                         │
       │  5. Response (200 OK)  │                         │
       │<─────────────────────────────────────────────────┤
       │                        │                         │
```

---

## User Registration Flow

### Step 1: User Submits Registration Form

**Frontend** (`/register` page):
```http
POST http://localhost:3000/api/auth/register
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "name": "John Doe"
}
```

### Step 2: Better Auth Creates User

**Better Auth**:
1. Validates email format and password strength
2. Hashes password with bcrypt (cost factor: 12)
3. Creates user record in `users` table (Neon PostgreSQL)
4. Generates JWT token with user info

**Database Insert**:
```sql
INSERT INTO users (email, password_hash, name, created_at, updated_at)
VALUES ('john@example.com', '$2b$12$...', 'John Doe', NOW(), NOW())
RETURNING id;
```

### Step 3: Better Auth Returns JWT Token

**Response (200 OK)**:
```json
{
  "user": {
    "id": 1,
    "email": "john@example.com",
    "name": "John Doe"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": "7d"
}
```

### Step 4: Frontend Stores Token

**Storage Options**:
1. **HTTP-only Cookie** (recommended for security)
   - Better Auth sets cookie automatically
   - Inaccessible to JavaScript (XSS protection)
   - Sent with every request to same origin

2. **localStorage** (alternative, less secure)
   - Frontend stores token manually
   - Accessible to JavaScript (XSS risk)
   - Must be included in Authorization header manually

**Better Auth Default**: HTTP-only cookie

---

## User Login Flow

### Step 1: User Submits Login Form

**Frontend** (`/login` page):
```http
POST http://localhost:3000/api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

### Step 2: Better Auth Validates Credentials

**Better Auth**:
1. Queries `users` table for email
   ```sql
   SELECT id, password_hash FROM users WHERE email = 'john@example.com';
   ```
2. Compares submitted password with stored hash (bcrypt)
3. If valid, generates JWT token

### Step 3: Better Auth Returns JWT Token

**Response (200 OK)**:
```json
{
  "user": {
    "id": 1,
    "email": "john@example.com",
    "name": "John Doe"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": "7d"
}
```

**Response (401 Unauthorized)** - Invalid Credentials:
```json
{
  "error": "Invalid credentials",
  "detail": "Email or password is incorrect"
}
```

### Step 4: Frontend Stores Token

Same as registration (HTTP-only cookie or localStorage).

---

## JWT Token Structure

### Token Format

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImVtYWlsIjoiam9obkBleGFtcGxlLmNvbSIsImlhdCI6MTczMzc0MDAwMCwiZXhwIjoxNzM0MzQ0ODB9.signature
```

**Parts**:
1. **Header** (Base64 encoded)
2. **Payload** (Base64 encoded)
3. **Signature** (HMAC-SHA256)

### Decoded Token

**Header**:
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload**:
```json
{
  "sub": 1,  // User ID (subject)
  "email": "john@example.com",
  "iat": 1733740000,  // Issued at (timestamp)
  "exp": 1734344800   // Expires at (timestamp, +7 days)
}
```

**Signature**:
```
HMAC-SHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  BETTER_AUTH_SECRET
)
```

### Claims

| **Claim** | **Type** | **Description** |
|-----------|----------|-----------------|
| `sub` | integer | User ID (primary key from `users` table) |
| `email` | string | User email |
| `iat` | integer | Issued At timestamp (Unix epoch) |
| `exp` | integer | Expiration timestamp (Unix epoch, +7 days) |

**Note**: Token does not contain password or sensitive data.

---

## API Authorization Flow

### Step 1: Frontend Makes API Request

**Frontend** (axios client):
```http
GET http://localhost:8000/api/1/tasks
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**JavaScript** (axios interceptor):
```javascript
axios.interceptors.request.use((config) => {
  const token = getTokenFromCookie() // or localStorage
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

### Step 2: Backend Extracts JWT

**FastAPI Middleware** (`app/middleware/auth.py`):
```python
from fastapi import Header, HTTPException

async def get_current_user(
    authorization: str = Header(None),
    session: AsyncSession = Depends(get_session)
) -> User:
    # Step 1: Extract token from header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = authorization.split(" ")[1]

    # Step 2: Decode and validate JWT
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Step 3: Extract user_id from payload
    user_id: int = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Step 4: Fetch user from database
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
```

### Step 3: Backend Validates User Permission

**API Route** (`app/api/tasks.py`):
```python
@router.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    # Verify user_id in path matches authenticated user
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # User is authorized, proceed with query
    tasks = await task_service.get_user_tasks(session, user_id)
    return tasks
```

### Step 4: Backend Returns Response

**Response (200 OK)**:
```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "Buy groceries",
    "completed": false,
    ...
  }
]
```

---

## Token Expiration & Refresh

### Token Lifetime

- **Expiration**: 7 days from issue
- **Refresh Tokens**: Not implemented in Phase 2
- **Behavior**: Users must re-login after 7 days

### Handling Expired Tokens

**Backend Response (401 Unauthorized)**:
```json
{
  "error": "Unauthorized",
  "detail": "Token expired"
}
```

**Frontend Behavior**:
1. Detect 401 response in axios interceptor
2. Clear stored token
3. Redirect to `/login`
4. Show message: "Session expired, please login again"

---

## Logout Flow

### Step 1: User Clicks Logout

**Frontend**:
```http
POST http://localhost:3000/api/auth/logout
```

### Step 2: Better Auth Clears Cookie

**Better Auth**:
1. Invalidates session cookie
2. Returns success response

**Response (200 OK)**:
```json
{
  "success": true
}
```

### Step 3: Frontend Clears Local State

**Frontend**:
1. Clear token from localStorage (if used)
2. Clear user state
3. Redirect to `/login`

**Note**: JWT tokens are stateless (not stored server-side), so logout only clears client-side storage. Token remains valid until expiration.

---

## Security Considerations

### Password Security

- **Hashing**: bcrypt with cost factor 12
- **Minimum Length**: 8 characters (enforced by Better Auth)
- **Strength**: Must include uppercase, lowercase, number, special char (configurable)

### JWT Security

- **Secret Key**: Minimum 32 characters, randomly generated
- **Algorithm**: HS256 (symmetric, shared secret)
- **Storage**: HTTP-only cookies (XSS protection)
- **Transport**: HTTPS in production (TLS encryption)

### Attack Prevention

**XSS (Cross-Site Scripting)**:
- HTTP-only cookies prevent JavaScript access to tokens
- Input sanitization on frontend forms

**CSRF (Cross-Site Request Forgery)**:
- SameSite cookie attribute (`Strict` or `Lax`)
- CORS policy restricts origins

**Token Theft**:
- HTTPS prevents man-in-the-middle attacks
- Short token lifetime (7 days) limits exposure

**Brute Force**:
- Rate limiting on login endpoint (Phase 3+)
- Account lockout after N failed attempts (Phase 3+)

---

## Environment Variables

### Frontend (.env.local)

```bash
BETTER_AUTH_SECRET=your-secret-key-min-32-chars-long
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=postgresql://user:password@neon-host/evolved_todo?sslmode=require
```

### Backend (.env)

```bash
BETTER_AUTH_SECRET=your-secret-key-min-32-chars-long  # Must match frontend!
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_DAYS=7
```

**CRITICAL**: `BETTER_AUTH_SECRET` must be identical in both `.env` files!

---

## Testing Authentication

### Test User Registration

```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Password123!",
    "name": "Test User"
  }'
```

### Test User Login

```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Password123!"
  }'
```

**Expected Response**:
```json
{
  "user": { "id": 1, "email": "test@example.com", "name": "Test User" },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": "7d"
}
```

### Test Authenticated API Request

```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://localhost:8000/api/1/tasks \
  -H "Authorization: Bearer $TOKEN"
```

### Test Invalid Token

```bash
curl -X GET http://localhost:8000/api/1/tasks \
  -H "Authorization: Bearer invalid-token"
```

**Expected Response (401)**:
```json
{
  "error": "Unauthorized",
  "detail": "Invalid token"
}
```

---

## Better Auth Configuration

**Frontend** (`lib/auth.ts`):
```typescript
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  database: {
    connectionString: process.env.DATABASE_URL!,
    type: "postgres"
  },
  secret: process.env.BETTER_AUTH_SECRET!,
  jwt: {
    expiresIn: "7d"
  },
  session: {
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60 * 1000 // 5 minutes
    }
  }
})
```

---

## Future Enhancements (Phase 3+)

1. **Refresh Tokens**: Long-lived refresh tokens for seamless re-authentication
2. **OAuth Providers**: Google, GitHub login
3. **Two-Factor Authentication (2FA)**: TOTP or SMS codes
4. **Password Reset**: Email-based password recovery
5. **Email Verification**: Verify email before account activation
6. **Session Management**: View and revoke active sessions
7. **Rate Limiting**: Throttle login attempts

---

**Next Steps**:
1. ✅ Authentication flow documented
2. → Review [request-schemas.md](./request-schemas.md) for detailed request formats
3. → Review [response-schemas.md](./response-schemas.md) for detailed response formats
4. → Review [api-endpoints.md](./api-endpoints.md) for all API endpoints
