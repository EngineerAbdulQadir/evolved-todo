"""
SQLModel database models.

This module exports all database models for the application.
Phase 2: User, Task, Account, Session
Phase 3: Conversation, Message (NEW)
"""

from sqlmodel import SQLModel

from .conversation import Conversation
from .message import Message, MessageRole
from .task import Priority, RecurrencePattern, Task
from .user import Account, Session, User

__all__ = [
    "SQLModel",
    "User",
    "Account",
    "Session",
    "Task",
    "Priority",
    "RecurrencePattern",
    "Conversation",
    "Message",
    "MessageRole",
]
