# Developer Quickstart: Phase 2 - Full-Stack Web Application

**Branch**: `002-phase2-web-app` | **Date**: 2025-12-10 | **Plan**: [plan.md](./plan.md)

---

## Prerequisites

### Required Software

**Operating System**: macOS, Linux, or Windows (with WSL2 recommended)

**Node.js**: v20+ (LTS)
```bash
node --version  # Should be >= 20.0.0
```

**Python**: 3.13+
```bash
python --version  # Should be >= 3.13.0
```

**UV** (Python Package Manager):
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# Verify
uv --version
```

**pnpm** (Frontend Package Manager):
```bash
npm install -g pnpm@latest

# Verify
pnpm --version
```

**Git**: Latest version
```bash
git --version
```

### Optional Tools

**PostgreSQL Client** (for manual database inspection):
```bash
# macOS
brew install postgresql@16

# Linux
sudo apt install postgresql-client

# Verify
psql --version
```

**Better Auth CLI** (optional):
```bash
pnpm add -g better-auth
```

---

## Project Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd evolved-todo
```

### 2. Checkout Phase 2 Branch

```bash
git checkout 002-phase2-web-app
```

### 3. Create Project Structure (If Not Exists)

```bash
mkdir -p frontend backend
```

---

## Backend Setup (FastAPI)

### 1. Navigate to Backend

```bash
cd backend
```

### 2. Install Dependencies with UV

```bash
# Initialize UV project (if not done)
uv init

# Install dependencies
uv sync

# This reads pyproject.toml and creates uv.lock
```

**Dependencies in `pyproject.toml`**:
```toml
[project]
name = "evolved-todo-backend"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "sqlmodel>=0.0.22",
    "asyncpg>=0.30.0",
    "alembic>=1.14.0",
    "pydantic>=2.9.0",
    "pydantic-settings>=2.6.0",
    "python-jose[cryptography]>=3.3.0",
    "python-multipart>=0.0.20",
    "email-validator>=2.2.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
    "httpx>=0.27.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0"
]

[tool.uv.scripts]
dev = "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
test = "pytest tests/ --cov=app --cov-report=term-missing"
migrate = "alembic upgrade head"
lint = "ruff check app/"
format = "ruff format app/"
typecheck = "mypy app/"
```

### 3. Configure Environment Variables

Create `.env` file in `backend/`:
```bash
# backend/.env

# Database
DATABASE_URL=postgresql+asyncpg://user:password@neon-host/evolved_todo?sslmode=require

# Better Auth Shared Secret (Must match frontend!)
BETTER_AUTH_SECRET=your-secret-key-min-32-chars-long

# JWT Configuration
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_DAYS=7

# CORS Origins (Frontend URL)
CORS_ORIGINS=["http://localhost:3000"]

# Environment
ENVIRONMENT=development
```

**Get Neon Database URL**:
1. Go to [Neon Console](https://console.neon.tech/)
2. Create new project: "evolved-todo"
3. Copy connection string
4. Replace `postgresql://` with `postgresql+asyncpg://`
5. Add `?sslmode=require` at the end

### 4. Initialize Database Migrations

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Edit alembic/env.py to use DATABASE_URL from .env
# (See data-model.md for Alembic configuration)

# Create initial migration
alembic revision --autogenerate -m "Initial schema: users and tasks"

# Review generated migration in alembic/versions/
# Edit if needed

# Apply migration
uv run alembic upgrade head
```

### 5. Run Development Server

```bash
# Using UV script
uv run dev

# Or directly
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Server starts at**: http://localhost:8000

**API Docs**: http://localhost:8000/docs (Swagger UI)

### 6. Verify Backend

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy"}
```

---

## Frontend Setup (Next.js)

### 1. Navigate to Frontend

```bash
cd ../frontend
```

### 2. Install Dependencies with pnpm

```bash
# Install all dependencies
pnpm install
```

**Dependencies in `package.json`**:
```json
{
  "name": "evolved-todo-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  },
  "dependencies": {
    "next": "^16.0.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "better-auth": "^1.1.0",
    "axios": "^1.7.0",
    "tailwindcss": "^3.4.0",
    "clsx": "^2.1.0",
    "date-fns": "^4.1.0"
  },
  "devDependencies": {
    "@types/node": "^22.0.0",
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "typescript": "^5.6.0",
    "eslint": "^9.0.0",
    "eslint-config-next": "^16.0.0",
    "jest": "^29.7.0",
    "@testing-library/react": "^16.0.0",
    "@testing-library/jest-dom": "^6.6.0",
    "@testing-library/user-event": "^14.5.0"
  }
}
```

### 3. Configure Environment Variables

Create `.env.local` file in `frontend/`:
```bash
# frontend/.env.local

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration
BETTER_AUTH_SECRET=your-secret-key-min-32-chars-long
BETTER_AUTH_URL=http://localhost:3000

# Database (Same as backend for Better Auth)
DATABASE_URL=postgresql://user:password@neon-host/evolved_todo?sslmode=require

# Environment
NODE_ENV=development
```

**IMPORTANT**: `BETTER_AUTH_SECRET` must match the backend `.env` file!

### 4. Initialize Better Auth

Create `lib/auth.ts`:
```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  database: {
    connectionString: process.env.DATABASE_URL!,
    type: "postgres"
  },
  secret: process.env.BETTER_AUTH_SECRET!,
  jwt: {
    expiresIn: "7d"
  },
  socialProviders: {
    // Add if using OAuth providers
  }
})

export type Session = typeof auth.$Infer.Session
```

Create auth API route `app/api/auth/[...all]/route.ts`:
```typescript
// app/api/auth/[...all]/route.ts
import { auth } from "@/lib/auth"

export const { GET, POST } = auth.handler()
```

### 5. Run Development Server

```bash
# Start Next.js dev server
pnpm dev
```

**Server starts at**: http://localhost:3000

### 6. Verify Frontend

Open browser:
- http://localhost:3000 → Should see login/register page
- http://localhost:3000/api/auth → Better Auth routes active

---

## Running Full Stack

### Option 1: Separate Terminals

**Terminal 1 (Backend)**:
```bash
cd backend
uv run dev
```

**Terminal 2 (Frontend)**:
```bash
cd frontend
pnpm dev
```

### Option 2: Using tmux/screen (Linux/macOS)

```bash
# Start tmux
tmux

# Split window horizontally
Ctrl+b "

# In top pane (Backend)
cd backend && uv run dev

# Switch to bottom pane
Ctrl+b ↓

# In bottom pane (Frontend)
cd frontend && pnpm dev
```

### Option 3: Using Docker Compose (Optional)

Create `docker-compose.yml` in project root:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    env_file:
      - ./frontend/.env.local
    volumes:
      - ./frontend:/app
    command: pnpm dev
```

```bash
docker-compose up
```

---

## Database Management

### View Database (psql)

```bash
# Connect to Neon database
psql "postgresql://user:password@neon-host/evolved_todo?sslmode=require"

# List tables
\dt

# View users table
SELECT * FROM users;

# View tasks table
SELECT * FROM tasks WHERE user_id = 1;

# Exit
\q
```

### Create Database Migration

```bash
cd backend

# After modifying SQLModel models
alembic revision --autogenerate -m "Add new field to tasks"

# Review generated migration
code alembic/versions/<timestamp>_add_new_field.py

# Apply migration
uv run alembic upgrade head

# Rollback (if needed)
uv run alembic downgrade -1
```

### Seed Test Data (Optional)

Create `backend/scripts/seed.py`:
```python
import asyncio
from app.core.database import async_session_maker
from app.models import User, Task

async def seed_data():
    async with async_session_maker() as session:
        # Create test user
        user = User(email="test@example.com", password_hash="hashed", name="Test User")
        session.add(user)
        await session.commit()

        # Create test tasks
        tasks = [
            Task(user_id=user.id, title="Sample task 1", completed=False),
            Task(user_id=user.id, title="Sample task 2", completed=True, priority="high"),
        ]
        session.add_all(tasks)
        await session.commit()

        print(f"Seeded user {user.id} with {len(tasks)} tasks")

if __name__ == "__main__":
    asyncio.run(seed_data())
```

```bash
uv run python scripts/seed.py
```

---

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
uv run test

# Run with coverage
uv run pytest tests/ --cov=app --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/test_task_service.py -v

# Run with specific marker
uv run pytest tests/ -m "unit"
```

### Frontend Tests

```bash
cd frontend

# Run all tests
pnpm test

# Run in watch mode
pnpm test:watch

# Run with coverage
pnpm test:coverage
```

---

## Code Quality

### Backend (Python)

```bash
cd backend

# Lint
uv run ruff check app/

# Format
uv run ruff format app/

# Type check
uv run mypy app/

# All quality checks
uv run ruff check app/ && uv run mypy app/ && uv run pytest tests/ --cov=app
```

### Frontend (TypeScript)

```bash
cd frontend

# Lint
pnpm lint

# Type check
pnpm tsc --noEmit

# Format (if Prettier configured)
pnpm format
```

---

## Troubleshooting

### "Connection refused" on backend

**Issue**: Frontend can't reach backend API

**Solution**:
1. Ensure backend is running: `curl http://localhost:8000/health`
2. Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
3. Verify CORS origins in `backend/.env`

### "Invalid JWT token"

**Issue**: Frontend auth token not accepted by backend

**Solution**:
1. Verify `BETTER_AUTH_SECRET` matches in both `.env` files
2. Check JWT algorithm is HS256 in both frontend and backend
3. Clear browser cookies and re-login

### "Database connection failed"

**Issue**: Can't connect to Neon PostgreSQL

**Solution**:
1. Verify `DATABASE_URL` in `.env` files
2. Check Neon project is active (not paused)
3. Ensure connection string ends with `?sslmode=require`
4. Test connection: `psql "postgresql://..."`

### "Module not found" errors

**Backend**:
```bash
cd backend
rm -rf .venv
uv sync
```

**Frontend**:
```bash
cd frontend
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

### Alembic "target database is not up to date"

**Solution**:
```bash
cd backend
uv run alembic current    # Check current version
uv run alembic history    # View migration history
uv run alembic upgrade head   # Apply pending migrations
```

---

## Next Steps

1. ✅ Development environment set up
2. → Create your first user via UI
3. → Create tasks and test all features
4. → Run tests to verify functionality
5. → Review [plan.md](./plan.md) for implementation phases
6. → Start implementing features from [tasks.md](./tasks.md)

## Useful Commands Quick Reference

```bash
# Backend
cd backend
uv run dev                 # Start backend server
uv run test                # Run tests
uv run alembic upgrade head  # Apply migrations
uv run ruff check app/     # Lint code

# Frontend
cd frontend
pnpm dev                   # Start frontend server
pnpm test                  # Run tests
pnpm lint                  # Lint code
pnpm build                 # Build for production

# Database
psql "postgresql://..."    # Connect to database
alembic revision --autogenerate -m "message"  # Create migration
alembic upgrade head       # Apply migrations
```

---

**Happy coding! 🚀**
