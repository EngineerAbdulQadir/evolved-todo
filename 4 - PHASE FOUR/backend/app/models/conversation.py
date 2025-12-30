"""Conversation model for AI chatbot state management.

This module defines the Conversation database model for Phase 3 stateless architecture.
Each conversation represents a chat session between a user and the AI assistant.

Task: T007 - Create Conversation model
Spec: specs/003-phase3-ai-chatbot/data-model.md
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    """
    Conversation model for chat sessions.

    Represents a conversation between a user and the AI assistant. All conversation
    state is persisted to the database (stateless architecture).

    Attributes:
        id: Primary key (auto-generated)
        user_id: Foreign key to user (data isolation)
        title: Conversation title/name (default: "New Chat", user-editable)
        created_at: When conversation started (indexed for sorting)
        updated_at: Last message timestamp (indexed for sorting)

    Relationships:
        - User (N:1): Each conversation belongs to one user
        - Message (1:N): Each conversation has many messages

    Business Rules:
        - Conversations are immutable once created (no deletion in Phase 3)
        - updated_at timestamp updated whenever new message added
        - All conversations isolated by user_id
        - Empty conversations allowed (user opens chat but doesn't send message)
    """

    __tablename__ = "conversations"

    # Primary and foreign keys
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True, max_length=255)

    # Conversation metadata
    title: str = Field(default="New Chat", max_length=255)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """SQLModel configuration."""

        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user_123abc",
                "title": "Task Management Chat",
                "created_at": "2025-12-19T12:00:00Z",
                "updated_at": "2025-12-19T12:05:00Z",
            }
        }
