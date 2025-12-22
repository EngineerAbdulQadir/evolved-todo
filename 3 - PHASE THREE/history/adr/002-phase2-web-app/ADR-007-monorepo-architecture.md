# ADR-007: Full-Stack Monorepo Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-11
- **Feature:** 002-phase2-web-app
- **Context:** Phase 2 requires a full-stack web application with separate frontend and backend codebases while maintaining a unified development workflow. The architecture must support independent deployment of frontend and backend, clear separation of concerns, and efficient developer experience for a team working across the stack.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Defines entire project structure
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Monorepo vs separate repos vs hybrid
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all development workflows
-->

## Decision

Adopt a **monorepo architecture** with isolated `frontend/` and `backend/` directories at repository root, without a monorepo orchestration tool (e.g., Turborepo, Nx, Lerna).

**Structure:**
- **Frontend Directory:** `frontend/` - Next.js 16+ application with independent `package.json`, managed by pnpm
- **Backend Directory:** `backend/` - FastAPI application with independent `pyproject.toml`, managed by UV
- **Shared Configuration:** `.env` files at each directory level, no shared code between frontend/backend
- **Independent Builds:** Each directory builds and deploys independently
- **Version Control:** Single Git repository with unified branching and PR workflow
- **CI/CD:** Single pipeline testing both frontend and backend with separate deployment stages

**No Orchestration Tool:**
- No Turborepo/Nx/Lerna configuration
- Simple `npm run` scripts and `uv run` commands
- Manual coordination for cross-stack changes (acceptable for 2-person team)

## Consequences

### Positive

- **Independent Deployment:** Frontend can deploy to Vercel, backend to any Python platform without coupling
- **Clear Boundaries:** Frontend and backend have explicit separation with no accidental coupling
- **Technology Freedom:** Each stack uses its native package manager (pnpm, UV) without abstraction
- **Unified Git Workflow:** Single repository for atomic commits across frontend/backend changes
- **Simplified Onboarding:** Developers clone one repo and have access to full stack
- **Easier Code Reviews:** PRs can span frontend + backend for complete feature review
- **Minimal Complexity:** No additional tooling overhead (Turborepo config, workspace management)
- **Fast Iteration:** No monorepo tool learning curve for small team

### Negative

- **Manual Coordination:** No automated task orchestration (e.g., "build all packages")
- **Potential Duplication:** Type definitions may need duplication (mitigated by OpenAPI schemas)
- **CI Complexity:** Must detect which stack changed to optimize CI runs (can use path filters)
- **No Shared Code:** Cannot share utilities between frontend/backend (by design for Phase 2)
- **Scaling Limitation:** If team grows >10 developers, may need orchestration tool

## Alternatives Considered

**Alternative A: Separate Repositories (frontend-repo, backend-repo)**
- **Pros:** True independence, separate CI/CD, easier to assign ownership
- **Cons:** Harder to coordinate breaking changes, duplicate issue tracking, complex version synchronization
- **Why Rejected:** Overhead of managing two repos outweighs benefits for 2-person team. Atomic commits across stack impossible.

**Alternative B: Monorepo with Turborepo/Nx**
- **Pros:** Task orchestration, caching, dependency graph management
- **Cons:** Learning curve, configuration overhead, overkill for 2 directories
- **Why Rejected:** Frontend and backend are independent enough that orchestration isn't needed. No shared packages to warrant tooling complexity.

**Alternative C: Backend-Embedded Frontend (frontend/ inside backend/static/)**
- **Pros:** Single deployment unit, simpler for small apps
- **Cons:** Couples frontend build to backend deployment, limits frontend deployment options (e.g., Vercel CDN)
- **Why Rejected:** Prevents independent scaling and deployment. Next.js optimizations (ISR, SSR) work best on Vercel.

## References

- Feature Spec: `specs/002-phase2-web-app/spec.md`
- Implementation Plan: `specs/002-phase2-web-app/plan.md` (lines 130-273)
- Research: `specs/002-phase2-web-app/research.md` (Monorepo tooling section)
- Related ADRs: ADR-008 (Frontend Stack), ADR-009 (Backend Stack)
- Evaluator Evidence: `history/prompts/002-phase2-web-app/014-create-adrs-phase2.misc.prompt.md`
