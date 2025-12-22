# Implementation Plan: AI-Powered Todo Chatbot (Phase 3)

**Branch**: `003-phase3-ai-chatbot` | **Date**: 2025-12-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/003-phase3-ai-chatbot/spec.md`

## Summary

Transform Phase 2 full-stack web application into an AI-powered conversational interface where users manage all 10 task features (Basic, Intermediate, Advanced) through natural language commands. Implement stateless chat endpoint using OpenAI ChatKit (frontend), OpenAI Agents SDK (AI logic), and Official MCP SDK (tools) with database-persisted conversation state.

**Technical Approach:**
- **Frontend**: Replace traditional UI forms with OpenAI ChatKit conversational interface
- **AI Agent**: OpenAI Agents SDK for intent recognition and natural language understanding
- **MCP Server**: Official MCP SDK (Python) with 6 stateless tools supporting all 10 features
- **Chat Endpoint**: Stateless POST /api/{user_id}/chat endpoint with conversation persistence
- **Database**: Add Conversation and Message tables to existing Neon PostgreSQL
- **Auth**: Maintain Better Auth JWT authentication from Phase 2

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**:
- Backend: FastAPI, OpenAI Agents SDK, Official MCP SDK (Python), SQLModel, Neon PostgreSQL
- Frontend: Next.js 16+, OpenAI ChatKit, TypeScript, Tailwind CSS

**Storage**: Neon Serverless PostgreSQL (existing) + new tables (conversations, messages)
**Testing**: pytest (backend + MCP tools + conversation flows), Jest/React Testing Library (frontend)
**Target Platform**: Web application (ChatKit UI), FastAPI backend, Neon cloud database
**Project Type**: Web (monorepo: frontend/ + backend/)
**Performance Goals**:
- Chat endpoint response time: <3 seconds for 95% of requests
- Intent recognition accuracy: 90% correct identification
- Database queries: <500ms each
- Support 1,000 concurrent users
- MCP tool execution: <200ms per tool

**Constraints**:
- Stateless architecture (no in-memory conversation state)
- Conversation history limited to 50 messages (token limits)
- All endpoints require JWT authentication
- User data isolation enforced at MCP tool level
- Test coverage >90% for backend, MCP tools, conversation flows

**Scale/Scope**:
- 6 MCP tools supporting 10 features
- 12 user stories with 60 acceptance scenarios
- 26 functional requirements
- 2 new database tables (conversations, messages)
- 1 new API endpoint (POST /api/{user_id}/chat)
- Natural language understanding for all task operations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Principle I - Spec-First Development**: Feature spec complete in `specs/003-phase3-ai-chatbot/spec.md` with all acceptance criteria, MCP tool schemas, and natural language examples

✅ **Principle II - Test-First (TDD)**: Planning includes MCP tool tests, conversation flow tests, and stateless architecture tests before implementation

✅ **Principle III - YAGNI (Phase 3 Scope)**: Implements ALL 10 features via natural language (Basic 1-5, Intermediate 6-8, Advanced 9-10). No Kubernetes, no Kafka (Phase IV/V)

✅ **Principle IV - Technology Stack**: Uses mandated stack (OpenAI ChatKit, Agents SDK, MCP SDK, FastAPI, Neon PostgreSQL, UV package manager)

✅ **Principle V - Clean Code & Modularity**: Monorepo structure with `backend/` (MCP server, agents, API) and `frontend/` (ChatKit integration)

✅ **Principle VI - Type Safety**: Python type hints with mypy strict mode, TypeScript strict mode, MCP tool schemas fully typed

✅ **Principle VII - Comprehensive Documentation**: Plan includes MCP tool docs, agent behavior docs, conversation examples, and architecture docs

✅ **Principle VIII - Error Handling**: MCP tool error schemas, conversational error recovery, graceful degradation for OpenAI API failures

✅ **Principle IX - Multi-User Data Isolation**: JWT authentication required, all MCP tools filter by user_id, conversation ownership enforced

✅ **Principle X - Database Schema Management**: SQLModel automatic table creation for Conversation and Message tables, schema documented

✅ **Principle XI - API Design**: RESTful conventions maintained, new chat endpoint follows REST principles (POST /api/{user_id}/chat)

✅ **Principle XII - AI Agent Development**: OpenAI Agents SDK integration, MCP server with 6 stateless tools, clear tool schemas, system prompt requirements documented

✅ **Principle XIII - Stateless Architecture**: Chat endpoint stateless, conversation state persisted to database, horizontally scalable, no in-memory state

✅ **Principle XIV - Natural Language Understanding**: Intent recognition patterns documented, entity extraction (task IDs, priorities, tags, dates, recurrence), system prompt examples provided

**Constitution Compliance**: ✅ **PASSED** - All 14 principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/003-phase3-ai-chatbot/
├── spec.md                    # Feature specification (COMPLETE)
├── checklists/
│   └── requirements.md        # Quality validation (PASSED)
├── plan.md                    # This file (IN PROGRESS)
├── research.md                # Phase 0 output (see below)
├── data-model.md              # Phase 1 output (see below)
├── quickstart.md              # Phase 1 output (see below)
├── contracts/                 # Phase 1 output (see below)
│   ├── mcp-tools.md           # MCP tool specifications
│   ├── chat-endpoint.md       # Chat API contract
│   └── agent-behavior.md      # Agent system prompt and behavior
└── tasks.md                   # Phase 2 output (/sp.tasks command - NOT YET CREATED)
```

### Source Code (repository root)

```text
evolved-todo/
├── .claude/                   # Agent configurations
│   ├── agents/                # Specialized agents
│   ├── commands/              # Slash commands (including /sp.plan)
│   └── skills/                # Implementation skills
├── .specify/                  # Spec-Kit Plus templates and scripts
│   ├── memory/
│   │   └── constitution.md    # Phase 3 constitution (v3.0.0)
│   ├── templates/             # Plan, spec, tasks templates
│   └── scripts/               # PowerShell scripts for setup
├── specs/                     # Feature specifications
│   ├── 001-phase1-todo-app/   # Phase 1 CLI app specs
│   ├── 002-phase2-web-app/    # Phase 2 web app specs
│   └── 003-phase3-ai-chatbot/ # Phase 3 chatbot specs (THIS FEATURE)
├── history/                   # ADRs and PHRs
│   ├── adr/                   # Architecture Decision Records
│   └── prompts/               # Prompt History Records
│       ├── constitution/      # Constitution updates
│       ├── 003-phase3-ai-chatbot/  # Feature PHRs
│       └── general/           # General prompts
├── backend/                   # Python FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI entry point
│   │   ├── models.py          # SQLModel models (Task, Conversation, Message)
│   │   ├── db.py              # Database connection and session
│   │   ├── auth.py            # JWT authentication middleware
│   │   ├── routes/
│   │   │   ├── tasks.py       # Task CRUD endpoints (Phase 2, kept for compatibility)
│   │   │   └── chat.py        # Chat endpoint (NEW - Phase 3)
│   │   ├── services/
│   │   │   └── task_service.py  # Task business logic (Phase 2, reused by MCP tools)
│   │   ├── mcp/               # MCP server and tools (NEW - Phase 3)
│   │   │   ├── server.py      # MCP server setup and registration
│   │   │   └── tools/         # MCP tool implementations
│   │   │       ├── add_task.py
│   │   │       ├── list_tasks.py
│   │   │       ├── search_tasks.py
│   │   │       ├── complete_task.py
│   │   │       ├── delete_task.py
│   │   │       └── update_task.py
│   │   └── agents/            # OpenAI Agents SDK config (NEW - Phase 3)
│   │       ├── todo_agent.py  # Main todo agent initialization
│   │       └── prompts.py     # System prompts and instructions
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── test_models.py     # Model validation tests
│   │   │   └── test_mcp_tools.py  # MCP tool unit tests (NEW)
│   │   ├── integration/
│   │   │   ├── test_chat_endpoint.py  # Chat endpoint tests (NEW)
│   │   │   └── test_conversation_flows.py  # End-to-end conversation tests (NEW)
│   │   └── conftest.py        # Pytest fixtures
│   ├── pyproject.toml         # UV dependencies
│   └── uv.lock                # UV lock file
├── frontend/                  # Next.js 16+ frontend
│   ├── app/                   # App Router pages
│   │   ├── (auth)/            # Auth routes (login, signup)
│   │   ├── (app)/             # Authenticated app routes
│   │   │   └── chat/          # Chat interface (NEW - Phase 3)
│   │   │       └── page.tsx   # ChatKit integration
│   │   └── layout.tsx         # Root layout with Better Auth
│   ├── components/
│   │   └── chat/              # Chat-related components (NEW)
│   │       ├── ChatInterface.tsx  # Main ChatKit wrapper
│   │       └── MessageList.tsx    # Conversation history display
│   ├── lib/
│   │   ├── api-client.ts      # API client for chat endpoint
│   │   └── auth.ts            # Better Auth client config
│   ├── types/
│   │   └── chat.ts            # TypeScript types for chat messages
│   ├── __tests__/             # Frontend tests
│   ├── package.json
│   └── tsconfig.json
├── AGENTS.md                  # Agent instructions for Spec-Driven Development
├── CLAUDE.md                  # Claude Code configuration
├── README.md                  # Project overview and setup
└── pyproject.toml             # Root UV dependencies (optional)
```

**Structure Decision**: Web application monorepo (frontend/ + backend/). Backend adds MCP server (backend/app/mcp/) and agents directory (backend/app/agents/) while maintaining existing API routes. Frontend replaces traditional UI with ChatKit conversational interface in new /chat route. All Phase 2 infrastructure (database, auth, task models) preserved and extended.

## Complexity Tracking

**No Violations** - All architecture decisions align with Phase 3 constitution requirements. No complexity exceptions needed.

---

# Phase 0: Research & Technology Decisions

## Research Findings

### 1. OpenAI ChatKit Integration

**Decision**: Use OpenAI ChatKit as the primary conversational UI component

**Rationale**:
- Pre-built chat interface with typing indicators, message formatting, and conversation history display
- Officially maintained by OpenAI, ensuring compatibility with Agents SDK
- Supports React/Next.js integration via npm package
- Handles UI concerns (scrolling, timestamps, user/assistant message styling) out of the box
- Reduces frontend complexity, allowing focus on AI logic

**Alternatives Considered**:
- **Custom React Chat UI**: More control but higher development overhead. ChatKit provides proven UX patterns.
- **Third-party chat libraries (stream-chat-react, react-chat-ui)**: Not optimized for AI agents, lack OpenAI integration.

**Implementation Approach**:
- Install `@openai/chatkit` npm package in frontend/
- Create ChatInterface component wrapping ChatKit with Better Auth token injection
- Configure ChatKit to send messages to backend chat endpoint
- Display conversation history from database on component mount

**Documentation**: https://platform.openai.com/docs/guides/chatkit

---

### 2. OpenAI Agents SDK for Intent Recognition

**Decision**: Use OpenAI Agents SDK for AI logic and natural language understanding

**Rationale**:
- Purpose-built for agentic workflows (intent recognition, tool calling, multi-turn conversations)
- Native support for MCP tools via tool definitions
- Handles conversation context management automatically
- Provides retry logic and error handling for OpenAI API calls
- Simplifies system prompt management and agent configuration

**Alternatives Considered**:
- **Direct OpenAI API calls**: Lower-level control but requires manual tool calling logic, conversation tracking, and error handling.
- **LangChain**: More abstraction layers, heavier dependency, overkill for simple tool calling.
- **Custom NLU with regex/NER**: Not robust enough for varied natural language inputs.

**Implementation Approach**:
- Install `openai-agents-sdk` via UV in backend/
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
    model="gpt-4",
    instructions=SYSTEM_PROMPT,
    tools=[add_task_tool, list_tasks_tool, search_tasks_tool,
           complete_task_tool, delete_task_tool, update_task_tool]
)
```

**Documentation**: https://github.com/openai/openai-agents-sdk

---

### 3. Official MCP SDK (Python) for Stateless Tools

**Decision**: Use Official MCP SDK (Python implementation) for tool definitions and execution

**Rationale**:
- Model Context Protocol (MCP) is emerging standard for AI tool interfaces
- Official SDK provides schema validation, error handling, and tool registration
- Stateless tool design enforces database persistence (aligns with Constitution Principle XIII)
- Clean separation between AI logic (agent) and task operations (tools)
- Tools are independently testable with mock database

**Alternatives Considered**:
- **Custom tool functions without MCP**: No standardization, harder to test, no schema validation.
- **OpenAI function calling directly**: Tightly coupled to OpenAI API, less portable, no MCP benefits.

**Implementation Approach**:
- Install `mcp` via UV in backend/
- Create `backend/app/mcp/server.py` to initialize MCP server
- Implement 6 tools in `backend/app/mcp/tools/` directory
- Each tool is a Python function with Pydantic input/output schemas
- Tools registered with MCP server using `@server.tool()` decorator
- MCP server runs within FastAPI backend (not separate process)

**MCP Tool Structure**:
```python
from mcp import Tool, MCPServer
from pydantic import BaseModel

class AddTaskInput(BaseModel):
    user_id: str
    title: str
    description: str | None = None
    priority: str | None = None
    # ... other optional fields

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
    # Implementation: validate user_id, create task in database, return result
    pass
```

**Documentation**: https://github.com/modelcontextprotocol/python-sdk

---

### 4. Stateless Chat Endpoint Architecture

**Decision**: Implement stateless POST /api/{user_id}/chat endpoint with database-persisted conversation state

**Rationale**:
- Horizontal scalability: any server instance can handle any request
- Resilience: server restarts don't lose conversation history
- Simplicity: no session management, no in-memory caches
- Database as single source of truth for all state
- Aligns with Constitution Principle XIII (Stateless Architecture)

**Alternatives Considered**:
- **Stateful WebSocket connections**: Requires sticky sessions, complex deployment, doesn't scale horizontally.
- **In-memory conversation cache**: Loses state on restart, not scalable, violates Phase 3 constitution.
- **Redis session store**: Adds complexity, not needed for Phase 3 scope (only 1,000 concurrent users).

**Implementation Approach**:
1. Receive POST request with optional `conversation_id` and required `message`
2. Fetch conversation history from database if `conversation_id` provided, else create new conversation
3. Store user message in `messages` table
4. Build message array from database: `[{role: "user", content: "..."}, {role: "assistant", content: "..."}, ...]`
5. Pass message array to OpenAI Agents SDK with agent and MCP tools
6. Agent processes message, calls appropriate MCP tools, generates response
7. Store assistant response in `messages` table
8. Return response to client with `conversation_id`
9. Server forgets everything (ready for next request)

**Request Cycle Performance**:
- Database fetch (conversation history): ~100ms
- OpenAI Agents SDK processing: ~1-2 seconds
- MCP tool execution: ~50-200ms per tool
- Database write (new messages): ~50ms
- Total: <3 seconds for 95% of requests (meets performance goal)

**Conversation History Management**:
- Limit to last 50 messages to prevent token overflow
- Older messages remain in database but not sent to agent
- User can still view full history in UI (separate query)

**Error Handling**:
- Database connection failures: Return 503 Service Unavailable
- OpenAI API failures: Return 503 with retry suggestion
- MCP tool errors: Agent handles gracefully with conversational response
- JWT token invalid: Return 401 Unauthorized

---

### 5. Database Schema for Conversations and Messages

**Decision**: Add two new tables (conversations, messages) to existing Neon PostgreSQL database

**Rationale**:
- Leverage existing Neon infrastructure from Phase 2
- SQLModel automatic table creation (no manual migrations needed in Phase 3)
- Normalized schema: conversations → messages (one-to-many)
- Efficient queries with indexes on user_id, conversation_id, created_at
- Preserves existing Task table from Phase 2 (all fields intact)

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

**Indexes**:
- `conversations.user_id` (for listing user's conversations)
- `messages.conversation_id` (for fetching conversation history)
- `messages.user_id` (for data isolation checks)
- `messages.created_at` (for ordering messages chronologically)

**Query Patterns**:
```sql
-- Fetch conversation history (most common query)
SELECT id, role, content, created_at
FROM messages
WHERE conversation_id = $1
ORDER BY created_at ASC
LIMIT 50;

-- Create new conversation
INSERT INTO conversations (user_id, created_at, updated_at)
VALUES ($1, NOW(), NOW())
RETURNING id;

-- Store new message
INSERT INTO messages (conversation_id, user_id, role, content, created_at)
VALUES ($1, $2, $3, $4, NOW());
```

**Data Retention**: No automatic cleanup in Phase 3. Future phases may add conversation archiving or deletion policies.

---

### 6. Natural Language Understanding Strategy

**Decision**: Use OpenAI GPT-4 with carefully crafted system prompt for intent recognition and entity extraction

**Rationale**:
- GPT-4 has strong natural language understanding capabilities out of the box
- System prompt engineering cheaper and faster than custom NLU models
- Agent SDK handles tool calling logic automatically
- No need for custom NER (Named Entity Recognition) or intent classifiers

**System Prompt Design**:
- Define agent personality (helpful, concise, friendly)
- List all 6 MCP tools with descriptions and when to use them
- Provide entity extraction guidelines (priorities, tags, dates, recurrence)
- Include example conversations for each feature
- Define error handling behavior (ask clarification, recover gracefully)
- Emphasize confirmation patterns ("I've added...", "Task completed!")

**Entity Extraction Patterns**:
- **Priorities**: "high priority", "urgent", "important" → priority="high"
- **Tags**: "work task", "personal reminder" → tags="work" or "personal"
- **Dates**: "tomorrow", "next Monday", "Dec 25" → due_date parsing
- **Times**: "5 PM", "at 2pm", "14:00" → due_time parsing
- **Recurrence**: "every day", "weekly", "every Monday" → recurrence pattern + day

**Example System Prompt Excerpt**:
```
You are a helpful todo assistant. When users mention adding or creating tasks,
use the add_task tool. Extract priority from phrases like "high priority" or "urgent"
(map to high/medium/low). Extract tags from phrases like "work task" or "personal reminder".
Extract due dates from relative ("tomorrow") or absolute ("Dec 25") date phrases.
Extract recurrence from "every day", "weekly", "every Monday", etc.

Always confirm actions: "I've added 'Buy groceries' to your task list. Task ID is 5."
If you can't find a task, ask for the task ID or more details.
```

**Testing Strategy**:
- Create test suite with 60 natural language examples from spec
- Verify correct tool calls for each example
- Verify correct entity extraction (priorities, tags, dates, recurrence)
- Verify error recovery for ambiguous inputs

---

### 7. JWT Authentication Flow

**Decision**: Maintain Better Auth JWT authentication from Phase 2, extend to chat endpoint

**Rationale**:
- No changes needed to auth system (already working in Phase 2)
- JWT tokens already include user_id claim
- FastAPI middleware already validates tokens
- Simply add JWT middleware to new chat endpoint

**Authentication Flow**:
1. User logs in via Better Auth (frontend)
2. Better Auth issues JWT token with user_id claim
3. Frontend stores token in localStorage or cookie
4. Frontend sends token in `Authorization: Bearer <token>` header with every chat request
5. Backend middleware validates JWT signature using BETTER_AUTH_SECRET
6. Middleware extracts user_id from token claims
7. Backend ensures path parameter {user_id} matches token user_id
8. If valid, request proceeds to chat handler
9. If invalid, return 401 Unauthorized

**Security Considerations**:
- BETTER_AUTH_SECRET must be identical in frontend and backend (shared secret)
- Tokens expire after 7 days (configurable)
- HTTPS enforced in production (Vercel/hosting platform)
- No token refresh needed for Phase 3 (users re-authenticate after expiry)

**MCP Tool Security**:
- All MCP tools receive user_id parameter from JWT token
- Tools filter all database queries by user_id
- No tool can access other users' data
- Agent cannot override user isolation (enforced at tool level)

---

### 8. Testing Strategy

**Decision**: Three-tier testing approach: MCP tool unit tests, conversation flow integration tests, end-to-end ChatKit tests

**Rationale**:
- MCP tools are independently testable (pure functions with database mocks)
- Conversation flows validate intent recognition and tool calling
- End-to-end tests validate full stack (ChatKit → Chat Endpoint → Agent → MCP → Database)

**Test Levels**:

**1. MCP Tool Unit Tests** (`tests/unit/test_mcp_tools.py`):
- Test each tool with mock database
- Test input validation (Pydantic schemas)
- Test success cases (task created, task listed, task completed, etc.)
- Test error cases (task not found, access denied, invalid input)
- Test recurring task logic (complete_task creates next occurrence)
- Coverage target: 100% for MCP tools

**2. Conversation Flow Integration Tests** (`tests/integration/test_conversation_flows.py`):
- Test natural language examples from spec
- Mock OpenAI API responses (no real API calls in tests)
- Verify correct tool calls for each intent
- Verify correct entity extraction (priorities, tags, dates)
- Verify error recovery (ambiguous input, non-existent tasks)
- Coverage target: All 60 acceptance scenarios from spec

**3. Chat Endpoint Tests** (`tests/integration/test_chat_endpoint.py`):
- Test stateless architecture (conversation persistence)
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
- Test JWT token injection
- Coverage target: >80% for chat components

**Test Tools**:
- Backend: pytest, pytest-cov, pytest-asyncio, httpx (async client)
- Frontend: Jest, React Testing Library, MSW (mock service worker)
- Mocking: unittest.mock for database, responses library for OpenAI API

---

### 9. Performance Optimization

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
- SQLModel/SQLAlchemy connection pool (default 5-10 connections)
- Configure pool size based on concurrent user load
- Recycle connections every 3600 seconds (avoid stale connections)

**3. OpenAI API Optimization**:
- Use `gpt-4-turbo` for faster responses (if accuracy acceptable)
- Limit conversation history to prevent token overflow
- Implement timeout (30 seconds) for OpenAI API calls
- Cache common responses (future optimization, not Phase 3)

**4. Async All the Way**:
- FastAPI with async route handlers
- SQLModel with async session
- OpenAI Agents SDK with async calls
- MCP tools with async functions
- No blocking operations in request cycle

**5. Monitoring**:
- Log response times for each request
- Log OpenAI API latency
- Log database query times
- Identify bottlenecks during testing

**Expected Performance**:
- Database fetch (50 messages): ~100ms
- OpenAI Agents SDK: ~1-2 seconds (largest component)
- MCP tool execution: ~50-200ms (1-3 tools per request)
- Database write (2 messages): ~50ms
- Total: ~1.5-2.5 seconds (well under 3 second target)

---

### 10. Error Handling and Recovery

**Decision**: Three-layer error handling: MCP tool errors, agent errors, chat endpoint errors

**Error Handling Layers**:

**1. MCP Tool Errors**:
- Tool validates inputs with Pydantic schemas
- Tool returns structured error responses: `{status: "error", message: "Task not found"}`
- Tool never throws unhandled exceptions
- Tool logs errors for debugging
- Agent receives error response and generates conversational error message

**2. Agent Errors**:
- Agent handles MCP tool errors gracefully
- Agent generates conversational responses: "I couldn't find task 999. Would you like to see your task list?"
- Agent asks clarifying questions for ambiguous input
- Agent continues conversation after errors (no crashes)
- Agent handles OpenAI API errors (rate limits, timeouts)

**3. Chat Endpoint Errors**:
- Endpoint validates JWT token (401 if invalid)
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
- All errors result in user-friendly conversational messages
- No technical error messages exposed to users
- Agent suggests next actions ("Would you like to see your task list?")
- Frontend displays errors in chat interface (not alert popups)

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
- Agent accuracy: Test with 60 acceptance scenarios, refine system prompt

---

# Phase 1: Design Artifacts

## Data Models

See [data-model.md](./data-model.md) for complete entity definitions.

**Summary**:
- **Conversation**: id, user_id, created_at, updated_at
- **Message**: id, conversation_id, user_id, role (user/assistant), content, created_at
- **Task**: (existing from Phase 2, all fields preserved including priority, tags, due_date, due_time, recurrence)

## API Contracts

See [contracts/](./contracts/) for complete specifications.

**Summary**:
- **POST /api/{user_id}/chat**: Chat endpoint with conversation persistence
- **6 MCP Tools**: add_task, list_tasks, search_tasks, complete_task, delete_task, update_task
- **Agent Behavior**: System prompt, intent recognition patterns, entity extraction

## Quickstart Guide

See [quickstart.md](./quickstart.md) for setup instructions.

**Summary**:
- Backend: Install dependencies, configure env vars, run MCP server
- Frontend: Install dependencies, configure ChatKit, run dev server
- Testing: Run pytest for backend, npm test for frontend
- Deployment: Vercel (frontend), any platform (backend)

---

# Implementation Plan Summary

## Phase 3 Workflow

**Phase 0: Research** ✅ COMPLETE
- Technology decisions finalized
- Architecture patterns validated
- Performance targets established
- Testing strategy defined

**Phase 1: Design** ✅ COMPLETE
- Data models documented (data-model.md)
- API contracts defined (contracts/)
- Quickstart guide created (quickstart.md)
- Agent context updated

**Phase 2: Task Breakdown** (Next: `/sp.tasks`)
- Generate atomic tasks from this plan
- Create test-first task sequence
- Include MCP tool tasks, agent tasks, chat endpoint tasks
- Include conversation flow testing tasks

**Phase 3: Implementation** (`/sp.implement`)
- Execute tasks in dependency order
- Follow TDD cycle (Red → Green → Refactor)
- Validate against constitution at each step
- Create PHRs for learning

**Phase 4: Validation**
- Run all quality gates (pytest, mypy, ruff, tsc, eslint)
- Verify all 60 acceptance scenarios pass
- Confirm constitution compliance
- Create demo video

---

## Next Steps

1. **Run `/sp.tasks`** to generate atomic, testable tasks from this plan
2. **Review tasks** for dependency order and completeness
3. **Run `/sp.implement`** to execute tasks with TDD workflow
4. **Validate** all quality gates pass
5. **Create PHR** for planning phase
6. **Proceed to implementation** with confidence

---

**Status**: ✅ Planning Phase Complete
**Ready for**: Task generation (`/sp.tasks`)
**Branch**: `003-phase3-ai-chatbot`
**Date**: 2025-12-17
