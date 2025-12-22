"""List tasks MCP tool for retrieving and filtering tasks.

This tool allows the AI agent to retrieve tasks with optional filtering and sorting.

Task: T033-T035 - Implement list_tasks MCP tool with schemas
Spec: specs/003-phase3-ai-chatbot/contracts/mcp-tools.md
"""

from datetime import date, time
from typing import List, Optional

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import Priority, RecurrencePattern, Task
from app.mcp.schemas import MCPErrorCode, MCPErrorOutput, MCPToolInput, MCPToolOutput


class ListTasksInput(MCPToolInput):
    """
    Input schema for list_tasks MCP tool.

    Task: T034 - Define ListTasksInput schema
    """

    status: Optional[str] = Field(
        None,
        description="Filter by completion status: 'all', 'pending', or 'completed'",
        examples=["all", "pending", "completed"],
    )
    priority: Optional[str] = Field(
        None,
        description="Filter by priority: 'high', 'medium', or 'low'",
        examples=["high", "medium", "low"],
    )
    tag: Optional[str] = Field(
        None,
        max_length=100,
        description="Filter by tag (substring match)",
        examples=["work", "personal", "urgent"],
    )
    sort_by: Optional[str] = Field(
        None,
        description="Sort field: 'id', 'title', 'priority', 'due_date', or 'created_at'",
        examples=["created_at", "due_date", "priority"],
    )
    sort_order: Optional[str] = Field(
        None,
        description="Sort order: 'asc' or 'desc'",
        examples=["asc", "desc"],
    )


class TaskItem(BaseModel):
    """Individual task item in list response."""

    id: int = Field(..., description="Task ID")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    is_complete: bool = Field(..., description="Completion status")
    priority: Optional[str] = Field(None, description="Task priority")
    tags: List[str] = Field(default_factory=list, description="Task tags")
    due_date: Optional[str] = Field(None, description="Due date (ISO format)")
    due_time: Optional[str] = Field(None, description="Due time (HH:MM:SS)")
    recurrence: Optional[str] = Field(None, description="Recurrence pattern")
    created_at: str = Field(..., description="Creation timestamp (ISO format)")


class ListTasksOutput(MCPToolOutput):
    """
    Output schema for list_tasks MCP tool.

    Task: T035 - Define ListTasksOutput schema
    """

    tasks: List[TaskItem] = Field(default_factory=list, description="List of tasks")
    count: int = Field(..., description="Number of tasks returned")


async def list_tasks(input_data: dict) -> dict:
    """
    Retrieve tasks with optional filtering and sorting.

    Task: T033 - Implement list_tasks MCP tool

    Args:
        input_data: Dictionary with filter and sort parameters

    Returns:
        ListTasksOutput dict with matching tasks

    Examples:
        {"user_id": "123", "status": "pending"}
        -> Returns all pending tasks for user 123

        {"user_id": "123", "priority": "high", "sort_by": "due_date"}
        -> Returns high priority tasks sorted by due date
    """
    # Validate input with Pydantic
    try:
        validated_input = ListTasksInput(**input_data)
    except Exception as e:
        return MCPErrorOutput(
            message=f"Invalid input: {str(e)}",
            error_code=MCPErrorCode.INVALID_INPUT,
            details={"input": input_data},
        ).model_dump()

    # Get database session
    async for session in get_session():
        try:
            # Build query with user isolation
            query = select(Task).where(Task.user_id == validated_input.user_id)

            # Apply status filter
            if validated_input.status == "pending":
                query = query.where(Task.is_complete == False)
            elif validated_input.status == "completed":
                query = query.where(Task.is_complete == True)
            # "all" or None -> no filter

            # Apply priority filter
            if validated_input.priority:
                try:
                    priority = Priority[validated_input.priority.upper()]
                    query = query.where(Task.priority == priority)
                except KeyError:
                    return MCPErrorOutput(
                        message=f"Invalid priority: {validated_input.priority}. Must be high, medium, or low.",
                        error_code=MCPErrorCode.INVALID_INPUT,
                        details={"priority": validated_input.priority},
                    ).model_dump()

            # Tag filtering will be done after fetching results
            # (SQLite doesn't support JSON array contains operations efficiently)

            # Apply sorting
            sort_by = validated_input.sort_by or "created_at"
            sort_order = validated_input.sort_order or "desc"

            # Map sort fields
            sort_field_map = {
                "id": Task.id,
                "title": Task.title,
                "priority": Task.priority,
                "due_date": Task.due_date,
                "created_at": Task.created_at,
            }

            if sort_by not in sort_field_map:
                return MCPErrorOutput(
                    message=f"Invalid sort_by field: {sort_by}. Must be one of: {', '.join(sort_field_map.keys())}",
                    error_code=MCPErrorCode.INVALID_INPUT,
                    details={"sort_by": sort_by},
                ).model_dump()

            sort_column = sort_field_map[sort_by]

            if sort_order == "asc":
                query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(sort_column.desc())

            # Execute query
            result = await session.execute(query)
            tasks = result.scalars().all()

            # Apply tag filter (post-query for SQLite compatibility)
            if validated_input.tag:
                tasks = [task for task in tasks if validated_input.tag in (task.tags or [])]

            # Convert tasks to TaskItem format
            task_items = []
            for task in tasks:
                task_items.append(
                    TaskItem(
                        id=task.id,
                        title=task.title,
                        description=task.description,
                        is_complete=task.is_complete,
                        priority=task.priority.value if task.priority else None,
                        tags=task.tags or [],
                        due_date=task.due_date.isoformat() if task.due_date else None,
                        due_time=task.due_time.isoformat() if task.due_time else None,
                        recurrence=task.recurrence.value if task.recurrence else None,
                        created_at=task.created_at.isoformat(),
                    )
                )

            # Return success response
            return ListTasksOutput(
                status="success",
                message=f"Found {len(task_items)} task(s).",
                tasks=task_items,
                count=len(task_items),
            ).model_dump()

        except Exception as e:
            return MCPErrorOutput(
                message=f"Database error: {str(e)}",
                error_code=MCPErrorCode.DATABASE_ERROR,
                details={"error": str(e)},
            ).model_dump()
