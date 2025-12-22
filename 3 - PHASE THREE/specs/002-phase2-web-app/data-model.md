# Data Model: Phase 2 - Full-Stack Web Application

**Branch**: `002-phase2-web-app` | **Date**: 2025-12-10 | **Plan**: [plan.md](./plan.md)

---

## Database: Neon Serverless PostgreSQL

**Connection**: postgresql+asyncpg://[credentials]@neon-host/evolved_todo
**Driver**: asyncpg (async PostgreSQL driver for Python)
**ORM**: SQLModel (SQLAlchemy 2.0 + Pydantic)
**Migrations**: Alembic

---

## Tables

### 1. users (Better Auth)

**Purpose**: Stores user accounts for authentication and authorization.

**Managed By**: Better Auth (Next.js frontend) creates and maintains this table.

**Schema**:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

**SQLModel Representation**:
```python
# app/models/user.py
from sqlmodel import SQLModel, Field
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    password_hash: str = Field(max_length=255)
    name: str | None = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Fields**:
- `id`: Auto-incrementing primary key
- `email`: Unique user email (used for login)
- `password_hash`: Hashed password (bcrypt via Better Auth)
- `name`: Optional display name
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

**Constraints**:
- `email` must be unique
- `email` and `password_hash` are required (NOT NULL)

**Indexes**:
- Primary key index on `id`
- Unique index on `email` (for login lookups)

**Notes**:
- Better Auth manages user creation, authentication, and session tokens
- FastAPI backend only reads from this table for JWT validation
- Password reset and email verification handled by Better Auth

---

### 2. tasks

**Purpose**: Stores all tasks created by users with full feature set from Phase 1 CLI.

**Managed By**: FastAPI backend (full CRUD operations).

**Schema**:
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Basic fields (P1 - Create/View)
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,

    -- Priority and Tags (P2 - Organization)
    priority VARCHAR(10),  -- 'low', 'medium', 'high', or NULL
    tags TEXT,  -- Comma-separated string

    -- Due Dates (P2 - Time Management)
    due_date DATE,
    due_time TIME,

    -- Recurrence (P3 - Advanced)
    recurrence_pattern VARCHAR(10),  -- 'daily', 'weekly', 'monthly', or NULL
    recurrence_day INTEGER,  -- 1-7 for weekly, 1-31 for monthly

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_priority ON tasks(priority);
```

**SQLModel Representation**:
```python
# app/models/task.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, date, time
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class RecurrencePattern(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    # Primary key
    id: int | None = Field(default=None, primary_key=True)

    # Foreign key
    user_id: int = Field(foreign_key="users.id", index=True, ondelete="CASCADE")

    # Basic fields
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)
    completed_at: datetime | None = Field(default=None)

    # Organization
    priority: Priority | None = Field(default=None, index=True)
    tags: str | None = Field(default=None)  # Comma-separated

    # Time management
    due_date: date | None = Field(default=None, index=True)
    due_time: time | None = Field(default=None)

    # Recurrence
    recurrence_pattern: RecurrencePattern | None = Field(default=None)
    recurrence_day: int | None = Field(default=None)  # 1-7 (weekly), 1-31 (monthly)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    user: User | None = Relationship()
```

**Fields**:

**Identity**:
- `id`: Auto-incrementing primary key
- `user_id`: Foreign key to users table (CASCADE delete)

**Basic Task Data (P1)**:
- `title`: Task title (max 200 chars, required)
- `description`: Task description (max 1000 chars, optional)
- `completed`: Boolean flag (default false)
- `completed_at`: Timestamp when task was completed (NULL if incomplete)

**Organization (P2)**:
- `priority`: Enum ('low', 'medium', 'high', or NULL)
- `tags`: Comma-separated string (e.g., "work,urgent,meeting")

**Time Management (P2)**:
- `due_date`: Date the task is due (YYYY-MM-DD, optional)
- `due_time`: Specific time task is due (HH:MM, optional, only used if due_date is set)

**Recurrence (P3)**:
- `recurrence_pattern`: Enum ('daily', 'weekly', 'monthly', or NULL)
- `recurrence_day`: Integer 1-7 for weekly (1=Monday, 7=Sunday), 1-31 for monthly

**Metadata**:
- `created_at`: Task creation timestamp (auto-set)
- `updated_at`: Last modification timestamp (auto-updated on PUT/PATCH)

**Constraints**:
- `title` NOT NULL
- `user_id` NOT NULL (foreign key)
- `priority` IN ('low', 'medium', 'high') OR NULL
- `recurrence_pattern` IN ('daily', 'weekly', 'monthly') OR NULL
- `recurrence_day` BETWEEN 1 AND 31 (validated in service layer)
- `due_time` can only be set if `due_date` is also set (validated in service layer)

**Indexes**:
- `id` (primary key, auto-indexed)
- `user_id` (filter by user - most common query)
- `created_at` (for sorting by newest/oldest)
- `due_date` (for filtering overdue, due today, upcoming)
- `completed` (for filtering active vs completed tasks)
- `priority` (for filtering by priority)

**Cascading Deletes**:
- If a user is deleted, all their tasks are deleted (ON DELETE CASCADE)

**Notes**:
- Tags stored as comma-separated string (no separate Tag table for Phase 2)
- Recurrence trigger: new instance created on completion (not time-based)
- All queries filter by `user_id` to ensure data isolation

---

## Relationships

```
users (1) ──< (many) tasks

One user can have many tasks.
Each task belongs to exactly one user.
```

**User deletion**: Cascades to all tasks (CASCADE DELETE)

---

## Alembic Migration

**Initial Migration**:
```python
# alembic/versions/001_initial_schema.py
def upgrade():
    # Users table (Better Auth creates this)
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now())
    )
    op.create_index('idx_users_email', 'users', ['email'])

    # Tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), default=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('priority', sa.String(10), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('due_time', sa.Time(), nullable=True),
        sa.Column('recurrence_pattern', sa.String(10), nullable=True),
        sa.Column('recurrence_day', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now())
    )

    # Create indexes
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_created_at', 'tasks', ['created_at'])
    op.create_index('idx_tasks_due_date', 'tasks', ['due_date'])
    op.create_index('idx_tasks_completed', 'tasks', ['completed'])
    op.create_index('idx_tasks_priority', 'tasks', ['priority'])

def downgrade():
    op.drop_table('tasks')
    op.drop_table('users')
```

---

## Data Examples

### User
```json
{
  "id": 1,
  "email": "john@example.com",
  "password_hash": "$2b$12$...",
  "name": "John Doe",
  "created_at": "2025-12-10T10:00:00Z",
  "updated_at": "2025-12-10T10:00:00Z"
}
```

### Task (Simple)
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
  "created_at": "2025-12-10T10:05:00Z",
  "updated_at": "2025-12-10T10:05:00Z"
}
```

### Task (Complete with All Fields)
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
  "recurrence_day": 1,  // Monday
  "created_at": "2025-12-10T10:10:00Z",
  "updated_at": "2025-12-10T10:10:00Z"
}
```

### Task (Completed)
```json
{
  "id": 3,
  "user_id": 1,
  "title": "Submit expense report",
  "description": "November expenses",
  "completed": true,
  "completed_at": "2025-12-10T14:30:00Z",
  "priority": "medium",
  "tags": "work,admin",
  "due_date": "2025-12-09",
  "due_time": null,
  "recurrence_pattern": "monthly",
  "recurrence_day": 5,  // 5th of each month
  "created_at": "2025-11-01T10:00:00Z",
  "updated_at": "2025-12-10T14:30:00Z"
}
```

---

## Query Patterns

### Get all tasks for a user
```sql
SELECT * FROM tasks
WHERE user_id = $1
ORDER BY created_at DESC;
```

### Get incomplete tasks
```sql
SELECT * FROM tasks
WHERE user_id = $1 AND completed = FALSE
ORDER BY created_at DESC;
```

### Get overdue tasks
```sql
SELECT * FROM tasks
WHERE user_id = $1
  AND completed = FALSE
  AND due_date < CURRENT_DATE
ORDER BY due_date ASC;
```

### Get tasks due today
```sql
SELECT * FROM tasks
WHERE user_id = $1
  AND completed = FALSE
  AND due_date = CURRENT_DATE
ORDER BY due_time ASC NULLS LAST;
```

### Get high priority tasks
```sql
SELECT * FROM tasks
WHERE user_id = $1
  AND priority = 'high'
ORDER BY created_at DESC;
```

### Search tasks by keyword
```sql
SELECT * FROM tasks
WHERE user_id = $1
  AND (title ILIKE '%' || $2 || '%' OR description ILIKE '%' || $2 || '%')
ORDER BY created_at DESC;
```

### Get tasks by tag
```sql
SELECT * FROM tasks
WHERE user_id = $1
  AND tags LIKE '%' || $2 || '%'
ORDER BY created_at DESC;
```

---

## Performance Considerations

**Indexes**: All frequently filtered columns are indexed (user_id, created_at, due_date, completed, priority)

**Query Optimization**:
- Always filter by `user_id` first (leverages index, reduces result set)
- Use LIMIT and OFFSET for pagination (if needed for 1000+ tasks)
- Avoid full table scans (all queries use indexed columns)

**Expected Query Times**:
- User's tasks (100 tasks): <50ms
- Filtered queries (priority, tags): <100ms
- Search queries (ILIKE): <200ms (consider full-text search for Phase 3+)

**Scaling**:
- Current schema handles 10,000 users × 1,000 tasks = 10M rows efficiently
- Consider partitioning by user_id if exceeding 100M rows (Phase 4+)

---

## Validation Rules (Enforced in Service Layer)

1. **Title**: Required, max 200 characters, trimmed
2. **Description**: Optional, max 1000 characters
3. **Priority**: Must be 'low', 'medium', 'high', or NULL
4. **Tags**: Comma-separated string, no validation on individual tags
5. **Due Date**: Valid ISO date (YYYY-MM-DD)
6. **Due Time**: Only allowed if due_date is set, format HH:MM
7. **Recurrence Pattern**: Must be 'daily', 'weekly', 'monthly', or NULL
8. **Recurrence Day**: 1-7 for weekly, 1-31 for monthly
9. **User ID**: Must reference existing user (foreign key enforced)

---

## Next Steps

1. ✅ Data model defined
2. → Create API contracts (`contracts/`)
3. → Create `quickstart.md` for database setup
4. → Generate `tasks.md` with `/sp.tasks` command
