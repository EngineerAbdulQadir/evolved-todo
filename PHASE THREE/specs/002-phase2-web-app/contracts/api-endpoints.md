# API Endpoints: Phase 2 - Full-Stack Web Application

**Branch**: `002-phase2-web-app` | **Date**: 2025-12-10 | **Plan**: [../plan.md](../plan.md)

---

## Base URL

**Development**: `http://localhost:8000`
**Production**: `https://api.evolved-todo.com` (TBD)

---

## Authentication

All endpoints (except health check) require JWT authentication via `Authorization` header:

```http
Authorization: Bearer <jwt_token>
```

**Token Lifetime**: 7 days

**Error Response (401 Unauthorized)**:
```json
{
  "error": "Unauthorized",
  "detail": "Missing or invalid token"
}
```

**Error Response (403 Forbidden)**:
```json
{
  "error": "Forbidden",
  "detail": "Access denied"
}
```

---

## Endpoints Overview

| **Endpoint** | **Method** | **Auth** | **Description** |
|--------------|------------|----------|-----------------|
| `/health` | GET | No | Health check |
| `/api/{user_id}/tasks` | GET | Yes | Get all tasks for user |
| `/api/{user_id}/tasks` | POST | Yes | Create new task |
| `/api/{user_id}/tasks/{id}` | GET | Yes | Get specific task |
| `/api/{user_id}/tasks/{id}` | PUT | Yes | Update task (full replacement) |
| `/api/{user_id}/tasks/{id}/complete` | PATCH | Yes | Toggle task completion |
| `/api/{user_id}/tasks/{id}` | DELETE | Yes | Delete task |

**Note**: Better Auth endpoints (`/api/auth/*`) are managed by Better Auth library and not documented here.

---

## 1. Health Check

**Purpose**: Verify API server is running.

### GET /health

**Authentication**: None

**Request**:
```http
GET /health
```

**Response (200 OK)**:
```json
{
  "status": "healthy"
}
```

**Error Responses**: None (always returns 200 if server is running)

---

## 2. Get All Tasks

**Purpose**: Retrieve all tasks for authenticated user with optional filtering and sorting.

### GET /api/{user_id}/tasks

**Authentication**: Required (JWT in Authorization header)

**Path Parameters**:
- `user_id` (integer, required): User ID from JWT token

**Query Parameters** (all optional):
- `completed` (boolean): Filter by completion status
  - `true`: Only completed tasks
  - `false`: Only incomplete tasks
  - Omit: All tasks
- `priority` (string): Filter by priority
  - `low`, `medium`, `high`
  - Omit: All priorities
- `tag` (string): Filter by tag (exact match)
  - Example: `tag=work`
- `search` (string): Search in title and description (case-insensitive)
  - Example: `search=meeting`
- `due_date_filter` (string): Filter by due date range
  - `overdue`: Due date < today AND incomplete
  - `today`: Due date = today
  - `this_week`: Due date within next 7 days
  - Omit: No due date filtering
- `sort_by` (string): Sort field
  - `created_at` (default), `due_date`, `priority`, `title`, `completed`
- `sort_order` (string): Sort direction
  - `desc` (default), `asc`

**Request Examples**:
```http
GET /api/1/tasks
GET /api/1/tasks?completed=false
GET /api/1/tasks?priority=high
GET /api/1/tasks?tag=work&completed=false
GET /api/1/tasks?search=meeting
GET /api/1/tasks?due_date_filter=overdue
GET /api/1/tasks?sort_by=due_date&sort_order=asc
```

**Response (200 OK)**:
```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "completed_at": null,
    "priority": "medium",
    "tags": "personal,errands",
    "due_date": "2025-12-15",
    "due_time": null,
    "recurrence_pattern": null,
    "recurrence_day": null,
    "created_at": "2025-12-10T10:00:00Z",
    "updated_at": "2025-12-10T10:00:00Z"
  },
  {
    "id": 2,
    "user_id": 1,
    "title": "Weekly standup",
    "description": "Discuss sprint progress",
    "completed": false,
    "completed_at": null,
    "priority": "high",
    "tags": "work,meeting",
    "due_date": "2025-12-11",
    "due_time": "09:00:00",
    "recurrence_pattern": "weekly",
    "recurrence_day": 1,
    "created_at": "2025-12-10T09:00:00Z",
    "updated_at": "2025-12-10T09:00:00Z"
  }
]
```

**Error Responses**:
- **401 Unauthorized**: Missing or invalid JWT token
- **403 Forbidden**: User trying to access another user's tasks

---

## 3. Create Task

**Purpose**: Create a new task for authenticated user.

### POST /api/{user_id}/tasks

**Authentication**: Required

**Path Parameters**:
- `user_id` (integer, required): User ID from JWT token

**Request Body** (JSON):
```json
{
  "title": "Submit expense report",
  "description": "November expenses",
  "priority": "medium",
  "tags": "work,admin",
  "due_date": "2025-12-15",
  "due_time": "17:00:00",
  "recurrence_pattern": "monthly",
  "recurrence_day": 5
}
```

**Required Fields**:
- `title` (string, max 200 chars)

**Optional Fields**:
- `description` (string, max 1000 chars)
- `priority` (enum: `low`, `medium`, `high`)
- `tags` (string, comma-separated)
- `due_date` (string, ISO date: YYYY-MM-DD)
- `due_time` (string, time: HH:MM:SS, requires `due_date`)
- `recurrence_pattern` (enum: `daily`, `weekly`, `monthly`)
- `recurrence_day` (integer, 1-7 for weekly, 1-31 for monthly)

**Response (201 Created)**:
```json
{
  "id": 3,
  "user_id": 1,
  "title": "Submit expense report",
  "description": "November expenses",
  "completed": false,
  "completed_at": null,
  "priority": "medium",
  "tags": "work,admin",
  "due_date": "2025-12-15",
  "due_time": "17:00:00",
  "recurrence_pattern": "monthly",
  "recurrence_day": 5,
  "created_at": "2025-12-10T11:00:00Z",
  "updated_at": "2025-12-10T11:00:00Z"
}
```

**Error Responses**:
- **400 Bad Request**: Validation error (e.g., missing title, invalid date, title too long)
  ```json
  {
    "error": "Validation error",
    "detail": "Title is required",
    "field": "title"
  }
  ```
- **401 Unauthorized**: Missing or invalid JWT token
- **403 Forbidden**: User trying to create task for another user

---

## 4. Get Single Task

**Purpose**: Retrieve specific task by ID.

### GET /api/{user_id}/tasks/{id}

**Authentication**: Required

**Path Parameters**:
- `user_id` (integer, required): User ID from JWT token
- `id` (integer, required): Task ID

**Request**:
```http
GET /api/1/tasks/3
```

**Response (200 OK)**:
```json
{
  "id": 3,
  "user_id": 1,
  "title": "Submit expense report",
  "description": "November expenses",
  "completed": false,
  "completed_at": null,
  "priority": "medium",
  "tags": "work,admin",
  "due_date": "2025-12-15",
  "due_time": "17:00:00",
  "recurrence_pattern": "monthly",
  "recurrence_day": 5,
  "created_at": "2025-12-10T11:00:00Z",
  "updated_at": "2025-12-10T11:00:00Z"
}
```

**Error Responses**:
- **401 Unauthorized**: Missing or invalid JWT token
- **403 Forbidden**: User trying to access another user's task
- **404 Not Found**: Task does not exist or belongs to another user
  ```json
  {
    "error": "Not found",
    "detail": "Task not found"
  }
  ```

---

## 5. Update Task

**Purpose**: Update all fields of an existing task (full replacement).

### PUT /api/{user_id}/tasks/{id}

**Authentication**: Required

**Path Parameters**:
- `user_id` (integer, required): User ID from JWT token
- `id` (integer, required): Task ID

**Request Body** (JSON):
```json
{
  "title": "Submit expense report (Updated)",
  "description": "November and December expenses",
  "priority": "high",
  "tags": "work,admin,urgent",
  "due_date": "2025-12-14",
  "due_time": "15:00:00",
  "recurrence_pattern": "monthly",
  "recurrence_day": 5
}
```

**Required Fields**:
- `title` (string, max 200 chars)

**Optional Fields**: Same as POST (all fields except `completed` and `completed_at`)

**Response (200 OK)**:
```json
{
  "id": 3,
  "user_id": 1,
  "title": "Submit expense report (Updated)",
  "description": "November and December expenses",
  "completed": false,
  "completed_at": null,
  "priority": "high",
  "tags": "work,admin,urgent",
  "due_date": "2025-12-14",
  "due_time": "15:00:00",
  "recurrence_pattern": "monthly",
  "recurrence_day": 5,
  "created_at": "2025-12-10T11:00:00Z",
  "updated_at": "2025-12-10T14:30:00Z"
}
```

**Error Responses**:
- **400 Bad Request**: Validation error
- **401 Unauthorized**: Missing or invalid JWT token
- **403 Forbidden**: User trying to update another user's task
- **404 Not Found**: Task does not exist

---

## 6. Toggle Task Completion

**Purpose**: Mark task as complete or incomplete (toggle completion status).

### PATCH /api/{user_id}/tasks/{id}/complete

**Authentication**: Required

**Path Parameters**:
- `user_id` (integer, required): User ID from JWT token
- `id` (integer, required): Task ID

**Request**: No body required

**Request**:
```http
PATCH /api/1/tasks/3/complete
```

**Response (200 OK)** - Marking Complete:
```json
{
  "id": 3,
  "user_id": 1,
  "title": "Submit expense report",
  "description": "November expenses",
  "completed": true,
  "completed_at": "2025-12-10T15:00:00Z",
  "priority": "medium",
  "tags": "work,admin",
  "due_date": "2025-12-15",
  "due_time": "17:00:00",
  "recurrence_pattern": "monthly",
  "recurrence_day": 5,
  "created_at": "2025-12-10T11:00:00Z",
  "updated_at": "2025-12-10T15:00:00Z"
}
```

**Response (200 OK)** - Marking Incomplete:
```json
{
  "id": 3,
  "user_id": 1,
  "title": "Submit expense report",
  "description": "November expenses",
  "completed": false,
  "completed_at": null,
  "priority": "medium",
  "tags": "work,admin",
  "due_date": "2025-12-15",
  "due_time": "17:00:00",
  "recurrence_pattern": "monthly",
  "recurrence_day": 5,
  "created_at": "2025-12-10T11:00:00Z",
  "updated_at": "2025-12-10T15:05:00Z"
}
```

**Response (200 OK)** - Recurring Task (Returns both old and new):
```json
{
  "completed_task": {
    "id": 3,
    "user_id": 1,
    "title": "Weekly standup",
    "completed": true,
    "completed_at": "2025-12-10T15:00:00Z",
    "recurrence_pattern": "weekly",
    "recurrence_day": 1,
    "created_at": "2025-12-10T09:00:00Z",
    "updated_at": "2025-12-10T15:00:00Z"
  },
  "new_instance": {
    "id": 4,
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

**Error Responses**:
- **401 Unauthorized**: Missing or invalid JWT token
- **403 Forbidden**: User trying to toggle another user's task
- **404 Not Found**: Task does not exist

---

## 7. Delete Task

**Purpose**: Permanently delete a task.

### DELETE /api/{user_id}/tasks/{id}

**Authentication**: Required

**Path Parameters**:
- `user_id` (integer, required): User ID from JWT token
- `id` (integer, required): Task ID

**Request**:
```http
DELETE /api/1/tasks/3
```

**Response (204 No Content)**: Empty body (task successfully deleted)

**Error Responses**:
- **401 Unauthorized**: Missing or invalid JWT token
- **403 Forbidden**: User trying to delete another user's task
- **404 Not Found**: Task does not exist or already deleted

---

## Error Response Format

All error responses follow this structure:

```json
{
  "error": "Error type",
  "detail": "Detailed error message",
  "field": "field_name"  // Optional, only for validation errors
}
```

**Common Error Types**:
- `Unauthorized`: Authentication failed
- `Forbidden`: Valid token but access denied
- `Not found`: Resource does not exist
- `Validation error`: Invalid request data
- `Internal server error`: Unexpected server error

---

## Rate Limiting (Phase 3+)

**Current**: No rate limiting in Phase 2

**Future**:
- 100 requests per minute per user
- 429 Too Many Requests response when exceeded

---

## Pagination (Phase 3+)

**Current**: Returns all tasks (no pagination in Phase 2)

**Future**:
- Query params: `limit` (default 100), `offset` (default 0)
- Response includes `total`, `limit`, `offset`, `items`

---

## Versioning

**Current Version**: v1 (implicit, no version prefix)

**Future**: API versioning will use `/v2/` prefix if breaking changes introduced

---

## CORS Configuration

**Allowed Origins**:
- `http://localhost:3000` (development)
- `https://evolved-todo.com` (production, TBD)

**Allowed Methods**: GET, POST, PUT, PATCH, DELETE, OPTIONS

**Allowed Headers**: Authorization, Content-Type

---

## Performance Targets

- **Response Time (p95)**: <500ms for all endpoints
- **Database Query Time**: <100ms for typical queries
- **Concurrent Users**: Support 1,000 concurrent users

---

**Next Steps**:
1. ✅ API endpoints documented
2. → Review [authentication.md](./authentication.md) for auth flow
3. → Review [request-schemas.md](./request-schemas.md) for detailed request formats
4. → Review [response-schemas.md](./response-schemas.md) for detailed response formats
