# Data Models: AI-Powered Todo Chatbot (Phase 3)

**Feature**: AI-Powered Todo Chatbot
**Date**: 2025-12-17
**Source**: [spec.md](./spec.md) | [plan.md](./plan.md)

## Overview

Phase 3 extends Phase 2 database schema with two new tables for conversation state management: **Conversation** and **Message**. The existing **Task** table from Phase 2 is preserved with all fields intact to support all 10 features via natural language.

**Key Design Principles**:
- **Stateless Architecture**: All conversation state persisted to database (no in-memory state)
- **User Isolation**: All tables include user_id with foreign key constraints
- **Performance**: Indexes on frequently queried columns (user_id, conversation_id, created_at)
- **Simplicity**: SQLModel automatic table creation (no manual migrations in Phase 3)

---

## Entity Relationship Diagram

```
┌──────────────────────┐
│       User           │
│  (Better Auth)       │
│ ─────────────────────│
│  id (PK, string)     │───┐
│  email               │   │
│  name                │   │
│  created_at          │   │
└──────────────────────┘   │
                           │
                           │ 1:N
                           │
         ┌─────────────────┴─────────────────┬──────────────────┐
         │                                   │                  │
         ▼                                   ▼                  ▼
┌──────────────────────┐         ┌──────────────────────┐   ┌──────────────────────┐
│   Conversation       │         │       Task           │   │      Message         │
│  (NEW - Phase 3)     │         │  (Phase 2, preserved)│   │  (NEW - Phase 3)     │
│ ─────────────────────│         │ ─────────────────────│   │ ─────────────────────│
│  id (PK)             │───┐     │  id (PK)             │   │  id (PK)             │
│  user_id (FK)        │   │     │  user_id (FK)        │   │  conversation_id (FK)│
│  created_at          │   │     │  title               │   │  user_id (FK)        │
│  updated_at          │   │     │  description         │   │  role                │
└──────────────────────┘   │     │  completed           │   │  content             │
                           │     │  priority            │   │  created_at          │
                           │     │  tags                │   └──────────────────────┘
                           │     │  due_date            │
                           │     │  due_time            │
                           │     │  recurrence          │
                           │     │  recurrence_day      │
                           │     │  created_at          │
                           │     │  updated_at          │
                           │     └──────────────────────┘
                           │
                           │ 1:N
                           │
                           ▼
                   ┌──────────────────────┐
                   │      Message         │
                   │  (linked to conv)    │
                   └──────────────────────┘
```

---

## Entities

### 1. User (Managed by Better Auth)

**Description**: User accounts managed by Better Auth. Existing table from Phase 2.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | string (UUID) | PRIMARY KEY | Unique user identifier (Better Auth UUID) |
| `email` | string | UNIQUE, NOT NULL, INDEX | User email address |
| `name` | string | NOT NULL | User display name |
| `created_at` | timestamp | DEFAULT NOW() | Account creation timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `email`

**Notes**:
- Managed by Better Auth (no manual changes)
- Used as foreign key in Conversation, Message, Task tables

---

### 2. Conversation (NEW - Phase 3)

**Description**: Represents a chat conversation between user and AI assistant. Each conversation contains multiple messages. Conversations are stateless - all state persisted to database.

**Purpose**: Enable multi-turn conversations with persistent history across server restarts.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | int | PRIMARY KEY, AUTO INCREMENT | Unique conversation identifier |
| `user_id` | string | FOREIGN KEY (users.id), NOT NULL, INDEX | Owner of conversation (data isolation) |
| `created_at` | timestamp | DEFAULT NOW(), INDEX | When conversation started |
| `updated_at` | timestamp | DEFAULT NOW() | Last message timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id` (for listing user's conversations)
- INDEX on `created_at` (for sorting conversations)

**Relationships**:
- **User** (N:1): Each conversation belongs to one user
- **Message** (1:N): Each conversation has many messages

**SQLModel Definition**:
```python
from sqlmodel import Field, SQLModel
from datetime import datetime

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Business Rules**:
1. Conversations are immutable once created (no deletion in Phase 3)
2. `updated_at` timestamp updated whenever new message added
3. All conversations isolated by `user_id` (users can only access their own)
4. Empty conversations allowed (user opens chat but doesn't send message yet)

**Query Patterns**:
```python
# List user's conversations (ordered by most recent)
conversations = session.exec(
    select(Conversation)
    .where(Conversation.user_id == user_id)
    .order_by(Conversation.updated_at.desc())
).all()

# Get specific conversation (with ownership check)
conversation = session.get(Conversation, conversation_id)
if conversation.user_id != user_id:
    raise HTTPException(403, "Access denied")
```

---

### 3. Message (NEW - Phase 3)

**Description**: Represents a single message in a conversation (either user message or assistant response). All messages persisted to database for stateless architecture.

**Purpose**: Store conversation history for context management and enable message retrieval across sessions.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | int | PRIMARY KEY, AUTO INCREMENT | Unique message identifier |
| `conversation_id` | int | FOREIGN KEY (conversations.id), NOT NULL, INDEX | Parent conversation |
| `user_id` | string | FOREIGN KEY (users.id), NOT NULL, INDEX | Message owner (data isolation) |
| `role` | enum ("user" \| "assistant") | NOT NULL, INDEX | Who sent the message |
| `content` | text | NOT NULL, MAX 5000 chars | Message text content |
| `created_at` | timestamp | DEFAULT NOW(), INDEX | When message was sent |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `conversation_id` (for fetching conversation history - most common query)
- INDEX on `user_id` (for data isolation checks)
- INDEX on `role` (for filtering by message type)
- INDEX on `created_at` (for ordering messages chronologically)

**Relationships**:
- **Conversation** (N:1): Each message belongs to one conversation
- **User** (N:1): Each message has an owner (for data isolation)

**SQLModel Definition**:
```python
from sqlmodel import Field, SQLModel
from typing import Literal
from datetime import datetime

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    role: Literal["user", "assistant"] = Field(index=True)
    content: str = Field(max_length=5000)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
```

**Business Rules**:
1. Messages are immutable once created (no editing or deletion in Phase 3)
2. `role` must be either "user" or "assistant" (enforced by Literal type)
3. `content` limited to 5000 characters (prevent abuse)
4. All messages isolated by `user_id` (inherited from conversation owner)
5. Messages ordered by `created_at` ascending for conversation flow

**Query Patterns**:
```python
# Fetch conversation history (last 50 messages)
messages = session.exec(
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.created_at.asc())
    .limit(50)
    .offset(max(0, total_count - 50))  # Get last 50 if > 50 messages
).all()

# Store new user message
user_message = Message(
    conversation_id=conversation_id,
    user_id=user_id,
    role="user",
    content=message_content
)
session.add(user_message)
session.commit()

# Store assistant response
assistant_message = Message(
    conversation_id=conversation_id,
    user_id=user_id,
    role="assistant",
    content=response_content
)
session.add(assistant_message)
session.commit()
```

**Performance Considerations**:
- Conversation history limited to last 50 messages (prevent token overflow, optimize query time)
- Older messages remain in database but not sent to OpenAI agent
- Index on `conversation_id` + `created_at` for fast history retrieval
- Single query to fetch all messages (no N+1 queries)

---

### 4. Task (Phase 2, Preserved)

**Description**: Represents a todo task with all features (priorities, tags, due dates, recurrence). Existing table from Phase 2, unchanged for Phase 3.

**Purpose**: Store task data accessed by MCP tools via AI agent.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | int | PRIMARY KEY, AUTO INCREMENT | Unique task identifier |
| `user_id` | string | FOREIGN KEY (users.id), NOT NULL, INDEX | Task owner |
| `title` | string | NOT NULL, MAX 200 chars | Task title |
| `description` | text | OPTIONAL, MAX 1000 chars | Task description |
| `completed` | boolean | DEFAULT FALSE, INDEX | Completion status |
| `priority` | string | OPTIONAL ("high" \| "medium" \| "low"), INDEX | Task priority (Intermediate Feature 6) |
| `tags` | string | OPTIONAL (comma-separated), INDEX | Task tags/categories (Intermediate Feature 6) |
| `due_date` | date | OPTIONAL, INDEX | Due date (Advanced Feature 10) |
| `due_time` | time | OPTIONAL | Due time (Advanced Feature 10) |
| `recurrence` | string | OPTIONAL ("daily" \| "weekly" \| "monthly") | Recurrence pattern (Advanced Feature 9) |
| `recurrence_day` | int | OPTIONAL (1-31) | Day of week/month for recurrence |
| `created_at` | timestamp | DEFAULT NOW(), INDEX | Task creation timestamp |
| `updated_at` | timestamp | DEFAULT NOW() | Last modification timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id` (for data isolation)
- INDEX on `completed` (for filtering pending/completed)
- INDEX on `priority` (for filtering by priority)
- INDEX on `due_date` (for sorting by due date)
- INDEX on `created_at` (for sorting by creation date)

**Relationships**:
- **User** (N:1): Each task belongs to one user

**SQLModel Definition**:
```python
from sqlmodel import Field, SQLModel
from datetime import datetime, date, time

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)

    # Intermediate Level (Priorities & Tags)
    priority: str | None = Field(default=None, index=True)  # "high", "medium", "low"
    tags: str | None = Field(default=None)  # Comma-separated tags

    # Advanced Level (Recurring & Due Dates)
    due_date: date | None = Field(default=None, index=True)
    due_time: time | None = Field(default=None)
    recurrence: str | None = Field(default=None)  # "daily", "weekly", "monthly"
    recurrence_day: int | None = Field(default=None)  # Day of week/month

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Business Rules**:
1. All MCP tools filter tasks by `user_id` (data isolation)
2. Recurring tasks: when completed, create new task with next due date
3. Tags stored as comma-separated string (e.g., "work,urgent,health")
4. Priority values: "high", "medium", "low" (validated by MCP tools)
5. Recurrence patterns: "daily", "weekly", "monthly" (validated by MCP tools)

**Query Patterns**:
```python
# List tasks with filters (used by list_tasks MCP tool)
query = select(Task).where(Task.user_id == user_id)
if status == "pending":
    query = query.where(Task.completed == False)
elif status == "completed":
    query = query.where(Task.completed == True)
if priority:
    query = query.where(Task.priority == priority)
if tag:
    query = query.where(Task.tags.contains(tag))
if sort_by:
    query = query.order_by(getattr(Task, sort_by))
tasks = session.exec(query).all()
```

---

## Database Initialization

**SQLModel Automatic Table Creation**:
```python
from sqlmodel import SQLModel, create_engine

# In backend/app/db.py
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

**Tables Created on First Run**:
1. `users` (Better Auth)
2. `tasks` (Phase 2, existing)
3. `conversations` (Phase 3, NEW)
4. `messages` (Phase 3, NEW)

**Foreign Key Relationships**:
- `tasks.user_id` → `users.id`
- `conversations.user_id` → `users.id`
- `messages.conversation_id` → `conversations.id`
- `messages.user_id` → `users.id`

---

## Data Retention & Cleanup

**Phase 3 Policy** (No Automatic Cleanup):
- Conversations and messages persist indefinitely
- No automatic archiving or deletion
- Users cannot delete conversations in Phase 3 (future feature)
- Tasks can be deleted via MCP tool (delete_task)

**Future Phases** (Out of Scope):
- Conversation archiving after 90 days of inactivity
- Message cleanup for conversations with >500 messages
- User-initiated conversation deletion
- Export conversation history as JSON/PDF

---

## Performance Considerations

**Query Optimization**:
1. **Conversation History Fetch** (most common query):
   - Index on `messages.conversation_id`
   - Index on `messages.created_at`
   - Limit to last 50 messages
   - Single query (no N+1)
   - Expected latency: ~100ms

2. **Task Filtering** (MCP tools):
   - Indexes on `user_id`, `completed`, `priority`, `due_date`
   - Filters applied at database level (not in-memory)
   - Expected latency: ~50-200ms

3. **User's Conversations List**:
   - Index on `conversations.user_id`
   - Ordered by `updated_at` desc
   - Expected latency: ~50ms

**Connection Pooling**:
- SQLModel/SQLAlchemy connection pool (5-10 connections)
- Configured in `backend/app/db.py`
- Recycle connections every 3600 seconds

**Scalability**:
- Neon Serverless PostgreSQL autoscaling
- Supports 1,000+ concurrent users
- Database queries optimized for <500ms latency

---

## Security & Data Isolation

**User Data Isolation**:
- All tables include `user_id` foreign key
- All queries filtered by `user_id`
- MCP tools enforce ownership checks
- JWT token provides authenticated `user_id`
- Path parameter `{user_id}` must match JWT `user_id`

**SQL Injection Prevention**:
- SQLModel parameterized queries (automatic)
- No raw SQL strings
- Pydantic validation for all inputs

**Data Access Control**:
- Users can only access their own conversations, messages, tasks
- 403 Forbidden if attempting to access others' data
- Enforced at MCP tool level and chat endpoint level

---

## Summary

**Phase 3 Database Schema**:
- ✅ 2 new tables: Conversation, Message (stateless conversation state)
- ✅ 1 existing table: Task (all Phase 2 fields preserved)
- ✅ All tables include `user_id` for data isolation
- ✅ Indexes optimized for common queries (conversation history, task filtering)
- ✅ SQLModel automatic table creation (no manual migrations)
- ✅ Performance target: <500ms for all database queries

**Next Steps**:
1. Implement database models in `backend/app/models.py`
2. Create database connection in `backend/app/db.py`
3. Write model validation tests in `tests/unit/test_models.py`
4. Implement MCP tools using these models
5. Implement chat endpoint with conversation persistence

---

**Status**: ✅ Data Model Design Complete
**Ready for**: Implementation (`/sp.tasks` → `/sp.implement`)
**Date**: 2025-12-17
