# ADR-010: Database & Persistence Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-11
- **Feature:** 002-phase2-web-app
- **Context:** Phase 2 replaces in-memory storage with persistent database to support multi-user scenarios. The database must support async operations, handle 1,000-10,000 users with up to 1,000 tasks each, provide ACID guarantees, and integrate seamlessly with FastAPI + SQLModel.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Defines all data persistence
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Neon vs self-hosted vs other platforms
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all data operations
-->

## Decision

Adopt **Neon Serverless PostgreSQL** with the following integrated persistence strategy:

**Database Platform:**
- **Provider:** Neon Serverless PostgreSQL (managed cloud database)
- **Database Engine:** PostgreSQL 15+ (ACID-compliant, JSON support, full-text search)
- **Connection Protocol:** postgresql+asyncpg:// (async driver)

**Database Driver:**
- **Driver:** asyncpg (native async PostgreSQL driver for Python)
- **Connection Pooling:** Built into asyncpg (max 100 concurrent connections)
- **SSL Mode:** Required (Neon enforces SSL)

**ORM & Schema Management:**
- **ORM:** SQLModel (SQLAlchemy 2.0 + Pydantic integration)
- **Migrations:** Alembic with auto-generate + manual review workflow
- **Schema Versioning:** Alembic version control in `backend/alembic/versions/`

**Database Schema:**
- **Tables:** `users` (Better Auth), `tasks` (FastAPI-managed)
- **Indexes:** Primary keys, foreign keys, user_id, created_at, due_date, completed, priority
- **Constraints:** Foreign key cascading deletes (tasks deleted when user deleted)

**Connection Management:**
- **Session Pattern:** Async context manager per request
- **Dependency Injection:** FastAPI `Depends(get_session)` provides session to routes
- **Connection Lifecycle:** Session created per request, committed, closed automatically

**Migration Workflow:**
- **Auto-Generate:** `alembic revision --autogenerate -m "description"`
- **Manual Review:** Developer reviews and edits migration before applying
- **Apply:** `alembic upgrade head` in production
- **Rollback:** `alembic downgrade -1` if issues detected

## Consequences

### Positive

- **Serverless Scaling:** Neon auto-scales compute and storage, pay only for usage
- **Developer Experience:** No database server management, instant provisioning
- **Async Performance:** asyncpg is one of the fastest PostgreSQL drivers
- **ACID Guarantees:** PostgreSQL ensures data integrity and consistency
- **Type Safety:** SQLModel models + mypy catch schema errors at compile time
- **Migration Safety:** Alembic version control enables safe schema evolution
- **Branching:** Neon database branching for development and testing environments
- **Backup & Recovery:** Automatic backups with point-in-time recovery
- **Connection Pooling:** asyncpg manages connections efficiently
- **Free Tier:** Neon free tier suitable for development and small deployments

### Negative

- **Vendor Lock-in:** Tightly coupled to Neon platform (mitigated: standard PostgreSQL)
- **Cold Start Latency:** Serverless databases may have cold start delays after inactivity
- **Connection Limits:** 100 concurrent connections on free tier (sufficient for Phase 2)
- **Cost Uncertainty:** Serverless pricing can be unpredictable at scale
- **Limited Control:** Cannot tune PostgreSQL server settings as deeply as self-hosted
- **Network Latency:** Cloud database adds latency vs local/VPC database
- **Migration Complexity:** Alembic auto-generate requires manual review and testing

## Alternatives Considered

**Alternative A: Self-Hosted PostgreSQL on VPS (DigitalOcean, Linode)**
- **Pros:** Full control, predictable pricing, no vendor lock-in
- **Cons:** Manual setup, maintenance burden, backup management, scaling complexity
- **Why Rejected:** Too much operational overhead for Phase 2. Neon removes database management.

**Alternative B: Supabase (PostgreSQL + Auth + Storage)**
- **Pros:** Integrated auth (replaces Better Auth), REST API auto-generation, realtime subscriptions
- **Cons:** More lock-in than Neon, learning curve for Supabase-specific features, overkill for simple CRUD
- **Why Rejected:** We already chose Better Auth. Supabase auth replacement would require architectural rework.

**Alternative C: PlanetScale (MySQL-compatible serverless)**
- **Pros:** Excellent branching workflow, autoscaling, generous free tier
- **Cons:** MySQL not PostgreSQL (different feature set), asyncmy driver less mature than asyncpg
- **Why Rejected:** PostgreSQL has better JSON support, full-text search, and Python ecosystem.

**Alternative D: AWS RDS PostgreSQL**
- **Pros:** Enterprise-grade reliability, VPC integration, mature platform
- **Cons:** More expensive, complex setup, always-on billing (not serverless)
- **Why Rejected:** Overkill for Phase 2. Neon's serverless pricing is more cost-effective for variable workloads.

**Alternative E: SQLite with Turso (edge-distributed SQLite)**
- **Pros:** Extremely fast local queries, zero configuration, embeddable
- **Cons:** Limited concurrency, async support is complex, migrations are manual
- **Why Rejected:** SQLite doesn't support true multi-user concurrent writes well. PostgreSQL is better for web apps.

## References

- Feature Spec: `specs/002-phase2-web-app/spec.md`
- Implementation Plan: `specs/002-phase2-web-app/plan.md` (lines 30-35)
- Research: `specs/002-phase2-web-app/research.md` (Neon PostgreSQL Connection Management section)
- Data Model: `specs/002-phase2-web-app/data-model.md` (complete schema)
- Related ADRs: ADR-009 (Backend Stack), ADR-011 (Authentication Strategy)
- Evaluator Evidence: `history/prompts/002-phase2-web-app/014-create-adrs-phase2.misc.prompt.md`
