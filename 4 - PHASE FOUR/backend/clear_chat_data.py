"""
Clear all chat conversations and messages from the database.

This script deletes all data from the conversations and messages tables
while preserving users, tasks, and other data.

Usage:
    python clear_chat_data.py
"""

import asyncio
from sqlmodel import select, delete
from app.core.database import get_session
from app.models.conversation import Conversation
from app.models.message import Message


async def clear_chat_data():
    """Delete all conversations and messages."""
    print("🗑️  Clearing chat data...")

    async for session in get_session():
        # Delete all messages first (foreign key constraint)
        result = await session.execute(delete(Message))
        messages_deleted = result.rowcount
        print(f"   ✅ Deleted {messages_deleted} messages")

        # Delete all conversations
        result = await session.execute(delete(Conversation))
        conversations_deleted = result.rowcount
        print(f"   ✅ Deleted {conversations_deleted} conversations")

        # Commit the changes
        await session.commit()
        print("\n✨ Chat data cleared successfully!")
        print(f"   Total: {conversations_deleted} conversations, {messages_deleted} messages removed")

        break  # Exit after first session


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  CLEAR CHAT DATA")
    print("=" * 60)
    print("\n⚠️  WARNING: This will delete all conversations and messages!")
    print("   (Users and tasks will NOT be affected)\n")

    confirm = input("Continue? (yes/no): ").strip().lower()

    if confirm in ['yes', 'y']:
        asyncio.run(clear_chat_data())
    else:
        print("\n❌ Operation cancelled.")
