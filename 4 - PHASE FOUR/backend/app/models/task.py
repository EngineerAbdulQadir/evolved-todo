"""
Task model for todo items with all Phase 1 features + Phase 3.1 multi-tenancy.

This module defines the Task database model with support for:
- Basic CRUD operations
- Priorities and tags
- Search and filtering
- Sorting
- Recurring tasks
- Due dates and reminders
- Multi-tenant organization → team → project → task hierarchy
- Task assignment to project members
- Soft delete with 30-day recovery

Task: T100 [US3] - Update Task model with multi-tenant fields
References:
- ADR-001: Multi-Tenant Data Isolation Strategy
- ADR-003: Soft Delete and Audit Trail Strategy
"""

from datetime import date, datetime, time, UTC
from enum import Enum
from typing import List, Optional
from uuid import UUID

from sqlalchemy import Column, JSON as SAJSON
from sqlmodel import Field, Relationship, SQLModel


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
    Task model with all Phase 1 features + Phase 3.1 multi-tenancy.

    Attributes:
        id: Primary key (auto-generated)
        user_id: Foreign key to user (task creator)
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

        Multi-Tenant Fields (Phase 3.1):
        organization_id: Parent organization UUID
        team_id: Parent team UUID
        project_id: Parent project UUID (all tasks belong to a project)
        assigned_to: User ID of assignee (optional, must be project member)
        deleted_at: Soft delete timestamp (NULL if active)
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

    # Multi-tenant fields (Phase 3.1)
    organization_id: Optional[UUID] = Field(
        default=None,
        foreign_key="organizations.id",
        index=True
    )
    team_id: Optional[UUID] = Field(
        default=None,
        foreign_key="teams.id",
        index=True
    )
    project_id: Optional[UUID] = Field(
        default=None,
        foreign_key="projects.id",
        index=True
    )
    assigned_to: Optional[str] = Field(default=None)  # User ID of assignee
    deleted_at: Optional[datetime] = Field(default=None, index=True)

    # Relationships
    project: Optional["Project"] = Relationship(back_populates="tasks")

    class Config:
        """SQLModel configuration."""

        use_enum_values = True  # Store enum values as strings in database
