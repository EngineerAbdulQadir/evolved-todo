"""
Reset database by dropping and recreating all tables.

WARNING: This will delete all data!
"""

import asyncio
from sqlmodel import SQLModel
from app.core.database import engine
from app.models import task, user  # Import models to register them


async def reset_database():
    """Drop all tables and recreate them."""
    print("Dropping all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    print("Creating all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    print("✅ Database reset complete!")


if __name__ == "__main__":
    asyncio.run(reset_database())
