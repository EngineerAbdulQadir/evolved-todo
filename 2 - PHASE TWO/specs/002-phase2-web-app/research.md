**Phase 0 Research: Phase 2 - Full-Stack Web Application**

**Branch**: `002-phase2-web-app` | **Date**: 2025-12-10 | **Plan**: [plan.md](./plan.md)

---

## 1. Next.js 16+ App Router Patterns

### Research Question
How should we structure a Next.js 16+ application with App Router for optimal performance, maintainability, and developer experience?

### Options Considered

**Option A: Route Groups for Organization**
- Pros: Clean URL structure, logical grouping, layout inheritance
- Cons: Additional directory nesting
- Use case: `(auth)/` for public routes, `(dashboard)/` for protected routes

**Option B: Flat Route Structure**
- Pros: Simple, fewer directories
- Cons: Harder to apply route-specific layouts, less organized
- Use case: All routes at root level with individual middleware

**Option C: Feature-Based Routes**
- Pros: Clear feature boundaries
- Cons: Can lead to deep nesting
- Use case: `/features/tasks/`, `/features/auth/`

### Decision: **Option A - Route Groups**

**Rationale**:
- Route groups `(auth)` and `(dashboard)` provide clean separation without affecting URLs
- Allows shared layouts per route group (auth layout vs dashboard layout)
- Middleware can be scoped to route groups for authentication
- Aligns with Next.js 16+ best practices

**Implementation Approach**:
```
app/
├── (auth)/
│   ├── login/page.tsx
│   ├── register/page.tsx
│   └── layout.tsx        # Auth-specific layout (no sidebar)
├── (dashboard)/
│   ├── layout.tsx        # Dashboard layout (sidebar, header, auth check)
│   ├── page.tsx          # Main task list
│   └── tasks/[id]/page.tsx
├── api/
│   └── auth/[...all]/route.ts  # Better Auth catch-all
├── layout.tsx            # Root layout
└── globals.css
```

**Server Components Strategy**:
- Default to Server Components for data fetching
- Use Client Components (`'use client'`) only for interactivity (forms, checkboxes, modals)
- Fetch task data in Server Components, pass to Client Components as props

**Data Fetching**:
- Server Components: `fetch()` with caching and revalidation
- Client Components: `useEffect` + API client for dynamic updates
- Mutations: Server Actions or API routes with `revalidatePath()`

---

## 2. FastAPI + SQLModel Best Practices

### Research Question
How should we structure a FastAPI backend with SQLModel ORM for clean architecture, testability, and type safety?

### Options Considered

**Option A: Layered Architecture (Models → Services → Routes)**
- Pros: Clear separation of concerns, testable business logic
- Cons: More boilerplate
- Layers: Models (database), Services (business logic), Routes (HTTP handlers)

**Option B: Feature-Based Modules**
- Pros: Feature isolation, easier to navigate
- Cons: Can lead to code duplication
- Structure: `/features/tasks/`, `/features/auth/`

**Option C: Thin Controllers (Routes call ORM directly)**
- Pros: Less code, faster development
- Cons: Hard to test, business logic mixed with HTTP concerns

### Decision: **Option A - Layered Architecture**

**Rationale**:
- Aligns with Phase 1 CLI architecture (models, services)
- Business logic in services is testable without HTTP layer
- Models focus on database schema, services handle validation and transformations
- Routes are thin HTTP handlers calling services

**Implementation Approach**:
```
app/
├── models/
│   ├── user.py          # SQLModel User (Better Auth integration)
│   └── task.py          # SQLModel Task
├── schemas/
│   ├── task.py          # Pydantic DTOs (TaskCreate, TaskUpdate, TaskResponse)
│   └── auth.py          # Auth request/response schemas
├── services/
│   ├── task_service.py  # CRUD logic, validation, recurrence
│   └── auth_service.py  # JWT validation
├── api/
│   ├── tasks.py         # FastAPI route handlers
│   └── health.py        # Health check
├── core/
│   ├── config.py        # Pydantic BaseSettings
│   ├── database.py      # Async SQLAlchemy engine, session
│   └── security.py      # JWT utilities
└── middleware/
    └── auth.py          # JWT authentication dependency
```

**Dependency Injection**:
```python
# Database session dependency
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

# Use in routes
@router.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    tasks = await task_service.get_user_tasks(session, user_id)
    return tasks
```

**Async Patterns**:
- All database operations use `async`/`await` with `asyncpg`
- Use `AsyncSession` from SQLAlchemy 2.0
- Background tasks for recurrence instance creation (if needed)

---

## 3. Better Auth JWT Implementation

### Research Question
How should we integrate Better Auth for Next.js frontend with custom FastAPI backend for JWT-based authentication?

### Options Considered

**Option A: Better Auth with Custom Backend Adapter**
- Pros: Unified auth library, session management
- Cons: Requires custom adapter implementation
- Implementation: Better Auth generates JWT, FastAPI validates it

**Option B: NextAuth.js**
- Pros: Popular, well-documented
- Cons: Opinionated, requires edge runtime for some features
- Implementation: Similar to Better Auth

**Option C: Custom JWT Implementation**
- Pros: Full control
- Cons: Security risks, reinventing wheel
- Implementation: Manual token generation and validation

### Decision: **Option A - Better Auth with Shared Secret**

**Rationale**:
- Better Auth is modern, lightweight, TypeScript-native
- Supports JWT tokens that can be validated by FastAPI backend
- Shared `BETTER_AUTH_SECRET` enables both frontend and backend to work with same tokens
- Better Auth handles user registration, login, session management
- FastAPI only needs to validate JWT tokens

**Implementation Approach**:

**Frontend (Better Auth)**:
```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  database: {
    // Neon PostgreSQL connection (same as backend)
    connectionString: process.env.DATABASE_URL!
  },
  secret: process.env.BETTER_AUTH_SECRET!,
  jwt: {
    expiresIn: "7d"
  }
})

// API route: app/api/auth/[...all]/route.ts
import { auth } from "@/lib/auth"
export const { GET, POST } = auth.handler()
```

**Backend (FastAPI JWT Validation)**:
```python
# core/security.py
import jwt
from datetime import datetime

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        # Fetch user from database
        return await get_user_by_id(session, user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Token Flow**:
1. User logs in via Better Auth (`/api/auth/login`)
2. Better Auth creates JWT token with user info
3. Frontend stores token (cookie or localStorage)
4. Frontend includes token in `Authorization: Bearer <token>` header
5. FastAPI middleware extracts token, validates signature, fetches user
6. Routes receive authenticated `User` object via dependency injection

**User Model Sharing**:
- Better Auth creates `users` table in PostgreSQL
- FastAPI Task model references `users.id` as foreign key
- Both systems work with same database schema

---

## 4. Neon PostgreSQL Connection Management

### Research Question
How should we configure database connections to Neon Serverless PostgreSQL for optimal performance and reliability?

### Options Considered

**Option A: Connection Pooling with asyncpg**
- Pros: Efficient connection reuse, async support
- Cons: Requires pool configuration
- Implementation: SQLAlchemy async engine with pool settings

**Option B: Direct Connections (No Pooling)**
- Pros: Simple setup
- Cons: Performance issues under load, connection limit exhaustion
- Implementation: New connection per request

**Option C: PgBouncer Proxy**
- Pros: Advanced pooling, connection multiplexing
- Cons: Additional infrastructure, complexity
- Implementation: PgBouncer between app and Neon

### Decision: **Option A - Connection Pooling with asyncpg**

**Rationale**:
- Neon has connection limits (dependent on plan)
- Connection pooling reuses connections efficiently
- asyncpg is fastest PostgreSQL driver for Python
- SQLAlchemy 2.0 has excellent async support

**Implementation Approach**:
```python
# core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")  # postgresql+asyncpg://...

engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set False in production
    pool_size=20,  # Max concurrent connections
    max_overflow=10,  # Extra connections under load
    pool_pre_ping=True,  # Test connections before use
    pool_recycle=3600  # Recycle connections hourly
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

**Connection String**:
```
DATABASE_URL=postgresql+asyncpg://user:pass@neon-host/dbname?sslmode=require
```

**SSL Configuration**:
- Neon requires SSL connections (`sslmode=require`)
- asyncpg handles SSL automatically

**Migration Strategy**:
- Use Alembic for schema migrations
- Run migrations before deployment
- Migrations use same async engine

---

## 5. API Authentication Patterns

### Research Question
How should we implement JWT authentication in FastAPI routes to ensure security and user isolation?

### Options Considered

**Option A: Middleware-Based Auth (Global)**
- Pros: All routes protected by default
- Cons: Hard to exempt public routes
- Implementation: Middleware extracts JWT, attaches user to request

**Option B: Dependency Injection (Per-Route)**
- Pros: Explicit, flexible (some routes public)
- Cons: Must remember to add dependency
- Implementation: `current_user = Depends(get_current_user)`

**Option C: Decorator-Based Auth**
- Pros: Clean syntax
- Cons: Less Pythonic for FastAPI, harder to test
- Implementation: `@require_auth` decorator on routes

### Decision: **Option B - Dependency Injection**

**Rationale**:
- FastAPI's dependency injection is idiomatic
- Routes explicitly declare authentication requirement
- Easy to test (mock the dependency)
- Allows public routes (health check) without special handling

**Implementation Approach**:
```python
# middleware/auth.py
from fastapi import Depends, HTTPException, Header

async def get_current_user(
    authorization: str = Header(None),
    session: AsyncSession = Depends(get_session)
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = authorization.split(" ")[1]
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_id = payload.get("sub")

    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

# api/tasks.py
@router.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # Verify user_id matches authenticated user
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    tasks = await task_service.get_user_tasks(session, user_id)
    return tasks
```

**User Isolation**:
- All task queries filter by `user_id`
- Middleware ensures `current_user.id == user_id` in path
- Return 403 Forbidden if user tries to access another user's tasks

---

## 6. Testing Strategies

### Research Question
How should we structure tests for backend (FastAPI) and frontend (Next.js) to achieve >90% and >80% coverage respectively?

### Backend Testing (pytest)

**Layers to Test**:
1. Models: Database constraints, relationships
2. Services: Business logic, validation, recurrence calculations
3. Routes: HTTP contracts, status codes, authentication

**Testing Approach**:
```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest.fixture
async def test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def session(test_db):
    async with AsyncSession(test_db) as session:
        yield session

@pytest.fixture
def test_user(session):
    user = User(id=1, email="test@example.com")
    session.add(user)
    await session.commit()
    return user

# tests/unit/test_task_service.py
async def test_create_task(session, test_user):
    task_data = TaskCreate(title="Test task", user_id=test_user.id)
    task = await task_service.create_task(session, task_data)
    assert task.id is not None
    assert task.title == "Test task"

# tests/integration/test_api_tasks.py
from httpx import AsyncClient

async def test_get_tasks_requires_auth(client: AsyncClient):
    response = await client.get("/api/1/tasks")
    assert response.status_code == 401

async def test_get_tasks_success(client: AsyncClient, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await client.get("/api/1/tasks", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### Frontend Testing (Jest + React Testing Library)

**Layers to Test**:
1. Components: Rendering, user interactions
2. Hooks: Custom hook logic (useTasks, useAuth)
3. API client: Request formation, error handling

**Testing Approach**:
```typescript
// __tests__/components/TaskList.test.tsx
import { render, screen } from '@testing-library/react'
import { TaskList } from '@/components/tasks/TaskList'

test('renders task list', () => {
  const tasks = [
    { id: 1, title: 'Test task', completed: false }
  ]
  render(<TaskList tasks={tasks} />)
  expect(screen.getByText('Test task')).toBeInTheDocument()
})

test('toggles task completion', async () => {
  const mockToggle = jest.fn()
  render(<TaskItem task={task} onToggle={mockToggle} />)

  const checkbox = screen.getByRole('checkbox')
  fireEvent.click(checkbox)

  expect(mockToggle).toHaveBeenCalledWith(1)
})

// __tests__/lib/api/tasks.test.ts
test('getTasks includes auth header', async () => {
  const mockFetch = jest.fn().mockResolvedValue({
    ok: true,
    json: async () => []
  })
  global.fetch = mockFetch

  await getTasks(1, 'fake-token')

  expect(mockFetch).toHaveBeenCalledWith(
    expect.any(String),
    expect.objectContaining({
      headers: expect.objectContaining({
        'Authorization': 'Bearer fake-token'
      })
    })
  )
})
```

**Coverage Goals**:
- Backend: >90% (enforce with pytest-cov)
- Frontend: >80% (enforce with Jest coverage)
- CI/CD: Fail build if coverage drops below threshold

---

## 7. Monorepo Tooling

### Research Question
How should we manage a monorepo with separate frontend (Node.js) and backend (Python) package managers?

### Options Considered

**Option A: Separate package.json and pyproject.toml (No Monorepo Tool)**
- Pros: Simple, no additional tooling
- Cons: Manual coordination, duplicate scripts
- Structure: `/frontend/package.json`, `/backend/pyproject.toml`

**Option B: npm/pnpm Workspaces**
- Pros: Shared dependencies, unified scripts
- Cons: Python not first-class citizen
- Structure: Root `package.json` with workspaces

**Option C: Turborepo or Nx**
- Pros: Advanced caching, task orchestration
- Cons: Overkill for simple project, learning curve
- Structure: Configured workspace with build pipelines

### Decision: **Option A - Independent Directories**

**Rationale**:
- Frontend and backend have no shared code (different languages)
- Simple project structure is easier to understand
- UV (backend) and npm/pnpm (frontend) are both fast
- CI/CD can run tests in parallel without orchestration tool

**Implementation Approach**:
```
evolved-todo/
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   └── ... (Next.js files)
├── backend/
│   ├── pyproject.toml
│   ├── uv.lock
│   └── ... (FastAPI files)
├── .gitignore
└── README.md
```

**Development Scripts**:
```json
// frontend/package.json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "test": "jest",
    "lint": "next lint"
  }
}
```

```toml
# backend/pyproject.toml
[tool.uv.scripts]
dev = "uvicorn app.main:app --reload"
test = "pytest tests/ --cov=app"
migrate = "alembic upgrade head"
lint = "ruff check app/"
```

**Shared Configuration**:
- Environment variables: `.env.local` (frontend), `.env` (backend)
- Shared secret: `BETTER_AUTH_SECRET` in both environments
- Database URL: Same Neon connection string

---

## 8. Database Migration Strategies

### Research Question
How should we manage database schema changes across development, staging, and production environments?

### Options Considered

**Option A: Alembic (SQLAlchemy Migration Tool)**
- Pros: Auto-generates migrations from models, version control
- Cons: Requires discipline to review generated migrations
- Implementation: `alembic revision --autogenerate -m "Add tasks table"`

**Option B: Manual SQL Scripts**
- Pros: Full control
- Cons: Error-prone, no rollback automation
- Implementation: SQL files applied in order

**Option C: ORM Auto-Create (No Migrations)**
- Pros: Simple
- Cons: Dangerous in production, no history
- Implementation: `Base.metadata.create_all()`

### Decision: **Option A - Alembic**

**Rationale**:
- Alembic is industry standard for SQLAlchemy projects
- Auto-generation from models reduces manual work
- Version control tracks schema evolution
- Supports rollback for failed migrations

**Implementation Approach**:
```bash
# Initial setup
cd backend
alembic init alembic

# Generate migration from models
alembic revision --autogenerate -m "Create users and tasks tables"

# Review generated migration
# Edit alembic/versions/xxx_create_users_and_tasks.py if needed

# Apply migration
alembic upgrade head

# Rollback (if needed)
alembic downgrade -1
```

**Configuration**:
```python
# alembic/env.py
from app.models import Base
from app.core.database import DATABASE_URL

target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", DATABASE_URL)
```

**Migration Workflow**:
1. Developer modifies SQLModel model (add field, change type)
2. Run `alembic revision --autogenerate`
3. Review generated migration, test locally
4. Commit migration file to Git
5. CI/CD runs `alembic upgrade head` before deploying new code

**Production Safety**:
- Always backup database before migration
- Test migrations on staging environment first
- Use `alembic current` to check current version
- Keep migrations idempotent (safe to run multiple times)

---

## 9. Error Handling Patterns

### Research Question
How should we handle and communicate errors consistently across backend API and frontend UI?

### Backend Error Handling

**HTTP Status Code Strategy**:
- 200 OK: Success
- 201 Created: Resource created
- 400 Bad Request: Validation error (e.g., missing title)
- 401 Unauthorized: Missing or invalid JWT token
- 403 Forbidden: Valid token but accessing another user's data
- 404 Not Found: Resource doesn't exist
- 500 Internal Server Error: Unexpected error

**Error Response Schema**:
```python
# schemas/error.py
class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
    field: str | None = None  # For validation errors

# Usage in route
@router.post("/api/{user_id}/tasks")
async def create_task(task_data: TaskCreate):
    if not task_data.title:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Validation error",
                "detail": "Title is required",
                "field": "title"
            }
        )
```

**Global Exception Handler**:
```python
# main.py
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log error
    logger.error(f"Unhandled error: {exc}")

    # Return generic error to client
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"}
    )
```

### Frontend Error Handling

**API Client Error Handling**:
```typescript
// lib/api/client.ts
export async function apiRequest<T>(
  url: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(url, options)

  if (!response.ok) {
    const error = await response.json()
    throw new APIError(error.error, error.detail, response.status)
  }

  return response.json()
}

class APIError extends Error {
  constructor(
    public message: string,
    public detail?: string,
    public status?: number
  ) {
    super(message)
  }
}
```

**Error Display Strategy**:
```typescript
// components/common/ErrorMessage.tsx
export function ErrorMessage({ error }: { error: Error }) {
  if (error instanceof APIError) {
    return (
      <div className="error-toast">
        <p>{error.message}</p>
        {error.detail && <p className="detail">{error.detail}</p>}
      </div>
    )
  }

  return <div className="error-toast">An unexpected error occurred</div>
}

// Usage in component
try {
  await createTask(taskData)
} catch (error) {
  setError(error)
  // Show toast notification
}
```

**Error Boundary (React)**:
```typescript
// app/error.tsx (Next.js 16+ error boundary)
'use client'

export default function Error({
  error,
  reset
}: {
  error: Error
  reset: () => void
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
```

---

## 10. Performance Optimization

### Research Question
How should we optimize application performance to meet targets (<500ms API, <2s dashboard load)?

### Backend Performance

**Database Query Optimization**:
```python
# Bad: N+1 query problem
tasks = await session.execute(select(Task).where(Task.user_id == user_id))
for task in tasks:
    # This queries database once per task
    user = await session.get(User, task.user_id)

# Good: Join or selectinload
tasks = await session.execute(
    select(Task)
    .options(selectinload(Task.user))  # Eager load user
    .where(Task.user_id == user_id)
)
```

**Indexes**:
```python
# models/task.py
class Task(SQLModel, table=True):
    user_id: int = Field(foreign_key="users.id", index=True)  # Index for filtering
    created_at: datetime = Field(index=True)  # Index for sorting
    due_date: date | None = Field(default=None, index=True)  # Index for due date queries
```

**Caching (Optional for Phase 2)**:
- In-memory cache for user sessions (if needed)
- Redis for shared caching (Phase 3+)

### Frontend Performance

**Code Splitting**:
```typescript
// Lazy load heavy components
const TaskDetail = dynamic(() => import('@/components/tasks/TaskDetail'), {
  loading: () => <Skeleton />
})
```

**Image Optimization**:
```typescript
import Image from 'next/image'

<Image
  src="/logo.png"
  alt="Logo"
  width={200}
  height={100}
  priority  // Preload above-the-fold images
/>
```

**Bundle Size**:
- Use `next/bundle-analyzer` to track bundle size
- Keep initial bundle <500KB
- Tree-shake unused code (Tailwind's purge, lodash-es)

**Rendering Strategy**:
- Server Components for initial render (faster First Contentful Paint)
- Client Components for interactivity (checkbox, modals)
- Use `revalidate` for data that changes infrequently

---

## Summary & Decisions

| **Topic** | **Decision** | **Rationale** |
|-----------|-------------|---------------|
| Next.js Structure | Route groups `(auth)` and `(dashboard)` | Clean separation, shared layouts, auth scoping |
| FastAPI Architecture | Layered (Models → Services → Routes) | Testable, separates concerns, aligns with Phase 1 |
| Authentication | Better Auth + FastAPI JWT validation | Modern, shared secret, unified user database |
| Database Connection | asyncpg with connection pooling | Efficient, async, handles Neon connection limits |
| API Auth Pattern | Dependency injection per route | Explicit, flexible, testable |
| Testing | pytest (backend >90%), Jest (frontend >80%) | Industry standard, high coverage enforcement |
| Monorepo | Independent frontend/ and backend/ | Simple, no overhead, separate package managers |
| Migrations | Alembic auto-generate with review | Version control, rollback support, industry standard |
| Error Handling | Structured errors + global handlers | Consistent client experience, detailed logs |
| Performance | Indexes, eager loading, code splitting | Meets <500ms API, <2s load targets |

**Next Steps**:
1. ✅ Research complete
2. → Generate `data-model.md` (Phase 1)
3. → Generate `contracts/` API specifications (Phase 1)
4. → Generate `quickstart.md` (Phase 1)
5. → Run `/sp.tasks` to create implementation tasks
