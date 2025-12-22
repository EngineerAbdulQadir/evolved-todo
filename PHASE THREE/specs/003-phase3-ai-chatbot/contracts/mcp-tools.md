# MCP Tool Contracts

**Feature**: AI-Powered Todo Chatbot (Phase 3)
**Date**: 2025-12-17
**Source**: [spec.md](../spec.md) | [plan.md](../plan.md)

## Overview

This document defines the contracts for all 6 MCP (Model Context Protocol) tools that enable the AI agent to perform task operations. All tools are **stateless** - they receive input, perform database operations, and return output with no internal state.

**Key Principles**:
- **Stateless**: No internal state, all state in database
- **Type-Safe**: Pydantic schemas for input and output
- **Error Handling**: Return structured errors, never crash
- **User Isolation**: All tools filter by user_id
- **Testable**: Pure functions with mock database

---

## Tool 1: add_task

**Purpose**: Create a new task for the user with optional fields (priority, tags, due dates, recurrence)

### Input Schema

```python
from pydantic import BaseModel, Field
from datetime import date, time

class AddTaskInput(BaseModel):
    user_id: str = Field(..., description="User ID from JWT token")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str | None = Field(None, max_length=1000, description="Optional task description")
    priority: str | None = Field(None, pattern="^(high|medium|low)$", description="Task priority: high, medium, or low")
    tags: str | None = Field(None, max_length=500, description="Comma-separated tags (e.g., 'work,urgent')")
    due_date: date | None = Field(None, description="Due date in ISO format (YYYY-MM-DD)")
    due_time: time | None = Field(None, description="Due time in ISO format (HH:MM:SS)")
    recurrence: str | None = Field(None, pattern="^(daily|weekly|monthly)$", description="Recurrence pattern")
    recurrence_day: int | None = Field(None, ge=1, le=31, description="Day of week (1-7) or month (1-31)")
```

### Output Schema

```python
class AddTaskOutput(BaseModel):
    task_id: int = Field(..., description="ID of created task")
    status: str = Field(..., pattern="^(created|error)$", description="Operation status")
    title: str = Field(..., description="Task title (confirmation)")
    message: str | None = Field(None, description="Success or error message")
```

### Success Response Example

```json
{
  "task_id": 42,
  "status": "created",
  "title": "Buy groceries",
  "message": "Task created successfully with high priority and work tag"
}
```

### Error Response Example

```json
{
  "task_id": 0,
  "status": "error",
  "title": "",
  "message": "Title cannot be empty"
}
```

### Business Rules

1. **Required**: `user_id`, `title`
2. **Optional**: All other fields
3. **Validation**:
   - `priority` must be one of: "high", "medium", "low" (if provided)
   - `recurrence` must be one of: "daily", "weekly", "monthly" (if provided)
   - `recurrence_day` must be 1-7 for weekly, 1-31 for monthly
   - `title` max 200 characters
   - `description` max 1000 characters
   - `tags` max 500 characters (comma-separated)
4. **Defaults**:
   - `completed` = False
   - `created_at` = NOW()
   - `updated_at` = NOW()
5. **User Isolation**: Task belongs to `user_id` from input

### Natural Language Examples

| User Says | Extracted Fields |
|-----------|------------------|
| "Add a task to buy groceries" | title="Buy groceries" |
| "Add a high priority task to call dentist" | title="Call dentist", priority="high" |
| "Create a work task for the presentation" | title="Presentation", tags="work" |
| "Add a weekly meeting task every Monday" | title="Weekly meeting", recurrence="weekly", recurrence_day=1 |
| "Remember to take medication daily" | title="Take medication", recurrence="daily" |

---

## Tool 2: list_tasks

**Purpose**: Retrieve tasks with optional filtering (status, priority, tag) and sorting

### Input Schema

```python
class ListTasksInput(BaseModel):
    user_id: str = Field(..., description="User ID from JWT token")
    status: str | None = Field(None, pattern="^(all|pending|completed)$", description="Filter by completion status")
    priority: str | None = Field(None, pattern="^(high|medium|low)$", description="Filter by priority")
    tag: str | None = Field(None, max_length=100, description="Filter by tag (exact match)")
    sort_by: str | None = Field(None, pattern="^(id|title|priority|due_date|created_at)$", description="Sort field")
    sort_order: str | None = Field(None, pattern="^(asc|desc)$", description="Sort order")
```

### Output Schema

```python
class TaskItem(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool
    priority: str | None
    tags: str | None
    due_date: str | None  # ISO format
    due_time: str | None  # HH:MM:SS
    recurrence: str | None
    created_at: str  # ISO format

class ListTasksOutput(BaseModel):
    tasks: list[TaskItem] = Field(..., description="List of tasks matching criteria")
    count: int = Field(..., description="Number of tasks returned")
    status: str = Field(..., pattern="^(success|error)$")
    message: str | None = Field(None, description="Error message if status=error")
```

### Success Response Example

```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Buy groceries",
      "description": null,
      "completed": false,
      "priority": "high",
      "tags": "personal,shopping",
      "due_date": "2025-12-20",
      "due_time": null,
      "recurrence": null,
      "created_at": "2025-12-17T10:30:00Z"
    },
    {
      "id": 2,
      "title": "Call dentist",
      "description": "Schedule cleaning appointment",
      "completed": false,
      "priority": "high",
      "tags": "health",
      "due_date": "2025-12-18",
      "due_time": "14:00:00",
      "recurrence": null,
      "created_at": "2025-12-17T11:00:00Z"
    }
  ],
  "count": 2,
  "status": "success",
  "message": null
}
```

### Business Rules

1. **Required**: `user_id`
2. **Filters**:
   - `status="pending"` → `completed=False`
   - `status="completed"` → `completed=True`
   - `status="all"` or `None` → no filter
   - `priority` → exact match (if provided)
   - `tag` → check if tags field contains the tag (substring match)
3. **Sorting**:
   - Default: `sort_by="created_at"`, `sort_order="desc"` (newest first)
   - Supported fields: id, title, priority, due_date, created_at
4. **User Isolation**: Only return tasks where `task.user_id == input.user_id`
5. **Empty Result**: Return empty array if no tasks match

### Natural Language Examples

| User Says | Extracted Fields |
|-----------|------------------|
| "Show me all my tasks" | status="all" |
| "What's pending?" | status="pending" |
| "Show me high priority tasks" | priority="high" |
| "Show me work tasks" | tag="work" |
| "Sort my tasks by due date" | sort_by="due_date", sort_order="asc" |

---

## Tool 3: search_tasks

**Purpose**: Search tasks by keyword in title and description

### Input Schema

```python
class SearchTasksInput(BaseModel):
    user_id: str = Field(..., description="User ID from JWT token")
    keyword: str = Field(..., min_length=1, max_length=200, description="Search keyword")
```

### Output Schema

```python
class SearchTasksOutput(BaseModel):
    tasks: list[TaskItem] = Field(..., description="List of tasks matching keyword")
    count: int = Field(..., description="Number of matching tasks")
    status: str = Field(..., pattern="^(success|error)$")
    message: str | None = Field(None)
```

### Business Rules

1. **Required**: `user_id`, `keyword`
2. **Search Logic**:
   - Case-insensitive search
   - Search in `title` AND `description` fields
   - Use SQL `ILIKE` or equivalent (PostgreSQL)
   - Example: `WHERE title ILIKE '%keyword%' OR description ILIKE '%keyword%'`
3. **User Isolation**: Only search tasks where `task.user_id == input.user_id`
4. **Empty Result**: Return empty array if no matches

### Natural Language Examples

| User Says | Extracted Fields |
|-----------|------------------|
| "Search for dentist" | keyword="dentist" |
| "Find tasks about groceries" | keyword="groceries" |
| "Look for meeting" | keyword="meeting" |

---

## Tool 4: complete_task

**Purpose**: Mark task as complete. If recurring, create next occurrence automatically.

### Input Schema

```python
class CompleteTaskInput(BaseModel):
    user_id: str = Field(..., description="User ID from JWT token")
    task_id: int = Field(..., ge=1, description="Task ID to complete")
```

### Output Schema

```python
class CompleteTaskOutput(BaseModel):
    task_id: int = Field(..., description="Completed task ID")
    status: str = Field(..., pattern="^(completed|error)$")
    title: str = Field(..., description="Task title")
    next_occurrence: dict | None = Field(None, description="Next task if recurring")
    message: str | None = Field(None)
```

### Success Response Example (Non-Recurring)

```json
{
  "task_id": 5,
  "status": "completed",
  "title": "Buy groceries",
  "next_occurrence": null,
  "message": "Task completed successfully"
}
```

### Success Response Example (Recurring)

```json
{
  "task_id": 10,
  "status": "completed",
  "title": "Weekly meeting",
  "next_occurrence": {
    "task_id": 15,
    "title": "Weekly meeting",
    "due_date": "2025-12-23"
  },
  "message": "Task completed! Next occurrence created for December 23"
}
```

### Business Rules

1. **Required**: `user_id`, `task_id`
2. **Validation**:
   - Task must exist
   - Task must belong to `user_id` (403 if not)
3. **Completion Logic**:
   - Set `completed = True`
   - Update `updated_at = NOW()`
4. **Recurring Task Logic**:
   - If `recurrence` is NOT NULL:
     - Create new task with same fields (title, description, priority, tags, recurrence)
     - Calculate next `due_date`:
       - `daily`: due_date + 1 day
       - `weekly`: due_date + 7 days (or next occurrence of recurrence_day)
       - `monthly`: due_date + 1 month (same day, handle month-end edge cases)
     - New task marked `completed = False`
     - Return new task info in `next_occurrence`
5. **Error Cases**:
   - Task not found: status="error", message="Task with ID {task_id} not found"
   - Access denied: status="error", message="Access denied to task {task_id}"

### Natural Language Examples

| User Says | Extracted Fields |
|-----------|------------------|
| "Mark task 3 as complete" | task_id=3 |
| "I finished the dentist appointment" | (agent searches for task, extracts task_id) |
| "Done with task 5" | task_id=5 |

---

## Tool 5: delete_task

**Purpose**: Remove a task from the database

### Input Schema

```python
class DeleteTaskInput(BaseModel):
    user_id: str = Field(..., description="User ID from JWT token")
    task_id: int = Field(..., ge=1, description="Task ID to delete")
```

### Output Schema

```python
class DeleteTaskOutput(BaseModel):
    task_id: int = Field(..., description="Deleted task ID")
    status: str = Field(..., pattern="^(deleted|error)$")
    title: str = Field(..., description="Deleted task title (confirmation)")
    message: str | None = Field(None)
```

### Business Rules

1. **Required**: `user_id`, `task_id`
2. **Validation**:
   - Task must exist
   - Task must belong to `user_id` (403 if not)
3. **Deletion Logic**:
   - DELETE task from database
   - No soft delete in Phase 3 (hard delete)
4. **Error Cases**:
   - Task not found: status="error", message="Task with ID {task_id} not found"
   - Access denied: status="error", message="Access denied to task {task_id}"

### Natural Language Examples

| User Says | Extracted Fields |
|-----------|------------------|
| "Delete task 3" | task_id=3 |
| "Remove the meeting task" | (agent searches, extracts task_id) |
| "Cancel the dentist task" | (agent searches, extracts task_id) |

---

## Tool 6: update_task

**Purpose**: Modify one or more fields of an existing task (partial update)

### Input Schema

```python
class UpdateTaskInput(BaseModel):
    user_id: str = Field(..., description="User ID from JWT token")
    task_id: int = Field(..., ge=1, description="Task ID to update")
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    priority: str | None = Field(None, pattern="^(high|medium|low)$")
    tags: str | None = Field(None, max_length=500)
    due_date: date | None = Field(None)
    due_time: time | None = Field(None)
    recurrence: str | None = Field(None, pattern="^(daily|weekly|monthly)$")
    recurrence_day: int | None = Field(None, ge=1, le=31)
```

### Output Schema

```python
class UpdateTaskOutput(BaseModel):
    task_id: int = Field(..., description="Updated task ID")
    status: str = Field(..., pattern="^(updated|error)$")
    title: str = Field(..., description="Task title (confirmation)")
    updated_fields: list[str] = Field(..., description="List of fields that were updated")
    message: str | None = Field(None)
```

### Success Response Example

```json
{
  "task_id": 3,
  "status": "updated",
  "title": "Call dentist at 2pm",
  "updated_fields": ["title", "due_time"],
  "message": "Task updated successfully"
}
```

### Business Rules

1. **Required**: `user_id`, `task_id`
2. **Optional**: All other fields (at least one field must be provided to update)
3. **Validation**:
   - Task must exist
   - Task must belong to `user_id` (403 if not)
4. **Update Logic**:
   - Update only fields that are provided (NOT NULL in input)
   - Skip fields with NULL value
   - Update `updated_at = NOW()`
5. **Error Cases**:
   - Task not found: status="error"
   - Access denied: status="error"
   - No fields provided: status="error", message="No fields to update"

### Natural Language Examples

| User Says | Extracted Fields |
|-----------|------------------|
| "Change task 1 to 'Call mom tonight'" | task_id=1, title="Call mom tonight" |
| "Make task 3 high priority" | task_id=3, priority="high" |
| "Set due date to Friday 5 PM for task 3" | task_id=3, due_date="2025-12-20", due_time="17:00:00" |
| "Add work tag to task 4" | task_id=4, tags="work" (append to existing tags) |

---

## MCP Server Configuration

### Tool Registration

```python
from mcp import MCPServer

server = MCPServer()

# Register all 6 tools
server.register_tool(add_task)
server.register_tool(list_tasks)
server.register_tool(search_tasks)
server.register_tool(complete_task)
server.register_tool(delete_task)
server.register_tool(update_task)
```

### Agent Integration

```python
from openai_agents import Agent

agent = Agent(
    name="todo_assistant",
    model="gpt-4",
    instructions=SYSTEM_PROMPT,
    tools=server.get_tools()  # All 6 MCP tools
)
```

---

## Testing Contract

All MCP tools MUST have:
1. **Unit tests** with mock database
2. **Input validation tests** (Pydantic schemas)
3. **Success scenario tests**
4. **Error scenario tests** (task not found, access denied, invalid input)
5. **User isolation tests** (cannot access other users' tasks)

**Test Coverage Target**: 100% for MCP tools

---

**Status**: ✅ MCP Tool Contracts Complete
**Date**: 2025-12-17
**Next**: Implement tools in `backend/app/mcp/tools/`
