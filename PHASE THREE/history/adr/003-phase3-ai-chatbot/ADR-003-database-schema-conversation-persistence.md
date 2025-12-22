# ADR-003: Database Schema for Conversation Persistence

**Status**: Accepted
**Date**: 2025-12-17
**Deciders**: Architecture Team
**Feature**: Phase 3 - AI-Powered Todo Chatbot

## Context

Phase 3 requires storing conversation history to enable multi-turn conversations and stateless architecture. The database must:

1. **Persist Conversation State**: Store all user and assistant messages for context
2. **Support Multi-User**: Isolate conversations by user_id
3. **Enable Fast Retrieval**: Fetch conversation history efficiently (<100ms)
4. **Scale with Usage**: Handle 1,000 concurrent users, growing message volume
5. **Integrate with Existing Schema**: Leverage Phase 2 Neon PostgreSQL infrastructure

**Constraints**:
- Must use existing Neon Serverless PostgreSQL (no new database technology)
- Must use SQLModel ORM (Phase 2 standard)
- Must support automatic table creation (no manual migrations in Phase 3)
- Must maintain existing Task table structure (all Phase 2 fields intact)
- Must enforce user data isolation via foreign keys and indexes

**Problem**: How should we model conversations and messages in the database to support stateless architecture, fast queries, and horizontal scaling?

## Decision

We will add **two new normalized tables** to the existing PostgreSQL database:

### 1. Conversations Table

**Purpose**: Represent a chat conversation between user and AI assistant

**Schema**:
```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id` (for listing user's conversations)
- INDEX on `created_at` (for sorting by recency)

**Relationships**:
- **User** (N:1): Each conversation belongs to one user
- **Message** (1:N): Each conversation has many messages

### 2. Messages Table

**Purpose**: Store individual messages within a conversation

**Schema**:
```python
class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    role: Literal["user", "assistant"] = Field(index=True)
    content: str = Field(max_length=5000)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
```

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `conversation_id` (for fetching conversation history - most common query)
- INDEX on `user_id` (for data isolation checks)
- INDEX on `role` (for filtering by message type)
- INDEX on `created_at` (for chronological ordering)

**Relationships**:
- **Conversation** (N:1): Each message belongs to one conversation
- **User** (N:1): Each message has an owner (for data isolation)

### 3. Existing Tasks Table (Unchanged)

**Purpose**: Store todo tasks (preserved from Phase 2)

**Schema**: No changes - all Phase 2 fields preserved (id, user_id, title, description, completed, priority, tags, due_date, due_time, recurrence, recurrence_day, created_at, updated_at)

## Consequences

### Positive

1. **Normalized Schema**: Conversations → Messages (1:N) prevents data duplication
2. **Fast Queries**: Index on `conversation_id` + `created_at` enables <100ms conversation history fetch
3. **User Isolation**: Foreign keys and indexes enforce multi-user data separation
4. **Relational Integrity**: Database enforces conversation-message relationships
5. **No N+1 Queries**: Single JOIN-free query fetches all messages for conversation
6. **Simple Pagination**: LIMIT and OFFSET work naturally for message history
7. **Auditability**: Full message history preserved for debugging and analysis
8. **SQLModel Automation**: Automatic table creation on first run (no manual migrations)
9. **Backward Compatible**: Existing Task table unchanged, Phase 2 functionality preserved

### Negative

1. **Storage Growth**: Message history grows unbounded (no automatic cleanup in Phase 3)
2. **Index Maintenance**: Multiple indexes require storage and update overhead
3. **No Built-in Archiving**: Old conversations remain in hot storage (no cold tier)
4. **Limited Message Size**: 5000 character limit per message (prevents abuse but limits long responses)
5. **No Message Editing**: Immutable messages (edit = new message, not in Phase 3)

### Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Storage growth over time | High | Low | Future: implement archiving policy (90 days inactive) |
| Slow queries on large tables | Low | Medium | Indexes on conversation_id, created_at; limit to 50 messages |
| Index bloat | Low | Low | PostgreSQL automatic index maintenance, VACUUM |
| Conversation orphaning | Low | Medium | Foreign key cascade on user deletion (preserve or cleanup) |
| Message table size | Medium | Low | Future: partition by created_at (monthly partitions) |

## Alternatives Considered

### Alternative 1: Single Table with JSON Column for Messages

**Approach**: Store all messages as JSON array in conversations table

**Schema**:
```python
class Conversation(SQLModel, table=True):
    id: int
    user_id: str
    messages: JSON  # [{role: "user", content: "..."}, ...]
    created_at: datetime
```

**Pros**:
- Single table, simpler schema
- All conversation data in one row (no JOIN needed)

**Cons**:
- Can't index messages (slow search within conversations)
- Can't paginate messages (all or nothing)
- Can't query by message role or content
- JSON size grows unbounded (no message-level limit)
- Violates database normalization principles
- Hard to analyze message patterns (aggregate queries)

**Why Rejected**: Poor query performance, can't paginate, violates normalization, hard to analyze

### Alternative 2: NoSQL Document Store (MongoDB)

**Approach**: Store conversations as documents with nested messages array

**Schema**:
```javascript
{
  _id: ObjectId,
  user_id: "user_xyz",
  messages: [
    {role: "user", content: "...", created_at: ISODate},
    {role: "assistant", content: "...", created_at: ISODate}
  ],
  created_at: ISODate
}
```

**Pros**:
- Flexible schema (nested documents)
- Good for nested data (conversations with messages)
- Could scale horizontally (sharding)

**Cons**:
- Adds new database technology (MongoDB deployment, monitoring)
- Data duplication (tasks in PostgreSQL, conversations in MongoDB)
- Migration complexity (sync user data across databases)
- No relational integrity with existing User and Task tables
- Team learning curve (SQL → NoSQL)
- Violates Phase 3 constraint (leverage existing Neon PostgreSQL)

**Why Rejected**: Adds unnecessary complexity, violates constraint to use existing infrastructure, data duplication issues

### Alternative 3: Time-Series Database (TimescaleDB)

**Approach**: Use TimescaleDB (PostgreSQL extension) for time-series message data

**Pros**:
- Optimized for time-series data (messages ordered by time)
- Automatic partitioning by time
- Fast range queries

**Cons**:
- Requires PostgreSQL extension (not available on all platforms)
- Neon may not support TimescaleDB extension
- Over-engineering for Phase 3 requirements
- Learning curve for team
- Standard PostgreSQL indexes sufficient for <1,000 users

**Why Rejected**: Premature optimization, may not be available on Neon, standard indexes sufficient

### Alternative 4: Separate Database for Conversations

**Approach**: Create separate PostgreSQL database for conversation data

**Pros**:
- Isolation between task data and conversation data
- Could scale conversation database independently

**Cons**:
- Adds operational complexity (two databases to manage)
- Cross-database foreign keys not supported (user_id references)
- More complex deployment and backup strategy
- No benefit for Phase 3 scope (single database handles 1,000 users)
- Violates YAGNI principle

**Why Rejected**: Unnecessary complexity, no scalability benefit for Phase 3 scope

## Query Patterns & Performance

### Most Common Query: Fetch Conversation History

```sql
SELECT id, role, content, created_at
FROM messages
WHERE conversation_id = $1
ORDER BY created_at ASC
LIMIT 50;
```

**Expected Latency**: ~100ms (with index on conversation_id + created_at)

### Create New Conversation

```sql
INSERT INTO conversations (user_id, created_at, updated_at)
VALUES ($1, NOW(), NOW())
RETURNING id;
```

**Expected Latency**: ~50ms

### Store New Message

```sql
INSERT INTO messages (conversation_id, user_id, role, content, created_at)
VALUES ($1, $2, $3, $4, NOW());
```

**Expected Latency**: ~25ms (2 messages per request = 50ms total)

## References

- [Phase 3 Implementation Plan](../../../specs/003-phase3-ai-chatbot/plan.md) (Section: Database Schema for Conversations and Messages)
- [Phase 3 Research Document](../../../specs/003-phase3-ai-chatbot/research.md) (Research Area 5)
- [Data Model Specification](../../../specs/003-phase3-ai-chatbot/data-model.md)
- [Phase 3 Constitution (v3.0.0)](../../../.specify/memory/constitution.md) (Principle X: Database Schema & Migration Management)
- [Chat Endpoint Contract](../../../specs/003-phase3-ai-chatbot/contracts/chat-endpoint.md)

## Notes

- Decision aligns with Constitution Principle X (Database Schema & Migration Management)
- SQLModel automatic table creation used (constitution allows for Phase 3)
- Normalized schema follows database best practices
- Existing Task table unchanged (backward compatibility with Phase 2)
- User data isolation enforced via foreign keys and indexes
- Performance targets met (<100ms conversation history fetch, <3 second total response)

---

**Last Updated**: 2025-12-17
**Supersedes**: None (Phase 3 initial schema)
**Superseded By**: None
