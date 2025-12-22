"""Search tasks MCP tool for finding tasks by keyword.

This tool allows the AI agent to search for tasks containing specific keywords.

Task: T080-T084 - Implement search_tasks MCP tool
Spec: specs/003-phase3-ai-chatbot/contracts/mcp-tools.md
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List
from app.models.task import Task
import logging
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy import or_, func


logger = logging.getLogger(__name__)


class TaskItem(BaseModel):
    """Task item for search results."""
    id: int
    title: str
    description: str | None
    is_complete: bool
    priority: str | None
    tags: List[str]
    due_date: str | None  # ISO format
    due_time: str | None  # HH:MM:SS
    recurrence: str | None
    created_at: str  # ISO format


class SearchTasksInput(BaseModel):
    """Input schema for search_tasks tool."""
    user_id: str = Field(..., description="User ID from JWT token")
    keyword: str = Field(..., min_length=1, max_length=200, description="Search keyword")


class SearchTasksOutput(BaseModel):
    """Output schema for search_tasks tool."""
    tasks: List[TaskItem] = Field(..., description="List of tasks matching keyword")
    count: int = Field(..., description="Number of matching tasks")
    status: str = Field(..., pattern="^(success|error)$")
    message: str | None = Field(None)


async def search_tasks(input_data: dict) -> dict:
    """Search tasks by keyword in title and description.

    Args:
        input_data: Dictionary with user_id and keyword

    Returns:
        SearchTasksOutput dict with matching tasks
    """
    from app.core.database import get_session  # Import here to avoid circular dependency

    # Validate input with Pydantic
    try:
        validated_input = SearchTasksInput(**input_data)
    except Exception as e:
        return SearchTasksOutput(
            tasks=[],
            count=0,
            status="error",
            message=f"Invalid input: {str(e)}"
        ).model_dump()

    try:
        # Get database session
        async for session in get_session():
            # Search for tasks containing the keyword in title or description (case-insensitive)
            keyword_lower = validated_input.keyword.lower()
            search_pattern = f"%{keyword_lower}%"

            query = select(Task).where(
                Task.user_id == validated_input.user_id
            ).where(
                or_(
                    func.lower(Task.title).like(search_pattern),
                    func.lower(func.coalesce(Task.description, "")).like(search_pattern)
                )
            )

            result = await session.execute(query)
            tasks = result.scalars().all()

            # Convert to TaskItem format
            task_items = []
            for task in tasks:
                task_item = TaskItem(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    is_complete=task.is_complete,
                    priority=task.priority.value if task.priority else None,
                    tags=task.tags if task.tags else [],
                    due_date=task.due_date.isoformat() if task.due_date else None,
                    due_time=task.due_time.strftime("%H:%M:%S") if task.due_time else None,
                    recurrence=task.recurrence.value if task.recurrence else None,
                    created_at=task.created_at.isoformat()
                )
                task_items.append(task_item)

            return SearchTasksOutput(
                tasks=task_items,
                count=len(task_items),
                status="success",
                message=f"Found {len(task_items)} tasks matching '{validated_input.keyword}'" if task_items else f"No tasks found matching '{validated_input.keyword}'"
            ).model_dump()

    except Exception as e:
        logger.error(f"Error searching tasks with keyword '{validated_input.keyword}': {str(e)}")
        return SearchTasksOutput(
            tasks=[],
            count=0,
            status="error",
            message=f"Error searching tasks: {str(e)}"
        ).model_dump()