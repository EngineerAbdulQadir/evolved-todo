"""
Task model for todo items with all Phase 1 features.

This module defines the Task database model with support for:
- Basic CRUD operations
- Priorities and tags
- Search and filtering
- Sorting
- Recurring tasks
- Due dates and reminders
"""

from datetime import date, datetime, time
from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, JSON as SAJSON
from sqlmodel import Field, SQLModel


class Priority(str, Enum):
    """Task priority levels."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecurrencePattern(str, Enum):
    """Task recurrence patterns."""

    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Task(SQLModel, table=True):
    """
    Task model with all Phase 1 features adapted for web application.

    Attributes:
        id: Primary key (auto-generated)
        user_id: Foreign key to user (for multi-user data isolation)
        title: Task name (required, 1-200 chars)
        description: Additional details (optional, max 1000 chars)
        is_complete: Completion status (default False)
        created_at: Creation timestamp (auto-set)
        priority: Priority level (high/medium/low)
        tags: Category labels (list of strings)
        due_date: Deadline date (optional)
        due_time: Deadline time (optional)
        recurrence: Recurrence pattern (daily/weekly/monthly)
        recurrence_day: Day for weekly (1-7) or monthly (1-31) recurrence
    """

    __tablename__ = "task"

    # Primary and foreign keys
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True, max_length=255)

    # Core attributes (Basic Level - Features 001-005)
    title: str = Field(max_length=200, min_length=1)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_complete: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)

    # Organization attributes (Intermediate Level - Feature 006)
    priority: Optional[Priority] = Field(default=None)
    tags: List[str] = Field(default_factory=list, sa_column=Column(SAJSON))

    # Scheduling attributes (Advanced Level - Features 009, 010)
    due_date: Optional[date] = Field(default=None)
    due_time: Optional[time] = Field(default=None)
    recurrence: Optional[RecurrencePattern] = Field(default=None)
    recurrence_day: Optional[int] = Field(default=None)

    class Config:
        """SQLModel configuration."""

        use_enum_values = True  # Store enum values as strings in database
