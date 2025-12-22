<!--
Sync Impact Report:
Version: 3.0.0 (MAJOR - Phase 3 Transition: Full-Stack Web App → AI Chatbot)
Previous Version: 2.0.0
Changes in v3.0.0:
  - MAJOR PHASE TRANSITION: Phase 2 (Full-Stack Web) → Phase 3 (AI Chatbot with MCP)
  - ADDED Technology Stack: OpenAI ChatKit, OpenAI Agents SDK, Official MCP SDK
  - ADDED Principle XII: AI Agent Development & MCP Server Architecture
  - ADDED Principle XIII: Stateless Architecture & Conversation State Management
  - ADDED Principle XIV: Natural Language Understanding & Intent Recognition
  - UPDATED Database Models: Added Conversation and Message tables
  - UPDATED API Design: New POST /api/{user_id}/chat endpoint for chatbot
  - UPDATED Development Workflow: AI-first conversational interface development
  - UPDATED Quality Gates: Added MCP tool testing, conversation flow testing, NLU testing
  - MAINTAINED all 11 principles from Phase 2 (I-XI unchanged in spirit, updated for Phase 3 context)
  - MAINTAINED All 10 features from Phase 2 (Basic + Intermediate + Advanced via natural language)
  - UPDATED Scope: AI chatbot in-scope with full feature set, Kubernetes/Kafka still out-of-scope (Phase IV/V)
Principles (Updated):
  - I. Spec-First Development (unchanged - applies to MCP tools and chatbot features)
  - II. Test-First (TDD - NON-NEGOTIABLE) (updated - includes MCP tool tests, conversation tests)
  - III. YAGNI Principle (UPDATED - Phase 3 implements ALL 10 features via AI chatbot)
  - IV. Technology Stack Requirements (BREAKING - added OpenAI stack, MCP SDK)
  - V. Clean Code & Modularity (UPDATED - includes MCP server structure, agents directory)
  - VI. Type Safety (unchanged - still applies to Python backend + MCP tools)
  - VII. Comprehensive Documentation (UPDATED - includes MCP tool specs, agent behavior docs)
  - VIII. Error Handling (UPDATED - includes MCP tool errors, conversation errors)
  - IX. Multi-User Data Isolation & Security (unchanged - JWT still required)
  - X. Database Schema & Migration Management (UPDATED - added Conversation, Message tables)
  - XI. API Design & RESTful Conventions (UPDATED - added chat endpoint, MCP tools)
  - XII. AI Agent Development & MCP Server Architecture (NEW)
  - XIII. Stateless Architecture & Conversation State Management (NEW)
  - XIV. Natural Language Understanding & Intent Recognition (NEW)
Templates Requiring Updates:
  - ⚠ plan-template.md (requires Phase 3 architecture patterns: MCP, stateless, AI agent)
  - ⚠ spec-template.md (requires chatbot user journeys, NLU examples, MCP tool specs)
  - ⚠ tasks-template.md (requires MCP tool implementation tasks, conversation flow tasks)
Follow-up TODOs:
  - Create Phase 3 feature specification for AI chatbot (all 10 features via NL)
  - Set up MCP server with 5 task operation tools
  - Configure OpenAI Agents SDK with MCP client
  - Set up OpenAI ChatKit frontend
  - Implement stateless chat endpoint with database persistence
  - Create comprehensive MCP tool tests and conversation flow tests
Ratification Date: 2025-12-06
Last Amended: 2025-12-17
-->

# Evolved Todo - Phase 3 Constitution

## Core Principles

### I. Spec-First Development
Every feature MUST have a specification written and approved before implementation begins. Specifications are the single source of truth for requirements, acceptance criteria, and implementation guidance.

**Rules:**
- Feature specs live in `specs/<feature>/spec.md`
- All specs follow the spec-template structure
- Specs must define clear acceptance criteria for chatbot interactions, MCP tools, and conversation flows
- Specs must include natural language examples, MCP tool schemas, and expected AI behavior
- Implementation must not begin until spec is approved
- Code that doesn't match spec is incorrect, regardless of functionality

**Phase 3 Additions:**
- MCP tool specifications must define input schemas, output schemas, and error cases
- Chatbot behavior must be specified with example conversations
- Agent prompts and system messages must be documented in specs

**Rationale:** Spec-first ensures alignment between architect (human or AI), developer (Claude Code), and stakeholder expectations before any code is written. In Phase 3, this extends to AI agent behavior, MCP tools, and conversational interfaces.

### II. Test-First (TDD - NON-NEGOTIABLE)
Test-Driven Development is mandatory for backend, MCP tools, and conversation flows. Tests MUST be written, reviewed, and approved before implementation code.

**Red-Green-Refactor Cycle (Strictly Enforced):**
1. **Red:** Write failing tests that capture acceptance criteria
2. **Green:** Implement minimal code to pass tests
3. **Refactor:** Improve code while keeping tests green

**Rules:**
- **Backend (FastAPI):** pytest for unit and integration tests
  - All API endpoints must have integration tests (including chat endpoint)
  - All service layer functions must have unit tests
  - All database models must have validation tests
- **MCP Tools:** pytest for MCP tool tests
  - All MCP tools must have unit tests with mock database
  - All MCP tool schemas must be validated
  - All MCP tool error paths must be tested
- **Conversation Flows:** pytest for conversation integration tests
  - All conversation flows must have end-to-end tests
  - All natural language intents must be tested
  - All conversation state persistence must be tested
- Tests written first → User approved → Tests fail → Then implement
- Edge cases and error paths must have tests
- Tests must be deterministic and isolated

**Rationale:** TDD ensures correctness, prevents regression, and serves as executable documentation for backend, MCP tools, and AI agent behavior.

### III. YAGNI Principle (Phase 3 Scope - All 10 Features via AI Chatbot)
"You Aren't Gonna Need It" - Implement ALL 10 features from Phase 2 (Basic + Intermediate + Advanced) via AI chatbot interface in Phase 3. No Kubernetes, no Kafka, no Dapr.

**Phase 3 Features - Basic Level (Core Essentials via Natural Language):**
1. Add Task – "Add a task to buy groceries"
2. Delete Task – "Delete task 3"
3. Update Task – "Change task 1 to 'Call mom tonight'"
4. View Task List – "Show me all my tasks"
5. Mark as Complete – "Mark task 2 as complete"

**Phase 3 Features - Intermediate Level (Organization & Usability):**
6. Priorities & Tags – "Add a high priority task" / "Tag this with work"
7. Search & Filter – "Show me high priority tasks" / "Filter by work tag"
8. Sort Tasks – "Sort my tasks by due date"

**Phase 3 Features - Advanced Level (Intelligent Features):**
9. Recurring Tasks – "Add a weekly meeting task every Monday"
10. Due Dates & Reminders – "Set due date to Friday 5 PM for task 3"

**Phase 3 Implementation Requirements:**
- All 10 features MUST work via natural language commands through chatbot
- OpenAI ChatKit frontend for conversational UI
- OpenAI Agents SDK for AI logic and intent recognition
- MCP server with tools for all task operations (CRUD, priorities, tags, filters, sorting, recurrence, due dates)
- Stateless chat endpoint with database-persisted conversation state
- Better Auth JWT authentication for multi-user support
- Full Task model from Phase 2 (includes priority, tags, due_date, due_time, recurrence fields)

**Forbidden in Phase 3:**
- ❌ Kubernetes deployment (Phase IV)
- ❌ Event-driven architecture with Kafka (Phase V)
- ❌ Dapr distributed runtime (Phase V)
- ❌ Any feature beyond the 10-feature list

**Rationale:** Phase 3 delivers the complete Phase 2 feature set via AI chatbot interface with stateless architecture and MCP tools. All 10 features via natural language before transitioning to cloud-native deployment in Phase IV.

### IV. Technology Stack Requirements (Phase 3)
Phase 3 MUST use the specified technology stack. No substitutions.

**Mandatory Stack:**

**Frontend:**
- **Framework:** OpenAI ChatKit (hosted or self-hosted)
- **Language:** TypeScript (strict mode)
- **Styling:** Tailwind CSS (for custom UI around ChatKit)
- **Authentication:** Better Auth with JWT

**Backend:**
- **Framework:** Python FastAPI
- **Language:** Python 3.13+
- **AI Framework:** OpenAI Agents SDK (for agent orchestration)
- **MCP Server:** Official MCP SDK (Python implementation)
- **ORM:** SQLModel
- **Database:** Neon Serverless PostgreSQL
- **Package Manager:** UV (not pip, not poetry)

**Testing & Quality:**
- **Backend Testing:** pytest, pytest-cov
- **MCP Testing:** pytest with mock tools
- **Conversation Testing:** pytest with mock OpenAI responses
- **Type Checking:** mypy (Python), TypeScript compiler
- **Linting:** ruff (Python), ESLint (TypeScript)
- **Formatting:** ruff format (Python), Prettier (TypeScript)

**Deployment (Optional for Phase 3):**
- **Frontend Hosting:** Vercel (or any platform supporting Next.js/ChatKit)
- **Backend Hosting:** Any Python-compatible platform
- **Database:** Neon Serverless PostgreSQL (managed)

**Rules:**
- All dependencies managed via `pyproject.toml` (backend) and `package.json` (frontend)
- Must use monorepo structure with `frontend/` and `backend/` folders
- JWT tokens for authentication between frontend and backend
- Shared `BETTER_AUTH_SECRET` environment variable for JWT signing
- MCP server runs within FastAPI backend (not separate process in Phase 3)
- OpenAI API key required for Agents SDK (`OPENAI_API_KEY` env var)

**Rationale:** Standardization ensures consistency and prepares for Phase IV (Kubernetes) migration. OpenAI stack chosen for simplicity and reliability.

### V. Clean Code & Modularity (Phase 3 - Monorepo with MCP Server)
Code MUST be well-organized, modular, and follow clean code principles. Phase 3 extends monorepo structure with MCP server and agents directory.

**Organization Requirements:**
- Separation of concerns (data models, business logic, API routes, MCP tools, AI agents)
- Single Responsibility Principle for all functions, classes, components, and MCP tools
- Clear, descriptive naming (no abbreviations like `td`, `lst`, `mgr`)
- Maximum function length: 20 lines (excluding docstrings)
- Maximum file length: 200 lines (300 for complex API routes or MCP tool implementations)

**Phase 3 Project Structure:**
```
evolved-todo/
├── .spec-kit/
│   └── config.yaml
├── specs/
│   ├── overview.md
│   ├── architecture.md
│   ├── features/          # Feature specifications
│   ├── api/               # API specifications (including chat endpoint)
│   ├── database/          # Database schema (including Conversation, Message)
│   ├── mcp/               # MCP tool specifications
│   └── ui/                # ChatKit UI specs
├── frontend/
│   ├── CLAUDE.md
│   ├── app/               # Next.js App Router pages
│   ├── components/        # ChatKit integration
│   ├── lib/               # API client for chat endpoint
│   ├── types/             # TypeScript types
│   └── __tests__/         # Frontend tests
├── backend/
│   ├── CLAUDE.md
│   ├── app/
│   │   ├── main.py        # FastAPI entry point
│   │   ├── models.py      # SQLModel database models (Task, Conversation, Message)
│   │   ├── routes/        # API route handlers (including chat.py)
│   │   ├── services/      # Business logic
│   │   ├── mcp/           # MCP server and tools
│   │   │   ├── server.py  # MCP server setup
│   │   │   └── tools/     # MCP tool implementations (add_task, list_tasks, etc.)
│   │   ├── agents/        # OpenAI Agents SDK configuration
│   │   │   ├── todo_agent.py  # Main todo agent
│   │   │   └── prompts.py     # System prompts and instructions
│   │   ├── auth.py        # JWT authentication
│   │   └── db.py          # Database connection
│   └── tests/             # Backend tests (including MCP tool tests)
├── docker-compose.yml
├── AGENTS.md
├── CLAUDE.md
└── README.md
```

**Rationale:** Clear structure separates AI components (agents, MCP) from traditional web components (API, database), making Phase 3 architecture easy to understand and maintain.

### VI. Type Safety (Phase 3 - Python & TypeScript)
All functions MUST have complete type annotations. Type checking MUST pass without errors for both Python and TypeScript.

**Backend (Python) Requirements:**
- Function signatures: parameters and return types fully annotated
- Class attributes: type annotations required
- No `Any` types unless explicitly justified
- Use generic types (`list[Task]`, not `list`)
- Enable strict mypy mode
- SQLModel models with proper type hints
- MCP tool input/output schemas fully typed

**Frontend (TypeScript) Requirements:**
- Enable strict mode in `tsconfig.json`
- All component props fully typed (no implicit `any`)
- API response types defined and validated
- ChatKit props and event handlers fully typed
- Use TypeScript generics where appropriate
- Avoid type assertions (`as`) unless necessary

**Example (Backend - MCP Tool):**
```python
from pydantic import BaseModel
from typing import Literal

class AddTaskInput(BaseModel):
    user_id: str
    title: str
    description: str | None = None

class AddTaskOutput(BaseModel):
    task_id: int
    status: Literal["created"]
    title: str

async def add_task(input: AddTaskInput) -> AddTaskOutput:
    # Implementation
    pass
```

**Example (Frontend - ChatKit):**
```typescript
interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface ChatResponse {
  conversation_id: number;
  response: string;
  tool_calls: string[];
}

async function sendMessage(userId: string, message: string): Promise<ChatResponse> {
  const response = await fetch(`/api/${userId}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`
    },
    body: JSON.stringify({ message })
  });
  return response.json();
}
```

**Rationale:** Type safety catches bugs at compile time, improves IDE support, and serves as inline documentation for backend, MCP tools, and frontend.

### VII. Comprehensive Documentation (Phase 3 - MCP Tools & AI Behavior)
Documentation MUST be thorough, clear, and maintained alongside code. Phase 3 includes MCP tool documentation, AI agent behavior documentation, and conversation flow documentation.

**Required Documentation:**

1. **README.md:**
   - Project overview and Phase 3 scope
   - Setup instructions (frontend, backend, MCP server, OpenAI API key)
   - Environment variables (OPENAI_API_KEY, BETTER_AUTH_SECRET, DATABASE_URL)
   - Running locally (frontend, backend with MCP server)
   - Running tests (backend, MCP tools, conversation flows)
   - Deployment instructions

2. **API Documentation:**
   - All API endpoints documented in `specs/api/rest-endpoints.md`
   - Chat endpoint specification (POST /api/{user_id}/chat)
   - Request/response schemas with examples
   - Authentication requirements (JWT token header)
   - Error response formats

3. **MCP Tool Documentation:**
   - All MCP tools documented in `specs/mcp/tools.md`
   - Tool schemas (input parameters, output format)
   - Tool behavior and side effects
   - Error handling for each tool
   - Usage examples with natural language triggers

4. **AI Agent Documentation:**
   - Agent behavior documented in `specs/mcp/agent-behavior.md`
   - System prompts and instructions
   - Intent recognition patterns
   - Conversation flow examples
   - Tool invocation logic

5. **Database Schema Documentation:**
   - Schema documented in `specs/database/schema.md`
   - All tables: Task, Conversation, Message
   - All columns, relationships, indexes
   - Migration strategy

6. **Docstrings/Comments (Backend):**
   - All public functions, classes, methods (Google style)
   - Include Args, Returns, Raises sections
   - FastAPI route handlers with OpenAPI descriptions
   - MCP tools with schema documentation

7. **Architecture Documentation:**
   - `specs/architecture.md` explaining Phase 3 architecture
   - Data flow: ChatKit → Chat Endpoint → OpenAI Agents SDK → MCP Tools → Database
   - Stateless architecture explanation
   - Conversation state persistence strategy
   - Design decisions and rationale

**Rationale:** Comprehensive docs enable onboarding, facilitate review, and prepare for Phase IV (Kubernetes) handoff. MCP and AI documentation critical for understanding agent behavior.

### VIII. Error Handling (Phase 3 - MCP Tool Errors & Conversation Errors)
Errors MUST be handled explicitly and gracefully. No silent failures. Phase 3 includes MCP tool error handling and conversational error recovery.

**Backend (FastAPI) Requirements:**
- Validate all inputs with Pydantic models
- Use HTTPException with appropriate status codes
- Return structured error responses with `detail` field
- Handle database errors (connection, constraints, etc.)
- Handle OpenAI API errors (rate limits, timeouts, etc.)
- Handle MCP tool errors (invalid input, tool failure, etc.)
- Log errors for debugging

**MCP Tool Requirements:**
- Validate all tool inputs with Pydantic schemas
- Return structured error responses
- Handle missing tasks gracefully ("Task not found")
- Handle permission errors ("Access denied to task")
- Never crash the agent on tool errors

**Frontend (ChatKit) Requirements:**
- Handle API errors gracefully (network errors, 4xx, 5xx)
- Display user-friendly error messages in chat interface
- Retry on transient failures (network timeout)
- Provide fallback responses for errors
- Never leave user without feedback

**Conversation Error Recovery:**
- Agent must acknowledge errors conversationally
- "I couldn't find that task. Could you provide the task ID?"
- "Something went wrong while adding the task. Please try again."
- Agent must continue conversation after errors (no crashes)

**HTTP Status Codes:**
- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid input validation
- `401 Unauthorized` - Missing or invalid JWT token
- `403 Forbidden` - User doesn't have access to resource
- `404 Not Found` - Resource doesn't exist
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - OpenAI API unavailable

**Example (MCP Tool Error Handling):**
```python
from pydantic import ValidationError

async def complete_task(input: CompleteTaskInput) -> CompleteTaskOutput:
    try:
        task = session.get(Task, input.task_id)
        if not task:
            return CompleteTaskOutput(
                task_id=input.task_id,
                status="error",
                message=f"Task with ID {input.task_id} not found"
            )
        if task.user_id != input.user_id:
            return CompleteTaskOutput(
                task_id=input.task_id,
                status="error",
                message="Access denied to this task"
            )
        task.completed = True
        session.commit()
        return CompleteTaskOutput(
            task_id=task.id,
            status="completed",
            title=task.title
        )
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        return CompleteTaskOutput(
            task_id=input.task_id,
            status="error",
            message="Failed to complete task"
        )
```

**Rationale:** Explicit error handling with conversational recovery prevents undefined behavior and improves user experience in AI chatbot interfaces.

### IX. Multi-User Data Isolation & Security (Phase 3 - Unchanged)
Every user MUST only see and modify their own data. Authentication and authorization are mandatory for all API endpoints, including chat endpoint.

**Authentication Requirements:**
- **Better Auth** on Next.js frontend for user signup/signin
- JWT tokens issued by Better Auth upon successful login
- JWT tokens include `user_id` claim for identification
- Tokens expire after 7 days (configurable)
- Refresh tokens supported for seamless re-authentication

**Authorization Requirements:**
- All API endpoints require valid JWT token in `Authorization: Bearer <token>` header
- Chat endpoint requires valid JWT token
- Requests without token receive `401 Unauthorized`
- Backend extracts `user_id` from JWT token
- All database queries filtered by `user_id`
- Task ownership enforced: users can only access their own tasks
- Conversation ownership enforced: users can only access their own conversations
- Path parameter `{user_id}` MUST match JWT token `user_id` claim

**MCP Tool Security:**
- All MCP tools receive `user_id` parameter
- All MCP tools filter database queries by `user_id`
- MCP tools never expose data from other users
- Agent cannot override user isolation

**Security Rules:**
- Shared `BETTER_AUTH_SECRET` between frontend and backend
- Secret stored in environment variables (never committed to git)
- JWT signature verified on every request
- No SQL injection (use parameterized queries via SQLModel)
- No XSS (escape all user inputs in UI)
- HTTPS required for production (enforced by Vercel/hosting)
- OpenAI API key stored securely in environment variables

**Rationale:** Multi-user data isolation ensures privacy, security, and prevents unauthorized access in AI chatbot application.

### X. Database Schema & Migration Management (Phase 3 - Added Conversation & Message)
Database schema MUST be versioned, documented, and managed through migrations. SQLModel provides automatic schema management.

**Database Requirements:**
- **Provider:** Neon Serverless PostgreSQL (managed, no local setup)
- **ORM:** SQLModel (combines SQLAlchemy + Pydantic)
- **Migrations:** SQLModel automatic table creation (Phase 3 only - manual migrations in Phase 4+)
- **Connection:** Connection string from `DATABASE_URL` environment variable

**Schema Design Rules:**
- All tables include `created_at` and `updated_at` timestamps
- Use appropriate indexes for query performance (`user_id`, `completed`, `conversation_id`, etc.)
- Foreign keys for relationships (users → tasks, users → conversations, conversations → messages)
- NOT NULL constraints for required fields
- VARCHAR limits for text fields (prevent abuse)

**Phase 3 Database Models:**

**Users Table (Managed by Better Auth):**
```python
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)  # UUID from Better Auth
    email: str = Field(unique=True, index=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Tasks Table:**
```python
from datetime import datetime, date, time
from sqlmodel import Field, SQLModel

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

**Conversations Table (NEW - Phase 3):**
```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Messages Table (NEW - Phase 3):**
```python
from typing import Literal

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    role: Literal["user", "assistant"] = Field(index=True)
    content: str = Field(max_length=5000)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
```

**Migration Strategy (Phase 3):**
- SQLModel creates tables automatically on first run
- Use `create_db_and_tables()` in `app/db.py`
- No manual migrations needed for Phase 3
- Schema documented in `specs/database/schema.md`

**Rationale:** Structured schema management ensures data integrity, query performance, and conversation state persistence for AI chatbot.

### XI. API Design & RESTful Conventions (Phase 3 - Added Chat Endpoint)
All API endpoints MUST follow RESTful conventions and return consistent, predictable responses. Phase 3 adds chat endpoint for conversational interface.

**RESTful Endpoint Design:**

| Method | Endpoint | Description | Request Body | Success Response |
|--------|----------|-------------|--------------|------------------|
| GET | `/api/{user_id}/tasks` | List all tasks | None | `200 OK` + Task[] |
| POST | `/api/{user_id}/tasks` | Create task | Task data | `201 Created` + Task |
| GET | `/api/{user_id}/tasks/{id}` | Get task | None | `200 OK` + Task |
| PUT | `/api/{user_id}/tasks/{id}` | Update task | Task data | `200 OK` + Task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task | None | `204 No Content` |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle complete | None | `200 OK` + Task |
| **POST** | **`/api/{user_id}/chat`** | **Send chat message** | **Chat message** | **`200 OK` + Response** |

**Chat Endpoint Specification:**

**Request:**
```json
{
  "conversation_id": 123,  // Optional: omit to create new conversation
  "message": "Add a task to buy groceries"
}
```

**Response:**
```json
{
  "conversation_id": 123,
  "response": "I've added 'Buy groceries' to your task list. Task ID is 5.",
  "tool_calls": ["add_task"]
}
```

**API Conventions:**
- All endpoints prefixed with `/api`
- User-scoped endpoints include `{user_id}` path parameter
- Use plural nouns for resources (`/tasks`, not `/task`)
- Use HTTP methods semantically (GET = read, POST = create, PUT = update, DELETE = delete, PATCH = partial update)
- Return appropriate status codes (2xx success, 4xx client error, 5xx server error)
- Return JSON responses with consistent structure

**Rationale:** RESTful conventions ensure predictable APIs. Chat endpoint provides conversational interface while maintaining REST principles.

### XII. AI Agent Development & MCP Server Architecture (NEW - Phase 3)
AI agents and MCP tools MUST be developed with clear separation of concerns, testability, and deterministic behavior.

**MCP Server Requirements:**
- MCP server runs within FastAPI backend (not separate process in Phase 3)
- Official MCP SDK (Python) for tool registration
- All tools registered with schemas (input/output types)
- Tools are stateless: receive input, return output, no side effects beyond database
- Tools never maintain internal state (all state in database)

**MCP Tool Design Rules:**
- Each tool is a single-purpose function
- Clear input schema with Pydantic models
- Clear output schema with Pydantic models
- Error responses are part of output schema (status: "success" | "error")
- Tools validate inputs before execution
- Tools handle errors gracefully (no crashes)
- Tools are fully testable with mock database

**Phase 3 MCP Tools (All 10 Features):**

**Basic Level Tools:**
1. **add_task** - Create new task
   - Input: user_id, title, description (optional), priority (optional), tags (optional), due_date (optional), due_time (optional), recurrence (optional)
   - Output: task_id, status, title
2. **list_tasks** - Retrieve tasks with filtering and sorting
   - Input: user_id, status (optional: "all" | "pending" | "completed"), priority (optional), tag (optional), sort_by (optional: "id" | "title" | "priority" | "due_date" | "created_at"), sort_order (optional: "asc" | "desc")
   - Output: Array of task objects
3. **complete_task** - Mark task complete (handles recurring task logic)
   - Input: user_id, task_id
   - Output: task_id, status, title, next_occurrence (if recurring)
4. **delete_task** - Remove task
   - Input: user_id, task_id
   - Output: task_id, status, title
5. **update_task** - Modify task (all fields)
   - Input: user_id, task_id, title (optional), description (optional), priority (optional), tags (optional), due_date (optional), due_time (optional), recurrence (optional)
   - Output: task_id, status, title

**Intermediate Level Tools:**
6. **search_tasks** - Search tasks by keyword
   - Input: user_id, keyword
   - Output: Array of matching task objects

**Note:** Filtering, sorting, priorities, and tags are integrated into the list_tasks and add_task/update_task tools above. No separate tools needed for these intermediate features.

**OpenAI Agents SDK Integration:**
- Agent initialized with system prompt defining behavior
- Agent has access to MCP tools via tool definitions
- Agent decides which tools to call based on user message
- Agent can chain multiple tool calls in single turn
- Agent provides conversational responses wrapping tool outputs

**Agent Behavior Specification:**
- When user mentions adding/creating/remembering → call add_task (extract priority, tags, due dates from natural language)
- When user asks to see/show/list → call list_tasks (extract filters and sort preferences)
- When user says done/complete/finished → call complete_task (handle recurring task logic automatically)
- When user says delete/remove/cancel → call delete_task
- When user says change/update/rename → call update_task (extract which fields to update)
- When user asks to search/find → call search_tasks
- When user mentions priority (high/medium/low) → extract and include in tool calls
- When user mentions tags/categories → extract and include in tool calls
- When user mentions dates/times → parse and include as due_date/due_time
- When user mentions recurring patterns (daily/weekly/monthly) → extract recurrence parameters
- Always confirm actions with friendly response
- Gracefully handle errors ("I couldn't find that task")

**Example (MCP Tool Registration):**
```python
from mcp import Tool, MCPServer

server = MCPServer()

@server.tool(
    name="add_task",
    description="Create a new task for the user",
    input_schema=AddTaskInput.schema(),
    output_schema=AddTaskOutput.schema()
)
async def add_task(input: AddTaskInput) -> AddTaskOutput:
    # Implementation
    pass
```

**Rationale:** Clear MCP architecture separates AI logic (agent) from task operations (tools), enabling testability, maintainability, and future extensibility.

### XIII. Stateless Architecture & Conversation State Management (NEW - Phase 3)
The chat endpoint MUST be stateless. All conversation state MUST be persisted to database. Server restarts MUST NOT lose conversation history.

**Stateless Server Requirements:**
- Chat endpoint does not maintain in-memory state
- Every request is independent
- Server can be restarted without losing conversations
- Horizontally scalable (any server can handle any request)

**Conversation State Persistence:**
- Conversation history stored in `conversations` and `messages` tables
- Each request fetches conversation history from database
- Each request stores new user message and assistant response
- Conversation history passed to OpenAI Agents SDK on every request

**Request Cycle:**
1. Receive user message + optional conversation_id
2. If conversation_id provided, fetch conversation history from database
3. If no conversation_id, create new conversation record
4. Store user message in messages table
5. Build message array for agent (history + new message)
6. Run agent with MCP tools (agent decides which tools to call)
7. Agent generates response
8. Store assistant response in messages table
9. Return response to client
10. Server forgets everything (ready for next request)

**Conversation History Management:**
- Full conversation history sent to agent on every request
- History includes all previous user and assistant messages
- History ordered by created_at timestamp
- History limited to prevent token overflow (last 50 messages recommended)

**Example (Chat Endpoint Implementation):**
```python
@app.post("/api/{user_id}/chat")
async def chat(
    user_id: str,
    request: ChatRequest,
    authenticated_user_id: str = Depends(verify_token)
):
    if user_id != authenticated_user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Fetch or create conversation
    if request.conversation_id:
        conversation = session.get(Conversation, request.conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(status_code=404, detail="Conversation not found")
        # Fetch conversation history
        messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at)
        ).all()
    else:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        messages = []

    # Store user message
    user_message = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="user",
        content=request.message
    )
    session.add(user_message)
    session.commit()

    # Build message history for agent
    history = [{"role": msg.role, "content": msg.content} for msg in messages]
    history.append({"role": "user", "content": request.message})

    # Run agent with MCP tools
    response = await run_agent(user_id, history)

    # Store assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="assistant",
        content=response["content"]
    )
    session.add(assistant_message)
    session.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        response=response["content"],
        tool_calls=response.get("tool_calls", [])
    )
```

**Rationale:** Stateless architecture enables scalability, resilience, and horizontal scaling. Database persistence ensures conversation history survives server restarts.

### XIV. Natural Language Understanding & Intent Recognition (NEW - Phase 3)
The AI agent MUST understand natural language commands and map them to appropriate MCP tool calls. Intent recognition MUST be robust and user-friendly.

**Natural Language Command Examples:**

| User Says | Agent Should |
|-----------|-------------|
| "Add a task to buy groceries" | Call add_task with title "Buy groceries" |
| "Add a high priority task to call dentist" | Call add_task with title "Call dentist", priority "high" |
| "Create a work task for the presentation" | Call add_task with title "Presentation", tags "work" |
| "Add a weekly meeting task every Monday" | Call add_task with title "Weekly meeting", recurrence "weekly", recurrence_day 1 |
| "Set due date to Friday 5 PM for task 3" | Call update_task with task_id 3, due_date "2025-12-19", due_time "17:00:00" |
| "Show me all my tasks" | Call list_tasks with status "all" |
| "Show me high priority tasks" | Call list_tasks with priority "high" |
| "Filter by work tag" | Call list_tasks with tag "work" |
| "Sort my tasks by due date" | Call list_tasks with sort_by "due_date" |
| "What's pending?" | Call list_tasks with status "pending" |
| "Search for dentist" | Call search_tasks with keyword "dentist" |
| "Mark task 3 as complete" | Call complete_task with task_id 3 (creates next occurrence if recurring) |
| "Delete the meeting task" | Call search_tasks first, identify task, then call delete_task |
| "Change task 1 to 'Call mom tonight'" | Call update_task with task_id 1, title "Call mom tonight" |
| "Make task 2 high priority" | Call update_task with task_id 2, priority "high" |
| "What have I completed?" | Call list_tasks with status "completed" |

**Intent Recognition Rules:**
- Agent must recognize various phrasings for same intent
- Agent must extract entities (task ID, title, description, status)
- Agent must handle ambiguous requests by asking clarification
- Agent must handle multi-step requests (e.g., "Show tasks and mark 3 complete")

**System Prompt Requirements:**
- Define agent personality (helpful, concise, friendly)
- Define tool usage guidelines
- Define error handling behavior
- Define confirmation patterns
- Provide example conversations

**Example (System Prompt):**
```
You are a helpful todo assistant. You help users manage their task list through natural language commands.

You have access to these tools:
- add_task: Create a new task (supports title, description, priority, tags, due dates, recurrence)
- list_tasks: Show tasks with filtering and sorting (status, priority, tags, sort options)
- search_tasks: Search tasks by keyword
- complete_task: Mark a task as done (automatically handles recurring tasks)
- delete_task: Remove a task
- update_task: Modify any task field (title, description, priority, tags, due dates, recurrence)

When users mention adding, creating, or remembering something, use add_task.
  - Extract priority from phrases like "high priority", "urgent", "important"
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

**Conversation Flow Testing:**
- All natural language examples must have integration tests
- Tests verify correct tool calls for each intent
- Tests verify correct responses for each scenario
- Tests verify error handling for edge cases

**Rationale:** Robust NLU ensures users can interact naturally with chatbot without learning specific commands. Intent recognition quality directly impacts user experience.

## Phase 3 Scope Constraints

### In-Scope
- **Frontend:** OpenAI ChatKit conversational interface
- **Backend:** FastAPI with OpenAI Agents SDK + MCP server
- **Database:** Neon PostgreSQL with Conversation, Message, Task tables
- **Authentication:** Better Auth with JWT tokens
- **Multi-User:** Complete user isolation and data privacy
- **All 10 Features:** Basic (1-5), Intermediate (6-8), Advanced (9-10) via natural language
- **MCP Tools:** 6 stateless tools supporting all task operations (CRUD, priorities, tags, filtering, sorting, recurrence, due dates)
- **Stateless Architecture:** Database-persisted conversation state
- **Testing:** Comprehensive test coverage (>90%) for backend, MCP tools, conversation flows
- **Deployment:** Frontend on Vercel, backend on any platform

### Out-of-Scope (Future Phases)
- ❌ Kubernetes deployment (Phase IV)
- ❌ Event-driven architecture with Kafka (Phase V)
- ❌ Dapr distributed runtime (Phase V)
- ❌ Helm charts (Phase IV)
- ❌ CI/CD pipelines (Phase V)

## Development Workflow (Phase 3)

### Feature Development Process
1. **Specification:** Write feature spec in `specs/features/<feature>/spec.md`
   - Include natural language examples
   - Include MCP tool specifications
   - Include agent behavior requirements
   - Include conversation flow examples
2. **Review Spec:** Ensure alignment with constitution and acceptance criteria
3. **Database First:** Update database models in `backend/app/models.py` (add Conversation, Message)
4. **Write MCP Tool Tests:** Create failing tests for each MCP tool
5. **Implement MCP Tools:** Write tool functions with schemas (Red → Green)
6. **Write Agent Tests:** Create failing tests for agent behavior
7. **Implement Agent:** Configure OpenAI Agents SDK with system prompt and tools
8. **Write Chat Endpoint Tests:** Create failing tests for stateless chat endpoint
9. **Implement Chat Endpoint:** Write FastAPI route with conversation persistence
10. **Write Frontend Tests:** Create failing tests for ChatKit integration
11. **Implement Frontend:** Integrate ChatKit with chat endpoint
12. **Integration Testing:** Test full flow (ChatKit → Chat Endpoint → Agent → MCP Tools → Database)
13. **Refactor:** Improve code quality while keeping tests green
14. **Documentation:** Update README, MCP docs, agent behavior docs, conversation examples
15. **Final Review:** Verify all quality gates pass

### Iteration Cycle
- Implement all 10 features (Basic + Intermediate + Advanced) via natural language
- Build MCP server with all 6 tools first (add_task, list_tasks, search_tasks, complete_task, delete_task, update_task)
- Then build agent with full system prompt
- Then build stateless chat endpoint
- Finally integrate ChatKit frontend

## Quality Gates (Phase 3)

All quality gates MUST pass before Phase 3 is considered complete.

### Automated Checks (Must Pass)

**Backend:**
- ✅ `pytest` - All backend tests pass
- ✅ `mypy` - No type errors (strict mode)
- ✅ `ruff check` - No linting errors
- ✅ `ruff format --check` - Code formatted correctly
- ✅ Test coverage >90% (pytest-cov)

**MCP Tools:**
- ✅ All 6 MCP tools have unit tests
- ✅ All MCP tool schemas validated
- ✅ All MCP tool error paths tested
- ✅ All MCP tools tested with mock database

**Conversation Flows:**
- ✅ All natural language examples have integration tests
- ✅ All conversation flows tested end-to-end
- ✅ All error recovery scenarios tested
- ✅ Stateless architecture validated (no in-memory state)

**Frontend:**
- ✅ `npm test` - All frontend tests pass
- ✅ `tsc --noEmit` - No TypeScript errors
- ✅ `eslint` - No linting errors
- ✅ `prettier --check` - Code formatted correctly
- ✅ `npm run build` - Production build succeeds

**Integration:**
- ✅ Chat endpoint returns correct responses
- ✅ JWT authentication works end-to-end
- ✅ Conversation state persisted to database
- ✅ Agent correctly invokes MCP tools
- ✅ Database queries are optimized (no N+1 queries)

### Manual Reviews (Must Confirm)
- ✅ Spec requirements met (all acceptance criteria)
- ✅ Constitution compliance (all principles followed)
- ✅ MCP tool documentation complete
- ✅ Agent behavior documented with examples
- ✅ ChatKit UI works smoothly
- ✅ Error handling for all edge cases
- ✅ Multi-user data isolation verified
- ✅ Conversation history survives server restart
- ✅ Natural language understanding is robust
- ✅ Security: JWT tokens, HTTPS, no SQL injection/XSS

### Pre-Submission Checklist
- [ ] All 10 features (Basic + Intermediate + Advanced) work via natural language
- [ ] All quality gates pass (backend + MCP + frontend)
- [ ] OpenAI ChatKit configured
- [ ] OpenAI Agents SDK integrated with MCP server
- [ ] All 6 MCP tools implemented and tested (supporting all 10 features)
- [ ] Stateless chat endpoint with database persistence
- [ ] Better Auth configured with JWT
- [ ] Neon database connected with Conversation and Message tables
- [ ] Chat endpoint secured with JWT middleware
- [ ] README includes setup instructions (OpenAI API key, etc.)
- [ ] Architecture documentation explains stateless architecture
- [ ] Frontend deployed to Vercel
- [ ] Backend deployed and accessible
- [ ] Demo video created (<90 seconds)

## Governance

### Constitution Authority
This constitution supersedes all other practices, preferences, or conventions. When in doubt, the constitution is the tiebreaker.

### Amendment Process
1. Constitution changes require explicit rationale
2. Version increments follow semantic versioning:
   - **MAJOR:** Principle removals or incompatible redefinitions, phase transitions
   - **MINOR:** New principles or significant expansions
   - **PATCH:** Clarifications, typo fixes, non-semantic changes
3. All amendments must update dependent templates (`plan-template.md`, `spec-template.md`, `tasks-template.md`)
4. Sync Impact Report required for all constitution updates

### Compliance Reviews
- **Per-Feature Review:** Verify spec, tests, implementation, docs against constitution
- **Pre-Submission Review:** Full constitution compliance audit before hackathon submission
- **AI Agent Guidance:** Claude Code must be instructed to validate constitution compliance for all work

### Phase Transition
When transitioning from Phase 3 → Phase 4:
1. Update this same `constitution.md` file (do not create separate files)
2. Increment version to 4.0.0 (MAJOR - phase transition with breaking changes)
3. Update principles to reflect Phase 4 requirements (Kubernetes, Helm, kubectl-ai, etc.)
4. Document breaking changes in Sync Impact Report at top of file
5. Update Last Amended date
6. Update all dependent templates and guidance for Phase 4 stack
7. Git history will preserve Phase 3 version for reference

**Note:** This constitution is a living document. All phase updates modify this single file with version increments tracked via git.

**Version:** 3.0.0 | **Ratified:** 2025-12-06 | **Last Amended:** 2025-12-17
