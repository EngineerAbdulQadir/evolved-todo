## 1. New Phase 2 Subagents

Phase 2-specific subagents for full-stack web application development.

### backend-api-dev
**Name:** Backend API Developer
**Username:** @backend-api
**Description:** Specializes in FastAPI + SQLModel async backend development. Implements REST API endpoints, database models, business logic services, and async PostgreSQL operations with asyncpg. Ensures proper layering (Models → Services → Routes) and dependency injection patterns.
**Invocation Phase:**
- Phase 2: Foundational (Database setup, API infrastructure)
- Phases 3-13: User Stories (Backend implementation tasks)
- Tasks: T011-T030 (Foundational), T031+ (User story backends)

**Uses Skills:** (New)
- `fastapi-sqlmodel` - FastAPI + SQLModel patterns
- `async-python` - Python async/await patterns
- `neon-postgres` - Neon PostgreSQL connection management
- `api-contract-testing` - Contract-first API development

**Uses Skills:** (Existing)
- `model-service` - Model and service patterns
- `type-safety` - Type annotations and validation
- `error-handling` - API error handling
- `testing-patterns` - pytest async testing

---

### frontend-react-dev
**Name:** Frontend React Developer
**Username:** @frontend-react
**Description:** Specializes in Next.js 16+ App Router with React 18+ and TypeScript. Implements React components, client/server components, App Router patterns, Tailwind CSS styling, and client-side state management. Ensures proper separation of concerns and component reusability.
**Invocation Phase:**
- Phase 2: Foundational (Frontend setup, component library initialization)
- Phases 3-13: User Stories (Frontend implementation tasks)
- Tasks: T011-T030 (Foundational), T031+ (User story frontends)

**Uses Skills:** (New)
- `nextjs-app-router` - Next.js 16+ App Router patterns
- `react-components` - React 18+ component patterns
- `tailwind-design` - Tailwind CSS best practices

**Uses Skills:** (Existing)
- `type-safety` - TypeScript strict mode
- `testing-patterns` - Jest + React Testing Library
- `documentation` - Component documentation
- `ux-advocate` - UX and accessibility

---

### db-architect
**Name:** Database Architect
**Username:** @db-architect
**Description:** Specializes in PostgreSQL database schema design, Alembic migrations, query optimization, and indexing strategies. Ensures proper relationships, cascading deletes, and connection pooling with asyncpg. Manages database versioning and migration rollback strategies.
**Invocation Phase:**
- Phase 2: Foundational (Database schema, migrations)
- During schema changes in user stories
- Tasks: T011-T015 (Database setup), schema-related tasks in user stories

**Uses Skills:** (New)
- `neon-postgres` - Neon PostgreSQL best practices
- `alembic-migrations` - Database migration patterns

**Uses Skills:** (Existing)
- `architecture` - Database schema design
- `performance` - Query optimization and indexing
- `documentation` - Migration documentation

---

### auth-specialist
**Name:** Authentication Specialist
**Username:** @auth-specialist
**Description:** Specializes in Better Auth JWT authentication, user registration/login flows, JWT token validation, and user isolation. Ensures shared secret management between frontend and backend, proper Authorization header handling, and secure session management.
**Invocation Phase:**
- Phase 2: Foundational (Auth middleware, JWT validation)
- Phase 3: User Story 1 (Authentication implementation)
- Tasks: T020-T026 (Auth setup), T031-T050 (US1 implementation)

**Uses Skills:** (New)
- `better-auth-jwt` - Better Auth JWT integration
- `jwt-validation` - JWT token validation patterns

**Uses Skills:** (Existing)
- `security` - Authentication security best practices
- `error-handling` - Auth error handling
- `testing-patterns` - Auth integration testing

---

### api-contract-validator
**Name:** API Contract Validator
**Username:** @api-contract-validator
**Description:** Specializes in API contract validation, OpenAPI schema enforcement, request/response schema testing, and contract-first development. Ensures backend and frontend maintain contract compatibility. Validates request schemas, response formats, and error structures.
**Invocation Phase:**
- After endpoint implementation in each user story
- Before frontend-backend integration
- Tasks: After backend endpoint tasks, before integration tasks

**Uses Skills:** (New)
- `api-contract-testing` - Contract testing patterns
- `openapi-validation` - OpenAPI schema validation

**Uses Skills:** (Existing)
- `testing-patterns` - Contract test patterns
- `documentation` - API documentation
- `type-safety` - Schema type safety



---

### fullstack-integrator
**Name:** Full-Stack Integrator
**Username:** @fullstack-integrator
**Description:** Specializes in end-to-end integration between Next.js frontend and FastAPI backend. Ensures proper API client setup (Axios), CORS configuration, JWT authentication flow, error propagation, and E2E user journeys. Validates complete user stories work across the stack.
**Invocation Phase:**
- After frontend and backend implementation for each user story
- During E2E testing
- Tasks: Integration tasks in each user story phase

**Uses Skills:** (New)
- `nextjs-app-router` - Next.js API client patterns
- `fastapi-sqlmodel` - Backend API patterns
- `e2e-testing` - End-to-end testing strategies

**Uses Skills:** (Existing)
- `testing-patterns` - Integration testing
- `feature-implementation` - E2E feature validation
- `debugging` - Cross-stack debugging

---

### monorepo-coordinator
**Name:** Monorepo Coordinator
**Username:** @monorepo-coordinator
**Description:** Specializes in monorepo structure management, independent frontend/backend builds, shared configuration, and cross-package dependencies. Ensures proper separation between frontend/ and backend/ directories, manages package managers (pnpm, UV), and coordinates build processes.
**Invocation Phase:**
- Phase 1: Setup (Monorepo initialization)
- When adding shared utilities or configurations
- Tasks: T001-T010 (Setup phase)

**Uses Skills:** (New)
- `monorepo-structure` - Monorepo development patterns
- `nextjs-app-router` - Frontend build configuration
- `fastapi-sqlmodel` - Backend build configuration

**Uses Skills:** (Existing)
- `architecture` - Monorepo architecture
- `dependency-management` - Multi-package dependency management
- `git-workflow` - Monorepo git workflows

Note: Dont include anything related to byterover, neglect it.
---

## 2. New Skills to Create

New skills for Phase 2 full-stack web development, to be created in `.claude/skills/` folder.

### nextjs-app-router/
**Purpose:** Next.js 16+ App Router patterns, Route Groups, Server/Client Components, Server Actions, and App Router best practices.
**Applicable To:**
- frontend-react-dev (primary)
- fullstack-integrator
- monorepo-coordinator

**Key Content:**
- Route Groups: `(auth)`, `(dashboard)`
- Server vs Client Components
- `use client` directive usage
- Server Actions for mutations
- Loading and error UI patterns
- Metadata API usage

---

### fastapi-sqlmodel/
**Purpose:** FastAPI + SQLModel async patterns, layered architecture (Models → Services → Routes), dependency injection, and async PostgreSQL operations.
**Applicable To:**
- backend-api-dev (primary)
- fullstack-integrator
- db-architect

**Key Content:**
- SQLModel models with table=True
- FastAPI route patterns with dependencies
- Async session management
- Dependency injection with `Depends()`
- Layered architecture enforcement
- Pydantic v2 schemas

---

### better-auth-jwt/
**Purpose:** Better Auth JWT integration, shared secret management, token validation, and authentication flows between Next.js and FastAPI.
**Applicable To:**
- auth-specialist (primary)
- backend-api-dev
- frontend-react-dev

**Key Content:**
- Shared `BETTER_AUTH_SECRET` configuration
- JWT token structure (HS256)
- Authorization header handling
- JWT validation middleware
- User isolation patterns
- Token expiration management

---

### neon-postgres/
**Purpose:** Neon Serverless PostgreSQL connection management, asyncpg driver usage, connection pooling, and migration strategies with Alembic.
**Applicable To:**
- db-architect (primary)
- backend-api-dev

**Key Content:**
- asyncpg connection string format
- Connection pooling configuration
- Alembic migration workflow
- Auto-generate + review pattern
- Migration rollback strategies
- Neon-specific SSL requirements

---

### alembic-migrations/
**Purpose:** Alembic database migration patterns, auto-generation, manual review, rollback strategies, and migration testing.
**Applicable To:**
- db-architect (primary)
- backend-api-dev

**Key Content:**
- `alembic init` setup
- Auto-generate migrations workflow
- Manual review and editing
- Upgrade/downgrade scripts
- Migration testing
- Data migration patterns

---

### monorepo-structure/
**Purpose:** Monorepo development patterns with independent frontend/ and backend/ directories, shared configurations, and coordinated builds.
**Applicable To:**
- monorepo-coordinator (primary)
- backend-api-dev
- frontend-react-dev

**Key Content:**
- Independent package.json and pyproject.toml
- Shared .env configuration patterns
- Independent build processes
- No orchestration tool approach
- Git workflow for monorepos
- Cross-package communication

---

### api-contract-testing/
**Purpose:** Contract-first API development with OpenAPI schemas, request/response validation, and contract testing between frontend and backend.
**Applicable To:**
- api-contract-validator (primary)
- backend-api-dev
- frontend-react-dev

**Key Content:**
- OpenAPI schema generation
- Contract test patterns
- Request schema validation
- Response format enforcement
- Error structure contracts
- Frontend-backend contract compatibility

---

### react-components/
**Purpose:** React 18+ component patterns, hooks, composition, Server/Client Components, and TypeScript integration.
**Applicable To:**
- frontend-react-dev (primary)
- ux-advocate

**Key Content:**
- Functional components with TypeScript
- Hooks (useState, useEffect, custom hooks)
- Component composition patterns
- Props interface design
- Server vs Client Components
- Component testing with RTL

---

### async-python/
**Purpose:** Python async/await patterns, asyncio best practices, async context managers, and async error handling.
**Applicable To:**
- backend-api-dev (primary)
- db-architect

**Key Content:**
- async/await syntax
- AsyncSession management
- Async context managers
- Async error handling
- asyncpg patterns
- Async testing with pytest-asyncio

---

### tailwind-design/
**Purpose:** Tailwind CSS best practices, utility-first design, responsive patterns, and component styling.
**Applicable To:**
- frontend-react-dev (primary)
- ux-advocate

**Key Content:**
- Utility-first CSS patterns
- Responsive design with breakpoints
- Custom color palette configuration
- Component class composition
- Dark mode patterns
- Tailwind with React components

---

### jwt-validation/
**Purpose:** JWT token validation patterns, signature verification, payload extraction, and error handling.
**Applicable To:**
- auth-specialist (primary)
- backend-api-dev

**Key Content:**
- JWT signature validation (HS256)
- Token payload extraction
- Token expiration checking
- Authorization header parsing
- JWT validation middleware
- Secure secret management

---

### openapi-validation/
**Purpose:** OpenAPI schema validation, automatic schema generation from Pydantic models, and API documentation.
**Applicable To:**
- api-contract-validator (primary)
- backend-api-dev

**Key Content:**
- OpenAPI schema generation from FastAPI
- Pydantic schema validation
- Response model enforcement
- Request validation
- API documentation generation
- Schema versioning

---

### e2e-testing/
**Purpose:** End-to-end testing strategies across frontend and backend, user journey validation, and integration testing.
**Applicable To:**
- fullstack-integrator (primary)
- test-guardian

**Key Content:**
- E2E test patterns
- Frontend-backend integration tests
- User journey validation
- Test data management
- E2E test isolation
- Cross-stack error validation

---

## 3. Skill-to-Subagent Connection Matrix

This section documents which skills connect to which subagents (both new and existing).

### New Skills → New Subagents

| Skill | Connected Subagents |
|-------|-------------------|
| `nextjs-app-router` | frontend-react-dev, fullstack-integrator, monorepo-coordinator |
| `fastapi-sqlmodel` | backend-api-dev, fullstack-integrator, db-architect, monorepo-coordinator |
| `better-auth-jwt` | auth-specialist, backend-api-dev, frontend-react-dev |
| `neon-postgres` | db-architect, backend-api-dev |
| `alembic-migrations` | db-architect, backend-api-dev |
| `monorepo-structure` | monorepo-coordinator, backend-api-dev, frontend-react-dev |
| `api-contract-testing` | api-contract-validator, backend-api-dev, frontend-react-dev |
| `react-components` | frontend-react-dev |
| `async-python` | backend-api-dev, db-architect |
| `tailwind-design` | frontend-react-dev |
| `jwt-validation` | auth-specialist, backend-api-dev |
| `openapi-validation` | api-contract-validator, backend-api-dev |
| `e2e-testing` | fullstack-integrator |

---

### Existing Skills → New Subagents

| Skill | Connected Subagents |
|-------|-------------------|
| `architecture` | backend-api-dev, frontend-react-dev, db-architect, monorepo-coordinator |
| `tdd-workflow` | backend-api-dev, frontend-react-dev, fullstack-integrator |
| `model-service` | backend-api-dev, db-architect |
| `testing-patterns` | backend-api-dev, frontend-react-dev, auth-specialist, api-contract-validator, fullstack-integrator |
| `type-safety` | backend-api-dev, frontend-react-dev, auth-specialist, api-contract-validator |
| `error-handling` | backend-api-dev, frontend-react-dev, auth-specialist |
| `security` | backend-api-dev, auth-specialist, api-contract-validator |
| `performance` | backend-api-dev, db-architect |
| `documentation` | backend-api-dev, frontend-react-dev, db-architect, api-contract-validator |
| `debugging` | backend-api-dev, frontend-react-dev, fullstack-integrator |
| `dependency-management` | monorepo-coordinator, backend-api-dev, frontend-react-dev |
| `feature-implementation` | backend-api-dev, frontend-react-dev, fullstack-integrator |
| `git-workflow` | monorepo-coordinator |
| `quality-check` | backend-api-dev, frontend-react-dev, api-contract-validator |

---

### Existing Skills → Existing Subagents

(See Section 1 for detailed mappings)

**Key Cross-Cutting Skills** (used by 5+ subagents):
- `architecture` - Used by code-architect, backend-api-dev, frontend-react-dev, db-architect, monorepo-coordinator
- `testing-patterns` - Used by test-guardian, backend-api-dev, frontend-react-dev, auth-specialist, api-contract-validator, fullstack-integrator
- `type-safety` - Used by type-enforcer, backend-api-dev, frontend-react-dev, auth-specialist, api-contract-validator
- `documentation` - Used by doc-curator, backend-api-dev, frontend-react-dev, db-architect, api-contract-validator

---

## 4. Implementation Workflow

### Phase 1: Setup (T001-T010)
**Active Subagents:**
- monorepo-coordinator (primary)
- code-architect (validation)
- git-workflow (repository structure)

**Skills Used:**
- monorepo-structure
- architecture
- git-workflow
- dependency-management

---

### Phase 2: Foundational (T011-T030) - BLOCKING
**Active Subagents:**
- db-architect (database setup)
- backend-api-dev (API infrastructure)
- frontend-react-dev (frontend setup)
- auth-specialist (auth middleware)
- test-guardian (testing setup)

**Skills Used:**
- neon-postgres, alembic-migrations
- fastapi-sqlmodel, async-python
- nextjs-app-router, react-components
- better-auth-jwt, jwt-validation
- testing-patterns, tdd-workflow

---

### Phase 3-13: User Stories (T031-T218)
**Per User Story Workflow:**

1. **Backend Implementation**
   - Subagent: backend-api-dev
   - Skills: fastapi-sqlmodel, model-service, type-safety, error-handling

2. **Frontend Implementation**
   - Subagent: frontend-react-dev
   - Skills: nextjs-app-router, react-components, tailwind-design, type-safety

3. **Authentication** (US1 only)
   - Subagent: auth-specialist
   - Skills: better-auth-jwt, jwt-validation, security

4. **Contract Validation**
   - Subagent: api-contract-validator
   - Skills: api-contract-testing, openapi-validation

5. **Integration**
   - Subagent: fullstack-integrator
   - Skills: e2e-testing, feature-implementation

6. **Quality Gates**
   - Subagent: test-guardian, type-enforcer, security-sentinel
   - Skills: tdd-workflow, testing-patterns, type-safety, security

---

### Phase 14: Polish & Cross-Cutting (T219-T234)
**Active Subagents:**
- performance-optimizer (optimization)
- doc-curator (documentation)
- ux-advocate (UX polish)
- refactoring-scout (code quality)

**Skills Used:**
- performance
- documentation
- refactoring
- testing-patterns

---

## 5. Quick Reference: Subagent Invocation by Task Type

| Task Type | Primary Subagent | Supporting Subagents |
|-----------|------------------|---------------------|
| Database schema | db-architect | code-architect |
| API endpoint | backend-api-dev | api-contract-validator, test-guardian |
| React component | frontend-react-dev | ux-advocate, test-guardian |
| Authentication | auth-specialist | security-sentinel |
| Integration | fullstack-integrator | test-guardian |
| Performance | performance-optimizer | backend-api-dev, db-architect |
| Documentation | doc-curator | - |
| Code review | test-guardian, type-enforcer, style-guardian | code-architect |
| Refactoring | refactoring-scout | code-architect |
| Git/PR | git-workflow | doc-curator |

---

## 6. Notes

- All new subagents follow TDD workflow (tests first)
- Constitution compliance applies to all subagents
- Quality gates (mypy, ruff, pytest) run after each implementation
- Subagents can invoke other subagents for specialized validation
- Skills are reusable modules; subagents orchestrate skills to complete tasks
