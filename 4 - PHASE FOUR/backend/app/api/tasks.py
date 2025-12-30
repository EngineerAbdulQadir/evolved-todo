"""
Task API endpoints.

This module provides REST API endpoints for task CRUD operations with multi-tenant support.

References:
- Task: T120-T122 [US3] - Multi-tenant task management
- specs/005-multi-tenant-collab/contracts/tasks.yaml
- ADR-001: Multi-Tenant Data Isolation Strategy
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.middleware.auth import get_current_user_id, validate_user_ownership
from app.models import PermissionDeniedError
from app.schemas.task import (
    TaskAssign,
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)
from app.services import task_service
from app.services.task_service import TaskNotFoundError


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get(
    "/{user_id}",
    response_model=TaskListResponse,
    summary="Get all tasks for user",
    description="Retrieve all tasks belonging to the authenticated user with optional filters, sorting, and multi-tenant scoping",
)
async def get_tasks(
    user_id: str,
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
    due_date_filter: Optional[str] = None,
    project_id: Optional[UUID] = None,
    team_id: Optional[UUID] = None,
    organization_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> TaskListResponse:
    """
    Get all tasks for a specific user with optional filtering and sorting.

    Args:
        user_id: User ID from path parameter
        completed: Filter by completion status (T147)
        priority: Filter by priority level (T147)
        tag: Filter by tag (T147)
        search: Search in title/description (T162)
        sort_by: Field to sort by (T176): created_at, due_date, priority, title, completed
        sort_order: Sort order (T176): asc, desc
        due_date_filter: Filter by due date range (T205): overdue, today, this_week
        project_id: Filter by project UUID (Phase 3.1 T121)
        team_id: Filter by team UUID (Phase 3.1 T121)
        organization_id: Filter by organization UUID (Phase 3.1 T121)
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        TaskListResponse with filtered and sorted list of tasks

    Raises:
        HTTPException 403: If user tries to access another user's tasks

    Task: T121 [US3] - Add multi-tenant filters to GET /tasks
    """
    # Validate user can only access their own tasks
    validate_user_ownership(user_id, current_user_id)

    # Get tasks with filters and sorting (T147-T149, T162-T164, T176-T179, T205-T207, T121)
    tasks = await task_service.get_user_tasks(
        db,
        user_id,
        completed=completed,
        priority=priority,
        tag=tag,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        due_date_filter=due_date_filter,
        project_id=project_id,
        team_id=team_id,
        organization_id=organization_id,
    )

    return TaskListResponse(tasks=tasks, total=len(tasks))


@router.post(
    "/{user_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new task",
    description="Create a new task for the authenticated user within a project (Phase 3.1)",
)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    project_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> TaskResponse:
    """
    Create a new task.

    Args:
        user_id: User ID from path parameter
        task_data: Task creation data
        project_id: Project UUID (optional, Phase 3.1)
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        TaskResponse with created task

    Raises:
        HTTPException 400: If validation fails
        HTTPException 403: If user tries to create task for another user or not project member
        HTTPException 404: If project not found

    Task: T120 [US3] - Add project_id parameter to POST /tasks
    """
    # Validate user can only create tasks for themselves
    validate_user_ownership(user_id, current_user_id)

    try:
        task = await task_service.create_task(db, user_id, task_data, project_id=project_id)
        return TaskResponse.model_validate(task)
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.put(
    "/{user_id}/{task_id}",
    response_model=TaskResponse,
    summary="Update task",
    description="Update an existing task",
)
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> TaskResponse:
    """
    Update an existing task.

    Args:
        user_id: User ID from path parameter
        task_id: Task ID to update
        task_data: Task update data
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        TaskResponse with updated task

    Raises:
        HTTPException 400: If validation fails
        HTTPException 403: If user tries to update another user's task
        HTTPException 404: If task not found
    """
    # Validate user can only update their own tasks
    validate_user_ownership(user_id, current_user_id)

    try:
        task = await task_service.update_task(db, task_id, user_id, task_data)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found",
            )

        return TaskResponse.model_validate(task)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete(
    "/{user_id}/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Delete a task permanently",
)
async def delete_task(
    user_id: str,
    task_id: int,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> None:
    """
    Delete a task.

    Args:
        user_id: User ID from path parameter
        task_id: Task ID to delete
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Raises:
        HTTPException 403: If user tries to delete another user's task
        HTTPException 404: If task not found
    """
    # Validate user can only delete their own tasks
    validate_user_ownership(user_id, current_user_id)

    deleted = await task_service.delete_task(db, task_id, user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )


@router.patch(
    "/{user_id}/{task_id}/complete",
    response_model=TaskResponse,
    summary="Toggle task completion",
    description="Mark task as complete or incomplete",
)
async def toggle_complete(
    user_id: str,
    task_id: int,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> TaskResponse:
    """
    Toggle task completion status.

    Args:
        user_id: User ID from path parameter
        task_id: Task ID to toggle
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        TaskResponse with updated task

    Raises:
        HTTPException 403: If user tries to update another user's task
        HTTPException 404: If task not found
    """
    # Validate user can only update their own tasks
    validate_user_ownership(user_id, current_user_id)

    task = await task_service.toggle_task_complete(db, task_id, user_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )

    return TaskResponse.model_validate(task)


@router.patch(
    "/{task_id}/assign",
    response_model=TaskResponse,
    summary="Assign task to project member",
    description="Assign task to a user who is a project member (Phase 3.1)",
)
async def assign_task(
    task_id: int,
    assignment_data: TaskAssign,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> TaskResponse:
    """
    Assign task to a project member.

    Args:
        task_id: Task ID to assign
        assignment_data: Assignment data with assigned_to user ID
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        TaskResponse with updated task assignment

    Raises:
        HTTPException 400: If task has no project_id
        HTTPException 403: If assignee is not a project member
        HTTPException 404: If task not found

    Task: T122 [US3] - Implement PATCH /tasks/{task_id}/assign
    """
    try:
        task = await task_service.assign_task(
            db=db,
            task_id=task_id,
            assigned_to_user_id=assignment_data.assigned_to,
            assigned_by_user_id=current_user_id,
        )
        return TaskResponse.model_validate(task)
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
