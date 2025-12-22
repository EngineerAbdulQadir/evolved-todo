# Request Schemas: Phase 2 - Full-Stack Web Application

**Branch**: `002-phase2-web-app` | **Date**: 2025-12-10 | **Plan**: [../plan.md](../plan.md)

---

## Overview

All API requests use JSON format with `Content-Type: application/json` header.

**Character Encoding**: UTF-8
**Date Format**: ISO 8601 (YYYY-MM-DD)
**Time Format**: 24-hour (HH:MM:SS)

---

## Task Creation Schema

**Endpoint**: `POST /api/{user_id}/tasks`

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200,
      "description": "Task title (required)"
    },
    "description": {
      "type": ["string", "null"],
      "maxLength": 1000,
      "description": "Task description (optional)"
    },
    "priority": {
      "type": ["string", "null"],
      "enum": ["low", "medium", "high", null],
      "description": "Priority level (optional)"
    },
    "tags": {
      "type": ["string", "null"],
      "pattern": "^([^,]+,)*[^,]+$",
      "description": "Comma-separated tags (optional)"
    },
    "due_date": {
      "type": ["string", "null"],
      "format": "date",
      "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
      "description": "Due date in YYYY-MM-DD format (optional)"
    },
    "due_time": {
      "type": ["string", "null"],
      "pattern": "^\\d{2}:\\d{2}:\\d{2}$",
      "description": "Due time in HH:MM:SS format (optional, requires due_date)"
    },
    "recurrence_pattern": {
      "type": ["string", "null"],
      "enum": ["daily", "weekly", "monthly", null],
      "description": "Recurrence pattern (optional)"
    },
    "recurrence_day": {
      "type": ["integer", "null"],
      "minimum": 1,
      "maximum": 31,
      "description": "Day for recurrence (1-7 for weekly, 1-31 for monthly)"
    }
  },
  "required": ["title"],
  "additionalProperties": false
}
```

### Examples

**Minimal (Title Only)**:
```json
{
  "title": "Buy groceries"
}
```

**Complete Task**:
```json
{
  "title": "Weekly team standup",
  "description": "Discuss sprint progress and blockers with the team",
  "priority": "high",
  "tags": "work,meeting,weekly",
  "due_date": "2025-12-11",
  "due_time": "09:00:00",
  "recurrence_pattern": "weekly",
  "recurrence_day": 1
}
```

**With Priority and Tags**:
```json
{
  "title": "Submit expense report",
  "description": "November expenses",
  "priority": "medium",
  "tags": "work,admin,finance"
}
```

**Daily Recurring Task**:
```json
{
  "title": "Daily standup",
  "recurrence_pattern": "daily"
}
```

**Monthly Recurring (5th of Each Month)**:
```json
{
  "title": "Pay rent",
  "due_date": "2025-12-05",
  "recurrence_pattern": "monthly",
  "recurrence_day": 5
}
```

### Validation Rules

| **Field** | **Rules** |
|-----------|-----------|
| `title` | Required, 1-200 characters, trimmed |
| `description` | Optional, max 1000 characters |
| `priority` | Must be `low`, `medium`, `high`, or `null` |
| `tags` | Comma-separated string, no validation on individual tags |
| `due_date` | ISO date format (YYYY-MM-DD), must be valid date |
| `due_time` | 24-hour format (HH:MM:SS), requires `due_date` to be set |
| `recurrence_pattern` | Must be `daily`, `weekly`, `monthly`, or `null` |
| `recurrence_day` | 1-7 for weekly (1=Mon, 7=Sun), 1-31 for monthly |

**Validation Errors**:
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

---

## Task Update Schema

**Endpoint**: `PUT /api/{user_id}/tasks/{id}`

### JSON Schema

Same as Task Creation Schema (all fields optional except `title`).

### Examples

**Update Title Only**:
```json
{
  "title": "Buy groceries and supplies"
}
```

**Update Multiple Fields**:
```json
{
  "title": "Submit expense report (UPDATED)",
  "description": "November and December expenses",
  "priority": "high",
  "tags": "work,admin,urgent",
  "due_date": "2025-12-14"
}
```

**Remove Optional Fields**:
```json
{
  "title": "Simple task",
  "description": null,
  "priority": null,
  "tags": null,
  "due_date": null,
  "recurrence_pattern": null
}
```

**Add Recurrence to Existing Task**:
```json
{
  "title": "Weekly review",
  "recurrence_pattern": "weekly",
  "recurrence_day": 1
}
```

---

## Query Parameters

**Endpoint**: `GET /api/{user_id}/tasks`

### Schema

| **Parameter** | **Type** | **Values** | **Description** |
|---------------|----------|------------|-----------------|
| `completed` | boolean | `true`, `false` | Filter by completion status |
| `priority` | string | `low`, `medium`, `high` | Filter by priority level |
| `tag` | string | Any string | Filter by exact tag match |
| `search` | string | Any string | Search in title and description |
| `due_date_filter` | string | `overdue`, `today`, `this_week` | Filter by due date range |
| `sort_by` | string | `created_at`, `due_date`, `priority`, `title`, `completed` | Sort field |
| `sort_order` | string | `asc`, `desc` | Sort direction |

### Examples

**Filter Incomplete Tasks**:
```
GET /api/1/tasks?completed=false
```

**Filter High Priority**:
```
GET /api/1/tasks?priority=high
```

**Filter by Tag**:
```
GET /api/1/tasks?tag=work
```

**Search for Keyword**:
```
GET /api/1/tasks?search=meeting
```

**Filter Overdue Tasks**:
```
GET /api/1/tasks?due_date_filter=overdue
```

**Sort by Due Date (Ascending)**:
```
GET /api/1/tasks?sort_by=due_date&sort_order=asc
```

**Combined Filters**:
```
GET /api/1/tasks?completed=false&priority=high&sort_by=due_date
```

---

## Authentication Requests

### User Registration

**Endpoint**: `POST http://localhost:3000/api/auth/register`

**JSON Schema**:
```json
{
  "type": "object",
  "properties": {
    "email": {
      "type": "string",
      "format": "email",
      "description": "User email address"
    },
    "password": {
      "type": "string",
      "minLength": 8,
      "description": "User password (min 8 chars)"
    },
    "name": {
      "type": ["string", "null"],
      "maxLength": 255,
      "description": "User display name (optional)"
    }
  },
  "required": ["email", "password"]
}
```

**Example**:
```json
{
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "name": "John Doe"
}
```

### User Login

**Endpoint**: `POST http://localhost:3000/api/auth/login`

**JSON Schema**:
```json
{
  "type": "object",
  "properties": {
    "email": {
      "type": "string",
      "format": "email",
      "description": "User email address"
    },
    "password": {
      "type": "string",
      "description": "User password"
    }
  },
  "required": ["email", "password"]
}
```

**Example**:
```json
{
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

---

## Pydantic Models (Backend)

### TaskCreate

```python
from pydantic import BaseModel, Field, field_validator
from datetime import date, time
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class RecurrencePattern(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    priority: Priority | None = None
    tags: str | None = None
    due_date: date | None = None
    due_time: time | None = None
    recurrence_pattern: RecurrencePattern | None = None
    recurrence_day: int | None = Field(None, ge=1, le=31)

    @field_validator('due_time')
    @classmethod
    def due_time_requires_due_date(cls, v, values):
        if v is not None and values.get('due_date') is None:
            raise ValueError('due_time can only be set if due_date is also set')
        return v

    @field_validator('title')
    @classmethod
    def trim_title(cls, v):
        return v.strip()
```

### TaskUpdate

```python
class TaskUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    priority: Priority | None = None
    tags: str | None = None
    due_date: date | None = None
    due_time: time | None = None
    recurrence_pattern: RecurrencePattern | None = None
    recurrence_day: int | None = Field(None, ge=1, le=31)

    @field_validator('due_time')
    @classmethod
    def due_time_requires_due_date(cls, v, values):
        if v is not None and values.get('due_date') is None:
            raise ValueError('due_time can only be set if due_date is also set')
        return v

    @field_validator('title')
    @classmethod
    def trim_title(cls, v):
        return v.strip()
```

---

## TypeScript Types (Frontend)

### TaskCreateDTO

```typescript
export enum Priority {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high"
}

export enum RecurrencePattern {
  DAILY = "daily",
  WEEKLY = "weekly",
  MONTHLY = "monthly"
}

export interface TaskCreateDTO {
  title: string
  description?: string | null
  priority?: Priority | null
  tags?: string | null
  due_date?: string | null  // ISO date string: "2025-12-15"
  due_time?: string | null  // Time string: "09:00:00"
  recurrence_pattern?: RecurrencePattern | null
  recurrence_day?: number | null  // 1-7 for weekly, 1-31 for monthly
}
```

### TaskUpdateDTO

```typescript
export interface TaskUpdateDTO {
  title: string
  description?: string | null
  priority?: Priority | null
  tags?: string | null
  due_date?: string | null
  due_time?: string | null
  recurrence_pattern?: RecurrencePattern | null
  recurrence_day?: number | null
}
```

---

**Next Steps**:
1. ✅ Request schemas documented
2. → Review [response-schemas.md](./response-schemas.md) for response formats
3. → Review [api-endpoints.md](./api-endpoints.md) for all API endpoints
4. → Review [authentication.md](./authentication.md) for auth flow
