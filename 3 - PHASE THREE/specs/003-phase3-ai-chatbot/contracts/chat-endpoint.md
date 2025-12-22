# Chat Endpoint Contract

**Feature**: AI-Powered Todo Chatbot (Phase 3)
**Date**: 2025-12-17
**Source**: [spec.md](../spec.md) | [plan.md](../plan.md)

## Overview

The chat endpoint is the primary interface for the AI-powered todo chatbot. It is **stateless** - all conversation state is persisted to the database. Every request fetches conversation history from the database, processes with the AI agent, and stores new messages.

**Endpoint**: `POST /api/{user_id}/chat`

**Architecture**: Stateless → Horizontally Scalable → Resilient to Restarts

---

## Request Specification

### HTTP Method & URL

```
POST /api/{user_id}/chat
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | User ID (must match JWT token user_id claim) |

### Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | Yes | Bearer token: `Bearer <JWT_TOKEN>` |
| `Content-Type` | Yes | `application/json` |

### Request Body Schema

```typescript
interface ChatRequest {
  conversation_id?: number;  // Optional: omit to start new conversation
  message: string;           // Required: user message content
}
```

### Request Body Example (New Conversation)

```json
{
  "message": "Add a task to buy groceries"
}
```

### Request Body Example (Continuing Conversation)

```json
{
  "conversation_id": 123,
  "message": "Mark task 3 as complete"
}
```

### Validation Rules

1. **message**: Required, min 1 character, max 5000 characters
2. **conversation_id**: Optional, must be positive integer if provided
3. **JWT Token**: Must be valid and not expired
4. **user_id Path Parameter**: Must match JWT token user_id claim (403 if mismatch)

---

## Response Specification

### Success Response (200 OK)

```typescript
interface ChatResponse {
  conversation_id: number;   // Conversation ID (new or existing)
  response: string;          // Assistant's response
  tool_calls: string[];      // Names of MCP tools called (e.g., ["add_task"])
}
```

### Success Response Example

```json
{
  "conversation_id": 123,
  "response": "I've added 'Buy groceries' to your task list. Task ID is 5.",
  "tool_calls": ["add_task"]
}
```

### Error Responses

#### 400 Bad Request

**When**: Invalid request body (missing message, message too long, etc.)

```json
{
  "error": "Bad Request",
  "message": "Message is required and cannot be empty",
  "status_code": 400
}
```

#### 401 Unauthorized

**When**: Missing JWT token or invalid/expired token

```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired authentication token",
  "status_code": 401
}
```

#### 403 Forbidden

**When**: user_id path parameter doesn't match JWT token user_id OR user trying to access another user's conversation

```json
{
  "error": "Forbidden",
  "message": "Access denied to this resource",
  "status_code": 403
}
```

#### 404 Not Found

**When**: conversation_id provided but conversation doesn't exist

```json
{
  "error": "Not Found",
  "message": "Conversation with ID 999 not found",
  "status_code": 404
}
```

#### 503 Service Unavailable

**When**: OpenAI API unavailable, database connection failure, or other transient errors

```json
{
  "error": "Service Unavailable",
  "message": "I'm having trouble connecting right now. Please try again in a moment.",
  "status_code": 503
}
```

---

## Request Processing Flow

### Stateless Request Cycle (10 Steps)

```
1. Receive POST request with conversation_id (optional) and message (required)
   ↓
2. Validate JWT token → Extract user_id
   ↓
3. Validate user_id path parameter matches JWT user_id (403 if not)
   ↓
4. IF conversation_id provided:
     - Fetch conversation from database
     - Verify conversation.user_id == user_id (403 if not)
     - Fetch last 50 messages ordered by created_at ASC
   ELSE:
     - Create new conversation record (user_id, created_at, updated_at)
     - Empty message history
   ↓
5. Store user message in messages table
     (conversation_id, user_id, role="user", content=message)
   ↓
6. Build message array for agent:
     [{role: "user", content: "..."}, {role: "assistant", content: "..."}, ...]
   ↓
7. Pass message array to OpenAI Agents SDK with agent + MCP tools
     response = await agent.run(messages=message_array, user_id=user_id)
   ↓
8. Agent processes message:
     - Recognizes intent (add task, list tasks, etc.)
     - Calls appropriate MCP tools
     - Generates conversational response
   ↓
9. Store assistant response in messages table
     (conversation_id, user_id, role="assistant", content=response)
   ↓
10. Return response to client (conversation_id, response, tool_calls)
   ↓
11. Server forgets everything → Ready for next request (STATELESS)
```

### Performance Targets

| Step | Target Latency | Notes |
|------|----------------|-------|
| Database fetch (conversation + messages) | ~100ms | Indexed query on conversation_id |
| OpenAI Agents SDK processing | ~1-2 seconds | Largest component, depends on model |
| MCP tool execution | ~50-200ms per tool | 1-3 tools per request |
| Database write (2 messages) | ~50ms | Two INSERT statements |
| **Total** | **<3 seconds (95% of requests)** | Meets Phase 3 performance goal |

---

## Authentication & Authorization

### JWT Token Validation

```python
from fastapi import Header, HTTPException

async def verify_token(authorization: str = Header(...)) -> str:
    """Verify JWT token and extract user_id."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid authorization header")

    token = authorization[7:]  # Remove "Bearer " prefix

    try:
        payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(401, "Invalid token payload")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")
```

### User Isolation

1. **Path Parameter Check**: Ensure `path_user_id == token_user_id` (403 if not)
2. **Conversation Ownership**: Ensure `conversation.user_id == token_user_id` (403 if not)
3. **Message Isolation**: All messages inherit conversation.user_id (stored for audit)
4. **MCP Tool Isolation**: All tools receive token_user_id, filter queries by user_id

---

## Conversation History Management

### Fetching Conversation History

```python
# Fetch last 50 messages for conversation
messages = session.exec(
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.created_at.asc())
    .limit(50)
    .offset(max(0, total_count - 50))  # Get last 50 if > 50 messages
).all()
```

### Why Limit to 50 Messages?

1. **Token Limits**: GPT-4 has token limits (8k-128k depending on version)
2. **Performance**: Smaller message array = faster processing
3. **Cost**: Fewer tokens = lower OpenAI API costs
4. **Sufficient Context**: 50 messages typically cover 10-15 conversation turns

### Older Messages

- Remain in database (not deleted)
- Not sent to agent (excluded from message array)
- User can still view full history in UI (separate read-only endpoint)

---

## Error Handling Strategy

### MCP Tool Errors

**Scenario**: Tool returns error status (e.g., task not found)

**Handling**:
- Agent receives error response from tool
- Agent generates conversational error message: "I couldn't find task 999. Would you like to see your task list?"
- No HTTP error code (200 OK with conversational error message)

### OpenAI API Errors

**Scenario**: OpenAI API returns 429 (rate limit) or 503 (service unavailable)

**Handling**:
- Catch OpenAI API exception
- Return 503 Service Unavailable
- User-friendly message: "I'm experiencing high demand. Please try again in a moment."

### Database Errors

**Scenario**: Database connection failure or query timeout

**Handling**:
- Catch database exception
- Return 503 Service Unavailable
- User-friendly message: "I'm having trouble saving your request. Please try again."

### Validation Errors

**Scenario**: Invalid input (empty message, invalid conversation_id)

**Handling**:
- FastAPI Pydantic validation automatically returns 422 Unprocessable Entity
- Or manually return 400 Bad Request with specific error message

---

## Testing Requirements

### Unit Tests

1. **JWT Validation**:
   - Valid token → Extract user_id
   - Invalid token → 401 Unauthorized
   - Expired token → 401 Unauthorized
   - Missing token → 401 Unauthorized

2. **User Isolation**:
   - Path user_id matches JWT user_id → Success
   - Path user_id doesn't match JWT user_id → 403 Forbidden
   - User accessing another user's conversation → 403 Forbidden

### Integration Tests

1. **New Conversation Flow**:
   - POST with no conversation_id
   - New conversation created
   - User message stored
   - Agent processes message
   - Assistant response stored
   - conversation_id returned

2. **Continuing Conversation Flow**:
   - POST with existing conversation_id
   - Conversation history fetched (last 50 messages)
   - User message appended
   - Agent has full context
   - Assistant response stored

3. **Stateless Architecture**:
   - Server restart between requests
   - Conversation history still accessible
   - No data loss

### End-to-End Tests

1. **Full User Journey**:
   - User logs in (get JWT token)
   - User sends "Add a task to buy groceries"
   - Verify conversation created, message stored, task created, response returned
   - User sends "Show me my tasks"
   - Verify conversation history includes previous messages
   - User sends "Mark task X as complete"
   - Verify task marked complete, response confirms

---

## Deployment Considerations

### Environment Variables

```bash
# Required for chat endpoint
OPENAI_API_KEY=sk-...                    # OpenAI API key for Agents SDK
BETTER_AUTH_SECRET=...                   # Shared secret for JWT validation
DATABASE_URL=postgresql://...            # Neon PostgreSQL connection string
```

### Monitoring & Logging

**Log Each Request**:
- Request ID
- User ID
- Conversation ID
- Message length
- Response time
- Tool calls made
- Errors (if any)

**Example Log Entry**:
```json
{
  "request_id": "req_abc123",
  "user_id": "user_xyz",
  "conversation_id": 123,
  "message_length": 28,
  "response_time_ms": 1850,
  "tool_calls": ["add_task"],
  "status": "success"
}
```

---

## Summary

**Endpoint**: `POST /api/{user_id}/chat`

**Key Characteristics**:
- ✅ Stateless (no in-memory state)
- ✅ Horizontally scalable
- ✅ Resilient to restarts
- ✅ Conversation history persisted to database
- ✅ JWT authentication required
- ✅ User data isolation enforced
- ✅ Performance target: <3 seconds for 95% of requests

**Next Steps**:
1. Implement endpoint in `backend/app/routes/chat.py`
2. Write integration tests in `tests/integration/test_chat_endpoint.py`
3. Test with mock OpenAI API responses
4. Validate stateless architecture (restart test)

---

**Status**: ✅ Chat Endpoint Contract Complete
**Date**: 2025-12-17
**Next**: Implement endpoint with TDD workflow
