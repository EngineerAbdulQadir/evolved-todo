"""Message model for conversation history.

This module defines the Message database model for Phase 3 stateless architecture.
Each message represents either a user input or assistant response in a conversation.

Task: T008 - Create Message model
Spec: specs/003-phase3-ai-chatbot/data-model.md
"""

from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from sqlmodel import Field, SQLModel


class MessageRole(str, Enum):
    """Message role enumeration."""

    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """
    Message model for conversation history.

    Represents a single message in a conversation (either user or assistant).
    All messages persisted to database for stateless architecture.

    Attributes:
        id: Primary key (auto-generated)
        conversation_id: Foreign key to conversation (indexed)
        user_id: Foreign key to user (data isolation, indexed)
        role: Who sent the message ("user" | "assistant")
        content: Message text content (max 5000 chars)
        created_at: When message was sent (indexed for ordering)

    Relationships:
        - Conversation (N:1): Each message belongs to one conversation
        - User (N:1): Each message has an owner (for data isolation)

    Business Rules:
        - Messages are immutable once created (no editing/deletion in Phase 3)
        - role must be either "user" or "assistant"
        - content limited to 5000 characters (prevent abuse)
        - All messages isolated by user_id (inherited from conversation owner)
        - Messages ordered by created_at ascending for conversation flow

    Performance:
        - Conversation history limited to last 50 messages (prevent token overflow)
        - Index on conversation_id + created_at for fast history retrieval
        - Single query to fetch all messages (no N+1 queries)
    """

    __tablename__ = "messages"

    # Primary and foreign keys
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(foreign_key="user.id", index=True, max_length=255)

    # Message content
    role: MessageRole = Field(index=True)
    content: str = Field(max_length=5000)

    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    class Config:
        """SQLModel configuration."""

        use_enum_values = True  # Store enum values as strings in database
        json_schema_extra = {
            "example": {
                "id": 1,
                "conversation_id": 1,
                "user_id": "user_123abc",
                "role": "user",
                "content": "Add a task to buy groceries",
                "created_at": "2025-12-19T12:00:00Z",
            }
        }
