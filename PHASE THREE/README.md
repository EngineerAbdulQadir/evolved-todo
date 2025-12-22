# Evolved Todo - AI-Powered Task Management

A full-stack todo application with natural language AI chatbot interface, built with Next.js, FastAPI, and OpenAI Agents SDK.

## Phase 3: AI Chatbot Features

This project implements a conversational AI assistant that understands natural language commands for task management:

- **Natural Language Understanding**: "Add a high priority task to buy groceries tomorrow at 5pm"
- **Task Operations**: Create, view, update, complete, and delete tasks via chat
- **Smart Parsing**: Automatic extraction of priorities, tags, due dates, times, and recurrence
- **Error Handling**: Graceful error messages and clarification prompts
- **Stateless Architecture**: All conversation state persisted to PostgreSQL database

## Tech Stack

### Frontend
- **Next.js 16+** with App Router
- **OpenAI ChatKit** for chat UI components
- **TypeScript** with strict type checking
- **Tailwind CSS** for styling
- **Better Auth** for JWT authentication

### Backend
- **FastAPI** with async/await
- **OpenAI Agents SDK** for AI orchestration
- **Official MCP SDK** for tool integration
- **SQLModel** with async PostgreSQL
- **Neon Serverless PostgreSQL** for database
- **pytest** for comprehensive testing

## Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL** (or Neon Serverless account)
- **OpenAI API Key** (for GPT-4)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd evolved-todo
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies with UV package manager
uv sync

# Create .env file (copy from .env.example)
cp .env.example .env
```

### 3. Configure Environment Variables

Edit `backend/.env` with your credentials:

```env
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@host/database

# OpenAI API
OPENAI_API_KEY=sk-...your-openai-api-key...

# Better Auth JWT Secret
BETTER_AUTH_SECRET=your-secret-key-min-32-chars

# CORS Origins (frontend URL)
CORS_ORIGINS=http://localhost:3000
```

### 4. Initialize Database

```bash
# Run migrations (creates tables)
cd backend
uv run alembic upgrade head

# Or use FastAPI auto-init (development only)
uv run uvicorn app.main:app --reload
```

### 5. Run Backend Server

```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### 6. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.example .env.local
```

Edit `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
BETTER_AUTH_URL=http://localhost:3000
```

### 7. Run Frontend Development Server

```bash
cd frontend
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## Usage Examples

### Natural Language Task Management

**Create Tasks:**
- "Add a task to buy groceries"
- "Create a high priority work task for the meeting tomorrow at 2pm"
- "Add a daily reminder to take medication"

**View Tasks:**
- "Show me all my tasks"
- "List pending tasks"
- "Show tasks sorted by priority"

**Update Tasks:**
- "Mark task 5 as complete"
- "Update task 3 to high priority"
- "Change the due date for task 2 to Friday"

**Search & Filter:**
- "Find tasks about groceries"
- "Show me high priority tasks"
- "List tasks due this week"

**Recurring Tasks:**
- "Add a weekly meeting task every Monday"
- "Create a monthly reminder on the 1st"

## API Endpoints

### Chat Endpoint
```
POST /api/chat/{user_id}
```

Request:
```json
{
  "message": "Add a task to buy groceries",
  "conversation_id": 123
}
```

Response:
```json
{
  "conversation_id": 123,
  "message": "I've added 'Buy groceries' to your task list (task #5).",
  "created_at": "2025-12-21T10:00:00Z"
}
```

### Task Management
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create task
- `GET /api/tasks/{task_id}` - Get task details
- `PUT /api/tasks/{task_id}` - Update task
- `DELETE /api/tasks/{task_id}` - Delete task
- `PATCH /api/tasks/{task_id}/complete` - Mark complete

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

## Testing

### Backend Tests

```bash
cd backend

# Run all tests with coverage
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/integration/test_conversation_flows.py -v

# Run with type checking
mypy app

# Run linting
ruff check app
ruff format app
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run type checking
npm run type-check

# Run linting
npm run lint
```

## Project Structure

```
evolved-todo/
├── backend/
│   ├── app/
│   │   ├── agents/          # OpenAI agent configuration
│   │   ├── api/             # FastAPI routes
│   │   ├── core/            # Database, settings
│   │   ├── mcp/             # MCP tools (add_task, list_tasks, etc.)
│   │   ├── middleware/      # JWT auth, rate limiting
│   │   ├── models/          # SQLModel database models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   └── services/        # Business logic layer
│   ├── tests/
│   │   ├── integration/     # Conversation flow tests
│   │   └── unit/            # Unit tests
│   └── pyproject.toml       # Python dependencies
├── frontend/
│   ├── app/                 # Next.js App Router pages
│   ├── components/          # React components
│   │   ├── chat/            # ChatKit integration
│   │   └── tasks/           # Task management UI
│   ├── lib/                 # API client, utilities
│   └── package.json         # Node dependencies
├── specs/                   # Feature specifications
│   └── 003-phase3-ai-chatbot/
│       ├── spec.md          # Requirements
│       ├── plan.md          # Architecture
│       └── tasks.md         # Implementation tasks
└── README.md                # This file
```

## Architecture

### Stateless Chat Architecture

1. **Frontend**: User sends message via ChatKit interface
2. **FastAPI Endpoint**: Receives message, fetches conversation history from DB
3. **OpenAI Agent**: Processes message with conversation context
4. **MCP Tools**: Agent calls task management tools (add_task, list_tasks, etc.)
5. **Database**: All conversation state and tasks persisted to PostgreSQL
6. **Response**: Assistant message returned to frontend and saved to DB

### Key Design Principles

- **Stateless Server**: No in-memory conversation state - survives restarts
- **Database-First**: All state in PostgreSQL (conversations, messages, tasks)
- **User Isolation**: JWT authentication + user_id filtering on all queries
- **Type Safety**: Full TypeScript (frontend) and Python type hints (backend)
- **Test-Driven**: >90% test coverage with pytest and Jest

## Performance

- **Database Indexes**: Optimized queries on user_id, conversation_id, created_at
- **Connection Pooling**: 20 connection pool with 3600s recycle
- **Message Limit**: 50-message conversation history to prevent token overflow
- **Response Time**: <100ms for task operations, <2s for AI chat responses

## Security

- **JWT Authentication**: All endpoints require valid Bearer token
- **User Isolation**: Users can only access their own tasks/conversations
- **Input Validation**: Pydantic schemas enforce constraints on all inputs
- **SQL Injection Protection**: SQLModel ORM with parameterized queries
- **CORS Configuration**: Restricted origins for production deployment

## Contributing

This project follows **Spec-Driven Development (SDD)**:

1. All features start with a specification (`specs/*/spec.md`)
2. Architecture planned in `specs/*/plan.md`
3. Tasks broken down in `specs/*/tasks.md`
4. Implementation follows TDD (Test-Driven Development)
5. Quality gates: mypy, ruff, pytest, >90% coverage

See `AGENTS.md` for AI agent collaboration guidelines.

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Documentation: See `specs/` directory for detailed specifications

---

**Current Phase**: Phase 3 - AI Chatbot (Complete)
**Next Phase**: Phase 4+ - Advanced Features (Kafka, Kubernetes, Analytics)
