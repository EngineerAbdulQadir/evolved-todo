# ADR-009: Backend Technology Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-11
- **Feature:** 002-phase2-web-app
- **Context:** Phase 2 requires a production-ready backend API with async database operations, type-safe models, comprehensive validation, and JWT authentication. The stack must support >90% test coverage, strict type checking, and seamless integration with Neon PostgreSQL.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Defines all backend development patterns
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - FastAPI vs Django vs Flask vs Node.js
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all API development
-->

## Decision

Adopt **Python 3.13+ with FastAPI** as the integrated backend technology stack with the following components:

**Core Framework:**
- **Framework:** FastAPI (async-first, OpenAPI auto-generation)
- **Runtime:** Python 3.13+ (latest stable with performance improvements)
- **Package Manager:** UV (fast, modern alternative to pip/poetry)

**Database & ORM:**
- **ORM:** SQLModel (SQLAlchemy 2.0 + Pydantic v2 integration)
- **Database Driver:** asyncpg (async PostgreSQL driver)
- **Migrations:** Alembic (auto-generate from SQLModel models)

**Validation & Serialization:**
- **Schema Validation:** Pydantic v2 models (request/response DTOs)
- **Type Checking:** mypy with strict mode enabled
- **Linting/Formatting:** Ruff (fast linter + formatter)

**Architecture Pattern:**
- **Layering:** Models (SQLModel) → Services (business logic) → Routes (HTTP handlers)
- **Dependency Injection:** FastAPI's `Depends()` for database sessions, auth
- **Error Handling:** Custom exception handlers with HTTP status codes

**Testing:**
- **Framework:** pytest + pytest-asyncio + pytest-cov
- **API Testing:** httpx (async HTTP client for testing FastAPI)
- **Coverage Target:** >90%
- **Test Types:** Unit tests (services), integration tests (API endpoints)

**Server:**
- **ASGI Server:** uvicorn (production-ready async server)
- **Configuration:** Pydantic BaseSettings for environment variables

## Consequences

### Positive

- **Async Performance:** Native async/await support throughout stack (FastAPI + asyncpg + uvicorn)
- **Type Safety:** SQLModel + Pydantic + mypy provide end-to-end type checking
- **Auto-Documentation:** OpenAPI schema auto-generated from FastAPI routes
- **Developer Experience:** Fast startup, excellent error messages, auto-reload in dev
- **Modern Python:** Python 3.13+ performance improvements and latest language features
- **ORM Simplicity:** SQLModel combines SQLAlchemy power with Pydantic simplicity
- **Testing:** pytest ecosystem is mature with excellent async support
- **Validation:** Pydantic v2 validates all inputs automatically with clear error messages
- **UV Speed:** Package installation and dependency resolution 10-100x faster than pip

### Negative

- **Async Complexity:** Async/await requires careful handling (no blocking I/O)
- **SQLModel Maturity:** Newer than pure SQLAlchemy, smaller community
- **UV Adoption:** UV is newer, less mature than pip/poetry (but stabilizing)
- **Migration Gap:** Alembic auto-generation requires manual review and editing
- **No Built-in Admin:** Unlike Django, no admin panel out of the box
- **Deployment Learning Curve:** ASGI deployment differs from traditional WSGI

## Alternatives Considered

**Alternative A: Django + Django REST Framework + PostgreSQL**
- **Pros:** Mature ecosystem, built-in admin, ORM stability, excellent documentation
- **Cons:** Synchronous (blocks on I/O), heavier framework, slower startup, less type-safe
- **Why Rejected:** Django ORM is synchronous. FastAPI's async approach is better for API performance.

**Alternative B: Flask + SQLAlchemy + PostgreSQL**
- **Pros:** Simple, flexible, mature ecosystem, team familiarity
- **Cons:** No native async, manual OpenAPI generation, less opinionated
- **Why Rejected:** No async support. FastAPI provides auto-documentation and better DX.

**Alternative C: Node.js + Express + Prisma + PostgreSQL**
- **Pros:** JavaScript across full stack, excellent async, Prisma ORM is modern
- **Cons:** Less strict typing than Python, different ecosystem from Phase 1 CLI
- **Why Rejected:** Phase 1 was Python. Team has Python expertise. Maintaining continuity.

**Alternative D: FastAPI + raw SQLAlchemy + psycopg3**
- **Pros:** More control, mature ORM, no SQLModel learning curve
- **Cons:** More boilerplate (separate SQLAlchemy models + Pydantic schemas), type safety gaps
- **Why Rejected:** SQLModel eliminates duplication. Single model serves as both DB model and Pydantic schema.

**Alternative E: FastAPI + Tortoise ORM**
- **Pros:** Native async ORM designed for FastAPI
- **Cons:** Smaller community than SQLAlchemy, less mature, fewer features
- **Why Rejected:** SQLModel's Pydantic integration is superior. Alembic migrations are battle-tested.

## References

- Feature Spec: `specs/002-phase2-web-app/spec.md`
- Implementation Plan: `specs/002-phase2-web-app/plan.md` (lines 20-30)
- Research: `specs/002-phase2-web-app/research.md` (FastAPI + SQLModel Best Practices section)
- Related ADRs: ADR-007 (Monorepo Architecture), ADR-010 (Database Strategy)
- Evaluator Evidence: `history/prompts/002-phase2-web-app/014-create-adrs-phase2.misc.prompt.md`
