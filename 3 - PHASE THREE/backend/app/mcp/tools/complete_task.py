"""Complete task MCP tool for marking tasks as complete.

This tool allows the AI agent to mark tasks as complete through natural language commands.
It also handles recurring task logic by creating the next occurrence when applicable.

Task: T043-T046 - Implement complete_task MCP tool with recurring task logic
Spec: specs/003-phase3-ai-chatbot/contracts/mcp-tools.md
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.task import Task, RecurrencePattern
from app.services.task_service import get_task_by_id
from app.services.recurrence_service import RecurrenceService
from app.mcp.schemas import MCPErrorCode, MCPErrorOutput, MCPToolInput, MCPToolOutput


class CompleteTaskInput(MCPToolInput):
    """
    Input schema for complete_task MCP tool.

    Task: T044 - Define CompleteTaskInput schema
    """

    user_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User ID from JWT token for data isolation",
        examples=["user_123", "auth0|abc123"],
    )
    task_id: int = Field(
        ...,
        ge=1,
        description="Task ID to mark as complete",
        examples=[1, 42, 100],
    )


class CompleteTaskOutput(MCPToolOutput):
    """
    Output schema for complete_task MCP tool.

    Task: T045 - Define CompleteTaskOutput schema
    """

    task_id: int = Field(..., description="ID of the completed task")
    title: str = Field(..., description="Task title for confirmation")
    status: str = Field(..., description="New status of the task", examples=["completed"])
    next_occurrence_date: Optional[str] = Field(
        None,
        description="Date of next occurrence for recurring tasks (YYYY-MM-DD)",
        examples=["2025-12-21", "2025-12-28"],
    )
    message: str = Field(..., description="Human-readable confirmation message")


async def complete_task(input_data: dict) -> dict:
    """
    Mark a task as complete and handle recurring tasks.

    Task: T043 - Implement complete_task MCP tool
    Task: T046 - Implement recurring task logic

    Args:
        input_data: Dictionary with user_id and task_id from AI agent

    Returns:
        CompleteTaskOutput dict with completion details

    Examples:
        Agent extracts from "Mark task 3 as complete":
        - user_id: "user_123"
        - task_id: 3

        Agent extracts from "Complete grocery shopping task":
        - user_id: "user_123"
        - task_id: 15 (from search context)
    """
    # Validate input with Pydantic
    try:
        validated_input = CompleteTaskInput(**input_data)
    except Exception as e:
        return MCPErrorOutput(
            message=f"Invalid input: {str(e)}",
            error_code=MCPErrorCode.INVALID_INPUT,
            details={"input": input_data},
        ).model_dump()

    # Get database session
    from app.core.database import get_session  # Import here to avoid circular dependency
    async for session in get_session():
        try:
            # Get the task to complete
            task = await get_task_by_id(session, validated_input.task_id, validated_input.user_id)
            if not task:
                return MCPErrorOutput(
                    message=f"Task with ID {validated_input.task_id} not found or doesn't belong to user",
                    error_code=MCPErrorCode.NOT_FOUND,
                    details={"task_id": validated_input.task_id, "user_id": validated_input.user_id},
                ).model_dump()

            # Check if task is already complete
            if task.is_complete:
                return MCPErrorOutput(
                    message=f"Task '{task.title}' (ID: {task.id}) is already marked as complete",
                    error_code=MCPErrorCode.INVALID_INPUT,
                    details={"task_id": task.id, "status": "already_complete"},
                ).model_dump()

            # Mark the task as complete
            task.is_complete = True
            task.completed_at = datetime.utcnow()
            session.add(task)
            await session.commit()
            await session.refresh(task)

            # Handle recurring task logic
            next_occurrence_date = None
            recurrence_service = RecurrenceService()
            new_task = None

            # Only process recurrence if the task has a recurrence pattern
            if task.recurrence and task.recurrence != RecurrencePattern.NONE:
                # Create the next occurrence of the recurring task
                new_task = await recurrence_service.create_next_instance(session, task)
                if new_task and new_task.due_date:
                    next_occurrence_date = new_task.due_date.isoformat()

            # Return success response
            message = f"Task '{task.title}' marked as complete."
            if next_occurrence_date:
                message += f" Next occurrence scheduled for {next_occurrence_date}."

            return CompleteTaskOutput(
                message=message,
                task_id=task.id,
                title=task.title,
                status="completed",
                next_occurrence_date=next_occurrence_date,
            ).model_dump()

        except Exception as e:
            return MCPErrorOutput(
                message=f"Database error: {str(e)}",
                error_code=MCPErrorCode.DATABASE_ERROR,
                details={"error": str(e)},
            ).model_dump()