"""
Task service for CRUD operations and business logic.

This module provides functions for managing tasks with multi-user isolation.
"""

from typing import List, Optional

from sqlalchemy import cast, String
from sqlmodel import select, or_, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


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

    Returns:
        List of Task objects matching filters (T149 - AND logic) and sorted (T177)
    """
    # Start with base query
    query = select(Task).where(Task.user_id == user_id)

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
    db: AsyncSession, user_id: str, task_data: TaskCreate
) -> Task:
    """
    Create a new task for a user.

    Args:
        db: Database session
        user_id: User ID (owner of the task)
        task_data: Task creation data

    Returns:
        Created Task object

    Raises:
        ValueError: If validation fails
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
    )

    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

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
    Delete a task.

    Args:
        db: Database session
        task_id: Task ID to delete
        user_id: User ID for ownership validation

    Returns:
        True if task was deleted, False if not found
    """
    task = await get_task_by_id(db, task_id, user_id)
    if not task:
        return False

    await db.delete(task)
    await db.commit()

    return True


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
