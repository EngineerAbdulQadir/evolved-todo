---
id: 013
title: Create Subagents Documentation
stage: misc
date: 2025-12-11
surface: agent
model: claude-sonnet-4-5
feature: 002-phase2-web-app
branch: 002-phase2-web-app
user: Engineer Abdul Qadir
command: direct-request
labels: ["subagents", "skills", "documentation", "phase-2", "full-stack", "architecture"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - subagents.md
tests:
 - none
---

## Prompt

now make a subagents.md in parent directory with first tell which existing subagents are able to connect with existing skills if needed and then for phase 2 create new sub agents with name username description and agent invocation phase and then create skills which are going to be created in skills folder, also tell if skills are needed to connect to any subagents.

## Response snapshot

Created comprehensive `subagents.md` documentation in repository root with the following structure:

**Section 1 - Existing Subagent-to-Skill Mappings:**
Mapped all 12 existing subagents to 17 existing skills:
- code-architect → architecture, model-service, feature-implementation, refactoring, spec-to-code
- test-guardian → tdd-workflow, testing-patterns, quality-check
- type-enforcer → type-safety, error-handling, model-service
- security-sentinel → security, error-handling, dependency-management
- performance-optimizer → performance, testing-patterns, debugging
- doc-curator → documentation, cli-command, error-handling
- style-guardian → refactoring, type-safety, documentation
- ux-advocate → cli-command, documentation, error-handling
- dependency-auditor → dependency-management, security, quality-check
- constitution-compliance → spec-to-code, feature-implementation, quality-check
- git-workflow → git-workflow, documentation
- refactoring-scout → refactoring, architecture, performance

**Section 2 - New Phase 2 Subagents (7 total):**
1. **backend-api-dev** (@backend-api) - FastAPI + SQLModel async backend development
2. **frontend-react-dev** (@frontend-react) - Next.js 16+ App Router with React 18+
3. **db-architect** (@db-architect) - PostgreSQL schema design and Alembic migrations
4. **auth-specialist** (@auth-specialist) - Better Auth JWT authentication
5. **api-contract-validator** (@api-contract-validator) - API contract validation and OpenAPI
6. **fullstack-integrator** (@fullstack-integrator) - Frontend-backend E2E integration
7. **monorepo-coordinator** (@monorepo-coordinator) - Monorepo structure management

Each subagent documented with: Name, Username, Description, Invocation Phase, Skills Used (new + existing)

**Section 3 - New Skills to Create (13 total):**
1. `nextjs-app-router/` - Next.js 16+ App Router patterns
2. `fastapi-sqlmodel/` - FastAPI + SQLModel async patterns
3. `better-auth-jwt/` - Better Auth JWT integration
4. `neon-postgres/` - Neon PostgreSQL connection management
5. `alembic-migrations/` - Database migration patterns
6. `monorepo-structure/` - Monorepo development patterns
7. `api-contract-testing/` - Contract-first API development
8. `react-components/` - React 18+ component patterns
9. `async-python/` - Python async/await patterns
10. `tailwind-design/` - Tailwind CSS best practices
11. `jwt-validation/` - JWT token validation patterns
12. `openapi-validation/` - OpenAPI schema validation
13. `e2e-testing/` - End-to-end testing strategies

Each skill documented with: Purpose, Applicable To (which subagents), Key Content

**Section 4 - Skill-to-Subagent Connection Matrix:**
- New Skills → New Subagents matrix (13 skills mapped)
- Existing Skills → New Subagents matrix (14 skills mapped)
- Key cross-cutting skills identified (architecture, testing-patterns, type-safety, documentation)

**Section 5 - Implementation Workflow:**
- Phase 1 Setup: monorepo-coordinator, code-architect, git-workflow
- Phase 2 Foundational: db-architect, backend-api-dev, frontend-react-dev, auth-specialist, test-guardian
- Phase 3-13 User Stories: Per-story workflow with backend → frontend → contract → integration → quality gates
- Phase 14 Polish: performance-optimizer, doc-curator, ux-advocate, refactoring-scout

**Section 6 - Quick Reference:**
Task-type to subagent mapping table for quick invocation reference

**Section 7 - Notes:**
- TDD workflow enforcement
- Constitution compliance
- Quality gates (mypy, ruff, pytest)
- Subagent orchestration patterns

## Outcome

- ✅ Impact: Created comprehensive subagent and skill documentation enabling Phase 2 full-stack implementation with clear invocation patterns and skill connections
- 🧪 Tests: None - documentation artifact
- 📁 Files: Created subagents.md (1 file, ~500 lines)
- 🔁 Next prompts: Begin creating the 13 new skills in `.claude/skills/` folder, then update agent context with `update-agent-context.ps1`
- 🧠 Reflection: Mapping subagents to skills creates clear specialization boundaries while enabling cross-cutting concerns through shared skills. The connection matrix enables efficient subagent orchestration during implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None - comprehensive mapping completed successfully with clear skill-subagent relationships
- Graders run and results (PASS/FAIL):
  - Completeness: PASS - All 12 existing subagents mapped, 7 new subagents defined, 13 new skills defined
  - Clarity: PASS - Each subagent and skill has clear purpose, invocation phase, and connections
  - Traceability: PASS - Connection matrix enables bidirectional lookup (subagent→skills, skill→subagents)
  - Practicality: PASS - Quick reference tables enable fast subagent invocation during implementation
- Prompt variant (if applicable): Standard documentation request with explicit structure requirements
- Next experiment (smallest change to try): Consider adding example invocation snippets for each subagent to accelerate developer onboarding
