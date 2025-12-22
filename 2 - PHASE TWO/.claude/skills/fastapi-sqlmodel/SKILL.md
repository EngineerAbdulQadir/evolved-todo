---
name: fastapi-sqlmodel
description: FastAPI + SQLModel async patterns, layered architecture (Models → Services → Routes), dependency injection, and async PostgreSQL operations.
---

# FastAPI + SQLModel

## Instructions

### When to Use

- Implementing REST API endpoints with FastAPI
- Creating database models with SQLModel
- Writing business logic services with async/await
- Setting up dependency injection patterns
- Implementing async PostgreSQL operations with asyncpg
- Validating request/response schemas with Pydantic v2

## Layered Architecture

```
┌─────────────────────────────────────┐
│   Routes Layer (api/routes/)        │  ← HTTP handlers
│   - tasks.py                        │
│   - users.py                        │
└──────────────┬──────────────────────┘
               │ depends on
               ▼
┌─────────────────────────────────────┐
│   Service Layer (services/)         │  ← Business logic
│   - task_service.py                 │
│   - user_service.py                 │
└──────────────┬──────────────────────┘
               │ depends on
               ▼
┌─────────────────────────────────────┐
│   Model Layer (models/)             │  ← Data structures
│   - task.py (SQLModel + Pydantic)   │
│   - user.py                         │
└──────────────┬──────────────────────┘
               │ depends on
               ▼
┌─────────────────────────────────────┐
│   Database Layer (asyncpg)          │  ← Persistence
│   - PostgreSQL + AsyncSession       │
└─────────────────────────────────────┘
```

## SQLModel Models (Database Tables)

```python
# models/task.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

# Database model (table=True)
class Task(SQLModel, table=True):
    """Task database model with SQLModel."""
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    priority: str = Field(default="medium")  # low, medium, high
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    user: Optional["User"] = Relationship(back_populates="tasks")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Complete project",
                "description": "Finish the todo app",
                "priority": "high"
            }
        }
```

## Pydantic Schemas (Request/Response)

```python
# schemas/task.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

# Request schema (for POST/PUT)
class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Complete project",
                "description": "Finish the todo app",
                "priority": "high"
            }
        }
    )

# Request schema for updates
class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[str] = Field(default=None, pattern="^(low|medium|high)$")
    completed: Optional[bool] = None

# Response schema
class TaskResponse(BaseModel):
    """Schema for task responses."""
    id: int
    user_id: int
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

## Service Layer (Business Logic)

```python
# services/task_service.py
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime
from typing import Optional, List

from models.task import Task
from schemas.task import TaskCreate, TaskUpdate

class TaskService:
    """Service layer for task business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(self, user_id: int, task_data: TaskCreate) -> Task:
        """Create a new task for a user."""
        task = Task(
            user_id=user_id,
            **task_data.model_dump()
        )

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def get_tasks(
        self,
        user_id: int,
        completed: Optional[bool] = None,
        priority: Optional[str] = None
    ) -> List[Task]:
        """Get tasks for a user with optional filters."""
        query = select(Task).where(Task.user_id == user_id)

        if completed is not None:
            query = query.where(Task.completed == completed)

        if priority is not None:
            query = query.where(Task.priority == priority)

        query = query.order_by(Task.created_at.desc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_task_by_id(self, user_id: int, task_id: int) -> Optional[Task]:
        """Get a specific task by ID for a user."""
        query = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_task(
        self,
        user_id: int,
        task_id: int,
        task_data: TaskUpdate
    ) -> Optional[Task]:
        """Update a task."""
        task = await self.get_task_by_id(user_id, task_id)

        if not task:
            return None

        # Update only provided fields
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        task.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def delete_task(self, user_id: int, task_id: int) -> bool:
        """Delete a task."""
        task = await self.get_task_by_id(user_id, task_id)

        if not task:
            return False

        await self.session.delete(task)
        await self.session.commit()

        return True
```

## Routes Layer (HTTP Handlers)

```python
# api/routes/tasks.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Optional

from database import get_session
from services.task_service import TaskService
from schemas.task import TaskCreate, TaskUpdate, TaskResponse
from api.deps import get_current_user

router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])

def get_task_service(
    session: AsyncSession = Depends(get_session)
) -> TaskService:
    """Dependency to get TaskService instance."""
    return TaskService(session)

@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    user_id: int,
    task_data: TaskCreate,
    task_service: TaskService = Depends(get_task_service),
    current_user: dict = Depends(get_current_user)
) -> TaskResponse:
    """Create a new task."""
    # Verify user_id matches authenticated user
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    task = await task_service.create_task(user_id, task_data)
    return TaskResponse.model_validate(task)

@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    user_id: int,
    completed: Optional[bool] = Query(default=None),
    priority: Optional[str] = Query(default=None, pattern="^(low|medium|high)$"),
    task_service: TaskService = Depends(get_task_service),
    current_user: dict = Depends(get_current_user)
) -> List[TaskResponse]:
    """List tasks with optional filters."""
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    tasks = await task_service.get_tasks(user_id, completed, priority)
    return [TaskResponse.model_validate(task) for task in tasks]

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: int,
    task_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: dict = Depends(get_current_user)
) -> TaskResponse:
    """Get a specific task."""
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    task = await task_service.get_task_by_id(user_id, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponse.model_validate(task)

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: int,
    task_id: int,
    task_data: TaskUpdate,
    task_service: TaskService = Depends(get_task_service),
    current_user: dict = Depends(get_current_user)
) -> TaskResponse:
    """Update a task."""
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    task = await task_service.update_task(user_id, task_id, task_data)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponse.model_validate(task)

@router.delete("/{task_id}", status_code=204)
async def delete_task(
    user_id: int,
    task_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: dict = Depends(get_current_user)
) -> None:
    """Delete a task."""
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    success = await task_service.delete_task(user_id, task_id)

    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
```

## Database Session Management

```python
# database.py
from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncSession, AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/dbname"

# Create async engine
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (disable in production)
    future=True,
    pool_size=20,
    max_overflow=10,
)

# Create async session factory
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
```

## Dependency Injection Pattern

```python
# api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession

from database import get_session
from services.auth_service import AuthService

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session)
) -> dict:
    """Validate JWT token and return current user."""
    auth_service = AuthService(session)

    try:
        user = await auth_service.verify_token(credentials.credentials)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
```

## Testing with pytest-asyncio

```python
# tests/test_task_service.py
import pytest
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from services.task_service import TaskService
from schemas.task import TaskCreate

@pytest.fixture
async def session():
    """Create test database session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

@pytest.mark.asyncio
async def test_create_task(session: AsyncSession):
    """Test creating a task."""
    task_service = TaskService(session)
    task_data = TaskCreate(
        title="Test task",
        description="Test description",
        priority="high"
    )

    task = await task_service.create_task(user_id=1, task_data=task_data)

    assert task.id is not None
    assert task.title == "Test task"
    assert task.priority == "high"
```

## Integration with backend-api-dev Subagent

This skill is primarily used by:
- **backend-api-dev** - For implementing FastAPI + SQLModel backend
- **fullstack-integrator** - For understanding backend API patterns
- **database-architect** - For database model patterns

### Key Principles

1. **Layered Architecture** - Models → Services → Routes
2. **Dependency Injection** - Use FastAPI's `Depends()` for services
3. **Async/Await** - All database operations are async
4. **Schema Validation** - Pydantic schemas for request/response
5. **User Isolation** - Always filter by `user_id` for data access
6. **Proper Error Handling** - HTTPException with appropriate status codes
