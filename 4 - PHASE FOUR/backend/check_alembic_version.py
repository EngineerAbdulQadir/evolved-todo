"""Check Alembic version in database"""
import asyncio
from sqlalchemy import text
from app.core.database import engine

async def check_version():
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT version_num FROM alembic_version"))
        versions = [row[0] for row in result]
        if versions:
            print(f"Current Alembic version(s): {versions}")
        else:
            print("No Alembic version found in database")
        return versions

if __name__ == "__main__":
    asyncio.run(check_version())
