"""Add task MCP tool for natural language task creation.

This tool allows the AI agent to create new tasks through natural language commands.

Task: T023-T025 - Implement add_task MCP tool with schemas
Task: T125 [US3] - Add project_id parameter for multi-tenant support
Spec: specs/003-phase3-ai-chatbot/contracts/mcp-tools.md
"""

from datetime import date, time
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import Priority, RecurrencePattern, PermissionDeniedError
from app.mcp.schemas import MCPErrorCode, MCPErrorOutput, MCPToolInput, MCPToolOutput
from app.schemas.task import TaskCreate
from app.services import task_service


class AddTaskInput(MCPToolInput):
    """
    Input schema for add_task MCP tool.

    Task: T024 - Define AddTaskInput schema
    Task: T125 [US3] - Add project_id for multi-tenant support
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title (required)",
        examples=["Buy groceries", "Dentist appointment at 3 PM"],
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional task description",
        examples=["Get milk, eggs, and bread"],
    )
    priority: Optional[str] = Field(
        None,
        description="Task priority: 'high', 'medium', or 'low'",
        examples=["high", "medium", "low"],
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Category tags for organization",
        examples=[["work", "urgent"], ["personal", "health"]],
    )
    due_date: Optional[str] = Field(
        None,
        description="Due date in YYYY-MM-DD format",
        examples=["2025-12-25", "2025-01-15"],
    )
    due_time: Optional[str] = Field(
        None,
        description="Due time in HH:MM format (24-hour)",
        examples=["14:30", "09:00", "17:00"],
    )
    recurrence: Optional[str] = Field(
        None,
        description="Recurrence pattern: 'daily', 'weekly', or 'monthly'",
        examples=["daily", "weekly", "monthly"],
    )
    recurrence_day: Optional[int] = Field(
        None,
        ge=1,
        le=31,
        description="Day for recurrence (1-7 for weekly, 1-31 for monthly)",
        examples=[1, 15, 7],
    )
    project_id: Optional[str] = Field(
        None,
        description="Project UUID (Phase 3.1 multi-tenant support)",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )


class AddTaskOutput(MCPToolOutput):
    """
    Output schema for add_task MCP tool.

    Task: T025 - Define AddTaskOutput schema
    """

    task_id: Optional[int] = Field(None, description="Created task ID")
    title: str = Field(..., description="Task title")
    priority: Optional[str] = Field(None, description="Task priority")
    due_date: Optional[str] = Field(None, description="Task due date")
    tags: Optional[List[str]] = Field(None, description="Task tags")


async def add_task(input_data: dict) -> dict:
    """
    Create a new task from natural language input.

    Task: T023 - Implement add_task MCP tool
    Task: T125 [US3] - Update to use task_service with project_id support

    Args:
        input_data: Dictionary with task fields from AI agent

    Returns:
        AddTaskOutput dict with created task details

    Examples:
        Agent extracts from "Add a task to buy groceries tomorrow":
        - title: "Buy groceries"
        - due_date: "2025-12-20" (tomorrow)

        Agent extracts from "Create high priority work task for meeting in Mobile App project":
        - title: "Meeting"
        - priority: "high"
        - tags: ["work"]
        - project_id: "uuid-here"
    """
    # Validate input with Pydantic
    try:
        validated_input = AddTaskInput(**input_data)
    except Exception as e:
        return MCPErrorOutput(
            message=f"Invalid input: {str(e)}",
            error_code=MCPErrorCode.INVALID_INPUT,
            details={"input": input_data},
        ).model_dump()

    # Get database session
    async for session in get_session():
        try:
            # Parse priority
            priority = None
            if validated_input.priority:
                try:
                    priority = Priority[validated_input.priority.upper()]
                except KeyError:
                    return MCPErrorOutput(
                        message=f"Invalid priority: {validated_input.priority}. Must be high, medium, or low.",
                        error_code=MCPErrorCode.INVALID_INPUT,
                        details={"priority": validated_input.priority},
                    ).model_dump()

            # Parse due_date
            parsed_due_date = None
            if validated_input.due_date:
                try:
                    parsed_due_date = date.fromisoformat(validated_input.due_date)
                except ValueError:
                    return MCPErrorOutput(
                        message=f"Invalid date format: {validated_input.due_date}. Use YYYY-MM-DD.",
                        error_code=MCPErrorCode.INVALID_INPUT,
                        details={"due_date": validated_input.due_date},
                    ).model_dump()

            # Parse due_time
            parsed_due_time = None
            if validated_input.due_time:
                try:
                    hour, minute = map(int, validated_input.due_time.split(":"))
                    parsed_due_time = time(hour=hour, minute=minute)
                except (ValueError, AttributeError):
                    return MCPErrorOutput(
                        message=f"Invalid time format: {validated_input.due_time}. Use HH:MM.",
                        error_code=MCPErrorCode.INVALID_INPUT,
                        details={"due_time": validated_input.due_time},
                    ).model_dump()

            # Parse recurrence
            recurrence = None
            if validated_input.recurrence:
                try:
                    recurrence = RecurrencePattern[validated_input.recurrence.upper()]
                except KeyError:
                    return MCPErrorOutput(
                        message=f"Invalid recurrence: {validated_input.recurrence}. Must be daily, weekly, or monthly.",
                        error_code=MCPErrorCode.INVALID_INPUT,
                        details={"recurrence": validated_input.recurrence},
                    ).model_dump()

            # Parse project_id
            project_uuid = None
            if validated_input.project_id:
                try:
                    project_uuid = UUID(validated_input.project_id)
                except ValueError:
                    return MCPErrorOutput(
                        message=f"Invalid project_id format: {validated_input.project_id}. Must be a valid UUID.",
                        error_code=MCPErrorCode.INVALID_INPUT,
                        details={"project_id": validated_input.project_id},
                    ).model_dump()

            # Create TaskCreate schema
            task_data = TaskCreate(
                title=validated_input.title,
                description=validated_input.description,
                priority=priority,
                tags=validated_input.tags or [],
                due_date=parsed_due_date,
                due_time=parsed_due_time,
                recurrence=recurrence,
                recurrence_day=validated_input.recurrence_day,
            )

            # Create task using service layer (T125 - multi-tenant support)
            task = await task_service.create_task(
                db=session,
                user_id=validated_input.user_id,
                task_data=task_data,
                project_id=project_uuid,
            )

            # Return success response
            return AddTaskOutput(
                status="success",
                message=f"Task '{task.title}' created successfully.",
                task_id=task.id,
                title=task.title,
                priority=task.priority.value if task.priority else None,
                due_date=task.due_date.isoformat() if task.due_date else None,
                tags=task.tags,
            ).model_dump()

        except PermissionDeniedError as e:
            return MCPErrorOutput(
                message=str(e),
                error_code=MCPErrorCode.PERMISSION_DENIED,
                details={"user_id": validated_input.user_id, "project_id": validated_input.project_id},
            ).model_dump()
        except ValueError as e:
            if "not found" in str(e).lower():
                return MCPErrorOutput(
                    message=str(e),
                    error_code=MCPErrorCode.NOT_FOUND,
                    details={"project_id": validated_input.project_id},
                ).model_dump()
            return MCPErrorOutput(
                message=f"Validation error: {str(e)}",
                error_code=MCPErrorCode.INVALID_INPUT,
                details={"error": str(e)},
            ).model_dump()
        except Exception as e:
            return MCPErrorOutput(
                message=f"Database error: {str(e)}",
                error_code=MCPErrorCode.DATABASE_ERROR,
                details={"error": str(e)},
            ).model_dump()
