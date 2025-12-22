# Response Schemas: Phase 2 - Full-Stack Web Application

**Branch**: `002-phase2-web-app` | **Date**: 2025-12-10 | **Plan**: [../plan.md](../plan.md)

---

## Overview

All API responses use JSON format with `Content-Type: application/json` header.

**Character Encoding**: UTF-8
**Date Format**: ISO 8601 (YYYY-MM-DD)
**Datetime Format**: ISO 8601 with timezone (YYYY-MM-DDTHH:MM:SSZ)

---

## Task Response Schema

**Used By**:
- `POST /api/{user_id}/tasks` (201 Created)
- `GET /api/{user_id}/tasks/{id}` (200 OK)
- `PUT /api/{user_id}/tasks/{id}` (200 OK)
- `PATCH /api/{user_id}/tasks/{id}/complete` (200 OK)

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "description": "Task ID (auto-generated)"
    },
    "user_id": {
      "type": "integer",
      "description": "Owner user ID"
    },
    "title": {
      "type": "string",
      "maxLength": 200,
      "description": "Task title"
    },
    "description": {
      "type": ["string", "null"],
      "maxLength": 1000,
      "description": "Task description"
    },
    "completed": {
      "type": "boolean",
      "description": "Completion status"
    },
    "completed_at": {
      "type": ["string", "null"],
      "format": "date-time",
      "description": "Completion timestamp (ISO 8601)"
    },
    "priority": {
      "type": ["string", "null"],
      "enum": ["low", "medium", "high", null],
      "description": "Priority level"
    },
    "tags": {
      "type": ["string", "null"],
      "description": "Comma-separated tags"
    },
    "due_date": {
      "type": ["string", "null"],
      "format": "date",
      "description": "Due date (YYYY-MM-DD)"
    },
    "due_time": {
      "type": ["string", "null"],
      "description": "Due time (HH:MM:SS)"
    },
    "recurrence_pattern": {
      "type": ["string", "null"],
      "enum": ["daily", "weekly", "monthly", null],
      "description": "Recurrence pattern"
    },
    "recurrence_day": {
      "type": ["integer", "null"],
      "minimum": 1,
      "maximum": 31,
      "description": "Day for recurrence"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "Creation timestamp (ISO 8601)"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time",
      "description": "Last update timestamp (ISO 8601)"
    }
  },
  "required": ["id", "user_id", "title", "completed", "created_at", "updated_at"],
  "additionalProperties": false
}
```

### Examples

**Simple Task**:
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Buy groceries",
  "description": null,
  "completed": false,
  "completed_at": null,
  "priority": null,
  "tags": null,
  "due_date": null,
  "due_time": null,
  "recurrence_pattern": null,
  "recurrence_day": null,
  "created_at": "2025-12-10T10:00:00Z",
  "updated_at": "2025-12-10T10:00:00Z"
}
```

**Complete Task with All Fields**:
```json
{
  "id": 2,
  "user_id": 1,
  "title": "Weekly team standup",
  "description": "Discuss sprint progress and blockers",
  "completed": false,
  "completed_at": null,
  "priority": "high",
  "tags": "work,meeting,weekly",
  "due_date": "2025-12-11",
  "due_time": "09:00:00",
  "recurrence_pattern": "weekly",
  "recurrence_day": 1,
  "created_at": "2025-12-10T09:00:00Z",
  "updated_at": "2025-12-10T09:00:00Z"
}
```

**Completed Task**:
```json
{
  "id": 3,
  "user_id": 1,
  "title": "Submit expense report",
  "description": "November expenses",
  "completed": true,
  "completed_at": "2025-12-10T15:30:00Z",
  "priority": "medium",
  "tags": "work,admin",
  "due_date": "2025-12-09",
  "due_time": null,
  "recurrence_pattern": "monthly",
  "recurrence_day": 5,
  "created_at": "2025-11-01T10:00:00Z",
  "updated_at": "2025-12-10T15:30:00Z"
}
```

---

## Task List Response Schema

**Used By**:
- `GET /api/{user_id}/tasks` (200 OK)

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "$ref": "#/definitions/Task"
  }
}
```

### Example

```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "Buy groceries",
    "completed": false,
    ...
  },
  {
    "id": 2,
    "user_id": 1,
    "title": "Weekly standup",
    "completed": false,
    ...
  }
]
```

**Empty List** (No Tasks):
```json
[]
```

---

## Recurring Task Completion Response

**Used By**:
- `PATCH /api/{user_id}/tasks/{id}/complete` (200 OK, if task is recurring)

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "completed_task": {
      "$ref": "#/definitions/Task",
      "description": "The task that was just completed"
    },
    "new_instance": {
      "$ref": "#/definitions/Task",
      "description": "Newly created instance for next occurrence"
    }
  },
  "required": ["completed_task", "new_instance"]
}
```

### Example

**Weekly Recurring Task Completed**:
```json
{
  "completed_task": {
    "id": 2,
    "user_id": 1,
    "title": "Weekly standup",
    "description": "Discuss sprint progress",
    "completed": true,
    "completed_at": "2025-12-10T15:00:00Z",
    "priority": "high",
    "tags": "work,meeting",
    "due_date": "2025-12-10",
    "due_time": "09:00:00",
    "recurrence_pattern": "weekly",
    "recurrence_day": 1,
    "created_at": "2025-12-03T09:00:00Z",
    "updated_at": "2025-12-10T15:00:00Z"
  },
  "new_instance": {
    "id": 10,
    "user_id": 1,
    "title": "Weekly standup",
    "description": "Discuss sprint progress",
    "completed": false,
    "completed_at": null,
    "priority": "high",
    "tags": "work,meeting",
    "due_date": "2025-12-17",
    "due_time": "09:00:00",
    "recurrence_pattern": "weekly",
    "recurrence_day": 1,
    "created_at": "2025-12-10T15:00:00Z",
    "updated_at": "2025-12-10T15:00:00Z"
  }
}
```

---

## Error Response Schema

**Used By**: All endpoints on error (4xx, 5xx)

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "error": {
      "type": "string",
      "description": "Error type (e.g., 'Validation error', 'Unauthorized')"
    },
    "detail": {
      "type": "string",
      "description": "Detailed error message"
    },
    "field": {
      "type": ["string", "null"],
      "description": "Field name for validation errors (optional)"
    }
  },
  "required": ["error", "detail"],
  "additionalProperties": false
}
```

### Examples

**401 Unauthorized**:
```json
{
  "error": "Unauthorized",
  "detail": "Missing or invalid token"
}
```

**403 Forbidden**:
```json
{
  "error": "Forbidden",
  "detail": "Access denied"
}
```

**404 Not Found**:
```json
{
  "error": "Not found",
  "detail": "Task not found"
}
```

**400 Bad Request (Validation)**:
```json
{
  "error": "Validation error",
  "detail": "Title is required",
  "field": "title"
}
```

```json
{
  "error": "Validation error",
  "detail": "Title cannot exceed 200 characters",
  "field": "title"
}
```

```json
{
  "error": "Validation error",
  "detail": "due_time can only be set if due_date is also set",
  "field": "due_time"
}
```

**500 Internal Server Error**:
```json
{
  "error": "Internal server error",
  "detail": "An unexpected error occurred"
}
```

---

## Health Check Response

**Used By**: `GET /health` (200 OK)

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["healthy"],
      "description": "Health status"
    }
  },
  "required": ["status"]
}
```

### Example

```json
{
  "status": "healthy"
}
```

---

## Authentication Responses

### User Registration/Login Success

**Used By**:
- `POST http://localhost:3000/api/auth/register` (200 OK)
- `POST http://localhost:3000/api/auth/login` (200 OK)

**JSON Schema**:
```json
{
  "type": "object",
  "properties": {
    "user": {
      "type": "object",
      "properties": {
        "id": { "type": "integer" },
        "email": { "type": "string", "format": "email" },
        "name": { "type": ["string", "null"] }
      },
      "required": ["id", "email"]
    },
    "token": {
      "type": "string",
      "description": "JWT token"
    },
    "expiresIn": {
      "type": "string",
      "description": "Token lifetime (e.g., '7d')"
    }
  },
  "required": ["user", "token", "expiresIn"]
}
```

**Example**:
```json
{
  "user": {
    "id": 1,
    "email": "john@example.com",
    "name": "John Doe"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImVtYWlsIjoiam9obkBleGFtcGxlLmNvbSIsImlhdCI6MTczMzc0MDAwMCwiZXhwIjoxNzM0MzQ0ODB9.signature",
  "expiresIn": "7d"
}
```

### Login Failure

**Status**: 401 Unauthorized

```json
{
  "error": "Invalid credentials",
  "detail": "Email or password is incorrect"
}
```

### Registration Failure

**Status**: 400 Bad Request

**Duplicate Email**:
```json
{
  "error": "Validation error",
  "detail": "Email already registered",
  "field": "email"
}
```

**Weak Password**:
```json
{
  "error": "Validation error",
  "detail": "Password must be at least 8 characters",
  "field": "password"
}
```

---

## Pydantic Models (Backend)

### TaskResponse

```python
from pydantic import BaseModel
from datetime import datetime, date, time

class TaskResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None
    completed: bool
    completed_at: datetime | None
    priority: str | None  # "low" | "medium" | "high"
    tags: str | None
    due_date: date | None
    due_time: time | None
    recurrence_pattern: str | None  # "daily" | "weekly" | "monthly"
    recurrence_day: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode
```

### RecurringTaskResponse

```python
class RecurringTaskResponse(BaseModel):
    completed_task: TaskResponse
    new_instance: TaskResponse
```

### ErrorResponse

```python
class ErrorResponse(BaseModel):
    error: str
    detail: str
    field: str | None = None
```

---

## TypeScript Types (Frontend)

### Task

```typescript
export interface Task {
  id: number
  user_id: number
  title: string
  description: string | null
  completed: boolean
  completed_at: string | null  // ISO datetime
  priority: 'low' | 'medium' | 'high' | null
  tags: string | null
  due_date: string | null  // ISO date: "2025-12-15"
  due_time: string | null  // Time: "09:00:00"
  recurrence_pattern: 'daily' | 'weekly' | 'monthly' | null
  recurrence_day: number | null
  created_at: string  // ISO datetime
  updated_at: string  // ISO datetime
}
```

### RecurringTaskResponse

```typescript
export interface RecurringTaskResponse {
  completed_task: Task
  new_instance: Task
}
```

### ErrorResponse

```typescript
export interface ErrorResponse {
  error: string
  detail: string
  field?: string
}
```

### HealthCheckResponse

```typescript
export interface HealthCheckResponse {
  status: 'healthy'
}
```

---

## Response Headers

**Content-Type**: `application/json; charset=utf-8`
**Date**: RFC 7231 date (e.g., `Tue, 10 Dec 2025 15:00:00 GMT`)
**Content-Length**: Byte size of response body

**CORS Headers** (Development):
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Allow-Credentials: true
```

---

## HTTP Status Codes

| **Code** | **Meaning** | **When Used** |
|----------|-------------|---------------|
| 200 | OK | Successful GET, PUT, PATCH, DELETE |
| 201 | Created | Successful POST (resource created) |
| 204 | No Content | Successful DELETE (no response body) |
| 400 | Bad Request | Validation error, malformed request |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | Valid token but access denied |
| 404 | Not Found | Resource does not exist |
| 500 | Internal Server Error | Unexpected server error |

---

**Next Steps**:
1. ✅ Response schemas documented
2. → Review [request-schemas.md](./request-schemas.md) for request formats
3. → Review [api-endpoints.md](./api-endpoints.md) for all API endpoints
4. → Review [authentication.md](./authentication.md) for auth flow
5. → All planning artifacts complete! Ready for `/sp.tasks`
