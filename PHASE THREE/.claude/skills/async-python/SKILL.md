---
name: async-python
description: Python async/await patterns, asyncio best practices, async context managers, and async error handling.
---

# Async Python

## Instructions

### When to Use

- Writing async functions with FastAPI
- Managing async database sessions
- Implementing async context managers
- Handling concurrent operations
- Error handling in async code
- Testing async code with pytest-asyncio

## Async/Await Basics

### Basic Async Function

```python
import asyncio

async def fetch_user(user_id: int) -> dict:
    """Async function that simulates fetching a user."""
    await asyncio.sleep(1)  # Simulate I/O operation
    return {"id": user_id, "name": "John Doe"}

# Calling async functions
async def main():
    user = await fetch_user(1)
    print(user)

# Run the async function
asyncio.run(main())
```

### Multiple Concurrent Operations

```python
import asyncio
from typing import List

async def fetch_task(task_id: int) -> dict:
    """Fetch a single task."""
    await asyncio.sleep(0.5)
    return {"id": task_id, "title": f"Task {task_id}"}

async def fetch_all_tasks(task_ids: List[int]) -> List[dict]:
    """
    Fetch multiple tasks concurrently.

    This runs all fetch operations in parallel.
    """
    tasks = [fetch_task(task_id) for task_id in task_ids]
    results = await asyncio.gather(*tasks)
    return results

# Usage
async def main():
    task_ids = [1, 2, 3, 4, 5]
    tasks = await fetch_all_tasks(task_ids)
    print(f"Fetched {len(tasks)} tasks")
```

## Async Database Operations

### AsyncSession with SQLModel

```python
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional, List

from models.task import Task

async def get_task_by_id(
    session: AsyncSession,
    task_id: int
) -> Optional[Task]:
    """
    Get a task by ID.

    Args:
        session: Async database session
        task_id: Task ID

    Returns:
        Task or None if not found
    """
    query = select(Task).where(Task.id == task_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def get_tasks_by_user(
    session: AsyncSession,
    user_id: int
) -> List[Task]:
    """Get all tasks for a user."""
    query = select(Task).where(Task.user_id == user_id)
    result = await session.execute(query)
    return list(result.scalars().all())

async def create_task(
    session: AsyncSession,
    task: Task
) -> Task:
    """
    Create a new task.

    Args:
        session: Async database session
        task: Task to create

    Returns:
        Created task with ID
    """
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

async def update_task(
    session: AsyncSession,
    task: Task
) -> Task:
    """Update an existing task."""
    await session.commit()
    await session.refresh(task)
    return task

async def delete_task(
    session: AsyncSession,
    task: Task
) -> None:
    """Delete a task."""
    await session.delete(task)
    await session.commit()
```

### Transaction Management

```python
async def transfer_task_ownership(
    session: AsyncSession,
    task_id: int,
    from_user_id: int,
    to_user_id: int
) -> Task:
    """
    Transfer task ownership atomically.

    Uses transaction to ensure consistency.
    """
    try:
        # Start implicit transaction
        task = await get_task_by_id(session, task_id)

        if not task or task.user_id != from_user_id:
            raise ValueError("Task not found or not owned by user")

        # Update ownership
        task.user_id = to_user_id

        # Commit transaction
        await session.commit()
        await session.refresh(task)

        return task

    except Exception:
        # Rollback on error
        await session.rollback()
        raise
```

## Async Context Managers

### Basic Async Context Manager

```python
from typing import AsyncGenerator

class AsyncDatabaseConnection:
    """Async context manager for database connections."""

    async def __aenter__(self):
        """Setup: open connection."""
        print("Opening database connection...")
        await asyncio.sleep(0.1)  # Simulate connection
        self.connection = "db_connection"
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Teardown: close connection."""
        print("Closing database connection...")
        await asyncio.sleep(0.1)  # Simulate cleanup
        self.connection = None
        return False  # Don't suppress exceptions

# Usage
async def main():
    async with AsyncDatabaseConnection() as db:
        print(f"Using connection: {db.connection}")
```

### AsyncGenerator for Session Management

```python
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from typing import AsyncGenerator

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async generator for database sessions.

    Ensures session is properly closed even if exception occurs.
    """
    async with AsyncSession(engine) as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Usage with FastAPI
from fastapi import Depends

@app.get("/tasks")
async def list_tasks(session: AsyncSession = Depends(get_session)):
    """FastAPI automatically handles the async generator."""
    tasks = await get_tasks_by_user(session, user_id=1)
    return tasks
```

## Error Handling in Async Code

### Try/Except with Async

```python
async def fetch_task_safe(task_id: int) -> Optional[Task]:
    """
    Fetch task with error handling.

    Returns None if task not found or error occurs.
    """
    try:
        task = await fetch_task(task_id)
        return task
    except TaskNotFoundError:
        logger.warning(f"Task {task_id} not found")
        return None
    except DatabaseError as e:
        logger.error(f"Database error fetching task {task_id}: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error fetching task {task_id}: {e}")
        return None
```

### Handling Multiple Concurrent Errors

```python
import asyncio
from typing import List, Tuple, Optional

async def fetch_tasks_with_error_handling(
    task_ids: List[int]
) -> Tuple[List[Task], List[int]]:
    """
    Fetch tasks, collecting successes and failures.

    Returns:
        Tuple of (successful_tasks, failed_task_ids)
    """
    async def fetch_safe(task_id: int) -> Optional[Task]:
        try:
            return await fetch_task(task_id)
        except Exception as e:
            logger.error(f"Failed to fetch task {task_id}: {e}")
            return None

    results = await asyncio.gather(*[fetch_safe(tid) for tid in task_ids])

    successful = [task for task in results if task is not None]
    failed_ids = [
        task_id
        for task_id, result in zip(task_ids, results)
        if result is None
    ]

    return successful, failed_ids

# Usage
async def main():
    task_ids = [1, 2, 3, 4, 5]
    successful, failed = await fetch_tasks_with_error_handling(task_ids)
    print(f"Successfully fetched: {len(successful)}")
    print(f"Failed to fetch: {failed}")
```

## Timeouts and Cancellation

### Setting Timeouts

```python
import asyncio

async def fetch_with_timeout(task_id: int, timeout: float = 5.0) -> Task:
    """
    Fetch task with timeout.

    Raises asyncio.TimeoutError if operation takes too long.
    """
    try:
        return await asyncio.wait_for(
            fetch_task(task_id),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        logger.error(f"Timeout fetching task {task_id}")
        raise
```

### Graceful Cancellation

```python
async def long_running_task():
    """Long-running task that can be cancelled."""
    try:
        for i in range(100):
            await asyncio.sleep(1)
            print(f"Progress: {i + 1}/100")
    except asyncio.CancelledError:
        print("Task was cancelled, cleaning up...")
        # Perform cleanup
        raise  # Re-raise to propagate cancellation

# Usage
async def main():
    task = asyncio.create_task(long_running_task())

    # Cancel after 5 seconds
    await asyncio.sleep(5)
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        print("Task successfully cancelled")
```

## Async Iteration

### Async Generators

```python
from typing import AsyncGenerator

async def fetch_tasks_paginated(
    user_id: int,
    page_size: int = 10
) -> AsyncGenerator[Task, None]:
    """
    Fetch tasks in pages, yielding one at a time.

    This is memory-efficient for large datasets.
    """
    offset = 0

    while True:
        # Fetch page
        query = (
            select(Task)
            .where(Task.user_id == user_id)
            .offset(offset)
            .limit(page_size)
        )

        result = await session.execute(query)
        tasks = list(result.scalars().all())

        if not tasks:
            break

        # Yield each task
        for task in tasks:
            yield task

        offset += page_size

# Usage
async def main():
    async for task in fetch_tasks_paginated(user_id=1):
        print(f"Processing task: {task.title}")
```

### Async Comprehensions

```python
# Async list comprehension
task_ids = [1, 2, 3, 4, 5]
tasks = [await fetch_task(tid) for tid in task_ids]

# Async generator expression
tasks_gen = (await fetch_task(tid) for tid in task_ids)

# Using async for
async def process_tasks(task_ids: List[int]):
    """Process tasks one by one."""
    async for task in (fetch_task(tid) for tid in task_ids):
        print(f"Processing: {task.title}")
```

## Testing Async Code

### pytest-asyncio

```python
# tests/test_tasks.py
import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

@pytest.mark.asyncio
async def test_create_task(session: AsyncSession):
    """Test creating a task."""
    task = Task(
        user_id=1,
        title="Test task",
        completed=False,
        priority="medium"
    )

    created_task = await create_task(session, task)

    assert created_task.id is not None
    assert created_task.title == "Test task"

@pytest.mark.asyncio
async def test_get_tasks_by_user(session: AsyncSession):
    """Test fetching tasks for a user."""
    # Create test tasks
    task1 = await create_task(session, Task(user_id=1, title="Task 1"))
    task2 = await create_task(session, Task(user_id=1, title="Task 2"))

    # Fetch tasks
    tasks = await get_tasks_by_user(session, user_id=1)

    assert len(tasks) >= 2
    assert any(t.id == task1.id for t in tasks)
    assert any(t.id == task2.id for t in tasks)

@pytest.mark.asyncio
async def test_concurrent_operations():
    """Test running operations concurrently."""
    task_ids = [1, 2, 3, 4, 5]

    # Fetch all tasks concurrently
    tasks = await asyncio.gather(*[fetch_task(tid) for tid in task_ids])

    assert len(tasks) == 5
    assert all(isinstance(t, Task) for t in tasks)
```

## Best Practices

### 1. Always Use await

```python
# ✅ Good: Use await for async functions
result = await async_function()

# ❌ Bad: Forgetting await (returns coroutine object, not result)
result = async_function()  # This is a coroutine, not the result!
```

### 2. Use asyncio.gather for Concurrent Operations

```python
# ✅ Good: Run operations concurrently
results = await asyncio.gather(
    fetch_user(1),
    fetch_user(2),
    fetch_user(3)
)

# ❌ Bad: Run operations sequentially (slower)
user1 = await fetch_user(1)
user2 = await fetch_user(2)
user3 = await fetch_user(3)
```

### 3. Handle Cancellation Properly

```python
# ✅ Good: Handle CancelledError
async def cancellable_task():
    try:
        await long_operation()
    except asyncio.CancelledError:
        await cleanup()
        raise  # Re-raise to propagate

# ❌ Bad: Swallow CancelledError
async def bad_task():
    try:
        await long_operation()
    except asyncio.CancelledError:
        pass  # Cancellation ignored!
```

### 4. Use Timeouts

```python
# ✅ Good: Set timeout for operations
try:
    result = await asyncio.wait_for(fetch_data(), timeout=5.0)
except asyncio.TimeoutError:
    logger.error("Operation timed out")

# ❌ Bad: No timeout (operation might hang forever)
result = await fetch_data()
```

## Integration with backend-api-dev Subagent

This skill is primarily used by:
- **backend-api-dev** - For async FastAPI and database operations
- **database-architect** - For async database sessions

### Key Principles

1. **Always await** - Never forget await on async functions
2. **Concurrent Operations** - Use asyncio.gather for parallel operations
3. **Error Handling** - Proper try/except in async code
4. **Context Managers** - Use async with for resource management
5. **Timeouts** - Set timeouts for I/O operations
6. **Testing** - Use pytest-asyncio for async tests
