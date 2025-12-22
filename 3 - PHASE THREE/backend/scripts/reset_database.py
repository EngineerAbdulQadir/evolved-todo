"""
Database reset script - Clear all data from all tables.

WARNING: This will delete ALL data from the database!
Use this only for development/testing purposes.
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.core.database import engine


async def reset_database():
    """Clear all data from all tables."""
    # Use autocommit for each statement to avoid transaction rollback issues
    async with engine.connect() as conn:
        print("Clearing all data from database...")

        # Delete from tables in order to respect foreign keys
        # Order matters: delete from child tables first, then parent tables

        # 1. Delete messages (child of conversations)
        try:
            result = await conn.execute(text("DELETE FROM messages;"))
            await conn.commit()
            print(f"  - Cleared messages ({result.rowcount} rows)")
        except Exception as e:
            await conn.rollback()
            print(f"  - Could not clear messages: {str(e)}")

        # 2. Delete conversations (child of user)
        try:
            result = await conn.execute(text("DELETE FROM conversations;"))
            await conn.commit()
            print(f"  - Cleared conversations ({result.rowcount} rows)")
        except Exception as e:
            await conn.rollback()
            print(f"  - Could not clear conversations: {str(e)}")

        # 3. Delete tasks (child of user)
        try:
            result = await conn.execute(text("DELETE FROM task;"))
            await conn.commit()
            print(f"  - Cleared task ({result.rowcount} rows)")
        except Exception as e:
            await conn.rollback()
            print(f"  - Could not clear task: {str(e)}")

        # 4. Delete accounts (Better Auth - child of user)
        try:
            result = await conn.execute(text("DELETE FROM account;"))
            await conn.commit()
            print(f"  - Cleared account ({result.rowcount} rows)")
        except Exception as e:
            await conn.rollback()
            print(f"  - Could not clear account: {str(e)}")

        # 5. Delete sessions (Better Auth - child of user)
        try:
            result = await conn.execute(text("DELETE FROM session;"))
            await conn.commit()
            print(f"  - Cleared session ({result.rowcount} rows)")
        except Exception as e:
            await conn.rollback()
            print(f"  - Could not clear session: {str(e)}")

        # 6. Delete verification tokens (Better Auth - child of user)
        try:
            result = await conn.execute(text("DELETE FROM verification;"))
            await conn.commit()
            print(f"  - Cleared verification ({result.rowcount} rows)")
        except Exception as e:
            await conn.rollback()
            print(f"  - Skipped verification (table may not exist)")

        # 7. Delete users (parent table)
        try:
            result = await conn.execute(text('DELETE FROM "user";'))
            await conn.commit()
            print(f"  - Cleared user ({result.rowcount} rows)")
        except Exception as e:
            await conn.rollback()
            print(f"  - Could not clear user: {str(e)}")

        print("\nDatabase reset complete! All data has been cleared.")


if __name__ == "__main__":
    asyncio.run(reset_database())
