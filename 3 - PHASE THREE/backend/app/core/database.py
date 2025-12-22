"""
Database configuration and connection management.

This module provides async SQLAlchemy engine configuration
for connecting to Neon PostgreSQL database.
"""

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from typing import AsyncGenerator

from app.core.settings import settings

# Get database URL from settings (loaded from .env file)
DATABASE_URL = settings.database_url

# Create async engine for PostgreSQL with asyncpg driver
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries in development
    future=True,
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600,  # Recycle connections every hour to prevent stale connections
    connect_args={
        "prepared_statement_cache_size": 0,  # Disable prepared statement cache to avoid schema change issues
    },
)


async def init_db() -> None:
    """Initialize database tables (development only)."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()


# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.

    Yields an async session and ensures proper cleanup.
    """
    async with async_session_factory() as session:
        yield session
