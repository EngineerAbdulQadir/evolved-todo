"""
Task service for CRUD operations and business logic.

This module provides functions for managing tasks with multi-user isolation
and multi-tenant organization → team → project → task hierarchy.

References:
- Task: T108-T111 [US3] - Multi-tenant task scoping and assignment
- ADR-001: Multi-Tenant Data Isolation Strategy
- ADR-003: Soft Delete and Audit Trail Strategy
- Constitution v5.0.0 Principle XIX: Multi-Tenancy & Data Isolation Hierarchy
"""

from datetime import datetime, UTC
from typing import List, Optional
from uuid import UUID

from sqlalchemy import cast, String
from sqlmodel import select, or_, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.task import Task
from app.models import Project, ProjectMember, PermissionDeniedError
from app.schemas.task import TaskCreate, TaskUpdate
from app.services import audit_service


class TaskNotFoundError(Exception):
    """Raised when task is not found."""
    pass


async def get_user_tasks(
    db: AsyncSession,
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
) -> List[Task]:
    """
    Get all tasks for a specific user with optional filtering and sorting.

    Args:
        db: Database session
        user_id: User's unique identifier
        completed: Filter by completion status (T148)
        priority: Filter by priority level (T148)
        tag: Filter by tag (T148)
        search: Search in title/description (T163-T164)
        sort_by: Field to sort by (T177-T178): created_at, due_date, priority, title, completed
        sort_order: Sort order (T179): asc, desc
        due_date_filter: Filter by due date range (T205): overdue, today, this_week
        project_id: Filter by project UUID (Phase 3.1)
        team_id: Filter by team UUID (Phase 3.1)
        organization_id: Filter by organization UUID (Phase 3.1)

    Returns:
        List of Task objects matching filters (T149 - AND logic) and sorted (T177)

    Task: T109 [US3] - Filter by project_id + organization_id + deleted_at IS NULL
    """
    # Start with base query filtering by user and excluding soft-deleted tasks
    query = select(Task).where(
        Task.user_id == user_id,
        Task.deleted_at.is_(None)  # Phase 3.1: Exclude soft-deleted tasks
    )

    # Multi-tenant filtering (Phase 3.1)
    if project_id is not None:
        query = query.where(Task.project_id == project_id)
    if team_id is not None:
        query = query.where(Task.team_id == team_id)
    if organization_id is not None:
        query = query.where(Task.organization_id == organization_id)

    # Apply filters with AND logic (T149)
    if completed is not None:
        query = query.where(Task.is_complete == completed)

    if priority is not None:
        query = query.where(Task.priority == priority)

    if tag is not None:
        # Filter tasks that contain the specified tag (T148)
        # Use database-agnostic approach: cast JSON to text and check if tag is present
        # This works with both SQLite and PostgreSQL
        tag_pattern = f'%"{tag}"%'
        query = query.where(cast(Task.tags, String).like(tag_pattern))

    if search is not None:
        # Case-insensitive search in title and description (T163-T164)
        # Use lower() for database-agnostic case-insensitive search
        search_lower = search.lower()
        search_pattern = f"%{search_lower}%"
        # Handle null description with coalesce
        query = query.where(
            or_(
                func.lower(Task.title).like(search_pattern),
                func.lower(func.coalesce(Task.description, "")).like(search_pattern)
            )
        )

    # Apply due date filtering (T205-T207)
    if due_date_filter is not None:
        from datetime import date, timedelta

        today = date.today()

        if due_date_filter == "overdue":
            # Overdue: due_date < today AND incomplete (T207)
            query = query.where(
                Task.due_date < today,
                Task.is_complete == False
            )
        elif due_date_filter == "today":
            # Due today: due_date == today (T206)
            query = query.where(Task.due_date == today)
        elif due_date_filter == "this_week":
            # Due this week: due_date between today and +7 days (T206)
            week_end = today + timedelta(days=7)
            query = query.where(
                Task.due_date >= today,
                Task.due_date <= week_end
            )

    # Apply sorting (T177-T179)
    if sort_by and sort_order:
        # Map sort field names to Task model attributes
        sort_fields = {
            "created_at": Task.created_at,
            "due_date": Task.due_date,
            "priority": Task.priority,
            "title": Task.title,
            "completed": Task.is_complete,
        }

        sort_field = sort_fields.get(sort_by, Task.created_at)

        if sort_order == "asc":
            query = query.order_by(sort_field.asc())
        else:
            query = query.order_by(sort_field.desc())
    else:
        # Default: order by creation date descending
        query = query.order_by(Task.created_at.desc())

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_task_by_id(
    db: AsyncSession, task_id: int, user_id: str
) -> Optional[Task]:
    """
    Get a specific task by ID with user ownership validation.

    Args:
        db: Database session
        task_id: Task ID
        user_id: User ID for ownership validation

    Returns:
        Task object if found and owned by user, None otherwise
    """
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_task(
    db: AsyncSession,
    user_id: str,
    task_data: TaskCreate,
    project_id: Optional[UUID] = None,
) -> Task:
    """
    Create a new task for a user within a project (Phase 3.1).

    Args:
        db: Database session
        user_id: User ID (creator of the task)
        task_data: Task creation data
        project_id: Project UUID (required for Phase 3.1 multi-tenant tasks)

    Returns:
        Created Task object

    Raises:
        ValueError: If validation fails
        PermissionDeniedError: If user is not project member

    Task: T108 [US3] - Add multi-tenant scoping, validate project membership
    """
    # Validate due_time requires due_date
    if task_data.due_time and not task_data.due_date:
        raise ValueError("Due time requires a due date")

    # Validate recurrence_day requirements
    if task_data.recurrence == "weekly" and task_data.recurrence_day:
        if not (1 <= task_data.recurrence_day <= 7):
            raise ValueError("Weekly recurrence requires day 1-7 (Mon-Sun)")
    elif task_data.recurrence == "monthly" and task_data.recurrence_day:
        if not (1 <= task_data.recurrence_day <= 31):
            raise ValueError("Monthly recurrence requires day 1-31")

    # Multi-tenant validation (Phase 3.1)
    organization_id = None
    team_id = None

    if project_id:
        # Get project and validate it exists
        project_query = select(Project).where(
            Project.id == project_id,
            Project.deleted_at.is_(None)
        )
        project_result = await db.execute(project_query)
        project = project_result.scalar_one_or_none()

        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Verify user is project member or org admin (implicit contributor permission)
        member_query = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        member_result = await db.execute(member_query)
        member = member_result.scalar_one_or_none()

        if not member:
            raise PermissionDeniedError(
                f"User {user_id} is not a member of project {project_id}"
            )

        # Set multi-tenant fields from project
        organization_id = project.organization_id
        team_id = project.team_id

    # Create task
    new_task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        tags=task_data.tags,
        due_date=task_data.due_date,
        due_time=task_data.due_time,
        recurrence=task_data.recurrence,
        recurrence_day=task_data.recurrence_day,
        # Multi-tenant fields (Phase 3.1)
        project_id=project_id,
        organization_id=organization_id,
        team_id=team_id,
        assigned_to=None,  # Can be assigned later via assign_task()
        deleted_at=None,
    )

    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    # Audit logging (T129 - ADR-003)
    if project_id and organization_id:
        await audit_service.log_action(
            session=db,
            organization_id=organization_id,
            user_id=UUID(user_id),
            resource_type="task",
            resource_id=UUID(str(new_task.id)),  # Convert int to UUID for audit
            action="create",
            context={
                "title": new_task.title,
                "project_id": str(project_id),
                "team_id": str(team_id),
                "organization_id": str(organization_id),
            },
        )
        await db.commit()

    return new_task


async def update_task(
    db: AsyncSession, task_id: int, user_id: str, task_data: TaskUpdate
) -> Optional[Task]:
    """
    Update an existing task.

    Args:
        db: Database session
        task_id: Task ID to update
        user_id: User ID for ownership validation
        task_data: Task update data

    Returns:
        Updated Task object if found, None otherwise

    Raises:
        ValueError: If validation fails
    """
    # Get existing task
    task = await get_task_by_id(db, task_id, user_id)
    if not task:
        return None

    # Update fields if provided
    update_dict = task_data.model_dump(exclude_unset=True)

    for field, value in update_dict.items():
        setattr(task, field, value)

    # Validate due_time requires due_date
    if task.due_time and not task.due_date:
        raise ValueError("Due time requires a due date")

    await db.commit()
    await db.refresh(task)

    return task


async def delete_task(db: AsyncSession, task_id: int, user_id: str) -> bool:
    """
    Soft delete a task (set deleted_at timestamp).

    Task: T201 [US8] - Verify all delete operations use soft delete

    Args:
        db: Database session
        task_id: Task ID to delete
        user_id: User ID for ownership validation

    Returns:
        True if task was deleted, False if not found
    """
    from datetime import datetime, UTC
    from app.services import audit_service
    from uuid import UUID

    task = await get_task_by_id(db, task_id, user_id)
    if not task:
        return False

    # Soft delete (set deleted_at timestamp)
    task.deleted_at = datetime.now(UTC)
    await db.commit()

    # Audit logging
    await audit_service.log_action(
        session=db,
        organization_id=task.organization_id,
        user_id=UUID(user_id),
        resource_type="task",
        resource_id=task.id,
        action="soft_delete",
        context={
            "title": task.title,
            "project_id": str(task.project_id),
        },
    )
    await db.commit()

    return True


async def recover_task(db: AsyncSession, task_id: int, user_id: str) -> Optional[Task]:
    """
    Recover soft-deleted task (clear deleted_at timestamp).

    Task: T200 [US8] - Implement recover_task()

    Args:
        db: Database session
        task_id: Task ID to recover
        user_id: User ID for ownership validation

    Returns:
        Recovered Task instance if found and deleted, None otherwise
    """
    from datetime import datetime, UTC
    from app.services import audit_service
    from uuid import UUID

    # Get task (including deleted)
    stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        return None

    # Verify task is actually deleted
    if task.deleted_at is None:
        return None

    # Clear deleted_at timestamp
    task.deleted_at = None
    await db.commit()
    await db.refresh(task)

    # Audit logging
    await audit_service.log_action(
        session=db,
        organization_id=task.organization_id,
        user_id=UUID(user_id),
        resource_type="task",
        resource_id=task.id,
        action="recover",
        context={
            "title": task.title,
            "project_id": str(task.project_id),
            "recovered_by": user_id,
        },
    )
    await db.commit()

    return task


async def toggle_task_complete(
    db: AsyncSession, task_id: int, user_id: str
) -> Optional[Task]:
    """
    Toggle task completion status and create next instance for recurring tasks (T192).

    When a recurring task is marked complete, a new instance is automatically
    created with the next due date.

    Args:
        db: Database session
        task_id: Task ID to toggle
        user_id: User ID for ownership validation

    Returns:
        Updated Task object if found, None otherwise
    """
    from datetime import datetime
    from app.services.recurrence_service import RecurrenceService

    task = await get_task_by_id(db, task_id, user_id)
    if not task:
        return None

    was_complete = task.is_complete
    task.is_complete = not task.is_complete

    # Set completed_at timestamp when marking complete (T118)
    # Clear completed_at when marking incomplete (T119)
    if task.is_complete:
        task.completed_at = datetime.utcnow()
    else:
        task.completed_at = None

    await db.commit()
    await db.refresh(task)

    # Create next instance if marking complete and task is recurring (T192)
    if task.is_complete and not was_complete:
        recurrence_service = RecurrenceService()
        await recurrence_service.create_next_instance(db, task)

    return task


async def assign_task(
    db: AsyncSession,
    task_id: int,
    assigned_to_user_id: str,
    assigned_by_user_id: str,
) -> Task:
    """
    Assign task to a project member (Phase 3.1).

    Args:
        db: Database session
        task_id: Task ID to assign
        assigned_to_user_id: User ID to assign the task to
        assigned_by_user_id: User ID performing assignment

    Returns:
        Updated Task object with assignment

    Raises:
        TaskNotFoundError: If task not found
        PermissionDeniedError: If assignee is not project member
        ValueError: If task has no project_id

    Task: T110 [US3] - Validate assignee is project member
    """
    # Get task
    task_query = select(Task).where(
        Task.id == task_id,
        Task.deleted_at.is_(None)
    )
    task_result = await db.execute(task_query)
    task = task_result.scalar_one_or_none()

    if not task:
        raise TaskNotFoundError(f"Task {task_id} not found")

    # Validate task has project_id (required for assignment)
    if not task.project_id:
        raise ValueError("Cannot assign tasks without a project")

    # Verify assignee is project member
    member_query = select(ProjectMember).where(
        ProjectMember.project_id == task.project_id,
        ProjectMember.user_id == assigned_to_user_id,
    )
    member_result = await db.execute(member_query)
    member = member_result.scalar_one_or_none()

    if not member:
        raise PermissionDeniedError(
            f"User {assigned_to_user_id} is not a member of project {task.project_id}"
        )

    # Store old assignee for audit log
    old_assignee = task.assigned_to

    # Assign task
    task.assigned_to = assigned_to_user_id

    await db.commit()
    await db.refresh(task)

    # Audit logging (T129 - ADR-003)
    if task.organization_id:
        await audit_service.log_action(
            session=db,
            organization_id=task.organization_id,
            user_id=UUID(assigned_by_user_id),
            resource_type="task",
            resource_id=UUID(str(task.id)),
            action="assign",
            context={
                "task_id": task_id,
                "task_title": task.title,
                "assigned_to": assigned_to_user_id,
                "assigned_by": assigned_by_user_id,
                "previous_assignee": old_assignee,
                "project_id": str(task.project_id),
            },
        )
        await db.commit()

    return task


async def unassign_task(
    db: AsyncSession,
    task_id: int,
    unassigned_by_user_id: str,
) -> Task:
    """
    Unassign task from current assignee (Phase 3.1).

    Args:
        db: Database session
        task_id: Task ID to unassign
        unassigned_by_user_id: User ID performing unassignment

    Returns:
        Updated Task object with assignment cleared

    Raises:
        TaskNotFoundError: If task not found

    Task: T111 [US3] - Clear assigned_to field
    """
    # Get task
    task_query = select(Task).where(
        Task.id == task_id,
        Task.deleted_at.is_(None)
    )
    task_result = await db.execute(task_query)
    task = task_result.scalar_one_or_none()

    if not task:
        raise TaskNotFoundError(f"Task {task_id} not found")

    # Store old assignee for audit log
    old_assignee = task.assigned_to

    # Unassign task
    task.assigned_to = None

    await db.commit()
    await db.refresh(task)

    # Audit logging (T129 - ADR-003)
    if task.organization_id and old_assignee:
        await audit_service.log_action(
            session=db,
            organization_id=task.organization_id,
            user_id=UUID(unassigned_by_user_id),
            resource_type="task",
            resource_id=UUID(str(task.id)),
            action="unassign",
            context={
                "task_id": task_id,
                "task_title": task.title,
                "previous_assignee": old_assignee,
                "unassigned_by": unassigned_by_user_id,
                "project_id": str(task.project_id) if task.project_id else None,
            },
        )
        await db.commit()

    return task
