"""Update task MCP tool for modifying task properties.

This tool allows the AI agent to update task properties based on user commands.

Task: T060-T064 - Implement update_task MCP tool
Spec: specs/003-phase3-ai-chatbot/contracts/mcp-tools.md
"""

from pydantic import BaseModel, Field
from datetime import date, time, datetime
from typing import List, Optional
from app.models.task import Task, Priority, RecurrencePattern
from app.services.task_service import get_task_by_id
import logging
from sqlmodel.ext.asyncio.session import AsyncSession


logger = logging.getLogger(__name__)


class UpdateTaskInput(BaseModel):
    """Input schema for update_task tool."""
    user_id: str = Field(..., description="User ID from JWT token")
    task_id: int = Field(..., ge=1, description="Task ID to update")
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    priority: str | None = Field(None, pattern="^(high|medium|low)$")
    tags: str | None = Field(None, max_length=500)  # Comma-separated tags
    due_date: date | None = Field(None)
    due_time: time | None = Field(None)
    recurrence: str | None = Field(None, pattern="^(daily|weekly|monthly)$")
    recurrence_day: int | None = Field(None, ge=1, le=31)


class UpdateTaskOutput(BaseModel):
    """Output schema for update_task tool."""
    task_id: int = Field(..., description="Updated task ID")
    status: str = Field(..., pattern="^(updated|error)$")
    title: str = Field(..., description="Task title (confirmation)")
    updated_fields: List[str] = Field(..., description="List of fields that were updated")
    message: str | None = Field(None)


async def update_task(input_data: dict) -> dict:
    """Update a task by ID with provided fields.

    Args:
        input_data: Dictionary with user_id, task_id, and fields to update

    Returns:
        UpdateTaskOutput dict with status and updated fields
    """
    from app.core.database import get_session  # Import here to avoid circular dependency
    from dateutil import parser as date_parser

    # Pre-process date/time strings before Pydantic validation
    processed_data = input_data.copy()

    # Convert date string to date object if present
    if "due_date" in processed_data and processed_data["due_date"] is not None:
        if isinstance(processed_data["due_date"], str):
            try:
                parsed_date = date_parser.parse(processed_data["due_date"])
                processed_data["due_date"] = parsed_date.date()
            except Exception as e:
                return UpdateTaskOutput(
                    task_id=input_data.get("task_id", 0),
                    status="error",
                    title="",
                    updated_fields=[],
                    message=f"Invalid date format: {str(e)}"
                ).model_dump()

    # Convert time string to time object if present
    if "due_time" in processed_data and processed_data["due_time"] is not None:
        if isinstance(processed_data["due_time"], str):
            try:
                # Handle HH:MM:SS or HH:MM format
                time_str = processed_data["due_time"]
                if len(time_str.split(':')) == 2:
                    time_str += ":00"
                parsed_time = datetime.strptime(time_str, "%H:%M:%S").time()
                processed_data["due_time"] = parsed_time
            except Exception as e:
                return UpdateTaskOutput(
                    task_id=input_data.get("task_id", 0),
                    status="error",
                    title="",
                    updated_fields=[],
                    message=f"Invalid time format: {str(e)}"
                ).model_dump()

    # Validate input with Pydantic
    try:
        # Debug logging
        logger.info(f"[UPDATE_TASK] Processing input: {processed_data}")
        validated_input = UpdateTaskInput(**processed_data)
        logger.info(f"[UPDATE_TASK] Validation successful")
    except Exception as e:
        logger.error(f"[UPDATE_TASK] Validation error: {str(e)}")
        logger.error(f"[UPDATE_TASK] Input data: {processed_data}")
        return UpdateTaskOutput(
            task_id=input_data.get("task_id", 0),
            status="error",
            title="",
            updated_fields=[],
            message=f"Invalid input: {str(e)}"
        ).model_dump()

    try:
        # Get database session
        async for session in get_session():
            # First, get the task to update
            task = await get_task_by_id(session, validated_input.task_id, validated_input.user_id)
            if not task:
                return UpdateTaskOutput(
                    task_id=validated_input.task_id,
                    status="error",
                    title="",
                    updated_fields=[],
                    message=f"Task with ID {validated_input.task_id} not found"
                ).model_dump()

            # Track which fields were updated
            updated_fields = []

            # Update fields if provided
            if validated_input.title is not None:
                task.title = validated_input.title
                updated_fields.append("title")

            if validated_input.description is not None:
                task.description = validated_input.description
                updated_fields.append("description")

            if validated_input.priority is not None:
                # Convert string to Priority enum
                try:
                    task.priority = Priority[validated_input.priority.upper()]
                    updated_fields.append("priority")
                except KeyError:
                    logger.error(f"[UPDATE_TASK] Invalid priority: {validated_input.priority}")
                    return UpdateTaskOutput(
                        task_id=validated_input.task_id,
                        status="error",
                        title="",
                        updated_fields=[],
                        message=f"Invalid priority value: {validated_input.priority}"
                    ).model_dump()

            if validated_input.tags is not None:
                # Convert comma-separated string to list
                tag_list = [tag.strip() for tag in validated_input.tags.split(",") if tag.strip()]
                task.tags = tag_list
                updated_fields.append("tags")

            if validated_input.due_date is not None:
                logger.info(f"[UPDATE_TASK] Setting due_date to: {validated_input.due_date}")
                task.due_date = validated_input.due_date
                updated_fields.append("due_date")

            if validated_input.due_time is not None:
                logger.info(f"[UPDATE_TASK] Setting due_time to: {validated_input.due_time}")
                task.due_time = validated_input.due_time
                updated_fields.append("due_time")

            if validated_input.recurrence is not None:
                # Convert string to RecurrencePattern enum
                try:
                    logger.info(f"[UPDATE_TASK] Setting recurrence to: {validated_input.recurrence}")
                    task.recurrence = RecurrencePattern[validated_input.recurrence.upper()]
                    updated_fields.append("recurrence")
                except KeyError:
                    logger.error(f"[UPDATE_TASK] Invalid recurrence: {validated_input.recurrence}")
                    return UpdateTaskOutput(
                        task_id=validated_input.task_id,
                        status="error",
                        title="",
                        updated_fields=[],
                        message=f"Invalid recurrence value: {validated_input.recurrence}"
                    ).model_dump()

            if validated_input.recurrence_day is not None:
                task.recurrence_day = validated_input.recurrence_day
                updated_fields.append("recurrence_day")

            # Commit changes
            session.add(task)
            await session.commit()
            await session.refresh(task)

            return UpdateTaskOutput(
                task_id=task.id,
                status="updated",
                title=task.title,
                updated_fields=updated_fields,
                message=f"Task updated successfully. Fields updated: {', '.join(updated_fields)}"
            ).model_dump()

    except Exception as e:
        logger.error(f"Error updating task {validated_input.task_id}: {str(e)}")
        return UpdateTaskOutput(
            task_id=validated_input.task_id,
            status="error",
            title="",
            updated_fields=[],
            message=f"Error updating task: {str(e)}"
        ).model_dump()