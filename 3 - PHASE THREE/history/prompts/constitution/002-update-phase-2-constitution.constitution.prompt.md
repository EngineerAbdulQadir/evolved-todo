---
id: 002
title: Update Phase 2 Constitution
stage: constitution
date: 2025-12-10
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: AQI
command: /sp.constitution
labels: ["phase-2", "constitution", "full-stack", "web-app", "database", "authentication"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - None (constitution document)
---

## Prompt

```text
we will not only cover basic levels:  All 5 Basic Level features from Phase 1:
    a. Add Task
    b. Delete Task
    c. Update Task
    d. View Task List
    e. Mark as Complete because we have implemented all basic to advance so we will transform all. also leave the timeline, now first update our constitution with phase 2 working. /sp.constitution
```

## Response snapshot

Constitution updated from v1.1.0 to v2.0.0 (MAJOR version bump - Phase transition).

**Key Changes:**

**Breaking Changes:**
- Removed in-memory constraint → Now requires Neon PostgreSQL database
- Removed CLI-only constraint → Now requires Next.js 16+ web interface
- Added multi-user requirement with Better Auth JWT authentication
- Complete technology stack overhaul for full-stack web development

**New Principles Added:**
- IX. Multi-User Data Isolation & Security (JWT authentication, user isolation)
- X. Database Schema & Migration Management (SQLModel, Neon PostgreSQL)
- XI. API Design & RESTful Conventions (REST API standards)

**Updated Principles:**
- IV. Technology Stack Requirements → Complete Phase 2 stack (Next.js, FastAPI, SQLModel, Better Auth)
- V. Clean Code & Modularity → Monorepo structure (frontend/ + backend/)
- VI. Type Safety → Now covers both Python and TypeScript
- VII. Comprehensive Documentation → API and UI documentation
- VIII. Error Handling → HTTP error responses with proper status codes

**Maintained:**
- All 10 features from Phase 1 (Basic + Intermediate + Advanced)
- Spec-First Development (Principle I)
- Test-First TDD (Principle II)
- YAGNI Principle (Principle III) - same 10 features, now as web app

**Monorepo Structure:**
```
evolved-todo/
├── frontend/          # Next.js 16+ (App Router)
├── backend/           # Python FastAPI
├── specs/             # Organized by type (features/, api/, database/, ui/)
├── .spec-kit/         # Spec-Kit config
└── CLAUDE.md          # Root instructions
```

**Technology Stack:**
- Frontend: Next.js 16+, TypeScript, Tailwind CSS, Better Auth
- Backend: Python 3.13+, FastAPI, SQLModel, UV
- Database: Neon Serverless PostgreSQL
- Testing: pytest (backend), Jest (frontend)

**API Endpoints (RESTful):**
- GET    /api/{user_id}/tasks
- POST   /api/{user_id}/tasks
- GET    /api/{user_id}/tasks/{id}
- PUT    /api/{user_id}/tasks/{id}
- DELETE /api/{user_id}/tasks/{id}
- PATCH  /api/{user_id}/tasks/{id}/complete

**Security:**
- JWT tokens for authentication
- User isolation (each user sees only their tasks)
- Shared BETTER_AUTH_SECRET for JWT signing
- All endpoints require valid JWT token

## Outcome

- ✅ Impact: MAJOR phase transition from CLI to full-stack web application with database persistence and multi-user support
- 🧪 Tests: Constitution document (no code tests)
- 📁 Files: 1 file modified (.specify/memory/constitution.md)
- 🔁 Next prompts:
  - Set up monorepo structure (frontend/ and backend/ folders)
  - Create .spec-kit/config.yaml for Phase 2
  - Create initial specs (architecture.md, database schema, API endpoints)
  - Set up Neon PostgreSQL database
  - Configure Better Auth with JWT
- 🧠 Reflection: Successfully transitioned constitution from Phase 1 (in-memory CLI) to Phase 2 (full-stack web with database). All 10 features maintained, new principles added for multi-user, security, database, and API design. Constitution now governs full-stack development with clear separation between frontend and backend.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (constitution document)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin Phase 2 implementation by setting up monorepo structure and creating initial specs
