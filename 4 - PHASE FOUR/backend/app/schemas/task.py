"""
Task request and response schemas.

This module defines Pydantic models for task operations.
"""

from datetime import date, datetime, time
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.task import Priority, RecurrencePattern


class TaskCreate(BaseModel):
    """Task creation request."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    priority: Optional[Priority] = Field(None, description="Priority level")
    tags: List[str] = Field(default_factory=list, max_items=10, description="Category tags")
    due_date: Optional[date] = Field(None, description="Deadline date")
    due_time: Optional[time] = Field(None, description="Deadline time")
    recurrence: Optional[RecurrencePattern] = Field(None, description="Recurrence pattern")
    recurrence_day: Optional[int] = Field(None, ge=1, le=31, description="Day for recurrence")


class TaskUpdate(BaseModel):
    """Task update request (all fields optional)."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[Priority] = None
    tags: Optional[List[str]] = Field(None, max_items=10)
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    recurrence: Optional[RecurrencePattern] = None
    recurrence_day: Optional[int] = Field(None, ge=1, le=31)
    is_complete: Optional[bool] = None


class TaskResponse(BaseModel):
    """Task information response."""

    id: int
    user_id: str
    title: str
    description: Optional[str]
    is_complete: bool
    created_at: datetime
    completed_at: Optional[datetime]
    priority: Optional[Priority]
    tags: List[str]
    due_date: Optional[date]
    due_time: Optional[time]
    recurrence: Optional[RecurrencePattern]
    recurrence_day: Optional[int]

    # Multi-tenant fields (Phase 3.1)
    organization_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    assigned_to: Optional[str] = None
    deleted_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class TaskAssign(BaseModel):
    """Task assignment request."""

    assigned_to: str = Field(..., description="User ID to assign task to")


class TaskListResponse(BaseModel):
    """List of tasks response."""

    tasks: List[TaskResponse]
    total: int
