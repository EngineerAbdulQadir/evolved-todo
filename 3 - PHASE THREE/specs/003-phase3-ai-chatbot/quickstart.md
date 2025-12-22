# Quickstart Guide: AI-Powered Todo Chatbot (Phase 3)

**Feature**: AI-Powered Todo Chatbot
**Date**: 2025-12-17
**Source**: [spec.md](./spec.md) | [plan.md](./plan.md)

## Overview

This guide provides step-by-step instructions to set up and run the Phase 3 AI-powered todo chatbot locally.

**What You'll Build**:
- ✅ Backend with FastAPI + OpenAI Agents SDK + MCP Server
- ✅ Frontend with Next.js + OpenAI ChatKit
- ✅ Database with Neon Serverless PostgreSQL
- ✅ Authentication with Better Auth JWT
- ✅ All 10 todo features via natural language

**Time to Complete**: ~30 minutes

---

## Prerequisites

### Required Software

1. **Python 3.13+**: Check with `python --version` or `python3 --version`
2. **UV Package Manager**: Install from https://github.com/astral-sh/uv
3. **Node.js 20+**: Check with `node --version`
4. **npm 10+**: Check with `npm --version`
5. **Git**: Check with `git --version`

### Required Accounts & Keys

1. **OpenAI API Key**: Get from https://platform.openai.com/api-keys
   - Required for OpenAI Agents SDK
   - Billing enabled (pay-as-you-go for API usage)

2. **Neon Database**: Get from https://neon.tech
   - Free tier sufficient for Phase 3
   - Copy connection string (looks like `postgresql://user:pass@host/db`)

3. **Better Auth Secret**: Generate with `openssl rand -hex 32`
   - Shared secret between frontend and backend for JWT signing

---

## Project Structure

```
evolved-todo/
├── backend/           # Python FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI entry point
│   │   ├── models.py          # SQLModel database models
│   │   ├── db.py              # Database connection
│   │   ├── auth.py            # JWT authentication
│   │   ├── routes/
│   │   │   ├── tasks.py       # Task CRUD endpoints (Phase 2)
│   │   │   └── chat.py        # Chat endpoint (Phase 3)
│   │   ├── mcp/               # MCP server and tools
│   │   │   ├── server.py
│   │   │   └── tools/         # 6 MCP tools
│   │   └── agents/            # OpenAI Agents SDK
│   │       ├── todo_agent.py
│   │       └── prompts.py
│   ├── tests/                 # Backend tests
│   ├── pyproject.toml         # UV dependencies
│   └── .env                   # Environment variables
├── frontend/          # Next.js 16+ frontend
│   ├── app/
│   │   ├── (auth)/            # Login, signup
│   │   └── (app)/
│   │       └── chat/          # ChatKit interface
│   ├── components/
│   │   └── chat/              # Chat components
│   ├── lib/
│   │   ├── api-client.ts      # API client
│   │   └── auth.ts            # Better Auth config
│   ├── package.json
│   └── .env.local             # Environment variables
└── specs/             # Feature specifications
```

---

## Backend Setup

### Step 1: Clone Repository & Navigate to Backend

```bash
cd evolved-todo/backend
```

### Step 2: Create Environment File

Create `backend/.env`:

```bash
# OpenAI API Key (required)
OPENAI_API_KEY=sk-proj-...

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:password@host/evolved_todo

# Better Auth (shared secret with frontend)
BETTER_AUTH_SECRET=your-32-character-hex-secret

# Application
APP_ENV=development
LOG_LEVEL=info
```

**Get Values**:
- `OPENAI_API_KEY`: https://platform.openai.com/api-keys
- `DATABASE_URL`: Neon dashboard → Connection String
- `BETTER_AUTH_SECRET`: Run `openssl rand -hex 32`

### Step 3: Install Dependencies

```bash
# Install UV package manager (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install backend dependencies
uv sync
```

**Dependencies Installed**:
- fastapi
- sqlmodel
- openai-agents-sdk
- mcp (Official MCP SDK)
- uvicorn (ASGI server)
- pydantic
- python-jose (JWT)
- pytest, pytest-cov (testing)

### Step 4: Initialize Database

```bash
# Create tables (SQLModel automatic creation)
uv run python -m app.db
```

**Tables Created**:
- `users` (Better Auth)
- `tasks` (Phase 2, existing)
- `conversations` (Phase 3, NEW)
- `messages` (Phase 3, NEW)

### Step 5: Run Backend

```bash
# Run with hot reload
uv run uvicorn app.main:app --reload --port 8000

# Or run with UV directly
uv run fastapi dev app/main.py --port 8000
```

**Backend Running**: http://localhost:8000

**API Docs**: http://localhost:8000/docs (FastAPI auto-generated Swagger UI)

### Step 6: Verify Backend

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status": "ok", "database": "connected"}
```

---

## Frontend Setup

### Step 1: Navigate to Frontend

```bash
cd evolved-todo/frontend
```

### Step 2: Create Environment File

Create `frontend/.env.local`:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth (shared secret with backend)
BETTER_AUTH_SECRET=your-32-character-hex-secret

# Better Auth URL (for authentication)
BETTER_AUTH_URL=http://localhost:3000
```

**Important**: `BETTER_AUTH_SECRET` must match backend!

### Step 3: Install Dependencies

```bash
npm install
```

**Dependencies Installed**:
- next (16+)
- react, react-dom
- @openai/chatkit (conversational UI)
- typescript
- tailwindcss
- better-auth (authentication)

### Step 4: Run Frontend

```bash
npm run dev
```

**Frontend Running**: http://localhost:3000

### Step 5: Verify Frontend

1. Open http://localhost:3000
2. You should see login/signup page (Better Auth)
3. Create account → Login → Chat interface

---

## Testing the Chatbot

### Step 1: Create Account

1. Navigate to http://localhost:3000
2. Click "Sign Up"
3. Enter email and password
4. Create account

### Step 2: Start Chatting

**Try These Commands**:

1. **Add Task**:
   ```
   Add a task to buy groceries
   ```
   Expected: "I've added 'Buy groceries' to your task list. Task ID is 1."

2. **Add High Priority Task**:
   ```
   Create a high priority task to call dentist tomorrow at 2pm
   ```
   Expected: Task created with priority="high", due_date=tomorrow, due_time=14:00

3. **View Tasks**:
   ```
   Show me my tasks
   ```
   Expected: List of all tasks

4. **Complete Task**:
   ```
   Mark task 1 as done
   ```
   Expected: "Task 1 'Buy groceries' is now complete!"

5. **Search Tasks**:
   ```
   Find tasks about dentist
   ```
   Expected: List of tasks with "dentist" in title/description

6. **Update Task**:
   ```
   Change task 2 priority to high
   ```
   Expected: "Updated task 2 priority to 'high'."

7. **Delete Task**:
   ```
   Delete task 1
   ```
   Expected: "Task 1 'Buy groceries' has been deleted."

8. **Recurring Task**:
   ```
   Add a weekly meeting task every Monday at 10am
   ```
   Expected: Task created with recurrence="weekly", recurrence_day=1

---

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_mcp_tools.py

# Run integration tests only
uv run pytest tests/integration/
```

**Test Coverage Target**: >90%

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test
npm test -- ChatInterface
```

---

## Development Workflow

### Making Changes

1. **Create Feature Branch**:
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make Changes** (following TDD):
   - Write failing test
   - Implement feature
   - Refactor
   - Commit

3. **Run Quality Gates**:
   ```bash
   # Backend
   cd backend
   uv run mypy app/              # Type checking
   uv run ruff check app/        # Linting
   uv run ruff format app/       # Formatting
   uv run pytest                 # Tests

   # Frontend
   cd frontend
   npm run type-check            # TypeScript
   npm run lint                  # ESLint
   npm run format                # Prettier
   npm test                      # Tests
   ```

4. **Commit & Push**:
   ```bash
   git add .
   git commit -m "feat: add new feature"
   git push origin feature/my-feature
   ```

---

## Troubleshooting

### Backend Issues

**Issue**: "Module 'openai_agents' not found"
**Solution**: Run `uv sync` to install dependencies

**Issue**: "Database connection failed"
**Solution**: Check `DATABASE_URL` in `.env`, verify Neon database is running

**Issue**: "OpenAI API error 401"
**Solution**: Check `OPENAI_API_KEY` in `.env`, verify key is valid

**Issue**: "JWT token invalid"
**Solution**: Check `BETTER_AUTH_SECRET` matches frontend

### Frontend Issues

**Issue**: "Module not found '@openai/chatkit'"
**Solution**: Run `npm install` to install dependencies

**Issue**: "API request failed (CORS error)"
**Solution**: Ensure backend is running on port 8000, check `NEXT_PUBLIC_API_URL`

**Issue**: "Authentication error"
**Solution**: Check `BETTER_AUTH_SECRET` matches backend

### General Issues

**Issue**: Port 8000 or 3000 already in use
**Solution**: Kill process or use different port:
```bash
# Backend on different port
uv run uvicorn app.main:app --reload --port 8001

# Frontend on different port
npm run dev -- -p 3001
```

---

## Production Deployment

### Backend Deployment

**Recommended Platforms**:
- Railway (easiest)
- Render
- Fly.io
- Any platform supporting Python + FastAPI

**Steps**:
1. Set environment variables (OPENAI_API_KEY, DATABASE_URL, BETTER_AUTH_SECRET)
2. Deploy from GitHub repository
3. Run database migrations (SQLModel auto-creates tables on first run)

### Frontend Deployment

**Recommended Platform**: Vercel (easiest for Next.js)

**Steps**:
1. Connect GitHub repository to Vercel
2. Set environment variables:
   - `NEXT_PUBLIC_API_URL` (backend URL)
   - `BETTER_AUTH_SECRET` (same as backend)
   - `BETTER_AUTH_URL` (frontend URL)
3. Deploy

---

## Environment Variables Reference

### Backend (.env)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | Yes | OpenAI API key | `sk-proj-abc123...` |
| `DATABASE_URL` | Yes | Neon PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `BETTER_AUTH_SECRET` | Yes | JWT signing secret (32 char hex) | `a1b2c3d4e5f6...` |
| `APP_ENV` | No | Environment (development/production) | `development` |
| `LOG_LEVEL` | No | Logging level | `info` |

### Frontend (.env.local)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL | `http://localhost:8000` |
| `BETTER_AUTH_SECRET` | Yes | JWT signing secret (same as backend) | `a1b2c3d4e5f6...` |
| `BETTER_AUTH_URL` | Yes | Frontend URL (for auth callbacks) | `http://localhost:3000` |

---

## Next Steps

1. ✅ **Run Tests**: Ensure all tests pass (`pytest` and `npm test`)
2. ✅ **Test All Features**: Verify all 10 features work via natural language
3. ✅ **Review Constitution**: Ensure compliance with Phase 3 constitution (v3.0.0)
4. ✅ **Create Demo Video**: Record <90 second demo of chatbot in action
5. ✅ **Deploy to Production**: Deploy backend and frontend to hosting platforms
6. ✅ **Submit for Hackathon**: Follow submission guidelines

---

## Additional Resources

- **Phase 3 Specification**: [spec.md](./spec.md)
- **Implementation Plan**: [plan.md](./plan.md)
- **Data Models**: [data-model.md](./data-model.md)
- **API Contracts**: [contracts/](./contracts/)
- **Constitution**: [.specify/memory/constitution.md](../.specify/memory/constitution.md)
- **OpenAI Agents SDK**: https://github.com/openai/openai-agents-sdk
- **MCP SDK**: https://github.com/modelcontextprotocol/python-sdk
- **OpenAI ChatKit**: https://platform.openai.com/docs/guides/chatkit
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Next.js Docs**: https://nextjs.org/docs

---

## Support

**Issues**: Report bugs or ask questions at project repository

**Community**: Join Discord/Slack channel for real-time support

---

**Status**: ✅ Quickstart Guide Complete
**Date**: 2025-12-17
**Ready to Start Development**: Follow these steps to get Phase 3 running locally!
