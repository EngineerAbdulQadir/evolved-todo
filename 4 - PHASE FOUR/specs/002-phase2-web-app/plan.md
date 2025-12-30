# Implementation Plan: Phase 2 - Full-Stack Web Application

**Branch**: `002-phase2-web-app` | **Date**: 2025-12-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specifications from all 11 feature specs in `002-phase2-web-app/`

## Summary

Transform the Phase 1 CLI todo application into a production-ready full-stack web application with database persistence and multi-user support. Maintain all 10 features from Phase 1 (Basic 1-5, Intermediate 6-8, Advanced 9-10) and add JWT authentication for multi-user isolation.

**Technical Approach:**
- **Frontend:** Next.js 16+ App Router with TypeScript and Tailwind CSS
- **Backend:** FastAPI with SQLModel ORM connected to Neon PostgreSQL
- **Authentication:** Better Auth JWT with 7-day token expiration
- **Architecture:** Monorepo with isolated frontend/ and backend/ directories
- **API Design:** RESTful endpoints with proper HTTP status codes
- **Testing:** TDD approach with pytest (backend) and Jest (frontend)

## Technical Context

**Language/Version**:
- Frontend: TypeScript (strict mode) with Next.js 16+
- Backend: Python 3.13+ with FastAPI

**Primary Dependencies**:
- Frontend: Next.js 16+, React 18+, Tailwind CSS 3.x, Better Auth, Axios
- Backend: FastAPI, SQLModel, asyncpg, uvicorn, pydantic v2
- Database Driver: asyncpg (PostgreSQL async driver)
- Package Managers: npm/pnpm (frontend), UV (backend)

**Storage**:
- Neon Serverless PostgreSQL (managed cloud database)
- Tables: users (Better Auth), tasks (with user_id foreign key)
- Connection pooling via asyncpg

**Testing**:
- Backend: pytest, pytest-cov, pytest-asyncio, httpx (API testing)
- Frontend: Jest, React Testing Library, @testing-library/user-event
- Coverage Goals: >90% backend, >80% frontend
- Test Types: Unit, Integration, E2E (frontend), Contract (API)

**Target Platform**:
- Frontend: Modern browsers (Chrome/Firefox/Safari latest 2 versions)
- Backend: Linux/Unix server (Python 3.13+ compatible)
- Database: Neon Serverless PostgreSQL (cloud-hosted)
- Deployment: Vercel (frontend), Python platform (backend)

**Project Type**: Web application (monorepo with frontend + backend)

**Performance Goals**:
- API Response Time: <500ms p95 for task operations
- Dashboard Load Time: <2 seconds for 100 tasks
- Database Query Time: <100ms for typical CRUD operations
- Frontend Bundle Size: <500KB initial load
- Concurrent Users: Support 1,000 concurrent users without degradation

**Constraints**:
- JWT token size: <4KB to fit in HTTP headers
- Database connections: Max 100 concurrent connections (Neon limit consideration)
- Authentication: 7-day JWT expiration (no refresh tokens in Phase 2)
- Single session per user (no multi-device session management)
- No real-time updates (WebSocket/SSE) in Phase 2

**Scale/Scope**:
- Users: 1,000-10,000 registered users
- Tasks per User: Up to 1,000 tasks
- Total Database Size: <10GB
- API Endpoints: 6 core REST endpoints + 1 auth endpoint
- Frontend Pages: 4-5 main pages (dashboard, login, register, task detail, settings)
- UI Components: 20-30 reusable React components

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Principle I: Spec-First Development
- **Status**: PASS
- **Evidence**: All 11 feature specifications created and validated before planning
- **Files**: `001-authentication/` through `011-due-dates-reminders-web/spec.md`

### ✅ Principle II: Test-First (TDD)
- **Status**: PASS (to be enforced during implementation)
- **Plan**: pytest for backend, Jest for frontend, written before implementation code
- **Coverage Targets**: >90% backend, >80% frontend

### ✅ Principle III: YAGNI Principle
- **Status**: PASS
- **Scope**: All 10 features from Phase 1 maintained, no additional features
- **Features**: Authentication + 10 task management features

### ✅ Principle IV: Technology Stack Requirements
- **Status**: PASS
- **Frontend**: Next.js 16+, TypeScript (strict), Tailwind CSS, Better Auth ✓
- **Backend**: Python 3.13+, FastAPI, SQLModel, Neon PostgreSQL, UV ✓
- **Testing**: pytest + Jest ✓

### ✅ Principle V: Clean Code & Modularity
- **Status**: PASS
- **Structure**: Monorepo with `frontend/` and `backend/` separation
- **Organization**: Clear layer separation (models, services, API, UI components)

### ✅ Principle VI: Type Safety
- **Status**: PASS
- **Backend**: mypy strict mode with comprehensive type annotations
- **Frontend**: TypeScript strict mode with proper type definitions

### ✅ Principle VII: Comprehensive Documentation
- **Status**: PASS (to be completed)
- **Planned**: API documentation (OpenAPI), README, quickstart, docstrings

### ✅ Principle VIII: Error Handling
- **Status**: PASS (to be implemented)
- **Plan**: HTTP status codes, error response schemas, user-friendly messages

### ✅ Principle IX: Multi-User Data Isolation & Security
- **Status**: PASS
- **Design**: JWT authentication, user_id filtering on all queries
- **Security**: Shared BETTER_AUTH_SECRET, 401/403 responses

### ✅ Principle X: Database Schema & Migration Management
- **Status**: PASS
- **Plan**: SQLModel models, Alembic migrations, Neon PostgreSQL

### ✅ Principle XI: API Design & RESTful Conventions
- **Status**: PASS
- **Endpoints**: Standard REST with proper HTTP verbs and status codes
- **Design**: `/api/{user_id}/tasks` pattern with JWT validation

**Constitution Compliance**: ✅ ALL GATES PASSED - Proceed to Phase 0 Research

## Project Structure

### Documentation (this feature)

```text
specs/002-phase2-web-app/
├── plan.md                      # This file (/sp.plan command output)
├── research.md                  # Phase 0 output (/sp.plan command) - PENDING
├── data-model.md                # Phase 1 output (/sp.plan command) - PENDING
├── quickstart.md                # Phase 1 output (/sp.plan command) - PENDING
├── contracts/                   # Phase 1 output (/sp.plan command) - PENDING
│   ├── api-endpoints.md         # REST API specifications
│   ├── authentication.md        # Auth flow documentation
│   ├── request-schemas.json     # OpenAPI request schemas
│   └── response-schemas.json    # OpenAPI response schemas
├── spec.md                      # Main Phase 2 specification (COMPLETED)
├── checklists/
│   └── requirements.md          # Spec validation checklist (COMPLETED)
└── [001-011 feature specs]/     # Individual feature specifications (COMPLETED)
    ├── spec.md
    └── checklists/requirements.md
```

### Source Code (repository root)

```text
evolved-todo/
├── frontend/
│   ├── app/                     # Next.js 16+ App Router
│   │   ├── (auth)/              # Auth route group
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── register/
│   │   │       └── page.tsx
│   │   ├── (dashboard)/         # Dashboard route group (protected)
│   │   │   ├── layout.tsx       # Auth middleware
│   │   │   ├── page.tsx         # Main dashboard
│   │   │   └── tasks/
│   │   │       └── [id]/
│   │   │           └── page.tsx # Task detail view
│   │   ├── layout.tsx           # Root layout
│   │   ├── globals.css          # Tailwind imports
│   │   └── api/                 # API routes (Better Auth)
│   │       └── auth/
│   │           └── [...all]/route.ts
│   ├── components/              # React components
│   │   ├── ui/                  # Base UI components (buttons, inputs, etc.)
│   │   ├── auth/                # Auth-specific components (LoginForm, RegisterForm)
│   │   ├── tasks/               # Task-related components
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskItem.tsx
│   │   │   ├── TaskForm.tsx
│   │   │   ├── TaskFilters.tsx
│   │   │   └── TaskDetail.tsx
│   │   ├── layout/              # Layout components (Header, Footer, Sidebar)
│   │   └── common/              # Shared components (Loading, Error, EmptyState)
│   ├── lib/                     # Utility functions and API client
│   │   ├── api/                 # API client (axios instance with JWT interceptor)
│   │   │   ├── client.ts
│   │   │   ├── tasks.ts         # Task API functions
│   │   │   └── auth.ts          # Auth API functions
│   │   ├── utils/               # Helper functions (date formatting, validation)
│   │   └── auth.ts              # Better Auth configuration
│   ├── types/                   # TypeScript type definitions
│   │   ├── task.ts              # Task entity types
│   │   ├── user.ts              # User entity types
│   │   └── api.ts               # API response types
│   ├── hooks/                   # Custom React hooks
│   │   ├── useTasks.ts          # Task management hook
│   │   ├── useAuth.ts           # Authentication hook
│   │   └── useFilters.ts        # Filter/sort/search hook
│   ├── __tests__/               # Frontend tests
│   │   ├── components/          # Component tests
│   │   ├── lib/                 # Utility function tests
│   │   └── integration/         # E2E tests
│   ├── public/                  # Static assets
│   ├── .env.local               # Environment variables (BETTER_AUTH_SECRET, API_URL)
│   ├── package.json
│   ├── tsconfig.json            # TypeScript configuration (strict mode)
│   ├── tailwind.config.js
│   ├── next.config.js
│   └── jest.config.js
│
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── models/              # SQLModel database models
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # User model (Better Auth integration)
│   │   │   └── task.py          # Task model (all fields from specs)
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── task.py          # Task DTOs
│   │   │   └── auth.py          # Auth DTOs
│   │   ├── services/            # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── task_service.py  # Task CRUD operations
│   │   │   ├── auth_service.py  # JWT validation
│   │   │   └── recurrence_service.py # Recurring task logic
│   │   ├── api/                 # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── tasks.py         # Task endpoints
│   │   │   └── health.py        # Health check endpoint
│   │   ├── core/                # Core configuration
│   │   │   ├── config.py        # Settings (Pydantic BaseSettings)
│   │   │   ├── database.py      # Database connection (asyncpg)
│   │   │   └── security.py      # JWT utilities
│   │   └── middleware/          # FastAPI middleware
│   │       ├── auth.py          # JWT authentication middleware
│   │       └── cors.py          # CORS configuration
│   ├── tests/                   # Backend tests
│   │   ├── __init__.py
│   │   ├── conftest.py          # pytest fixtures
│   │   ├── unit/                # Unit tests
│   │   │   ├── test_models.py
│   │   │   ├── test_services.py
│   │   │   └── test_security.py
│   │   └── integration/         # Integration tests
│   │       ├── test_api_tasks.py
│   │       └── test_api_auth.py
│   ├── alembic/                 # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   ├── .env                     # Environment variables (DATABASE_URL, BETTER_AUTH_SECRET)
│   ├── pyproject.toml           # UV dependencies
│   ├── alembic.ini              # Alembic configuration
│   └── pytest.ini               # pytest configuration
│
├── .gitignore
├── README.md
├── docker-compose.yml           # Optional: local dev environment
└── .github/
    └── workflows/
        └── ci.yml               # CI/CD pipeline (tests, lint, type-check)
```

**Structure Decision**:
We selected **Option 2: Web application** structure with clear frontend/backend separation. This monorepo approach provides:
- Independent deployment capabilities
- Clear separation of concerns
- Shared type definitions via OpenAPI schemas
- Independent testing strategies for each layer
- Simplified CI/CD pipeline configuration

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. All constitutional requirements are met by the planned architecture.

## Phase 0: Research (NEXT STEP)

**Output**: `research.md`

**Research Tasks:**
1. Next.js 16+ App Router patterns (routing, layouts, server components)
2. FastAPI + SQLModel best practices (async patterns, dependency injection)
3. Better Auth JWT implementation (frontend + backend integration)
4. Neon PostgreSQL connection management (connection pooling, SSL)
5. API authentication patterns (JWT in headers, token refresh alternatives)
6. Testing strategies (pytest fixtures, Jest mocking, E2E with Playwright)
7. Monorepo tooling (workspace management, shared types)
8. Database migration strategies (Alembic workflows)
9. Error handling patterns (API error schemas, frontend error boundaries)
10. Performance optimization (database indexes, caching strategies, bundle size)

**Deliverable**: Comprehensive research document with decisions, rationale, and alternatives considered for each topic.

## Phase 1: Design & Contracts (AFTER RESEARCH)

**Prerequisites:** `research.md` complete

**Outputs:**
1. **data-model.md**: Complete database schema with:
   - User table (Better Auth structure)
   - Task table (all fields from 11 feature specs)
   - Indexes for performance (user_id, created_at, due_date, completed)
   - Constraints and validation rules

2. **contracts/**: API specifications including:
   - `api-endpoints.md`: All REST endpoints with full documentation
   - `authentication.md`: Auth flow diagrams and JWT structure
   - `request-schemas.json`: OpenAPI request bodies
   - `response-schemas.json`: OpenAPI response formats

3. **quickstart.md**: Developer setup guide with:
   - Prerequisites and system requirements
   - Installation steps (UV, npm/pnpm)
   - Environment configuration (.env setup)
   - Database setup (Neon connection)
   - Running dev servers (Next.js + FastAPI)
   - Running tests (pytest + Jest)

## Next Steps After Planning

1. ✅ **Plan Complete** (this file)
2. 🔄 **Generate research.md** (Phase 0 - agent task)
3. 🔄 **Generate data-model.md** (Phase 1 - agent task)
4. 🔄 **Generate contracts/** (Phase 1 - agent task)
5. 🔄 **Generate quickstart.md** (Phase 1 - agent task)
6. 🔄 **Update agent context** (run update-agent-context.ps1)
7. ⏭️ **Generate tasks.md** (`/sp.tasks` command - separate workflow)
8. ⏭️ **Begin implementation** (`/sp.implement` command)

**Timeline**: Phase 0 + Phase 1 planning artifacts to be generated next. Implementation begins after tasks.md is created.
