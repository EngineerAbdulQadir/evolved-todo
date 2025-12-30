---
name: neon-postgres
description: Neon Serverless PostgreSQL connection management, asyncpg driver usage, connection pooling, and migration strategies with Alembic.
---

# Neon Serverless PostgreSQL

## Instructions

### When to Use

- Setting up database connections to Neon PostgreSQL
- Configuring asyncpg connection pooling
- Handling Neon-specific connection requirements (SSL, pooling)
- Implementing database branching strategies
- Managing connection strings and authentication
- Optimizing for Neon's serverless architecture

## What is Neon?

Neon is a serverless PostgreSQL platform that provides:
- **Serverless Architecture** - Automatic scaling and zero-downtime deployments
- **Database Branching** - Git-like branching for development and testing
- **Instant Provisioning** - Create databases in seconds
- **Connection Pooling** - Built-in connection pooling with pgBouncer
- **Pay-per-Use** - Only pay for compute time and storage used

## Getting Started with Neon

### 1. Create a Neon Project

```bash
# Sign up at https://neon.tech
# Create a new project through the Neon dashboard
# Copy the connection string
```

### 2. Connection String Format

```
postgresql://[user]:[password]@[endpoint]/[database]?sslmode=require
```

**Example:**
```
postgresql://alex:AbC123dEf@ep-cool-darkness-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**For asyncpg (Python):**
```
postgresql+asyncpg://alex:AbC123dEf@ep-cool-darkness-123456.us-east-2.aws.neon.tech/neondb?ssl=require
```

### 3. Environment Variables

```bash
# .env
DATABASE_URL="postgresql+asyncpg://user:pass@host.neon.tech/dbname?ssl=require"

# Connection pool settings
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800  # 30 minutes
```

## Python Setup with asyncpg

### Installation

```bash
uv add asyncpg sqlalchemy[asyncio] sqlmodel alembic
```

### Database Configuration

```python
# app/database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import AsyncGenerator

# Load from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# Create async engine with Neon-optimized settings
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging in development
    future=True,

    # Connection pool settings
    pool_size=20,           # Number of permanent connections
    max_overflow=10,        # Additional connections when pool is full
    pool_timeout=30,        # Seconds to wait for connection
    pool_recycle=1800,      # Recycle connections after 30 minutes
    pool_pre_ping=True,     # Verify connections before using them

    # Neon-specific: Handle connection timeouts gracefully
    connect_args={
        "ssl": "require",
        "server_settings": {
            "application_name": "evolved-todo",
        },
    },
)

# Create async session factory
async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
    autoflush=False,         # Manually control flushing
    autocommit=False,        # Explicit transaction management
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.

    Usage:
        @app.get("/tasks")
        async def get_tasks(session: AsyncSession = Depends(get_session)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db() -> None:
    """
    Initialize database tables.

    Call this on application startup to create all tables.
    """
    async with engine.begin() as conn:
        # Create all tables defined in SQLModel models
        await conn.run_sync(SQLModel.metadata.create_all)

async def close_db() -> None:
    """
    Close database connections.

    Call this on application shutdown.
    """
    await engine.dispose()
```

### FastAPI Integration

```python
# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database import init_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown.
    """
    # Startup
    print("🚀 Starting application...")
    await init_db()
    print("✅ Database initialized")

    yield

    # Shutdown
    print("🛑 Shutting down application...")
    await close_db()
    print("✅ Database connections closed")

app = FastAPI(
    title="Evolved Todo API",
    version="1.0.0",
    lifespan=lifespan,
)
```

## Connection Pooling Best Practices

### Understanding Pool Settings

```python
# pool_size: Number of permanent connections to maintain
# - Too low: Bottleneck under load
# - Too high: Wastes resources
# - Recommended: 10-20 for small apps, 20-50 for medium apps
pool_size=20

# max_overflow: Additional connections when pool is exhausted
# - Allows temporary spikes in traffic
# - These connections are closed after use
# - Recommended: 50% of pool_size
max_overflow=10

# pool_timeout: Seconds to wait for available connection
# - If all connections busy, wait this long before error
# - Recommended: 30 seconds
pool_timeout=30

# pool_recycle: Seconds before recycling a connection
# - Neon may close idle connections after 5 minutes
# - Recycle before that to avoid "connection closed" errors
# - Recommended: 1800 (30 minutes)
pool_recycle=1800

# pool_pre_ping: Test connection before using it
# - Adds slight overhead but prevents "connection closed" errors
# - Recommended: True for Neon
pool_pre_ping=True
```

### Handling Connection Errors

```python
# app/database.py
from sqlalchemy.exc import OperationalError, DBAPIError
import logging

logger = logging.getLogger(__name__)

async def get_session_with_retry() -> AsyncGenerator[AsyncSession, None]:
    """
    Get session with automatic retry on connection failure.
    """
    max_retries = 3
    retry_delay = 1  # seconds

    for attempt in range(max_retries):
        try:
            async with async_session_maker() as session:
                yield session
                return
        except (OperationalError, DBAPIError) as e:
            logger.warning(f"Database connection failed (attempt {attempt + 1}/{max_retries}): {e}")

            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error("All database connection attempts failed")
                raise
```

## Neon Database Branching

Neon supports Git-like branching for databases:

### Creating a Branch

```bash
# Via Neon CLI
neon branches create --name feature/authentication

# Via API
curl -X POST https://console.neon.tech/api/v2/projects/PROJECT_ID/branches \
  -H "Authorization: Bearer $NEON_API_KEY" \
  -d '{"name": "feature/authentication"}'
```

### Using Branches for Development

```bash
# .env.development
DATABASE_URL="postgresql://...@branch-name.neon.tech/..."

# .env.staging
DATABASE_URL="postgresql://...@staging-branch.neon.tech/..."

# .env.production
DATABASE_URL="postgresql://...@main-branch.neon.tech/..."
```

### Benefits of Branching

1. **Isolated Testing** - Test schema changes without affecting production
2. **Safe Migrations** - Run migrations on a branch first
3. **Instant Provisioning** - Create branches in seconds (copy-on-write)
4. **Cost Effective** - Only pay for storage differences

## Monitoring and Debugging

### Connection Pool Monitoring

```python
# app/database.py
from sqlalchemy import event
from sqlalchemy.pool import Pool
import logging

logger = logging.getLogger(__name__)

@event.listens_for(Pool, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log when a new connection is created."""
    logger.info("New database connection created")

@event.listens_for(Pool, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log when a connection is checked out from pool."""
    logger.debug("Connection checked out from pool")

@event.listens_for(Pool, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """Log when a connection is returned to pool."""
    logger.debug("Connection returned to pool")

# Get pool statistics
def get_pool_stats():
    """Get current connection pool statistics."""
    return {
        "size": engine.pool.size(),
        "checked_in": engine.pool.checkedin(),
        "checked_out": engine.pool.checkedout(),
        "overflow": engine.pool.overflow(),
        "total": engine.pool.size() + engine.pool.overflow(),
    }
```

### Health Check Endpoint

```python
# app/api/routes/health.py
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text

from app.database import get_session

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    """Basic health check."""
    return {"status": "healthy"}

@router.get("/db")
async def database_health(session: AsyncSession = Depends(get_session)):
    """
    Database health check.

    Verifies connection to Neon PostgreSQL.
    """
    try:
        # Execute simple query
        result = await session.execute(text("SELECT 1"))
        result.scalar()

        return {
            "status": "healthy",
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
        }
```

## Performance Optimization

### 1. Use Connection Pooling

```python
# ✅ Good: Use connection pool
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
)

# ❌ Bad: Create new connection for each request
engine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,  # No pooling
)
```

### 2. Enable pool_pre_ping

```python
# ✅ Good: Verify connections before use (prevents stale connection errors)
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

# ❌ Bad: No pre-ping (may get "connection closed" errors)
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=False,
)
```

### 3. Set Appropriate pool_recycle

```python
# ✅ Good: Recycle connections before Neon closes them
engine = create_async_engine(
    DATABASE_URL,
    pool_recycle=1800,  # 30 minutes
)

# ❌ Bad: Never recycle (connections may become stale)
engine = create_async_engine(
    DATABASE_URL,
    pool_recycle=-1,
)
```

## Neon-Specific Configuration

### SSL/TLS Requirements

Neon requires SSL/TLS connections:

```python
# For asyncpg
DATABASE_URL = "postgresql+asyncpg://...?ssl=require"

# Connection args
connect_args = {
    "ssl": "require",
}
```

### Autoscaling Considerations

Neon can autoscale compute resources:

```python
# Set reasonable timeouts to handle cold starts
engine = create_async_engine(
    DATABASE_URL,
    pool_timeout=30,        # Wait for connection
    connect_args={
        "timeout": 10,      # Connection timeout
        "command_timeout": 60,  # Query timeout
    },
)
```

## Integration with database-architect Subagent

This skill is primarily used by:
- **database-architect** - For Neon PostgreSQL connection and configuration
- **backend-api-dev** - For database access in API services
- **alembic-migrations** - For migration execution on Neon

### Key Principles

1. **Always Use SSL** - Neon requires `ssl=require` or `sslmode=require`
2. **Connection Pooling** - Use pool_size 10-50 depending on load
3. **pool_pre_ping=True** - Prevents stale connection errors
4. **pool_recycle** - Set to 1800 (30 minutes) to avoid Neon idle timeouts
5. **Branching** - Use database branches for development and testing
6. **Environment-Specific** - Different connection strings per environment
