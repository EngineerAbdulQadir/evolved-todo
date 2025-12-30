# FastAPI + SQLModel Async Patterns

**Skill**: fastapi-sqlmodel
**Version**: 1.0.0  
**Primary Users**: backend-api-developer, database-architect
**Prerequisites**: Python 3.13+, FastAPI, SQLModel, asyncpg

## Purpose
Build async FastAPI applications with SQLModel ORM for stateless architecture with database-persisted state.

## Core Patterns

### SQLModel Models
```python
from sqlmodel import Field, SQLModel
from datetime import datetime

class Conversation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
```

### Async Session
```python
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine("postgresql+asyncpg://...")

async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session
```

### FastAPI Endpoint
```python
@app.post("/api/chat")
async def chat(message: str, session: AsyncSession = Depends(get_session)):
    result = await session.exec(select(Message).where(Message.id == 1))
    msg = result.first()
    return {"content": msg.content}
```

## Best Practices
- Always use async/await for database operations
- Type hints required: `int | None` for optional fields
- Index frequently queried columns (user_id, conversation_id)
- Session per request via dependency injection
- Commit explicitly with `await session.commit()`

## Related Skills
async-python, neon-postgres, type-safety

See examples.md and reference.md for more details.
