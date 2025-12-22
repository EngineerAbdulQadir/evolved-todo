# Research: AI-Powered Todo Chatbot (Phase 3)

**Feature**: AI-Powered Todo Chatbot
**Date**: 2025-12-17
**Source**: [spec.md](./spec.md) | [plan.md](./plan.md)

## Overview

This document consolidates all research findings and technology decisions for Phase 3 AI chatbot implementation. All decisions have been validated against the Phase 3 constitution (v3.0.0) and architectural requirements.

---

## Research Areas

### 1. OpenAI ChatKit Integration

**Research Question**: Which conversational UI component should we use for the chatbot interface?

**Options Evaluated**:
1. **OpenAI ChatKit** (SELECTED)
2. Custom React Chat UI
3. Third-party libraries (stream-chat-react, react-chat-ui)

**Decision**: Use OpenAI ChatKit as the primary conversational UI component

**Rationale**:
- ✅ Pre-built chat interface with typing indicators, message formatting, conversation history display
- ✅ Officially maintained by OpenAI, ensuring compatibility with Agents SDK
- ✅ Supports React/Next.js integration via npm package (`@openai/chatkit`)
- ✅ Handles UI concerns (scrolling, timestamps, user/assistant message styling) out of the box
- ✅ Reduces frontend complexity, allowing focus on AI logic and MCP tools
- ✅ Proven UX patterns for conversational interfaces
- ✅ Regular updates and bug fixes from OpenAI team

**Alternatives Considered**:
- **Custom React Chat UI**:
  - Pros: Full control over design and behavior
  - Cons: High development overhead, need to implement scrolling, message formatting, typing indicators, accessibility
  - Rejected: ChatKit provides proven UX patterns, not worth reinventing

- **Third-party chat libraries (stream-chat-react, react-chat-ui)**:
  - Pros: Pre-built components, some customization
  - Cons: Not optimized for AI agents, lack OpenAI integration, dependency on third-party maintenance
  - Rejected: ChatKit better integrated with OpenAI ecosystem

**Implementation Approach**:
- Install `@openai/chatkit` npm package in frontend/
- Create ChatInterface component wrapping ChatKit with Better Auth token injection
- Configure ChatKit to send messages to backend chat endpoint (`POST /api/{user_id}/chat`)
- Display conversation history from database on component mount
- Handle message sending, receiving, and error states
- Integrate with existing Better Auth JWT authentication

**Documentation**: https://platform.openai.com/docs/guides/chatkit

**Risk Assessment**: Low risk - officially supported, well-documented, active development

---

### 2. OpenAI Agents SDK for Intent Recognition

**Research Question**: Which AI framework should we use for natural language understanding and tool calling?

**Options Evaluated**:
1. **OpenAI Agents SDK** (SELECTED)
2. Direct OpenAI API calls with function calling
3. LangChain framework
4. Custom NLU with regex/NER

**Decision**: Use OpenAI Agents SDK for AI logic and natural language understanding

**Rationale**:
- ✅ Purpose-built for agentic workflows (intent recognition, tool calling, multi-turn conversations)
- ✅ Native support for MCP tools via tool definitions
- ✅ Handles conversation context management automatically (maintains message history)
- ✅ Provides retry logic and error handling for OpenAI API calls
- ✅ Simplifies system prompt management and agent configuration
- ✅ Built-in support for streaming responses (future enhancement)
- ✅ Aligns with Constitution Principle XII (AI Agent Development)

**Alternatives Considered**:
- **Direct OpenAI API calls with function calling**:
  - Pros: Lower-level control, no SDK dependency
  - Cons: Requires manual tool calling logic, conversation tracking, error handling, retry logic
  - Rejected: Too much boilerplate, agents SDK abstracts complexity

- **LangChain framework**:
  - Pros: Many abstractions, large ecosystem, supports multiple LLMs
  - Cons: More abstraction layers, heavier dependency, overkill for simple tool calling, steeper learning curve
  - Rejected: Adds unnecessary complexity for Phase 3 requirements

- **Custom NLU with regex/NER**:
  - Pros: Full control, no API costs
  - Cons: Not robust enough for varied natural language inputs, requires training data, maintenance burden
  - Rejected: GPT-4 already handles NLU well, no need to reinvent

**Implementation Approach**:
- Install `openai-agents-sdk` via UV in backend/ (`uv add openai-agents-sdk`)
- Create `backend/app/agents/todo_agent.py` with agent initialization
- Define system prompt in `backend/app/agents/prompts.py`
- Register MCP tools with agent via tool definitions
- Agent receives conversation history + new message, decides which tools to call
- Agent returns conversational response wrapping tool outputs

**Key Configuration**:
```python
from openai_agents import Agent, Tool

agent = Agent(
    name="todo_assistant",
    model="gpt-4",  # or "gpt-4-turbo" for faster responses
    instructions=SYSTEM_PROMPT,
    tools=[add_task_tool, list_tasks_tool, search_tasks_tool,
           complete_task_tool, delete_task_tool, update_task_tool]
)

# Run agent with conversation history
response = await agent.run(
    messages=conversation_history,
    user_id=user_id
)
```

**Documentation**: https://github.com/openai/openai-agents-sdk

**Risk Assessment**: Low risk - officially supported by OpenAI, production-ready, active development

---

### 3. Official MCP SDK (Python) for Stateless Tools

**Research Question**: How should we implement task operation tools for the AI agent?

**Options Evaluated**:
1. **Official MCP SDK (Python)** (SELECTED)
2. Custom tool functions without MCP
3. OpenAI function calling directly

**Decision**: Use Official MCP SDK (Python implementation) for tool definitions and execution

**Rationale**:
- ✅ Model Context Protocol (MCP) is emerging standard for AI tool interfaces
- ✅ Official SDK provides schema validation, error handling, and tool registration
- ✅ Stateless tool design enforces database persistence (aligns with Constitution Principle XIII)
- ✅ Clean separation between AI logic (agent) and task operations (tools)
- ✅ Tools are independently testable with mock database
- ✅ Future-proof: MCP gaining adoption across AI ecosystem
- ✅ Type-safe with Pydantic schemas for inputs and outputs

**Alternatives Considered**:
- **Custom tool functions without MCP**:
  - Pros: No external dependency, full control
  - Cons: No standardization, harder to test, no schema validation, reinventing the wheel
  - Rejected: MCP provides proven patterns for tool interfaces

- **OpenAI function calling directly**:
  - Pros: Native OpenAI integration
  - Cons: Tightly coupled to OpenAI API, less portable, no MCP benefits, no tool server abstraction
  - Rejected: MCP provides better separation of concerns

**Implementation Approach**:
- Install `mcp` via UV in backend/ (`uv add mcp`)
- Create `backend/app/mcp/server.py` to initialize MCP server
- Implement 6 tools in `backend/app/mcp/tools/` directory:
  - `add_task.py`: Create new task
  - `list_tasks.py`: Retrieve tasks with filtering and sorting
  - `search_tasks.py`: Search tasks by keyword
  - `complete_task.py`: Mark task complete (handle recurring logic)
  - `delete_task.py`: Remove task
  - `update_task.py`: Modify task fields
- Each tool is a Python async function with Pydantic input/output schemas
- Tools registered with MCP server using `@server.tool()` decorator
- MCP server runs within FastAPI backend (not separate process in Phase 3)

**MCP Tool Structure**:
```python
from mcp import Tool, MCPServer
from pydantic import BaseModel

class AddTaskInput(BaseModel):
    user_id: str
    title: str
    description: str | None = None
    priority: str | None = None
    tags: str | None = None
    due_date: str | None = None  # ISO format
    due_time: str | None = None  # HH:MM format
    recurrence: str | None = None  # "daily" | "weekly" | "monthly"
    recurrence_day: int | None = None

class AddTaskOutput(BaseModel):
    task_id: int
    status: str  # "created" or "error"
    title: str
    message: str | None = None

server = MCPServer()

@server.tool(
    name="add_task",
    description="Create a new task for the user",
    input_schema=AddTaskInput.schema(),
    output_schema=AddTaskOutput.schema()
)
async def add_task(input: AddTaskInput) -> AddTaskOutput:
    # Validate user_id, create task in database, return result
    pass
```

**Documentation**: https://github.com/modelcontextprotocol/python-sdk

**Risk Assessment**: Low risk - official SDK, well-documented, growing adoption

---

### 4. Stateless Chat Endpoint Architecture

**Research Question**: How should we design the chat endpoint to ensure scalability and resilience?

**Options Evaluated**:
1. **Stateless POST endpoint with database-persisted state** (SELECTED)
2. Stateful WebSocket connections with in-memory state
3. Stateful HTTP with in-memory cache
4. Stateful HTTP with Redis session store

**Decision**: Implement stateless POST /api/{user_id}/chat endpoint with database-persisted conversation state

**Rationale**:
- ✅ Horizontal scalability: any server instance can handle any request
- ✅ Resilience: server restarts don't lose conversation history
- ✅ Simplicity: no session management, no in-memory caches, no sticky sessions
- ✅ Database as single source of truth for all state
- ✅ Aligns with Constitution Principle XIII (Stateless Architecture)
- ✅ Cost-effective: no need for Redis or session management infrastructure
- ✅ Easier deployment: no special routing or session affinity required
- ✅ Testable: each request is independent, easy to write integration tests

**Alternatives Considered**:
- **Stateful WebSocket connections**:
  - Pros: Real-time bidirectional communication, lower latency
  - Cons: Requires sticky sessions, complex deployment, doesn't scale horizontally, connection management overhead
  - Rejected: Adds unnecessary complexity for Phase 3 requirements

- **In-memory conversation cache**:
  - Pros: Fast access to conversation history
  - Cons: Loses state on restart, not scalable, violates Phase 3 constitution, requires cache invalidation logic
  - Rejected: Violates Constitution Principle XIII (stateless architecture)

- **Redis session store**:
  - Pros: Distributed state storage, faster than database
  - Cons: Adds infrastructure complexity, another service to manage, not needed for 1,000 concurrent users
  - Rejected: Premature optimization, database performance sufficient for Phase 3 scope

**Implementation Approach**:

**Request Cycle** (10 steps):
1. Receive POST request with optional `conversation_id` and required `message`
2. Validate JWT token, extract `user_id`
3. If `conversation_id` provided:
   - Fetch conversation from database
   - Verify `conversation.user_id == user_id` (403 if mismatch)
   - Fetch last 50 messages from database
4. If no `conversation_id`:
   - Create new conversation record in database
   - Empty message history
5. Store user message in `messages` table
6. Build message array: `[{role: "user", content: "..."}, {role: "assistant", content: "..."}, ...]`
7. Pass message array to OpenAI Agents SDK with agent and MCP tools
8. Agent processes message, calls appropriate MCP tools, generates response
9. Store assistant response in `messages` table
10. Return response to client with `conversation_id`
11. Server forgets everything (ready for next request)

**Request Cycle Performance**:
- Database fetch (conversation + messages): ~100ms
- OpenAI Agents SDK processing: ~1-2 seconds
- MCP tool execution: ~50-200ms per tool (1-3 tools per request)
- Database write (2 new messages): ~50ms
- **Total: ~1.5-2.5 seconds** (well under 3 second target)

**Conversation History Management**:
- Limit to last 50 messages to prevent token overflow (GPT-4 has 8k-128k token limit)
- Older messages remain in database but not sent to agent
- User can still view full history in UI (separate read-only query)
- `updated_at` timestamp on conversation updated on each new message

**Error Handling**:
- Database connection failures: Return 503 Service Unavailable
- OpenAI API failures: Return 503 with retry suggestion
- MCP tool errors: Agent handles gracefully with conversational response
- JWT token invalid/expired: Return 401 Unauthorized
- User accessing wrong conversation: Return 403 Forbidden

**Risk Assessment**: Low risk - proven architecture pattern, aligns with constitution, simple to implement

---

### 5. Database Schema for Conversations and Messages

**Research Question**: How should we store conversation state in the database?

**Options Evaluated**:
1. **Two tables: conversations + messages** (SELECTED)
2. Single table with JSON column for messages
3. NoSQL document store (MongoDB)

**Decision**: Add two new tables (conversations, messages) to existing Neon PostgreSQL database

**Rationale**:
- ✅ Leverage existing Neon infrastructure from Phase 2
- ✅ SQLModel automatic table creation (no manual migrations needed in Phase 3)
- ✅ Normalized schema: conversations → messages (one-to-many)
- ✅ Efficient queries with indexes on user_id, conversation_id, created_at
- ✅ Preserves existing Task table from Phase 2 (all fields intact)
- ✅ Relational integrity with foreign keys
- ✅ Easy to query conversation history with single JOIN-free query

**Alternatives Considered**:
- **Single table with JSON column for messages**:
  - Pros: Single table, fewer joins
  - Cons: Can't index messages, harder to query, harder to paginate, violates normalization
  - Rejected: Poor query performance, can't filter/sort messages efficiently

- **NoSQL document store (MongoDB)**:
  - Pros: Flexible schema, good for nested data
  - Cons: Adds new database technology, data duplication with tasks in PostgreSQL, migration complexity
  - Rejected: Unnecessary complexity, PostgreSQL handles this use case well

**Schema Design**:

**conversations table**:
- `id` (int, primary key, auto-increment)
- `user_id` (string, foreign key to users.id, indexed)
- `created_at` (timestamp, indexed)
- `updated_at` (timestamp)

**messages table**:
- `id` (int, primary key, auto-increment)
- `conversation_id` (int, foreign key to conversations.id, indexed)
- `user_id` (string, foreign key to users.id, indexed for data isolation)
- `role` (enum: "user" | "assistant", indexed)
- `content` (text, max 5000 characters)
- `created_at` (timestamp, indexed for ordering)

**Indexes** (critical for performance):
- `conversations.user_id` (for listing user's conversations)
- `messages.conversation_id` (for fetching conversation history - most common query)
- `messages.user_id` (for data isolation checks)
- `messages.created_at` (for ordering messages chronologically)

**Query Patterns**:
```sql
-- Fetch conversation history (most common query - executed on every chat request)
SELECT id, role, content, created_at
FROM messages
WHERE conversation_id = $1
ORDER BY created_at ASC
LIMIT 50;
-- Expected latency: ~100ms with index

-- Create new conversation
INSERT INTO conversations (user_id, created_at, updated_at)
VALUES ($1, NOW(), NOW())
RETURNING id;
-- Expected latency: ~50ms

-- Store new message
INSERT INTO messages (conversation_id, user_id, role, content, created_at)
VALUES ($1, $2, $3, $4, NOW());
-- Expected latency: ~25ms
```

**Data Retention**: No automatic cleanup in Phase 3. Future phases may add:
- Conversation archiving after 90 days of inactivity
- Message cleanup for conversations with >500 messages
- User-initiated conversation deletion
- Export conversation history as JSON/PDF

**Risk Assessment**: Low risk - straightforward relational schema, proven patterns, SQLModel handles automatically

---

### 6. Natural Language Understanding Strategy

**Research Question**: How should we implement intent recognition and entity extraction?

**Options Evaluated**:
1. **OpenAI GPT-4 with system prompt engineering** (SELECTED)
2. Fine-tuned GPT model for task intents
3. Custom NER with spaCy or similar
4. Hybrid: LLM + regex fallbacks

**Decision**: Use OpenAI GPT-4 with carefully crafted system prompt for intent recognition and entity extraction

**Rationale**:
- ✅ GPT-4 has strong natural language understanding capabilities out of the box
- ✅ System prompt engineering cheaper and faster than fine-tuning
- ✅ Agent SDK handles tool calling logic automatically
- ✅ No need for custom NER (Named Entity Recognition) or intent classifiers
- ✅ Handles varied phrasings and colloquial language
- ✅ Can ask clarifying questions for ambiguous input
- ✅ Aligns with Constitution Principle XIV (Natural Language Understanding)

**Alternatives Considered**:
- **Fine-tuned GPT model**:
  - Pros: Potentially higher accuracy for specific intents
  - Cons: Requires training data, expensive, maintenance overhead, longer development time
  - Rejected: GPT-4 baseline accuracy sufficient (90% target), prompt engineering faster

- **Custom NER with spaCy**:
  - Pros: Faster inference, no API costs
  - Cons: Not robust for varied natural language, requires training data, limited to predefined patterns
  - Rejected: GPT-4 handles variations better

- **Hybrid: LLM + regex fallbacks**:
  - Pros: Fallback for common patterns
  - Cons: Adds complexity, regex brittle, harder to maintain
  - Rejected: GPT-4 handles edge cases well enough

**System Prompt Design**:

**Structure**:
1. **Agent Personality**: Define helpful, concise, friendly tone
2. **Tool Descriptions**: List all 6 MCP tools with descriptions and when to use them
3. **Entity Extraction Guidelines**: How to extract priorities, tags, dates, times, recurrence patterns
4. **Example Conversations**: Show correct tool usage for each feature
5. **Error Handling Behavior**: Ask clarification, recover gracefully
6. **Confirmation Patterns**: Always confirm actions ("I've added...", "Task completed!")

**Entity Extraction Patterns**:
- **Priorities**:
  - "high priority", "urgent", "important", "critical" → priority="high"
  - "low priority", "not urgent", "sometime" → priority="low"
  - Default: priority="medium"

- **Tags**:
  - "work task", "for work" → tags="work"
  - "personal reminder", "for me" → tags="personal"
  - "health appointment" → tags="health"
  - Multiple: "work and urgent" → tags="work,urgent"

- **Dates**:
  - Relative: "tomorrow", "next Monday", "Friday", "next week", "in 3 days"
  - Absolute: "December 25", "12/20/2025", "Dec 25th"
  - Parse using date logic (handle current year, week calculation)

- **Times**:
  - "5 PM", "at 2pm", "14:00", "noon", "midnight"
  - Convert to 24-hour format (17:00, 14:00, etc.)

- **Recurrence**:
  - "every day", "daily" → recurrence="daily"
  - "weekly", "every week", "every Monday" → recurrence="weekly", recurrence_day=1
  - "monthly", "every month", "on the 1st" → recurrence="monthly", recurrence_day=1

**Example System Prompt Excerpt**:
```
You are a helpful todo assistant. You help users manage their task list through natural language commands.

You have access to these tools:
- add_task: Create a new task (supports title, description, priority, tags, due dates, recurrence)
- list_tasks: Show tasks with filtering and sorting (status, priority, tags, sort options)
- search_tasks: Search tasks by keyword
- complete_task: Mark a task as done (automatically handles recurring tasks)
- delete_task: Remove a task
- update_task: Modify any task field

When users mention adding, creating, or remembering something, use add_task.
  - Extract priority from phrases like "high priority", "urgent", "important" (map to high/medium/low)
  - Extract tags from phrases like "work task", "personal reminder", "health"
  - Extract due dates from phrases like "by Friday", "tomorrow at 5pm", "next Monday"
  - Extract recurrence from phrases like "every day", "weekly", "every Monday"

When users ask to see, show, or list tasks, use list_tasks.
  - Apply filters when users mention status (pending/completed), priority, or tags
  - Sort when users mention "by due date", "by priority", "alphabetically"

When users want to search or find tasks, use search_tasks with the keyword.

When users say done, complete, or finished, use complete_task.
  - If the task is recurring, automatically create the next occurrence

When users say delete, remove, or cancel, use delete_task.

When users say change, update, or rename, use update_task.
  - Update only the fields mentioned by the user

Always confirm actions with a friendly response showing what was changed.
If you can't find a task, ask the user for the task ID or search keyword.
If a request is ambiguous, ask clarifying questions.
Be concise but helpful.
```

**Testing Strategy**:
- Create test suite with 60 natural language examples from spec
- Verify correct tool calls for each example
- Verify correct entity extraction (priorities, tags, dates, recurrence)
- Verify error recovery for ambiguous inputs
- Mock OpenAI API responses for deterministic testing

**Risk Assessment**: Medium risk - depends on prompt quality, requires iterative refinement based on user testing

---

### 7. JWT Authentication Flow

**Research Question**: How should we secure the chat endpoint and MCP tools?

**Decision**: Maintain Better Auth JWT authentication from Phase 2, extend to chat endpoint

**Rationale**:
- ✅ No changes needed to auth system (already working in Phase 2)
- ✅ JWT tokens already include user_id claim
- ✅ FastAPI middleware already validates tokens
- ✅ Simply add JWT middleware to new chat endpoint
- ✅ All MCP tools receive authenticated user_id
- ✅ Aligns with Constitution Principle IX (Multi-User Data Isolation)

**Authentication Flow**:
1. User logs in via Better Auth (frontend)
2. Better Auth issues JWT token with user_id claim
3. Frontend stores token in httpOnly cookie or localStorage
4. Frontend sends token in `Authorization: Bearer <token>` header with every chat request
5. Backend middleware validates JWT signature using BETTER_AUTH_SECRET
6. Middleware extracts user_id from token claims
7. Backend ensures path parameter {user_id} matches token user_id
8. If valid, request proceeds to chat handler
9. If invalid, return 401 Unauthorized

**Security Considerations**:
- BETTER_AUTH_SECRET must be identical in frontend and backend (shared secret)
- Tokens expire after 7 days (configurable in Better Auth settings)
- HTTPS enforced in production (Vercel/hosting platform)
- No token refresh needed for Phase 3 (users re-authenticate after expiry)
- JWT signature verification on every request (no trust by default)

**MCP Tool Security**:
- All MCP tools receive user_id parameter from JWT token
- Tools filter all database queries by user_id
- No tool can access other users' data (enforced at database query level)
- Agent cannot override user isolation (enforced at tool level, not agent level)
- Conversation ownership checked: conversation.user_id must match JWT user_id

**Risk Assessment**: Low risk - existing working auth system, proven JWT patterns

---

### 8. Testing Strategy

**Research Question**: How should we ensure quality and correctness for AI chatbot features?

**Decision**: Three-tier testing approach: MCP tool unit tests, conversation flow integration tests, end-to-end ChatKit tests

**Rationale**:
- ✅ MCP tools are independently testable (pure functions with database mocks)
- ✅ Conversation flows validate intent recognition and tool calling
- ✅ End-to-end tests validate full stack (ChatKit → Chat Endpoint → Agent → MCP → Database)
- ✅ Aligns with Constitution Principle II (Test-First TDD)
- ✅ Target: >90% test coverage

**Test Levels**:

**1. MCP Tool Unit Tests** (`tests/unit/test_mcp_tools.py`):
- Test each tool with mock database (no real DB calls)
- Test input validation (Pydantic schemas)
- Test success cases (task created, task listed, task completed, etc.)
- Test error cases (task not found, access denied, invalid input)
- Test recurring task logic (complete_task creates next occurrence)
- Coverage target: 100% for MCP tools (they're pure functions, easy to achieve)

**2. Conversation Flow Integration Tests** (`tests/integration/test_conversation_flows.py`):
- Test natural language examples from spec (all 60 acceptance scenarios)
- Mock OpenAI API responses (no real API calls in tests, use `responses` library)
- Verify correct tool calls for each intent
- Verify correct entity extraction (priorities, tags, dates)
- Verify error recovery (ambiguous input, non-existent tasks)
- Coverage target: All 60 acceptance scenarios from spec

**3. Chat Endpoint Tests** (`tests/integration/test_chat_endpoint.py`):
- Test stateless architecture (conversation persistence across requests)
- Test JWT authentication (valid/invalid tokens)
- Test user data isolation (users can't access others' conversations)
- Test error handling (database failures, API timeouts)
- Test conversation history loading (last 50 messages)
- Coverage target: >90% for chat endpoint

**4. Frontend ChatKit Tests** (`frontend/__tests__/`):
- Test ChatInterface component rendering
- Test message sending (API client calls)
- Test conversation history display
- Test error handling (network failures, 401/500 errors)
- Test JWT token injection in API calls
- Coverage target: >80% for chat components

**Test Tools**:
- Backend: pytest, pytest-cov, pytest-asyncio, httpx (async test client)
- Frontend: Jest, React Testing Library, MSW (Mock Service Worker)
- Mocking: unittest.mock for database, responses library for OpenAI API

**Risk Assessment**: Low risk - comprehensive testing strategy ensures quality

---

### 9. Performance Optimization

**Research Question**: How do we meet the <3 second response time target?

**Decision**: Optimize database queries, implement connection pooling, limit conversation history

**Performance Targets**:
- Chat endpoint response time: <3 seconds for 95% of requests
- Database queries: <500ms each
- MCP tool execution: <200ms per tool
- Support 1,000 concurrent users

**Optimization Strategies**:

**1. Database Query Optimization**:
- Index on `messages.conversation_id` for fast history fetching
- Index on `messages.created_at` for ordering
- Limit conversation history to 50 messages (reduces query time and token usage)
- Use `SELECT` with specific columns (not `SELECT *`)
- Single query to fetch conversation history (no N+1 queries)

**2. Connection Pooling**:
- SQLModel/SQLAlchemy connection pool (configure 5-20 connections based on load)
- Recycle connections every 3600 seconds (avoid stale connections)
- Monitor pool exhaustion and adjust size

**3. OpenAI API Optimization**:
- Use `gpt-4-turbo` for faster responses (if accuracy acceptable over `gpt-4`)
- Limit conversation history to prevent token overflow
- Implement timeout (30 seconds) for OpenAI API calls
- Retry on transient failures (429, 503 status codes)

**4. Async All the Way**:
- FastAPI with async route handlers (`async def`)
- SQLModel with async session
- OpenAI Agents SDK with async calls
- MCP tools with async functions
- No blocking operations in request cycle

**5. Monitoring**:
- Log response times for each request
- Log OpenAI API latency
- Log database query times
- Identify bottlenecks during testing
- Use FastAPI middleware for request timing

**Expected Performance Breakdown**:
- Database fetch (50 messages): ~100ms
- OpenAI Agents SDK: ~1-2 seconds (largest component, depends on model and token count)
- MCP tool execution: ~50-200ms per tool (1-3 tools per request)
- Database write (2 messages): ~50ms
- **Total: ~1.5-2.5 seconds** (well under 3 second target)

**Risk Assessment**: Low risk - performance targets achievable with optimizations

---

### 10. Error Handling and Recovery

**Research Question**: How should we handle errors gracefully in a conversational interface?

**Decision**: Three-layer error handling: MCP tool errors, agent errors, chat endpoint errors

**Error Handling Layers**:

**1. MCP Tool Errors**:
- Tool validates inputs with Pydantic schemas (automatic validation)
- Tool returns structured error responses: `{status: "error", message: "Task not found"}`
- Tool never throws unhandled exceptions (wrap in try-except)
- Tool logs errors for debugging
- Agent receives error response and generates conversational error message

**2. Agent Errors**:
- Agent handles MCP tool errors gracefully
- Agent generates conversational responses: "I couldn't find task 999. Would you like to see your task list?"
- Agent asks clarifying questions for ambiguous input: "Which task did you mean?"
- Agent continues conversation after errors (no crashes, no hard stops)
- Agent handles OpenAI API errors (rate limits, timeouts): "I'm experiencing high demand. Please try again in a moment."

**3. Chat Endpoint Errors**:
- Endpoint validates JWT token (401 if invalid/expired)
- Endpoint validates user ownership (403 if accessing others' conversations)
- Endpoint handles database errors (503 Service Unavailable)
- Endpoint handles OpenAI API errors (503 with retry suggestion)
- Endpoint returns structured error responses with appropriate HTTP status codes

**Error Response Format**:
```json
{
  "error": "Service unavailable",
  "message": "I'm having trouble connecting right now. Please try again in a moment.",
  "status_code": 503
}
```

**User Experience**:
- All errors result in user-friendly conversational messages (no stack traces)
- No technical error messages exposed to users
- Agent suggests next actions ("Would you like to see your task list?")
- Frontend displays errors in chat interface (not alert popups)
- Retry button for transient failures

**Risk Assessment**: Low risk - comprehensive error handling ensures good UX

---

## Research Summary

**Technology Stack Finalized**:
- ✅ Frontend: OpenAI ChatKit (React/Next.js integration)
- ✅ AI Framework: OpenAI Agents SDK (intent recognition, tool calling)
- ✅ MCP Server: Official MCP SDK Python (6 stateless tools)
- ✅ Chat Endpoint: Stateless POST /api/{user_id}/chat with database persistence
- ✅ Database: Neon PostgreSQL (add conversations, messages tables)
- ✅ Auth: Better Auth JWT (existing, extend to chat endpoint)

**Key Architectural Decisions**:
- ✅ Stateless architecture (Constitution Principle XIII)
- ✅ Database-persisted conversation state
- ✅ Conversation history limited to 50 messages
- ✅ MCP tools independently testable
- ✅ Three-tier testing strategy (tool → flow → e2e)
- ✅ Performance target: <3 seconds for 95% of requests

**Risk Mitigation**:
- OpenAI API rate limits: Implement retry logic, handle 429 errors gracefully
- Token limits: Limit conversation history to 50 messages
- Database scaling: Neon autoscaling handles increased load
- Agent accuracy: Test with 60 acceptance scenarios, refine system prompt iteratively
- Infrastructure simplicity: No Redis, no WebSockets, no complex deployment

**All Decisions Validated Against Constitution v3.0.0** ✅

---

**Status**: ✅ Research Complete
**Date**: 2025-12-17
**Next**: Implementation via `/sp.tasks` → `/sp.implement`
