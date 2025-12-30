import asyncio
from sqlmodel import delete
from app.core.database import get_session
from app.models.conversation import Conversation
from app.models.message import Message


async def clear():
    async for session in get_session():
        await session.execute(delete(Message))
        await session.execute(delete(Conversation))
        await session.commit()
        print("Database cleared successfully")
        break


if __name__ == "__main__":
    asyncio.run(clear())
