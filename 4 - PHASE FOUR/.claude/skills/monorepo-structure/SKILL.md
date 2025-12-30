---
name: monorepo-structure
description: Monorepo development patterns with independent frontend/ and backend/ directories, shared configurations, and coordinated builds.
---

# Monorepo Structure

## Instructions

### When to Use

- Setting up monorepo project structure
- Managing independent frontend and backend builds
- Configuring shared environment variables
- Coordinating development workflows
- Managing cross-package dependencies
- Setting up Git workflows for monorepos

## What is a Monorepo?

A monorepo is a single repository containing multiple projects (frontend + backend). Benefits:
- **Single Source of Truth** - All code in one place
- **Atomic Changes** - Change frontend and backend together
- **Simplified Dependency Management** - Shared configurations and tools
- **Easier Code Review** - See full picture of changes
- **Consistent Versioning** - Tag releases across entire stack

## Project Structure

```
evolved-todo/                    # Root directory
├── .git/                        # Single git repository
├── .gitignore                   # Shared git ignore
├── README.md                    # Project documentation
│
├── frontend/                    # Next.js application
│   ├── app/                     # Next.js App Router
│   ├── components/              # React components
│   ├── lib/                     # Utilities and helpers
│   ├── public/                  # Static assets
│   ├── .env.local               # Frontend environment variables
│   ├── package.json             # Frontend dependencies (pnpm)
│   ├── tsconfig.json            # TypeScript config
│   ├── next.config.js           # Next.js config
│   └── tailwind.config.js       # Tailwind CSS config
│
├── backend/                     # FastAPI application
│   ├── app/                     # Application code
│   │   ├── api/                 # API routes
│   │   ├── models/              # Database models
│   │   ├── services/            # Business logic
│   │   ├── schemas/             # Pydantic schemas
│   │   └── main.py              # FastAPI app entry
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # Backend tests
│   ├── .env                     # Backend environment variables
│   ├── pyproject.toml           # Backend dependencies (UV)
│   └── alembic.ini              # Alembic config
│
├── .specify/                    # Spec-Driven Development templates
│   ├── memory/                  # Project constitution
│   ├── scripts/                 # Helper scripts
│   └── templates/               # Document templates
│
├── specs/                       # Feature specifications
│   └── 002-phase2-web-app/      # Current feature specs
│
├── history/                     # Project history
│   ├── adr/                     # Architecture Decision Records
│   └── prompts/                 # Prompt History Records
│
└── .claude/                     # Claude Code configuration
    ├── agents/                  # Subagent definitions
    └── skills/                  # Skill definitions
```

## Independent Package Management

### Frontend (pnpm)

```json
// frontend/package.json
{
  "name": "evolved-todo-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "^16.0.0",
    "react": "^18.0.0",
    "better-auth": "^1.0.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "tailwindcss": "^3.4.0",
    "@types/react": "^18.0.0"
  }
}
```

```bash
# Install frontend dependencies
cd frontend
pnpm install

# Run frontend development server
pnpm dev

# Build frontend for production
pnpm build
```

### Backend (UV)

```toml
# backend/pyproject.toml
[project]
name = "evolved-todo-backend"
version = "1.0.0"
description = "FastAPI backend for Evolved Todo"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.109.0",
    "sqlmodel>=0.0.14",
    "asyncpg>=0.29.0",
    "alembic>=1.13.0",
    "pyjwt[crypto]>=2.8.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "httpx>=0.25.0",
    "mypy>=1.8.0",
    "ruff>=0.1.0",
]

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.mypy]
python_version = "3.13"
strict = true
```

```bash
# Install backend dependencies
cd backend
uv sync

# Run backend development server
uv run uvicorn app.main:app --reload

# Run backend tests
uv run pytest
```

## Environment Variables

### Shared Configuration Pattern

```bash
# Root .env (not committed - for local development only)
# Shared across frontend and backend

# Database
DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/evolved_todo"

# Authentication
BETTER_AUTH_SECRET="your-secret-key-minimum-32-characters-long"

# API Configuration
API_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"
```

### Frontend Environment Variables

```bash
# frontend/.env.local (not committed)
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=postgresql://user:pass@localhost:5432/evolved_todo
```

### Backend Environment Variables

```bash
# backend/.env (not committed)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/evolved_todo
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long
CORS_ORIGINS=http://localhost:3000
```

### Environment Variable Template

```bash
# .env.example (committed - template for developers)
# Copy this to .env and fill in the values

# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# Authentication (must match between frontend and backend)
BETTER_AUTH_SECRET=generate-a-random-32-character-string

# API Configuration
API_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# Neon PostgreSQL (production)
# DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.neon.tech/dbname?ssl=require
```

## Development Workflow

### Running Both Services

```bash
# Terminal 1: Backend
cd backend
uv run uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
pnpm dev
```

### Using Concurrently (Optional)

```json
// Root package.json
{
  "name": "evolved-todo",
  "private": true,
  "scripts": {
    "dev": "concurrently \"npm:dev:backend\" \"npm:dev:frontend\"",
    "dev:backend": "cd backend && uv run uvicorn app.main:app --reload",
    "dev:frontend": "cd frontend && pnpm dev",
    "build": "npm run build:backend && npm run build:frontend",
    "build:backend": "cd backend && uv sync",
    "build:frontend": "cd frontend && pnpm build"
  },
  "devDependencies": {
    "concurrently": "^8.2.0"
  }
}
```

```bash
# Run both services with one command
pnpm dev
```

## Git Workflow

### Single Repository

```bash
# All changes in one commit
git add frontend/ backend/
git commit -m "feat: implement task creation (frontend + backend)"
```

### Separate Commits (When Appropriate)

```bash
# Backend changes
git add backend/
git commit -m "feat(backend): add task creation endpoint"

# Frontend changes
git add frontend/
git commit -m "feat(frontend): add task creation form"
```

### .gitignore

```gitignore
# Root .gitignore

# Environment variables
.env
.env.local
.env.production

# Frontend
frontend/node_modules/
frontend/.next/
frontend/out/

# Backend
backend/.venv/
backend/__pycache__/
backend/*.pyc
backend/.pytest_cache/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```

## Build Process

### Frontend Build

```bash
cd frontend

# Development build
pnpm dev

# Production build
pnpm build

# Start production server
pnpm start
```

### Backend Build

```bash
cd backend

# Install dependencies
uv sync

# Run migrations
uv run alembic upgrade head

# Start production server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Deployment

### Vercel (Frontend)

```bash
# Deploy frontend to Vercel
cd frontend
vercel deploy --prod
```

### Railway/Render (Backend)

```bash
# Deploy backend to Railway
cd backend

# Railway auto-detects Python and runs:
# uv sync
# alembic upgrade head
# uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Docker (Full Stack)

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install
COPY . .
RUN pnpm build
CMD ["pnpm", "start"]
```

```dockerfile
# backend/Dockerfile
FROM python:3.13-slim
WORKDIR /app
RUN pip install uv
COPY pyproject.toml ./
RUN uv sync
COPY . .
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml (root)
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
    depends_on:
      - backend

  db:
    image: postgres:16
    environment:
      - POSTGRES_DB=evolved_todo
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## No Orchestration Tool

This monorepo does NOT use:
- ❌ Turborepo
- ❌ Nx
- ❌ Lerna
- ❌ Rush

**Rationale:**
- Simple project with only 2 packages (frontend + backend)
- Different languages (TypeScript + Python)
- Independent build processes
- No shared code between packages
- Adding orchestration tool is overkill

## Integration with monorepo-coordinator Subagent

This skill is primarily used by:
- **monorepo-coordinator** - For managing monorepo structure
- **backend-api-dev** - For backend development in monorepo
- **frontend-react-dev** - For frontend development in monorepo

### Key Principles

1. **Independent Packages** - frontend/ and backend/ are fully independent
2. **Shared Environment** - Single .env for local development
3. **Single Git Repository** - All code in one repo
4. **Independent Builds** - Each package builds independently
5. **No Orchestration Tool** - Simple enough without Turborepo/Nx
6. **Coordinated Deployment** - Deploy frontend and backend together
