"""Delete task MCP tool for removing tasks.

This tool allows the AI agent to delete tasks based on user commands.

Task: T070-T074 - Implement delete_task MCP tool
Spec: specs/003-phase3-ai-chatbot/contracts/mcp-tools.md
"""

from pydantic import BaseModel, Field
from datetime import datetime
from app.models.task import Task
from app.services.task_service import get_task_by_id
import logging
from sqlmodel.ext.asyncio.session import AsyncSession


logger = logging.getLogger(__name__)


class DeleteTaskInput(BaseModel):
    """Input schema for delete_task tool."""
    user_id: str = Field(..., description="User ID from JWT token")
    task_id: int = Field(..., ge=1, description="Task ID to delete")


class DeleteTaskOutput(BaseModel):
    """Output schema for delete_task tool."""
    task_id: int = Field(..., description="Deleted task ID")
    status: str = Field(..., pattern="^(deleted|error)$")
    title: str = Field(..., description="Deleted task title (confirmation)")
    message: str | None = Field(None)


async def delete_task(input_data: dict) -> dict:
    """Delete a task by ID.

    Args:
        input_data: Dictionary with user_id and task_id

    Returns:
        DeleteTaskOutput dict with status and confirmation
    """
    from app.core.database import get_session  # Import here to avoid circular dependency

    # Validate input with Pydantic
    try:
        validated_input = DeleteTaskInput(**input_data)
    except Exception as e:
        return DeleteTaskOutput(
            task_id=input_data.get("task_id", 0),
            status="error",
            title="",
            message=f"Invalid input: {str(e)}"
        ).model_dump()

    try:
        # Get database session
        async for session in get_session():
            # First, get the task to delete
            task = await get_task_by_id(session, validated_input.task_id, validated_input.user_id)
            if not task:
                return DeleteTaskOutput(
                    task_id=validated_input.task_id,
                    status="error",
                    title="",
                    message=f"Task with ID {validated_input.task_id} not found"
                ).model_dump()

            # Store title for confirmation
            task_title = task.title

            # Delete the task
            await session.delete(task)
            await session.commit()

            return DeleteTaskOutput(
                task_id=task.id,
                status="deleted",
                title=task_title,
                message=f"Task '{task_title}' has been deleted successfully"
            ).model_dump()

    except Exception as e:
        logger.error(f"Error deleting task {validated_input.task_id}: {str(e)}")
        return DeleteTaskOutput(
            task_id=validated_input.task_id,
            status="error",
            title="",
            message=f"Error deleting task: {str(e)}"
        ).model_dump()