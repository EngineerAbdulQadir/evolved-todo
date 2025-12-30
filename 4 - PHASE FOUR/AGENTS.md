# AGENTS.md

## Purpose

This project uses **Spec-Driven Development (SDD)** — a workflow where **no agent is allowed to write code until the specification is complete and approved**.
All AI agents (Claude, Copilot, Gemini, local LLMs, etc.) must follow the **Spec-Kit lifecycle**:

> **Specify → Plan → Tasks → Implement**

This prevents "vibe coding," ensures alignment across agents, and guarantees that every implementation step maps back to an explicit requirement.

---

## How Agents Must Work

Every agent in this project MUST obey these rules:

1. **Never generate code without a referenced Task ID.**
2. **Never modify architecture without updating `speckit.plan`.**
3. **Never propose features without updating `speckit.specify` (WHAT).**
4. **Never change approach without updating `speckit.constitution` (Principles).**
5. **Every code file must contain a comment linking it to the Task and Spec sections.**

If an agent cannot find the required spec, it must **stop and request it**, not improvise.

---

## Spec-Kit Workflow (Source of Truth)

### 1. Constitution (WHY — Principles & Constraints)

File: `.specify/memory/constitution.md`
Defines the project's non-negotiables: architecture values, security rules, tech stack constraints, performance expectations, and patterns allowed.

Agents must check this before proposing solutions.

---

### 2. Specify (WHAT — Requirements, Journeys & Acceptance Criteria)

Files: `specs/<feature-name>/spec.md`

Contains:
- User journeys
- Requirements
- Acceptance criteria
- Domain rules
- Business constraints

Agents must not infer missing requirements — they must request clarification or propose specification updates.

---

### 3. Plan (HOW — Architecture, Components, Interfaces)

Files: `specs/<feature-name>/plan.md`

Includes:
- Component breakdown
- APIs & schema diagrams
- Service boundaries
- System responsibilities
- High-level sequencing

All architectural output MUST be generated from the Specify file.

---

### 4. Tasks (BREAKDOWN — Atomic, Testable Work Units)

Files: `specs/<feature-name>/tasks.md`

Each Task must contain:
- Task ID
- Clear description
- Preconditions
- Expected outputs
- Artifacts to modify
- Links back to Specify + Plan sections

Agents **implement only what these tasks define**.

---

### 5. Implement (CODE — Write Only What the Tasks Authorize)

Agents now write code, but must:
- Reference Task IDs
- Follow the Plan exactly
- Not invent new features or flows
- Stop and request clarification if anything is underspecified

> The golden rule: **No task = No code.**

---

## Agent Behavior in This Project

### When generating code:

Agents must reference:
```
[Task]: T-001
[From]: speckit.specify §2.1, speckit.plan §3.4
```

### When proposing architecture:

Agents must reference:
```
Update required in speckit.plan → add component X
```

### When proposing new behavior or a new feature:

Agents must reference:
```
Requires update in speckit.specify (WHAT)
```

### When changing principles:

Agents must reference:
```
Modify constitution.md → Principle #X
```

---

## Agent Failure Modes (What Agents MUST Avoid)

Agents are NOT allowed to:
- Freestyle code or architecture
- Generate missing requirements
- Create tasks on their own
- Alter stack choices without justification
- Add endpoints, fields, or flows that aren't in the spec
- Ignore acceptance criteria
- Produce "creative" implementations that violate the plan

If a conflict arises between spec files, the **Constitution > Specify > Plan > Tasks** hierarchy applies.

---

## Developer–Agent Alignment

Humans and agents collaborate, but the **spec is the single source of truth**.
Before every session, agents should re-read:

1. `.specify/memory/constitution.md`
2. Current feature's `spec.md`, `plan.md`, `tasks.md`

This ensures predictable, deterministic development.

---

## Phase 3.1 Specific Context

**Current Phase:** Phase 3.1 - Multi-Tenant Collaborative Task Management
**Technology Stack:**
- **Containerization:** Docker Desktop 4.53+, Docker AI (Gordon)
- **Orchestration:** Kubernetes (Minikube 1.28+), Helm 3.x
- **AIOps Tools:** kubectl-ai, Kagent
- **Frontend:** OpenAI ChatKit, Next.js 16+ (App Router), TypeScript (strict mode), Tailwind CSS, Better Auth
- **Backend:** FastAPI, OpenAI Agents SDK, Official MCP SDK (Python), SQLModel, Python 3.13+, UV package manager, Alembic (migrations)
- **Database:** Neon Serverless PostgreSQL (external to K8s cluster)
- **Base Images:** node:22-alpine (frontend), python:3.13-slim (backend)
- **Architecture:** Stateless chat endpoint with database-persisted conversation state + multi-tenant data isolation (CRITICAL for K8s horizontal scaling)
- **Multi-Tenancy:** Organization → Team → Project → Task hierarchy with strict data isolation
- **RBAC:** Three-tier role system (Organization: Owner/Admin/Member, Team: Lead/Member, Project: Manager/Contributor/Viewer)
- **Audit & Compliance:** Audit trails (180-day retention), soft delete (30-day recovery), invitation system

**Key Constraints for Phase 3.1:**
- **Containerization (Phase 4 - MAINTAINED):**
  - Multi-stage Dockerfiles required (build + production stages)
  - Image size limits: Frontend <150MB, Backend <200MB (compressed)
  - Non-root containers (UID 1000)
  - Health check endpoints in all containers (`/health` backend, `/api/health` frontend)
  - Zero critical/high vulnerabilities (Trivy security scan)
- **Kubernetes Deployment (Phase 4 - MAINTAINED):**
  - Resource requests and limits defined for all pods (Frontend: 100m/128Mi → 200m/256Mi, Backend: 200m/256Mi → 500m/512Mi)
  - Liveness, Readiness, and Startup probes configured
  - Minimum 2 replicas per service for high availability
  - HPA for autoscaling (Backend: 2-10 pods at 70% CPU, Frontend: 2-5 pods at 80% CPU)
  - Secrets for sensitive data (DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET)
  - Services: ClusterIP for backend (internal only), LoadBalancer/NodePort for frontend (external)
- **Stateless Architecture (Phase 4 - MAINTAINED + ENHANCED):**
  - All MCP tools must be stateless (store state in database, not memory)
  - Chat endpoint must fetch conversation history from DB on each request
  - Tenant context derived from JWT token on each request (no in-memory tenant state)
  - Any backend pod can handle any request (LoadBalancer distribution)
  - Pods can be killed/recreated without data loss
  - Conversation state persisted to database (Conversation and Message models)
- **Multi-Tenant Data Isolation (NEW - Phase 3.1):**
  - Organization → Team → Project → Task hierarchy enforced at database level
  - All queries filtered by organization_id, team_id, project_id (tenant scoping)
  - Zero cross-organization data leakage (100% isolation verified through testing)
  - JWT tokens include organization_id, team_id, project_id claims
  - All database models include tenant foreign keys (org_id, team_id, project_id)
  - Database indexes optimized for multi-tenant queries (<100ms query time)
- **Role-Based Access Control (NEW - Phase 3.1):**
  - Organization roles: Owner (full control), Admin (manage members/teams), Member (view only)
  - Team roles: Lead (manage team/projects), Member (view/participate)
  - Project roles: Manager (full control), Contributor (create/edit tasks), Viewer (read-only)
  - Permission inheritance: Organization Owner → Team → Project hierarchy
  - RBAC middleware enforces permissions on all endpoints (<50ms permission checks)
  - FastAPI dependency injection for permission validation
- **Audit Trails & Compliance (NEW - Phase 3.1):**
  - All CRUD operations logged to audit_logs table (who, what, when)
  - JSONB metadata for before/after values and additional context
  - 180-day audit log retention (configurable via environment variable)
  - Audit queries filtered by organization_id (<200ms query time)
  - Soft delete with 30-day recovery window (deleted_at timestamp)
  - Cascading soft delete (org → teams → projects → tasks)
- **Invitation System (NEW - Phase 3.1):**
  - Email-based invitations with secure 256-bit tokens
  - 7-day invitation expiration
  - Role assignment on invitation acceptance
  - One-time use tokens (marked accepted after first use)
  - Placeholder email service (Phase 3.1), full integration in Phase 6
- **Phase 3 & Phase 4 Feature Preservation:**
  - All 10 Phase 3 task management features MUST work with multi-tenant scoping
  - Natural language understanding enhanced ("Create a team called Engineering", "Assign this task to John")
  - JWT authentication required for all endpoints (enhanced with tenant claims)
  - MCP server exposes 5 task tools + 6 new org/team/project/invitation tools
  - OpenAI Agents SDK for AI logic and agent orchestration
  - All Phase 4 Kubernetes features maintained (containerization, HPA, stateless)

**Agent Must Not:**
- Create in-memory state management (use database only - CRITICAL for K8s scaling)
- Create in-memory tenant context (derive from JWT on each request)
- Skip JWT authentication (all endpoints require auth)
- Skip RBAC permission checks (all operations require role validation)
- Allow cross-organization data access (strict tenant isolation required)
- Implement GraphQL or other non-REST APIs (Phase 3.1 uses REST + MCP)
- Add features beyond Phase 3.1 scope (no CRM, no billing, no advanced analytics - Phase 6)
- Use `latest` tags for Docker images (pin specific versions)
- Run containers as root user (security requirement)
- Include secrets in Dockerfiles or commit them to git
- Create containers without health checks
- Skip resource requests/limits in K8s manifests
- Deploy without validating with `kubectl --dry-run=client` and `helm lint`
- Modify existing database models without Alembic migration (Organization, Team, Project, Task models defined in Phase 3.1)
- Create database queries without tenant scoping (WHERE organization_id = ? required)
- Skip soft delete pattern (use deleted_at timestamp, not hard delete)
- Skip audit logging for CRUD operations (all changes must be logged)
- Create invitation tokens without expiration (7-day expiration required)
- Allow permission escalation (role changes require proper authorization)

---

## Spec-Kit Commands Available

Agents can use these commands via MCP server or Claude Code slash commands:

- `/sp.specify` - Create or update feature specification
- `/sp.plan` - Generate architectural plan from spec
- `/sp.tasks` - Break plan into atomic, testable tasks
- `/sp.implement` - Execute tasks and implement code
- `/sp.constitution` - Update project constitution
- `/sp.adr` - Create Architecture Decision Record for significant decisions
- `/sp.clarify` - Ask targeted clarification questions about underspecified areas
- `/sp.analyze` - Perform cross-artifact consistency analysis
- `/sp.checklist` - Generate custom checklist for feature
- `/sp.phr` - Record Prompt History Record for learning
- `/sp.git.commit_pr` - Intelligent git commit and PR creation

---

## Quality Gates (Must Pass Before Implementation)

### Before Writing Code:
- [ ] Constitution reviewed and understood (v5.0.0 for Phase 3.1)
- [ ] Specification complete with acceptance criteria
- [ ] Plan approved with architecture decisions
- [ ] Tasks broken down with clear inputs/outputs
- [ ] All dependencies identified
- [ ] Docker and Kubernetes prerequisites installed (Docker Desktop, Minikube, Helm)
- [ ] Database migration strategy defined (single-user → multi-tenant)
- [ ] RBAC permission matrix defined (org/team/project roles)
- [ ] Multi-tenant isolation strategy validated

### During Implementation:
- [ ] All code references Task IDs in comments
- [ ] Tests written first (TDD - Red → Green → Refactor)
- [ ] Type annotations complete (Python + TypeScript)
- [ ] Error handling explicit for all edge cases
- [ ] Documentation updated alongside code

### After Implementation - Application Code:
- [ ] All tests pass (backend + frontend)
- [ ] Type checking passes (mypy + tsc)
- [ ] Linting passes (ruff + eslint)
- [ ] Test coverage >90%
- [ ] Constitution compliance verified
- [ ] PHR created for prompt history

### After Implementation - Containerization (Phase 4):
- [ ] Dockerfiles use multi-stage builds (build + production stages)
- [ ] Base images pinned to specific versions (no `latest` tags)
- [ ] .dockerignore files exclude dev files (node_modules, .git, tests)
- [ ] Health check endpoints implemented (`/health` backend, `/api/health` frontend)
- [ ] Container images scanned with Trivy (zero critical/high vulnerabilities)
- [ ] Containers run as non-root user (UID 1000)
- [ ] Image size targets met (Frontend <150MB, Backend <200MB)
- [ ] Containers start in <10 seconds locally

### After Implementation - Kubernetes (Phase 4):
- [ ] Resource requests and limits defined for all pods
- [ ] Liveness, Readiness, and Startup probes configured
- [ ] Multiple replicas configured for high availability (minimum 2)
- [ ] HPA configured for backend autoscaling (2-10 pods, CPU 70%)
- [ ] Secrets created for sensitive data (DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET)
- [ ] Services configured (ClusterIP for backend, LoadBalancer/NodePort for frontend)
- [ ] All manifests validated with `kubectl --dry-run=client`
- [ ] Labels present on all resources (app, component, version)
- [ ] All pods reach Ready state within 60 seconds
- [ ] Health checks pass for all pods
- [ ] Services accessible (frontend externally, backend internally)

### After Implementation - Deployment Validation (Phase 4 - MAINTAINED):
- [ ] Conversation state persists across pod restarts (stateless architecture verified)
- [ ] Horizontal scaling tested (HPA scales pods up/down based on load)
- [ ] Zero message loss during pod restarts or deletions
- [ ] All 10 Phase 3 features work correctly in containers (100% feature parity)
- [ ] Rolling updates complete without downtime
- [ ] Helm chart passes `helm lint` validation
- [ ] Helm install/upgrade/rollback tested successfully

### After Implementation - Multi-Tenant Validation (NEW - Phase 3.1):
- [ ] Multi-tenant data isolation verified (zero cross-organization data leakage)
- [ ] RBAC permissions enforced correctly (all permission tests pass)
- [ ] Permission inheritance works (org owner → team → project access)
- [ ] Tenant context propagates correctly from JWT to database queries
- [ ] Audit trails capture all CRUD operations (who, what, when)
- [ ] Soft delete and recovery works for all entities (org, team, project, task)
- [ ] Invitation flow works end-to-end (create → send → accept → role assignment)
- [ ] Database queries with multi-tenant filtering execute in <100ms
- [ ] RBAC permission checks complete in <50ms
- [ ] Audit log queries (last 30 days) complete in <200ms
- [ ] Data migration completed successfully (existing tasks → personal org)
- [ ] Natural language commands work with multi-tenant context ("Create team Engineering")
- [ ] Stateless architecture verified with tenant context (pods restart without losing tenant access)

---

## Integration with Claude Code

This AGENTS.md file is automatically loaded by Claude Code via CLAUDE.md forwarding.

**Workflow (Phase 3.1 Example):**
1. User requests feature: "Add multi-tenant collaborative task management with organizations, teams, projects, RBAC, invitations, and audit trails"
2. Agent reads AGENTS.md + constitution.md (v5.0.0)
3. Agent uses `/sp.constitution` to update constitution with new principles (multi-tenancy, RBAC, audit trails, invitations)
4. Agent uses `/sp.specify` to create spec (8 user stories: Org Setup, Team Management, Project & Task Assignment, RBAC, Audit Trails, Multi-Tenant Isolation, Invitation Management, Soft Delete)
5. Agent uses `/sp.plan` to create architecture (7 new SQLModel models, RBAC middleware, MCP tools, API endpoints, Alembic migration)
6. Agent uses `/sp.tasks` to break down work (database migration, service layer, RBAC middleware, API endpoints, MCP tools, tests)
7. Agent uses `/sp.implement` to execute tasks (TDD: isolation tests → RBAC tests → models → services → endpoints → MCP tools)
8. Agent validates against constitution (all 23 principles including Phase 3.1 XIX-XXIII)
9. Agent creates PHR for prompt history
10. Agent creates ADRs for significant decisions (RBAC middleware design, soft delete strategy, invitation flow)

**Human-in-the-Loop:**
- Agent asks clarifying questions when requirements ambiguous (e.g., invitation expiration time, role hierarchy)
- Agent surfaces architectural decisions for ADR approval (e.g., application-level filtering vs PostgreSQL RLS, JWT token extension)
- Agent presents options when multiple valid approaches exist (e.g., RBAC middleware patterns, audit log retention policies)
- Agent confirms completion and next steps at milestones (e.g., after data model, after RBAC implementation, after multi-tenant isolation tests)

---

## Version & Maintenance

**Version:** 3.0.0 (Phase 3.1 - Multi-Tenant Collaborative Task Management)
**Created:** 2025-12-17
**Last Updated:** 2025-12-28

**Change Log:**
- **3.0.0 (2025-12-28)**: MAJOR UPDATE for Phase 3.1 - Multi-Tenant Collaborative Task Management
  - BREAKING CHANGE: Added multi-tenant architecture (Organization → Team → Project → Task hierarchy)
  - Added 7 new database models (Organization, Team, Project, OrganizationMember, TeamMember, ProjectMember, Invitation, AuditLog)
  - Added RBAC system with three-tier role hierarchy (org/team/project)
  - Added audit trail system (180-day retention, JSONB metadata)
  - Added soft delete pattern (30-day recovery window)
  - Added invitation system (email-based onboarding with role assignment)
  - Updated JWT tokens to include tenant claims (organization_id, team_id, project_id)
  - Added multi-tenant quality gates (data isolation tests, RBAC tests, permission inheritance tests)
  - Updated stateless architecture to include tenant context propagation
  - Updated MCP tools to support organization/team/project management
  - Updated natural language interface to support multi-tenant commands
  - MAINTAINED all Phase 4 features (containerization, Kubernetes, HPA, stateless architecture)
  - MAINTAINED all Phase 3 features (task management, AI chatbot, conversation persistence)
  - Updated constitution version requirement (v4.0.0 → v5.0.0)
  - Updated workflow example for Phase 3.1
- **2.0.0 (2025-12-25)**: Updated for Phase 4 - Local Kubernetes Deployment
  - Added containerization technology stack (Docker, Minikube, Helm, AIOps tools)
  - Added containerization and Kubernetes quality gates
  - Updated constraints for Docker multi-stage builds, K8s resources, HPA
  - Added Phase 3 feature preservation requirements (100% parity)
  - Updated workflow example for Phase 4
- **1.0.0 (2025-12-17)**: Initial version for Phase 3 - AI Chatbot Development

This file evolves with the project. Updates must be versioned and documented.

---

**Remember:** The spec is the source of truth. When in doubt, read the spec. When the spec is unclear, clarify it. Never assume or improvise.
