<!--
Sync Impact Report:
Version: 5.0.0 (MAJOR - Phase 3.1: Multi-Tenancy & Collaborative Task Management)
Previous Version: 4.0.0
Changes in v5.0.0:
  - MAJOR ARCHITECTURAL TRANSITION: Single-User → Multi-Tenant Collaborative System
  - BREAKING CHANGE: Data model expanded from Task-centric to Organization → Team → Project → Task hierarchy
  - BREAKING CHANGE: Authentication expanded from User → multi-role RBAC (Organization/Team/Project roles)
  - ADDED Technology Stack: Enhanced Better Auth with organization/team support
  - ADDED Database Models: Organization, Team, Project, OrganizationMember, TeamMember, ProjectMember, Invitation, AuditLog
  - ADDED API Endpoints: /organizations, /teams, /projects, /invitations, /members (20+ new endpoints)
  - ADDED Principle XIX: Multi-Tenancy & Data Isolation Hierarchy
  - ADDED Principle XX: Role-Based Access Control (RBAC)
  - ADDED Principle XXI: Collaboration & Team Management
  - ADDED Principle XXII: Audit Trails & Change History
  - ADDED Principle XXIII: Invitation System & User Onboarding
  - UPDATED Principle IX: Multi-User Data Isolation → Multi-Tenant Data Isolation (hierarchical scoping)
  - UPDATED Principle X: Database Schema → Added 7 new models for multi-tenancy
  - UPDATED Principle XI: API Design → Added organization/team/project RESTful endpoints
  - UPDATED Principle XII: MCP Server Architecture → Added org/team/project management tools
  - UPDATED Principle XIII: Stateless Architecture → Enhanced with tenant context propagation
  - UPDATED Project Structure: Added backend/app/rbac/, backend/app/audit/ modules
  - UPDATED Scope: Added multi-tenancy, collaboration, invitations (Phase 3.1 enhancements)
  - MAINTAINED all 18 principles from Phase 4 (I-XVIII unchanged in spirit, updated for multi-tenant context)
  - MAINTAINED All Phase 4 Kubernetes functionality (containerization, HPA, stateless architecture)
  - MAINTAINED All Phase 3 chatbot functionality (natural language, MCP tools, OpenAI Agents SDK)

Principles (Updated):
  - I-VIII. (unchanged - apply to all code including multi-tenant features)
  - IX. Multi-Tenant Data Isolation & Security (BREAKING - hierarchical org/team/project scoping)
  - X. Database Schema & Migration Management (BREAKING - 7 new models)
  - XI. API Design & RESTful Conventions (BREAKING - 20+ new endpoints)
  - XII. AI Agent Development & MCP Server Architecture (UPDATED - new MCP tools)
  - XIII. Stateless Architecture & Conversation State Management (UPDATED - tenant context)
  - XIV-XVIII. (unchanged - apply to multi-tenant features)
  - XIX. Multi-Tenancy & Data Isolation Hierarchy (NEW - Phase 3.1)
  - XX. Role-Based Access Control (RBAC) (NEW - Phase 3.1)
  - XXI. Collaboration & Team Management (NEW - Phase 3.1)
  - XXII. Audit Trails & Change History (NEW - Phase 3.1)
  - XXIII. Invitation System & User Onboarding (NEW - Phase 3.1)

Templates Requiring Updates:
  - ⚠ spec-template.md (requires multi-tenancy acceptance criteria, RBAC scenarios, invitation flows)
  - ⚠ plan-template.md (requires organization/team/project data models, RBAC design patterns)
  - ⚠ tasks-template.md (requires multi-tenant task categories: org setup, team mgmt, project mgmt, RBAC, invitations)
  - ⚠ API contract docs (requires new endpoints: organizations, teams, projects, invitations, members)

Follow-up TODOs:
  - Create Phase 3.1 feature specification for multi-tenancy
  - Design database schema for Organization, Team, Project, OrganizationMember, TeamMember, ProjectMember models
  - Design Invitation model with email verification and role assignment
  - Design AuditLog model for change tracking (who, what, when)
  - Implement RBAC middleware for organization/team/project access control
  - Implement row-level security for multi-tenant data isolation
  - Create MCP tools for organization/team/project management
  - Update Better Auth configuration for organization support
  - Create API endpoints for organizations, teams, projects, invitations, members
  - Create migration strategy for existing single-user tasks → personal organization
  - Add database indexes for multi-tenant queries (org_id, team_id, project_id)
  - Implement soft delete for organizations, teams, projects, tasks
  - Test multi-tenant data isolation (no cross-organization leakage)
  - Test RBAC permissions (organization admin, team lead, project manager, member)
  - Validate Phase 4 Kubernetes horizontal scaling with multi-tenant load

Ratification Date: 2025-12-06
Last Amended: 2025-12-28
-->

# Evolved Todo - Phase 3.1 Constitution

## Core Principles

### I. Spec-First Development
Every feature MUST have a specification written and approved before implementation begins. This includes multi-tenant features, RBAC systems, organization management specs, and invitation workflows. Specifications are the single source of truth for requirements, acceptance criteria, and implementation guidance.

**Rules:**
- Feature specs live in `specs/<feature>/spec.md`
- All specs follow the spec-template structure
- Specs must define clear acceptance criteria for application functionality, RBAC rules, multi-tenant isolation, and K8s deployment
- Specs must include organization/team/project hierarchy, role definitions, and permission matrices
- Implementation must not begin until spec is approved
- Code/manifests that don't match spec are incorrect, regardless of functionality

**Phase 3.1 Additions:**
- Multi-tenant feature specifications must define organization/team/project scoping rules
- RBAC specifications must define all roles (Organization: Owner/Admin/Member, Team: Lead/Member, Project: Manager/Contributor/Viewer)
- Invitation flow specifications must define invitation creation, acceptance, role assignment, and expiration
- Audit trail specifications must define what events are logged and who can view logs
- Data migration specifications must define how existing single-user data transitions to multi-tenant model

**Rationale:** Spec-first ensures alignment between architect (human or AI), developer (Claude Code), and stakeholder expectations before any code or infrastructure is written. In Phase 3.1, this extends to multi-tenant data models, RBAC systems, and collaborative workflows.

### II. Test-First (TDD - NON-NEGOTIABLE)
Test-Driven Development is mandatory for backend, MCP tools, conversation flows, deployment validation, multi-tenant features, RBAC logic, and organization management. Tests MUST be written, reviewed, and approved before implementation code and infrastructure.

**Red-Green-Refactor Cycle (Strictly Enforced):**
1. **Red:** Write failing tests that capture acceptance criteria
2. **Green:** Implement minimal code to pass tests
3. **Refactor:** Improve code while keeping tests green

**Rules:**
- **Backend (FastAPI):** pytest for unit and integration tests
  - All API endpoints must have integration tests (including new org/team/project endpoints)
  - All service layer functions must have unit tests
  - All database models must have validation tests (including Organization, Team, Project)
  - All RBAC middleware must have permission tests
- **MCP Tools:** pytest for MCP tool tests
  - All MCP tools must have unit tests with mock database (including new org/team/project tools)
  - All MCP tool schemas must be validated
  - All MCP tool error paths must be tested
  - All multi-tenant scoping must be tested (org/team/project context)
- **Conversation Flows:** pytest for conversation integration tests
  - All conversation flows must have end-to-end tests
  - All natural language intents must be tested
  - All conversation state persistence must be tested
- **Multi-Tenant Isolation Tests (NEW - Phase 3.1):**
  - All organization boundaries must be tested (no cross-org data leakage)
  - All team boundaries must be tested (no cross-team access)
  - All project boundaries must be tested (no cross-project access)
  - All RBAC rules must be tested (role-based access enforcement)
  - All permission inheritance must be tested (org → team → project)
- **Invitation System Tests (NEW - Phase 3.1):**
  - All invitation creation flows must be tested
  - All invitation acceptance flows must be tested
  - All invitation expiration logic must be tested
  - All role assignment on invitation acceptance must be tested
- **Audit Trail Tests (NEW - Phase 3.1):**
  - All audit log creation must be tested (who, what, when)
  - All audit log queries must be tested (permission-based access)
  - All soft delete operations must be tested
- **Container Testing:** Docker image validation (unchanged from Phase 4)
- **Deployment Validation:** Kubernetes deployment tests (unchanged from Phase 4)
- Tests written first → User approved → Tests fail → Then implement
- Edge cases and error paths must have tests
- Tests must be deterministic and isolated

**Rationale:** TDD ensures correctness, prevents regression, and serves as executable documentation for backend, MCP tools, AI agent behavior, containerization, Kubernetes deployment, multi-tenant isolation, RBAC enforcement, and collaborative workflows.

### III. YAGNI Principle (Phase 3.1 Scope - Multi-Tenancy & Collaboration)
"You Aren't Gonna Need It" - Implement multi-tenant features (Organization, Team, Project hierarchy), RBAC, collaboration, invitations, and audit trails for Phase 3.1. No CRM features, no billing, no advanced analytics yet.

**Phase 3.1 Features - Multi-Tenancy & Collaboration:**
1. Organization Management – Create/update/delete organizations, invite members
2. Team Management – Create teams within organizations, manage team members
3. Project Management – Create projects within teams, assign tasks to projects
4. RBAC – Organization/Team/Project roles with permission inheritance
5. Invitation System – Email-based invitations with role assignment
6. Audit Trails – Track all modifications (who, what, when) for compliance
7. Task Assignment – Assign tasks to team members (collaborative workflows)
8. Soft Delete – Recoverable deletion for organizations, teams, projects, tasks

**Phase 3.1 Implementation Requirements:**
- All Phase 4 Kubernetes features MUST continue working (containerization, HPA, stateless architecture)
- All Phase 3 chatbot features (all 10 task features via natural language) MUST continue working
- Data model: User → Organization → Team → Project → Task hierarchy
- RBAC: Organization (Owner, Admin, Member), Team (Lead, Member), Project (Manager, Contributor, Viewer)
- Invitation flow: Create invitation → Send email → Accept invitation → Join org/team/project with role
- Audit log: Record all CRUD operations on organizations, teams, projects, tasks with user_id, timestamp, action
- Soft delete: Mark as deleted (deleted_at timestamp), allow recovery within 30 days
- Database indexes for multi-tenant queries (org_id, team_id, project_id)
- Row-level security enforcing tenant boundaries
- Better Auth integration for organization context
- MCP tools for organization/team/project management
- API endpoints for organizations, teams, projects, invitations, members (RESTful)

**Forbidden in Phase 3.1:**
- ❌ CRM features (customer management, sales pipelines - Phase 6)
- ❌ Billing and subscription management (Phase 6)
- ❌ Advanced analytics and reporting (Phase 6)
- ❌ Time tracking and productivity metrics (Phase 6)
- ❌ File attachments and document management (Phase 6)
- ❌ Real-time collaboration (live editing, presence - Phase 6)
- ❌ Mobile apps (iOS/Android - Phase 6)
- ❌ Any feature beyond multi-tenancy, RBAC, collaboration, and audit trails

**Rationale:** Phase 3.1 delivers collaborative, multi-tenant task management with organizations, teams, and projects. This enables team-based workflows while preserving all Phase 4 Kubernetes features. Advanced features come in Phase 6.

### IV. Technology Stack Requirements (Phase 3.1)
Phase 3.1 MUST use the Phase 4 technology stack with enhancements for multi-tenancy. No substitutions.

**Mandatory Stack:**

**Containerization:** (unchanged from Phase 4)
- **Container Runtime:** Docker Desktop (latest stable)
- **Docker AI:** Docker AI Agent (Gordon) for intelligent container operations
- **Base Images:** Node 22-alpine (frontend), Python 3.13-slim (backend)
- **Multi-Stage Builds:** Required for frontend and backend
- **Health Checks:** Mandatory in all Dockerfiles

**Orchestration:** (unchanged from Phase 4)
- **Platform:** Kubernetes via Minikube (local)
- **K8s Version:** Latest stable (1.28+)
- **Package Manager:** Helm 3.x
- **AIOps Tools:** kubectl-ai, Kagent

**Frontend:**
- **Framework:** OpenAI ChatKit (hosted or self-hosted)
- **Runtime:** Next.js 16+ (App Router)
- **Language:** TypeScript (strict mode)
- **Styling:** Tailwind CSS
- **Authentication:** Better Auth with JWT (ENHANCED for organization support)
- **Container:** Node 22-alpine with Next.js production build

**Backend:**
- **Framework:** Python FastAPI
- **Language:** Python 3.13+
- **AI Framework:** OpenAI Agents SDK
- **MCP Server:** Official MCP SDK (Python)
- **ORM:** SQLModel
- **Database:** Neon Serverless PostgreSQL (external to cluster)
- **Package Manager:** UV (not pip, not poetry)
- **Container:** Python 3.13-slim with production dependencies
- **RBAC Library:** (built-in FastAPI dependencies for permission checking)

**Testing & Quality:** (unchanged from Phase 4)
- **Backend Testing:** pytest, pytest-cov
- **Container Testing:** Docker health checks, Trivy security scanner
- **Deployment Testing:** kubectl, Helm test hooks
- **Type Checking:** mypy (Python), TypeScript compiler
- **Linting:** ruff (Python), ESLint (TypeScript)
- **Formatting:** ruff format (Python), Prettier (TypeScript)

**Deployment (Phase 3.1):** (unchanged from Phase 4)
- **Local Cluster:** Minikube with Docker driver
- **Container Registry:** Docker Hub (public) or local registry
- **Frontend Hosting:** Kubernetes Service (NodePort or LoadBalancer)
- **Backend Hosting:** Kubernetes Service (ClusterIP)
- **Database:** Neon Serverless PostgreSQL (external, accessed via K8s Secret)

**Multi-Tenancy Enhancements (NEW - Phase 3.1):**
- **Better Auth:** Extended with organization_id claim in JWT tokens
- **Database Models:** Organization, Team, Project, OrganizationMember, TeamMember, ProjectMember, Invitation, AuditLog
- **Row-Level Security:** SQLModel queries filtered by org_id, team_id, project_id
- **RBAC Middleware:** FastAPI dependencies for permission checking
- **Audit Logging:** Automatic logging of all CRUD operations to AuditLog table

**Rules:**
- All dependencies managed via `pyproject.toml` (backend) and `package.json` (frontend)
- Must use monorepo structure with `frontend/`, `backend/`, `docker/`, `k8s/`, and `helm/` folders
- All sensitive data (API keys, DB credentials) stored in Kubernetes Secrets
- JWT tokens for authentication between frontend and backend (now include org_id, team_id, project_id claims)
- MCP server runs within FastAPI backend container
- OpenAI API key stored in Kubernetes Secret (`OPENAI_API_KEY`)
- Neon database connection string stored in Kubernetes Secret (`DATABASE_URL`)
- Better Auth secret stored in Kubernetes Secret (`BETTER_AUTH_SECRET`)

**Rationale:** Standardization ensures consistency and prepares for Phase 5 (cloud deployment). Multi-tenancy enhancements enable organization/team/project hierarchy with RBAC while maintaining Phase 4 Kubernetes architecture.

### V. Clean Code & Modularity (Phase 3.1 - Monorepo with RBAC & Audit Modules)
Code, Dockerfiles, K8s manifests, Helm charts, RBAC logic, and audit trail implementations MUST be well-organized, modular, and follow clean code principles. Phase 3.1 extends monorepo structure with RBAC and audit modules.

**Organization Requirements:**
- Separation of concerns (application code, container configs, K8s manifests, Helm charts, RBAC logic, audit logging)
- Single Responsibility Principle for all functions, classes, components, MCP tools, Dockerfiles, and K8s resources
- Clear, descriptive naming (no abbreviations like `td`, `lst`, `mgr`, `k8s-svc-1`, `org-mgr`)
- Maximum function length: 20 lines (excluding docstrings)
- Maximum file length: 200 lines (300 for complex API routes, MCP tools, RBAC middleware, or Helm templates)

**Phase 3.1 Project Structure:**
```
evolved-todo/
├── .specify/
│   └── memory/
│       └── constitution.md
├── specs/
│   ├── overview.md
│   ├── architecture.md
│   ├── features/          # Feature specifications
│   ├── api/               # API specifications
│   ├── database/          # Database schema (UPDATED - Phase 3.1)
│   ├── mcp/               # MCP tool specifications
│   ├── ui/                # ChatKit UI specs
│   ├── rbac/              # RBAC specifications (NEW - Phase 3.1)
│   ├── docker/            # Docker specifications
│   ├── kubernetes/        # K8s deployment specs
│   └── helm/              # Helm chart specs
├── frontend/
│   ├── CLAUDE.md
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── app/               # Next.js App Router pages
│   ├── components/        # ChatKit integration (UPDATED - org/team/project UI)
│   ├── lib/               # API client for chat endpoint
│   ├── types/             # TypeScript types (UPDATED - org/team/project types)
│   └── __tests__/         # Frontend tests
├── backend/
│   ├── CLAUDE.md
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── app/
│   │   ├── main.py        # FastAPI entry point with health checks
│   │   ├── models.py      # SQLModel database models (UPDATED - Phase 3.1)
│   │   ├── routes/        # API route handlers (UPDATED - Phase 3.1)
│   │   │   ├── tasks.py
│   │   │   ├── organizations.py  # (NEW - Phase 3.1)
│   │   │   ├── teams.py          # (NEW - Phase 3.1)
│   │   │   ├── projects.py       # (NEW - Phase 3.1)
│   │   │   ├── invitations.py    # (NEW - Phase 3.1)
│   │   │   └── members.py        # (NEW - Phase 3.1)
│   │   ├── services/      # Business logic (UPDATED - Phase 3.1)
│   │   │   ├── task_service.py
│   │   │   ├── organization_service.py  # (NEW - Phase 3.1)
│   │   │   ├── team_service.py          # (NEW - Phase 3.1)
│   │   │   ├── project_service.py       # (NEW - Phase 3.1)
│   │   │   └── invitation_service.py    # (NEW - Phase 3.1)
│   │   ├── mcp/           # MCP server and tools (UPDATED - Phase 3.1)
│   │   │   ├── server.py
│   │   │   └── tools/
│   │   │       ├── task_tools.py
│   │   │       ├── organization_tools.py  # (NEW - Phase 3.1)
│   │   │       ├── team_tools.py          # (NEW - Phase 3.1)
│   │   │       └── project_tools.py       # (NEW - Phase 3.1)
│   │   ├── rbac/          # RBAC middleware (NEW - Phase 3.1)
│   │   │   ├── permissions.py   # Permission definitions
│   │   │   ├── roles.py         # Role definitions
│   │   │   └── middleware.py    # Permission checking middleware
│   │   ├── audit/         # Audit trail (NEW - Phase 3.1)
│   │   │   ├── logger.py        # Audit log creation
│   │   │   └── models.py        # AuditLog model
│   │   ├── agents/        # OpenAI Agents SDK configuration
│   │   ├── auth.py        # JWT authentication (UPDATED - org/team/project claims)
│   │   ├── db.py          # Database connection
│   │   └── health.py      # Health check endpoints
│   └── tests/             # Backend tests (UPDATED - Phase 3.1)
│       ├── test_organizations.py
│       ├── test_teams.py
│       ├── test_projects.py
│       ├── test_rbac.py
│       └── test_audit.py
├── k8s/                   # Kubernetes manifests
├── helm/                  # Helm charts
├── docker-compose.yml
├── AGENTS.md
├── CLAUDE.md
└── README.md
```

**Rationale:** Clear structure separates application code, containerization configs, orchestration manifests, RBAC logic, and audit trail implementations, making Phase 3.1 multi-tenant architecture easy to understand, maintain, and extend for Phase 5.

### VI. Type Safety (Phase 3.1 - Python, TypeScript & YAML Validation)
All functions MUST have complete type annotations. All manifests MUST be validated. Type checking MUST pass without errors for Python, TypeScript, and Kubernetes YAML.

**Backend (Python) Requirements:**
- Function signatures: parameters and return types fully annotated
- Class attributes: type annotations required
- No `Any` types unless explicitly justified
- Use generic types (`list[Task]`, not `list`)
- Enable strict mypy mode
- SQLModel models with proper type hints (including Organization, Team, Project)
- MCP tool input/output schemas fully typed (including new org/team/project tools)
- RBAC permission functions fully typed (role enums, permission checks)

**Frontend (TypeScript) Requirements:**
- Enable strict mode in `tsconfig.json`
- All component props fully typed (no implicit `any`)
- API response types defined and validated (including org/team/project types)
- ChatKit props and event handlers fully typed
- Use TypeScript generics where appropriate
- Avoid type assertions (`as`) unless necessary
- Organization/Team/Project types fully defined

**Infrastructure (YAML Validation) Requirements:** (unchanged from Phase 4)
- All Kubernetes manifests validated with `kubectl --dry-run=client`
- All Helm templates validated with `helm lint`
- All Helm values validated with JSON Schema
- No deprecated API versions
- All resource requests and limits specified
- All required labels present (app, component, version)

**Rationale:** Type safety catches bugs at compile time, improves IDE support, and serves as inline documentation. YAML validation prevents deployment failures from invalid manifests.

### VII. Comprehensive Documentation (Phase 3.1 - Multi-Tenancy & RBAC)
Documentation MUST be thorough, clear, and maintained alongside code. Phase 3.1 includes multi-tenancy documentation, RBAC permission matrices, invitation workflows, and audit trail usage.

**Required Documentation:**

1. **README.md:**
   - Project overview and Phase 3.1 scope (multi-tenancy, RBAC, collaboration)
   - Prerequisites (Docker Desktop, Minikube, Helm, kubectl-ai, Kagent)
   - Quick start guide for local development
   - Environment variables and Kubernetes Secrets
   - Running locally (docker-compose for dev, Minikube for prod simulation)
   - Running tests (backend, MCP tools, conversation flows, container tests, RBAC tests)
   - Deployment instructions (Minikube setup, Helm deployment)

2. **Multi-Tenancy Documentation (NEW - Phase 3.1):**
   - Organization/Team/Project hierarchy explanation
   - Data model: Organization → Team → Project → Task
   - Organization creation and member invitation flows
   - Team creation within organizations
   - Project creation within teams
   - Task assignment to projects and team members

3. **RBAC Documentation (NEW - Phase 3.1):**
   - Role definitions (Organization: Owner/Admin/Member, Team: Lead/Member, Project: Manager/Contributor/Viewer)
   - Permission matrix (who can do what at each level)
   - Permission inheritance (org → team → project)
   - Role assignment workflows (via invitations)
   - Permission checking patterns in code

4. **Invitation System Documentation (NEW - Phase 3.1):**
   - Invitation creation flow (org/team/project admins create invitations)
   - Email delivery mechanism (or placeholder for email service)
   - Invitation acceptance flow (user clicks link, joins with role)
   - Invitation expiration policy (default 7 days)
   - Role assignment on acceptance

5. **Audit Trail Documentation (NEW - Phase 3.1):**
   - What events are logged (all CRUD operations)
   - Audit log schema (user_id, resource_type, resource_id, action, timestamp, metadata)
   - Who can view audit logs (org admins, team leads, project managers)
   - Audit log retention policy (180 days)
   - Querying audit logs via API

6. **API Documentation:**
   - All API endpoints documented in `specs/api/rest-endpoints.md` (UPDATED - Phase 3.1)
   - Organization endpoints: GET/POST/PUT/DELETE /organizations, /organizations/{id}/members
   - Team endpoints: GET/POST/PUT/DELETE /teams, /teams/{id}/members
   - Project endpoints: GET/POST/PUT/DELETE /projects, /projects/{id}/members
   - Invitation endpoints: POST /invitations, PUT /invitations/{id}/accept
   - Member endpoints: GET/DELETE /organizations/{id}/members/{user_id}
   - Task endpoints (unchanged from Phase 3)
   - Chat endpoint specification (UPDATED - org/team/project context)
   - Request/response schemas with examples
   - Authentication requirements (JWT token header with org/team/project claims)
   - Error response formats

7. **MCP Tool Documentation:**
   - All MCP tools documented in `specs/mcp/tools.md` (UPDATED - Phase 3.1)
   - Organization tools: create_organization, list_organizations, update_organization, delete_organization
   - Team tools: create_team, list_teams, add_team_member, remove_team_member
   - Project tools: create_project, list_projects, assign_task_to_project
   - Task tools (unchanged from Phase 3)
   - Tool schemas (input parameters, output format)
   - Tool behavior and side effects
   - Error handling for each tool
   - Usage examples with natural language triggers

8. **Database Schema Documentation:**
   - Schema documented in `specs/database/schema.md` (UPDATED - Phase 3.1)
   - All tables: User, Organization, Team, Project, Task, OrganizationMember, TeamMember, ProjectMember, Invitation, Conversation, Message, AuditLog
   - All columns, relationships, indexes
   - Foreign key constraints
   - Unique constraints
   - Multi-tenant indexing strategy (org_id, team_id, project_id)
   - Soft delete columns (deleted_at)

9. **Docstrings/Comments (Backend):**
   - All public functions, classes, methods (Google style)
   - Include Args, Returns, Raises sections
   - FastAPI route handlers with OpenAPI descriptions
   - MCP tools with schema documentation
   - RBAC permission functions with role/permission documentation

10. **Docker Documentation:** (unchanged from Phase 4)
11. **Kubernetes Documentation:** (unchanged from Phase 4)
12. **Helm Documentation:** (unchanged from Phase 4)

**Rationale:** Comprehensive docs enable onboarding, facilitate review, and prepare for Phase 5. Multi-tenancy and RBAC documentation critical for understanding hierarchical data model and permission system.

### VIII. Error Handling (Phase 3.1 - Container & K8s Resilience + RBAC Errors)
Errors MUST be handled explicitly and gracefully at all layers: application, container, and orchestration. No silent failures. Phase 3.1 adds RBAC permission errors, invitation errors, and organization hierarchy errors.

**Backend (FastAPI) Requirements:**
- Validate all inputs with Pydantic models
- Use HTTPException with appropriate status codes
- Return structured error responses with `detail` field
- Handle database errors (connection, constraints, etc.)
- Handle OpenAI API errors (rate limits, timeouts, etc.)
- Handle MCP tool errors (invalid input, tool failure, etc.)
- Handle RBAC permission errors (403 Forbidden with clear message)
- Handle organization hierarchy errors (team not in org, project not in team)
- Handle invitation errors (expired, already accepted, invalid role)
- Log errors for debugging (structured logging with JSON)

**RBAC Permission Errors (NEW - Phase 3.1):**
- `403 Forbidden` - User lacks permission (e.g., "Not an organization admin")
- `403 Forbidden` - Resource not in user's scope (e.g., "Team not in your organization")
- `403 Forbidden` - Hierarchical violation (e.g., "Cannot assign task to project in different team")
- All permission errors include clear, user-friendly messages

**Invitation Errors (NEW - Phase 3.1):**
- `400 Bad Request` - Invalid invitation data (missing email, invalid role)
- `404 Not Found` - Invitation not found or expired
- `409 Conflict` - User already member of organization/team/project
- `410 Gone` - Invitation already accepted

**Organization Hierarchy Errors (NEW - Phase 3.1):**
- `400 Bad Request` - Team not in organization
- `400 Bad Request` - Project not in team
- `400 Bad Request` - Task not in project
- `409 Conflict` - Circular dependency detected

**Container Health Checks:** (unchanged from Phase 4)
**Kubernetes Probes:** (unchanged from Phase 4)
**Deployment Error Recovery:** (unchanged from Phase 4)
**MCP Tool Requirements:** (unchanged from Phase 3, UPDATED for multi-tenancy)
**Frontend (ChatKit) Requirements:** (unchanged from Phase 3)

**HTTP Status Codes:**
- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid input validation
- `401 Unauthorized` - Missing or invalid JWT token
- `403 Forbidden` - User doesn't have permission (RBAC)
- `404 Not Found` - Resource doesn't exist
- `409 Conflict` - Resource conflict (duplicate, circular dependency)
- `410 Gone` - Resource permanently deleted or expired
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - OpenAI API or database unavailable

**Rationale:** Explicit error handling with container health checks, Kubernetes probes, and RBAC permission errors ensures resilient deployments and clear user feedback for multi-tenant access control.

### IX. Multi-Tenant Data Isolation & Security (Phase 3.1 - Hierarchical Scoping)
Every user MUST only see and modify data within their organization/team/project scope. Multi-tenant data isolation is MANDATORY with hierarchical scoping (Organization → Team → Project → Task). Authentication and authorization are mandatory for all API endpoints.

**Authentication Requirements:** (unchanged from Phase 3, ENHANCED for multi-tenancy)
- **Better Auth** on Next.js frontend for user signup/signin
- JWT tokens issued by Better Auth upon successful login
- JWT tokens include `user_id`, `org_id` (current organization), `team_id` (current team), `project_id` (current project) claims
- Tokens expire after 7 days (configurable)
- Refresh tokens supported for seamless re-authentication

**Multi-Tenant Hierarchy (NEW - Phase 3.1):**
```
Organization (tenant boundary)
├── Team 1
│   ├── Project A
│   │   └── Tasks
│   └── Project B
│       └── Tasks
└── Team 2
    └── Project C
        └── Tasks
```

**Authorization Requirements:**
- All API endpoints require valid JWT token in `Authorization: Bearer <token>` header
- Requests without token receive `401 Unauthorized`
- Backend extracts `user_id`, `org_id`, `team_id`, `project_id` from JWT token
- All database queries filtered by organization/team/project scope
- **Organization-level access:** User must be member of organization
- **Team-level access:** User must be member of team (and team must be in user's organization)
- **Project-level access:** User must be member of project (and project must be in user's team)
- **Task-level access:** User must have access to project containing the task
- Path parameters MUST match JWT token claims for scope validation

**Row-Level Security (NEW - Phase 3.1):**
- All database queries automatically filtered by `org_id` (organization boundary)
- Team queries filtered by `org_id` AND `team_id`
- Project queries filtered by `org_id` AND `team_id` AND `project_id`
- Task queries filtered by `org_id` AND `team_id` AND `project_id`
- No cross-organization data leakage allowed
- Database indexes on `org_id`, `team_id`, `project_id` for query performance

**RBAC Integration (see Principle XX):**
- Organization roles: Owner, Admin, Member
- Team roles: Team Lead, Member
- Project roles: Project Manager, Contributor, Viewer
- Permission inheritance: Organization → Team → Project
- Fine-grained permissions enforced via RBAC middleware

**Kubernetes Secrets Management:** (unchanged from Phase 4)
**Container Security:** (unchanged from Phase 4)
**Network Security:** (unchanged from Phase 4)
**MCP Tool Security:**
- All MCP tools receive `user_id`, `org_id`, `team_id`, `project_id` parameters
- All MCP tools filter database queries by organization/team/project scope
- MCP tools enforce RBAC permissions before operations
- MCP tools never expose data from other organizations/teams/projects
- Agent cannot override multi-tenant isolation or RBAC

**Rationale:** Multi-tenant data isolation with hierarchical scoping ensures privacy and security across organizations, teams, and projects. Kubernetes Secrets provide secure credential storage. RBAC enforces fine-grained access control.

### X. Database Schema & Migration Management (Phase 3.1 - Multi-Tenant Models)
Database schema MUST be versioned, documented, and managed through migrations. Phase 3.1 expands schema with Organization, Team, Project, membership tables, invitations, and audit logs.

**Database Requirements:**
- **Provider:** Neon Serverless PostgreSQL (managed, external to K8s cluster)
- **ORM:** SQLModel (combines SQLAlchemy + Pydantic)
- **Migrations:** SQLModel automatic table creation (Phase 3.1 - manual migrations recommended for Phase 5+)
- **Connection:** Connection string from Kubernetes Secret (`DATABASE_URL`)
- **Access:** Backend pods connect to Neon cloud endpoint (not in cluster)

**Schema Design Rules:**
- All tables include `id` (primary key, UUID), `created_at`, `updated_at` timestamps
- Multi-tenant tables include `org_id` (foreign key to Organization)
- Team tables include `org_id` AND `team_id`
- Project tables include `org_id` AND `team_id` AND `project_id`
- Use appropriate indexes for query performance (especially multi-tenant queries)
- Foreign keys for relationships with CASCADE/SET NULL policies
- NOT NULL constraints for required fields
- VARCHAR limits for text fields
- Unique constraints where appropriate (e.g., email per organization)
- Soft delete columns (`deleted_at` timestamp) for recoverable deletion

**Phase 3.1 Database Models:**

**1. User** (managed by Better Auth, ENHANCED for multi-tenancy)
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**2. Organization** (NEW - Phase 3.1)
```sql
CREATE TABLE organizations (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  slug VARCHAR(100) UNIQUE NOT NULL,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_at TIMESTAMP NULL
);
CREATE INDEX idx_org_slug ON organizations(slug);
CREATE INDEX idx_org_deleted ON organizations(deleted_at) WHERE deleted_at IS NULL;
```

**3. OrganizationMember** (NEW - Phase 3.1)
```sql
CREATE TABLE organization_members (
  id UUID PRIMARY KEY,
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  role VARCHAR(50) NOT NULL, -- 'owner', 'admin', 'member'
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(org_id, user_id)
);
CREATE INDEX idx_org_member_org ON organization_members(org_id);
CREATE INDEX idx_org_member_user ON organization_members(user_id);
```

**4. Team** (NEW - Phase 3.1)
```sql
CREATE TABLE teams (
  id UUID PRIMARY KEY,
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_at TIMESTAMP NULL,
  UNIQUE(org_id, name)
);
CREATE INDEX idx_team_org ON teams(org_id);
CREATE INDEX idx_team_deleted ON teams(deleted_at) WHERE deleted_at IS NULL;
```

**5. TeamMember** (NEW - Phase 3.1)
```sql
CREATE TABLE team_members (
  id UUID PRIMARY KEY,
  team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  role VARCHAR(50) NOT NULL, -- 'lead', 'member'
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(team_id, user_id)
);
CREATE INDEX idx_team_member_team ON team_members(team_id);
CREATE INDEX idx_team_member_user ON team_members(user_id);
```

**6. Project** (NEW - Phase 3.1)
```sql
CREATE TABLE projects (
  id UUID PRIMARY KEY,
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_at TIMESTAMP NULL,
  UNIQUE(team_id, name)
);
CREATE INDEX idx_project_org ON projects(org_id);
CREATE INDEX idx_project_team ON projects(team_id);
CREATE INDEX idx_project_deleted ON projects(deleted_at) WHERE deleted_at IS NULL;
```

**7. ProjectMember** (NEW - Phase 3.1)
```sql
CREATE TABLE project_members (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  role VARCHAR(50) NOT NULL, -- 'manager', 'contributor', 'viewer'
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(project_id, user_id)
);
CREATE INDEX idx_project_member_project ON project_members(project_id);
CREATE INDEX idx_project_member_user ON project_members(user_id);
```

**8. Task** (UPDATED from Phase 3 - add org/team/project foreign keys)
```sql
CREATE TABLE tasks (
  id UUID PRIMARY KEY,
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE, -- task owner
  assigned_to UUID REFERENCES users(id) ON DELETE SET NULL, -- assigned team member (NEW)
  title VARCHAR(500) NOT NULL,
  description TEXT,
  status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'in_progress', 'completed'
  priority VARCHAR(50) DEFAULT 'medium', -- 'low', 'medium', 'high', 'urgent'
  due_date TIMESTAMP NULL,
  completed_at TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_at TIMESTAMP NULL
);
CREATE INDEX idx_task_org ON tasks(org_id);
CREATE INDEX idx_task_team ON tasks(team_id);
CREATE INDEX idx_task_project ON tasks(project_id);
CREATE INDEX idx_task_user ON tasks(user_id);
CREATE INDEX idx_task_assigned ON tasks(assigned_to);
CREATE INDEX idx_task_status ON tasks(status);
CREATE INDEX idx_task_deleted ON tasks(deleted_at) WHERE deleted_at IS NULL;
```

**9. Invitation** (NEW - Phase 3.1)
```sql
CREATE TABLE invitations (
  id UUID PRIMARY KEY,
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  team_id UUID REFERENCES teams(id) ON DELETE SET NULL, -- NULL for org-level invitations
  project_id UUID REFERENCES projects(id) ON DELETE SET NULL, -- NULL for team-level invitations
  email VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL, -- role to assign on acceptance
  invited_by UUID REFERENCES users(id),
  accepted_at TIMESTAMP NULL,
  accepted_by UUID REFERENCES users(id) ON DELETE SET NULL,
  expires_at TIMESTAMP NOT NULL, -- default 7 days
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_invitation_org ON invitations(org_id);
CREATE INDEX idx_invitation_email ON invitations(email);
CREATE INDEX idx_invitation_expires ON invitations(expires_at);
```

**10. Conversation** (unchanged from Phase 3)
**11. Message** (unchanged from Phase 3)

**12. AuditLog** (NEW - Phase 3.1)
```sql
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY,
  org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  resource_type VARCHAR(50) NOT NULL, -- 'organization', 'team', 'project', 'task', etc.
  resource_id UUID NOT NULL,
  action VARCHAR(50) NOT NULL, -- 'create', 'update', 'delete', 'restore'
  metadata JSONB, -- additional context (old_value, new_value, etc.)
  created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_audit_org ON audit_logs(org_id);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at);
```

**Migration Strategy (Phase 3.1):**
- SQLModel creates tables automatically on first run
- Use `create_db_and_tables()` in `app/db.py`
- Connection string from Kubernetes Secret
- Manual migrations recommended for Phase 5+ (use Alembic)
- Schema documented in `specs/database/schema.md`
- Data migration script for existing single-user tasks → personal organization

**Kubernetes Database Access:** (unchanged from Phase 4)

**Rationale:** Multi-tenant database schema with Organization → Team → Project → Task hierarchy enables collaborative task management. Membership tables support RBAC. Invitation table enables onboarding. AuditLog provides compliance and change tracking.

### XI. API Design & RESTful Conventions (Phase 3.1 - Multi-Tenant Endpoints)
All API endpoints MUST follow RESTful conventions and return consistent, predictable responses. Phase 3.1 adds organization, team, project, invitation, and member management endpoints.

**RESTful Endpoint Design:**

**Organization Endpoints (NEW - Phase 3.1):**
| Method | Endpoint | Description | Auth | Success |
|--------|----------|-------------|------|---------|
| GET | `/api/organizations` | List user's organizations | JWT (user) | `200 OK` + Organization[] |
| POST | `/api/organizations` | Create organization | JWT (user) | `201 Created` + Organization |
| GET | `/api/organizations/{org_id}` | Get organization | JWT (org member) | `200 OK` + Organization |
| PUT | `/api/organizations/{org_id}` | Update organization | JWT (org admin) | `200 OK` + Organization |
| DELETE | `/api/organizations/{org_id}` | Delete organization (soft) | JWT (org owner) | `204 No Content` |
| GET | `/api/organizations/{org_id}/members` | List organization members | JWT (org member) | `200 OK` + OrganizationMember[] |
| POST | `/api/organizations/{org_id}/members` | Invite member | JWT (org admin) | `201 Created` + Invitation |
| DELETE | `/api/organizations/{org_id}/members/{user_id}` | Remove member | JWT (org admin) | `204 No Content` |

**Team Endpoints (NEW - Phase 3.1):**
| Method | Endpoint | Description | Auth | Success |
|--------|----------|-------------|------|---------|
| GET | `/api/organizations/{org_id}/teams` | List organization teams | JWT (org member) | `200 OK` + Team[] |
| POST | `/api/organizations/{org_id}/teams` | Create team | JWT (org admin) | `201 Created` + Team |
| GET | `/api/teams/{team_id}` | Get team | JWT (team member) | `200 OK` + Team |
| PUT | `/api/teams/{team_id}` | Update team | JWT (team lead) | `200 OK` + Team |
| DELETE | `/api/teams/{team_id}` | Delete team (soft) | JWT (org admin) | `204 No Content` |
| GET | `/api/teams/{team_id}/members` | List team members | JWT (team member) | `200 OK` + TeamMember[] |
| POST | `/api/teams/{team_id}/members` | Add team member | JWT (team lead) | `201 Created` + TeamMember |
| DELETE | `/api/teams/{team_id}/members/{user_id}` | Remove team member | JWT (team lead) | `204 No Content` |

**Project Endpoints (NEW - Phase 3.1):**
| Method | Endpoint | Description | Auth | Success |
|--------|----------|-------------|------|---------|
| GET | `/api/teams/{team_id}/projects` | List team projects | JWT (team member) | `200 OK` + Project[] |
| POST | `/api/teams/{team_id}/projects` | Create project | JWT (team lead) | `201 Created` + Project |
| GET | `/api/projects/{project_id}` | Get project | JWT (project member) | `200 OK` + Project |
| PUT | `/api/projects/{project_id}` | Update project | JWT (project manager) | `200 OK` + Project |
| DELETE | `/api/projects/{project_id}` | Delete project (soft) | JWT (project manager) | `204 No Content` |
| GET | `/api/projects/{project_id}/members` | List project members | JWT (project member) | `200 OK` + ProjectMember[] |
| POST | `/api/projects/{project_id}/members` | Add project member | JWT (project manager) | `201 Created` + ProjectMember |
| DELETE | `/api/projects/{project_id}/members/{user_id}` | Remove project member | JWT (project manager) | `204 No Content` |

**Invitation Endpoints (NEW - Phase 3.1):**
| Method | Endpoint | Description | Auth | Success |
|--------|----------|-------------|------|---------|
| GET | `/api/invitations` | List user's pending invitations | JWT (user) | `200 OK` + Invitation[] |
| POST | `/api/invitations` | Create invitation | JWT (admin) | `201 Created` + Invitation |
| PUT | `/api/invitations/{id}/accept` | Accept invitation | JWT (invitee) | `200 OK` + Membership |
| DELETE | `/api/invitations/{id}` | Cancel invitation | JWT (inviter or admin) | `204 No Content` |

**Task Endpoints (UPDATED from Phase 3 - add project scoping):**
| Method | Endpoint | Description | Auth | Success |
|--------|----------|-------------|------|---------|
| GET | `/api/projects/{project_id}/tasks` | List project tasks | JWT (project member) | `200 OK` + Task[] |
| POST | `/api/projects/{project_id}/tasks` | Create task | JWT (project contributor) | `201 Created` + Task |
| GET | `/api/tasks/{task_id}` | Get task | JWT (project member) | `200 OK` + Task |
| PUT | `/api/tasks/{task_id}` | Update task | JWT (task owner or manager) | `200 OK` + Task |
| DELETE | `/api/tasks/{task_id}` | Delete task (soft) | JWT (task owner or manager) | `204 No Content` |
| PATCH | `/api/tasks/{task_id}/complete` | Toggle complete | JWT (task owner or assignee) | `200 OK` + Task |
| PATCH | `/api/tasks/{task_id}/assign` | Assign to team member | JWT (project manager) | `200 OK` + Task |

**Chat Endpoint (UPDATED from Phase 3 - add org/team/project context):**
| Method | Endpoint | Description | Auth | Success |
|--------|----------|-------------|------|---------|
| POST | `/api/chat` | Send chat message | JWT (user with org/team/project context) | `200 OK` + Response |

**Health Check Endpoint:** (unchanged from Phase 4)
| Method | Endpoint | Description | Auth | Success |
|--------|----------|-------------|------|---------|
| GET | `/health` | Backend health | None | `200 OK` + Status |

**API Conventions:**
- All endpoints prefixed with `/api`
- Multi-tenant endpoints include `{org_id}`, `{team_id}`, `{project_id}` path parameters
- Use plural nouns for resources (`/tasks`, `/teams`, `/projects`)
- Use HTTP methods semantically
- Return appropriate status codes
- Return JSON responses with consistent structure
- RBAC enforced on all endpoints (see Principle XX)

**Rationale:** RESTful conventions ensure predictable APIs. Multi-tenant endpoints enable organization/team/project hierarchy management. RBAC integration ensures permission-based access control.

### XII. AI Agent Development & MCP Server Architecture (Phase 3.1 - Multi-Tenant Tools)
AI agents and MCP tools MUST be developed with clear separation of concerns, testability, and deterministic behavior. Phase 3.1 adds organization, team, and project management tools with multi-tenant scoping.

**MCP Server Requirements:**
- MCP server runs within FastAPI backend container
- Official MCP SDK (Python) for tool registration
- All tools registered with schemas (input/output types)
- Tools are stateless: receive input, return output, no side effects beyond database
- Tools never maintain internal state (all state in database)
- All tools enforce multi-tenant scoping (org_id, team_id, project_id)
- All tools enforce RBAC permissions before operations

**Phase 3.1 Container Considerations:** (unchanged from Phase 4)

**MCP Tool Design Rules:**
- Each tool is a single-purpose function
- Clear input/output schemas with Pydantic models
- Error responses part of output schema
- Tools validate inputs before execution
- Tools handle errors gracefully (no crashes)
- Tools are fully testable with mock database
- Tools receive `user_id`, `org_id`, `team_id`, `project_id` parameters
- Tools check RBAC permissions before operations

**Phase 3 MCP Tools:** (unchanged - task management)
- add_task, list_tasks, search_tasks, complete_task, delete_task, update_task

**Phase 3.1 MCP Tools (NEW - Multi-Tenant Management):**

**Organization Tools:**
- `create_organization(user_id, name, slug)` → Organization
- `list_organizations(user_id)` → Organization[]
- `get_organization(user_id, org_id)` → Organization
- `update_organization(user_id, org_id, name)` → Organization (requires admin)
- `delete_organization(user_id, org_id)` → Success (requires owner)
- `list_organization_members(user_id, org_id)` → OrganizationMember[]
- `invite_organization_member(user_id, org_id, email, role)` → Invitation (requires admin)
- `remove_organization_member(user_id, org_id, member_user_id)` → Success (requires admin)

**Team Tools:**
- `create_team(user_id, org_id, name, description)` → Team (requires org admin)
- `list_teams(user_id, org_id)` → Team[]
- `get_team(user_id, team_id)` → Team (requires team member)
- `update_team(user_id, team_id, name, description)` → Team (requires team lead)
- `delete_team(user_id, team_id)` → Success (requires org admin)
- `add_team_member(user_id, team_id, member_user_id, role)` → TeamMember (requires team lead)
- `remove_team_member(user_id, team_id, member_user_id)` → Success (requires team lead)

**Project Tools:**
- `create_project(user_id, team_id, name, description)` → Project (requires team lead)
- `list_projects(user_id, team_id)` → Project[]
- `get_project(user_id, project_id)` → Project (requires project member)
- `update_project(user_id, project_id, name, description)` → Project (requires project manager)
- `delete_project(user_id, project_id)` → Success (requires project manager)
- `add_project_member(user_id, project_id, member_user_id, role)` → ProjectMember (requires project manager)
- `remove_project_member(user_id, project_id, member_user_id)` → Success (requires project manager)
- `assign_task_to_project(user_id, task_id, project_id)` → Task (requires project contributor)

**OpenAI Agents SDK Integration:**
- Agent initialized with system prompt defining multi-tenant behavior
- Agent has access to all MCP tools (task + org/team/project tools)
- Agent decides which tools to call based on user message and context
- Agent can chain multiple tool calls in single turn
- Agent provides conversational responses wrapping tool outputs
- Agent understands organization/team/project hierarchy
- Agent suggests appropriate actions based on user's current context (org/team/project)

**Natural Language Examples (Phase 3.1):**
- "Create a new team called Engineering in my organization" → create_team tool
- "Add John to the Marketing team" → add_team_member tool
- "Create a project called Website Redesign in the Engineering team" → create_project tool
- "Assign the homepage task to the Website Redesign project" → assign_task_to_project tool
- "Show me all projects in the Engineering team" → list_projects tool
- "Invite sarah@example.com as an admin to my organization" → invite_organization_member tool

**Rationale:** Clear MCP architecture separates AI logic (agent) from operations (tools). Multi-tenant tools enable organization/team/project management via natural language. RBAC enforcement ensures permission-based tool execution.

### XIII. Stateless Architecture & Conversation State Management (Phase 3.1 - Tenant Context)
The chat endpoint MUST be stateless. All conversation state MUST be persisted to database. This architecture is CRITICAL for Kubernetes horizontal scaling. Pods can be added/removed without losing state. Phase 3.1 enhances with tenant context propagation (org/team/project).

**Stateless Server Requirements:**
- Chat endpoint does not maintain in-memory state
- Every request is independent
- Server can be restarted without losing conversations
- **Horizontally scalable:** Any pod can handle any request
- **Kubernetes-native:** Pods can be killed and recreated without impact
- **Autoscaling-compatible:** HPA can scale pods up/down based on load
- **Tenant context included in every request:** org_id, team_id, project_id

**Tenant Context Propagation (NEW - Phase 3.1):**
- JWT token includes `org_id`, `team_id`, `project_id` claims
- Chat endpoint extracts tenant context from JWT
- Tenant context passed to OpenAI agent on every request
- Agent uses tenant context to scope MCP tool calls
- All database queries filtered by tenant context
- No tenant context leakage across organizations/teams/projects

**Kubernetes Scaling Benefits:** (unchanged from Phase 4)

**Conversation State Persistence:**
- Conversation history stored in `conversations` and `messages` tables
- Each request fetches conversation history from database
- Each request stores new user message and assistant response
- Conversation history passed to OpenAI Agents SDK on every request
- Tenant context (org_id, team_id, project_id) stored with conversation

**Request Cycle (UPDATED for Phase 3.1):**
1. Receive user message + optional conversation_id + JWT token
2. Extract `user_id`, `org_id`, `team_id`, `project_id` from JWT
3. Validate user has access to organization/team/project (RBAC)
4. If conversation_id provided, fetch conversation history from database (validate ownership)
5. If no conversation_id, create new conversation record with tenant context
6. Store user message in messages table
7. Build message array for agent (history + new message + tenant context)
8. Run agent with MCP tools (tools receive tenant context)
9. Agent generates response (scoped to tenant context)
10. Store assistant response in messages table
11. Return response to client
12. **Pod forgets everything (ready for next request on any pod)**

**Kubernetes Deployment Pattern:** (unchanged from Phase 4)

**Rationale:** Stateless architecture is MANDATORY for Kubernetes horizontal scaling. Database persistence ensures conversation history survives pod restarts, deletions, and autoscaling events. Tenant context propagation ensures multi-tenant isolation in stateless environment.

### XIV. Natural Language Understanding & Intent Recognition (Phase 3.1 - Multi-Tenant Commands)
The AI agent MUST understand natural language commands and map them to appropriate MCP tool calls. Intent recognition MUST be robust and user-friendly. Phase 3.1 extends NLU to understand organization/team/project management commands.

**Natural Language Command Examples (UPDATED - Phase 3.1):**

**Organization Management:**
- "Create a new organization called Acme Corp"
- "Show me all my organizations"
- "Rename our organization to Acme Corporation"
- "Invite john@acme.com as an admin to our organization"
- "Remove Sarah from our organization"

**Team Management:**
- "Create a team called Engineering"
- "Show all teams in our organization"
- "Add Alice to the Engineering team"
- "Make Bob the lead of the Marketing team"
- "Remove Charlie from the Sales team"

**Project Management:**
- "Create a project called Website Redesign in the Engineering team"
- "Show all projects in the Engineering team"
- "Add Diana to the Website Redesign project as a contributor"
- "Assign the homepage task to the Website Redesign project"
- "Move this task to the Mobile App project"

**Task Management (unchanged from Phase 3):**
- "Add a task to buy groceries"
- "Show me all my pending tasks"
- "Mark task 5 as complete"
- "Assign the API development task to Frank"

**Intent Recognition Rules:**
- Agent must recognize various phrasings for same intent
- Agent must extract entities (org name, team name, project name, user email, role)
- Agent must handle ambiguous requests by asking clarification
- Agent must handle multi-step requests (e.g., "Create a team and add 3 members")
- Agent must understand hierarchical context (org → team → project)
- Agent must suggest appropriate actions based on user's current context

**System Prompt Requirements:**
- Define agent personality (helpful, concise, friendly)
- Define multi-tenant context awareness
- Define tool usage guidelines for org/team/project management
- Define RBAC-aware responses (e.g., "You need to be a team lead to do that")
- Define error handling behavior
- Define confirmation patterns for destructive operations
- Provide example conversations for multi-tenant scenarios

**Rationale:** Robust NLU ensures users can interact naturally with multi-tenant chatbot. Organization/team/project management via natural language reduces friction and improves user experience.

### XV. Containerization & Docker Best Practices (Phase 3.1 - Unchanged)
All application components MUST be containerized using Docker with production-ready best practices. Containers MUST be optimized for size, security, and performance.

(Content unchanged from Phase 4 - see Phase 4 constitution for full details)

### XVI. Kubernetes Deployment & Orchestration (Phase 3.1 - Unchanged)
All application components MUST be deployed on Kubernetes with production-ready manifests. Deployments MUST be scalable, resilient, and observable.

(Content unchanged from Phase 4 - see Phase 4 constitution for full details)

### XVII. Helm Chart Management (Phase 3.1 - Unchanged)
All Kubernetes resources MUST be managed via Helm charts for templating, versioning, and simplified deployment. Charts MUST follow best practices for reusability and maintainability.

(Content unchanged from Phase 4 - see Phase 4 constitution for full details)

### XVIII. AIOps & Infrastructure as Code (Phase 3.1 - Unchanged)
Infrastructure deployment and operations MUST leverage AI-powered tools for intelligent automation, troubleshooting, and optimization. All infrastructure MUST be defined as code.

(Content unchanged from Phase 4 - see Phase 4 constitution for full details)

### XIX. Multi-Tenancy & Data Isolation Hierarchy (NEW - Phase 3.1)
Multi-tenant architecture MUST enforce strict data isolation at every layer (Organization → Team → Project → Task). No cross-organization data leakage allowed. All database queries MUST be scoped to tenant context.

**Tenant Hierarchy:**
```
Organization (Top-level tenant boundary)
  ├── Organization Members (Users with roles: Owner, Admin, Member)
  ├── Teams
  │     ├── Team Members (Users with roles: Lead, Member)
  │     └── Projects
  │           ├── Project Members (Users with roles: Manager, Contributor, Viewer)
  │           └── Tasks
  │                 ├── Task Owner (creator)
  │                 └── Assigned To (optional team member)
```

**Data Isolation Rules:**
- **Organization Boundary:** Top-level tenant isolation
  - All data scoped to `org_id`
  - No user can access data from organizations they're not a member of
  - Organization deletion cascades to all teams, projects, tasks
- **Team Boundary:** Second-level isolation within organization
  - All teams scoped to `org_id` (must belong to organization)
  - Team members must be organization members
  - Team deletion cascades to all projects and tasks
- **Project Boundary:** Third-level isolation within team
  - All projects scoped to `team_id` (must belong to team)
  - Project members must be team members
  - Project deletion cascades to all tasks
- **Task Boundary:** Fourth-level isolation within project
  - All tasks scoped to `project_id` (must belong to project)
  - Task owner and assignee must be project members
  - Task soft-deleted when deleted (recoverable)

**Database Query Scoping:**
- All queries MUST include `WHERE org_id = :org_id`
- Team queries MUST include `WHERE org_id = :org_id AND team_id = :team_id`
- Project queries MUST include `WHERE org_id = :org_id AND team_id = :team_id AND project_id = :project_id`
- Task queries MUST include `WHERE org_id = :org_id AND team_id = :team_id AND project_id = :project_id`
- Never use global queries without tenant scoping

**Indexing Strategy:**
- All multi-tenant tables indexed on `org_id`
- Team tables indexed on `(org_id, team_id)`
- Project tables indexed on `(org_id, team_id, project_id)`
- Task tables indexed on `(org_id, team_id, project_id, user_id)`
- Composite indexes for common query patterns

**N+1 Query Prevention:**
- Use eager loading for relationships (JOIN queries)
- Batch load members when loading teams/projects
- Cache organization/team/project metadata per request
- Avoid loading full object graphs when not needed

**Soft Delete Strategy:**
- Organization soft delete: set `deleted_at` timestamp
- Soft-deleted organizations excluded from queries: `WHERE deleted_at IS NULL`
- Cascade soft delete to teams, projects, tasks
- Recovery within 30 days: set `deleted_at = NULL`
- Hard delete after 30 days (permanent)

**Rationale:** Hierarchical multi-tenant architecture ensures data isolation, prevents cross-organization leakage, and enables collaborative workflows within organizations. Indexing strategy ensures query performance at scale.

### XX. Role-Based Access Control (RBAC) (NEW - Phase 3.1)
RBAC MUST be enforced at every layer (Organization, Team, Project). Permissions MUST be checked before all CRUD operations. Permission inheritance MUST flow from Organization → Team → Project.

**Role Definitions:**

**Organization Roles:**
- **Owner:** Full control (create/update/delete org, manage all members, all team/project operations)
- **Admin:** Manage organization (update org, invite members, create teams, manage all teams/projects)
- **Member:** View organization, view teams, request team membership

**Team Roles:**
- **Lead:** Manage team (update team, add/remove members, create projects, manage all projects)
- **Member:** View team, view projects, request project membership, create tasks in projects

**Project Roles:**
- **Manager:** Manage project (update project, add/remove members, manage all tasks, assign tasks)
- **Contributor:** Create and update tasks, complete own tasks
- **Viewer:** View project and tasks (read-only)

**Permission Matrix:**

| Action | Org Owner | Org Admin | Org Member | Team Lead | Team Member | Project Manager | Project Contributor | Project Viewer |
|--------|-----------|-----------|------------|-----------|-------------|-----------------|---------------------|----------------|
| Create Organization | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Update Organization | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Delete Organization | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Invite Org Member | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Remove Org Member | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Create Team | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Update Team | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Delete Team | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Add Team Member | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Remove Team Member | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Create Project | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Update Project | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ |
| Delete Project | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ |
| Add Project Member | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ |
| Remove Project Member | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ |
| Create Task | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Update Own Task | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Update Any Task | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ |
| Delete Task | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | Owner only | ❌ |
| Assign Task | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ |
| Complete Own Task | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |

**Permission Inheritance:**
- Organization Owner/Admin has full access to all teams, projects, tasks within organization
- Team Lead has full access to all projects and tasks within team
- Project Manager has full access to all tasks within project
- Lower roles inherit no permissions from higher levels (explicit membership required)

**RBAC Middleware Implementation:**
```python
# Example FastAPI dependency
def require_organization_admin(
    org_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    member = db.query(OrganizationMember).filter(
        OrganizationMember.org_id == org_id,
        OrganizationMember.user_id == current_user.id,
        OrganizationMember.role.in_(['owner', 'admin'])
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Organization admin required")
    return current_user
```

**Permission Checking Patterns:**
1. Extract user_id from JWT token
2. Query membership table (OrganizationMember, TeamMember, ProjectMember)
3. Check role against required permission
4. Raise 403 Forbidden if permission denied
5. Log permission check in audit log (optional)

**Rationale:** RBAC ensures fine-grained access control across organization hierarchy. Permission matrix defines clear rules for who can do what. Permission inheritance simplifies management while maintaining security.

### XXI. Collaboration & Team Management (NEW - Phase 3.1)
Team collaboration features MUST enable seamless workflows with task assignments, project visibility, and team-based access control. All collaboration features MUST respect RBAC and multi-tenant isolation.

**Task Assignment:**
- Tasks can be assigned to team members within the project
- `assigned_to` field (user_id) references project member
- Only project managers can assign tasks to others
- Task owners can self-assign
- Assigned user can update and complete task
- Assignment history tracked in audit log

**Project Visibility:**
- Projects visible to all team members
- Project members can view all project tasks
- Non-members cannot see project tasks (403 Forbidden)
- Team leads can see all projects in team
- Organization admins can see all projects in organization

**Team-Based Access Control:**
- Team membership required for project access
- Organization membership required for team access
- Hierarchical scoping enforced (org → team → project → task)
- Membership validated on every request (via RBAC middleware)

**Invitation Workflows:**
- Organization admins invite users to organization (assign role: owner/admin/member)
- Team leads invite organization members to teams (assign role: lead/member)
- Project managers invite team members to projects (assign role: manager/contributor/viewer)
- Invitations sent via email with acceptance link
- Invitations expire after 7 days (configurable)
- Accepted invitations create membership record with assigned role

**Member Management:**
- List members at any level (organization/team/project)
- Add members with role assignment
- Update member roles (promote/demote)
- Remove members (cascade delete from child levels)
- Member removal tracked in audit log

**Collaboration Patterns:**
- Create organization → Invite team members → Create teams → Create projects → Create tasks → Assign to members
- User receives invitation → Accepts invitation → Joins organization/team/project → Can collaborate on tasks
- Team lead creates project → Adds team members to project → Members create tasks → Manager assigns tasks

**Rationale:** Collaboration features enable team-based workflows while maintaining security through RBAC. Task assignment improves accountability. Invitation system simplifies onboarding.

### XXII. Audit Trails & Change History (NEW - Phase 3.1)
All CRUD operations MUST be logged to audit trail for compliance, debugging, and accountability. Audit logs MUST include who, what, when, and context. Access to audit logs MUST be permission-based.

**Audit Log Schema:**
```python
class AuditLog:
    id: UUID
    org_id: UUID  # Organization scope
    user_id: UUID  # Who performed the action
    resource_type: str  # 'organization', 'team', 'project', 'task', etc.
    resource_id: UUID  # ID of affected resource
    action: str  # 'create', 'update', 'delete', 'restore', 'invite', 'accept', etc.
    metadata: dict  # Additional context (old_value, new_value, field_name, etc.)
    created_at: datetime  # When action occurred
```

**What to Log:**
- **Organization:** create, update, delete, restore, invite_member, remove_member
- **Team:** create, update, delete, restore, add_member, remove_member, change_lead
- **Project:** create, update, delete, restore, add_member, remove_member, change_manager
- **Task:** create, update, delete, restore, complete, assign, unassign
- **Invitation:** create, accept, reject, expire, cancel
- **Membership:** join, leave, role_change

**Metadata Examples:**
```json
// Task update
{
  "field_name": "status",
  "old_value": "pending",
  "new_value": "completed",
  "completed_by": "user-id"
}

// Task assignment
{
  "assigned_to": "user-id",
  "assigned_by": "manager-id",
  "project_id": "project-id"
}

// Member removal
{
  "removed_user_id": "user-id",
  "removed_by": "admin-id",
  "role": "member"
}
```

**Audit Log Access Control:**
- Organization admins can view all organization audit logs
- Team leads can view team-level audit logs (teams, projects, tasks)
- Project managers can view project-level audit logs (projects, tasks)
- Regular members cannot view audit logs
- Audit logs filtered by organization (no cross-org access)

**Audit Log Retention:**
- Audit logs retained for 180 days (configurable)
- Old logs archived or deleted based on compliance requirements
- Deleted resources' audit logs retained (for recovery and compliance)

**Automatic Audit Logging:**
```python
# Example decorator for automatic audit logging
@audit_log(resource_type="task", action="update")
async def update_task(task_id: UUID, data: TaskUpdate, user: User, db: Session):
    task = db.query(Task).get(task_id)
    # Update task
    # Audit log created automatically with old_value/new_value
```

**Rationale:** Audit trails provide accountability, compliance, and debugging capabilities. Change history enables recovery and understanding of system state evolution. Permission-based access protects sensitive audit data.

### XXIII. Invitation System & User Onboarding (NEW - Phase 3.1)
Invitation system MUST enable seamless user onboarding to organizations, teams, and projects with role assignment. Invitations MUST expire, be trackable, and handle edge cases gracefully.

**Invitation Flow:**
1. **Create Invitation:**
   - Admin/Lead/Manager creates invitation with email and role
   - System generates unique invitation ID and link
   - Invitation stored in database with expiration timestamp (7 days)
   - (Optional) Email sent to invitee with acceptance link

2. **Accept Invitation:**
   - User clicks invitation link (or enters invitation code)
   - System validates invitation (exists, not expired, not accepted)
   - If user not registered, redirect to signup
   - If user registered, create membership record with assigned role
   - Mark invitation as accepted (accepted_at, accepted_by)
   - Redirect user to organization/team/project

3. **Invitation Expiration:**
   - Invitations expire after 7 days (configurable)
   - Expired invitations cannot be accepted
   - System periodically cleans up expired invitations (soft delete)

4. **Edge Cases:**
   - User already member: Return 409 Conflict
   - Invitation already accepted: Return 410 Gone
   - Invitation expired: Return 404 Not Found (or 410 Gone)
   - Invalid invitation ID: Return 404 Not Found
   - User not organization member (for team/project invitations): Auto-add to organization first

**Invitation Types:**
- **Organization Invitation:** Invites user to organization with role (owner/admin/member)
- **Team Invitation:** Invites organization member to team with role (lead/member)
- **Project Invitation:** Invites team member to project with role (manager/contributor/viewer)

**Invitation Schema:**
```python
class Invitation:
    id: UUID
    org_id: UUID  # Organization scope
    team_id: UUID | None  # NULL for org-level invitations
    project_id: UUID | None  # NULL for team-level invitations
    email: str  # Invitee email
    role: str  # Role to assign on acceptance
    invited_by: UUID  # Who created the invitation
    accepted_at: datetime | None  # When invitation was accepted
    accepted_by: UUID | None  # Who accepted the invitation
    expires_at: datetime  # Expiration timestamp (7 days from creation)
    created_at: datetime
```

**Invitation Link Format:**
```
https://app.example.com/invitations/{invitation_id}/accept?email={email}
```

**Invitation API Endpoints:**
- `POST /api/invitations` - Create invitation (admin/lead/manager)
- `GET /api/invitations` - List user's pending invitations
- `PUT /api/invitations/{id}/accept` - Accept invitation
- `DELETE /api/invitations/{id}` - Cancel invitation (inviter or admin)

**Email Notification (Optional - Phase 3.1):**
- Email service integration (SendGrid, AWS SES, etc.) recommended but not required
- Email template with invitation link, organization/team/project name, inviter name
- If no email service, show invitation link in UI for manual sharing

**Invitation Tracking:**
- All invitation actions logged in audit trail
- Invitation creation, acceptance, cancellation tracked
- Failed acceptance attempts logged (expired, already accepted, etc.)

**Rationale:** Invitation system simplifies user onboarding with clear role assignment. Expiration prevents stale invitations. Email delivery (when implemented) reduces manual coordination. Audit trail ensures transparency.

## Phase 3.1 Scope Constraints

### In-Scope (Phase 3.1 Additions to Phase 4)
- **Multi-Tenancy:** Organization → Team → Project → Task hierarchy
- **Organization Management:** Create/update/delete organizations, manage members
- **Team Management:** Create teams within organizations, manage team members
- **Project Management:** Create projects within teams, assign tasks to projects
- **RBAC:** Organization/Team/Project roles with permission inheritance
- **Invitation System:** Email-based invitations with role assignment
- **Audit Trails:** Track all CRUD operations with who/what/when
- **Task Assignment:** Assign tasks to team members for collaboration
- **Soft Delete:** Recoverable deletion for organizations, teams, projects, tasks
- **Data Migration:** Migrate existing single-user tasks to personal organization
- **All Phase 4 Features:** Kubernetes deployment, containerization, HPA, stateless architecture
- **All Phase 3 Features:** AI chatbot, natural language, MCP tools, OpenAI Agents SDK

### Out-of-Scope (Future Phases)
- ❌ CRM features (customer management, sales pipelines - Phase 6)
- ❌ Billing and subscription management (Phase 6)
- ❌ Advanced analytics and reporting (Phase 6)
- ❌ Time tracking and productivity metrics (Phase 6)
- ❌ File attachments and document management (Phase 6)
- ❌ Real-time collaboration (live editing, presence - Phase 6)
- ❌ Mobile apps (iOS/Android - Phase 6)
- ❌ Event-driven architecture with Kafka (Phase 5)
- ❌ Dapr distributed runtime (Phase 5)
- ❌ Cloud deployment (DigitalOcean, GCP, Azure - Phase 5)
- ❌ CI/CD pipelines (Phase 5)

## Development Workflow (Phase 3.1)

### Feature Development Process (Phase 3.1)
1. **Specification:** Write feature spec for multi-tenant features (org/team/project management, RBAC, invitations, audit)
2. **Review Spec:** Ensure alignment with constitution and multi-tenancy constraints
3. **Database Design:** Design Organization, Team, Project, membership, invitation, audit log models
4. **RBAC Design:** Define roles, permissions, permission matrix
5. **API Design:** Design RESTful endpoints for organizations, teams, projects, invitations, members
6. **MCP Tools:** Design organization/team/project management tools
7. **Backend Development:** Implement models, services, routes, RBAC middleware, audit logging
8. **Frontend Development:** Implement organization/team/project UI components in ChatKit
9. **Testing:** Write and run tests (unit, integration, RBAC, multi-tenant isolation, audit)
10. **Containerization:** Update Dockerfiles if needed (no changes expected)
11. **K8s Deployment:** Update K8s manifests if needed (no changes expected)
12. **Helm Charts:** Update Helm charts if needed (no changes expected)
13. **Data Migration:** Migrate existing single-user tasks to personal organization
14. **Validation:** Verify all quality gates pass
15. **Documentation:** Update API docs, database schema, RBAC docs, invitation docs, audit docs

### Iteration Cycle (Phase 3.1)
- Phase 4 Kubernetes features MUST continue working (containerization, HPA, stateless architecture)
- Phase 3 chatbot features MUST continue working (natural language, MCP tools)
- Implement multi-tenant models first (Organization, Team, Project, memberships)
- Implement RBAC middleware and permission checking
- Implement audit logging system
- Implement invitation system
- Test multi-tenant data isolation (no cross-org leakage)
- Test RBAC permissions (role-based access enforcement)
- Test stateless architecture with tenant context propagation
- Validate all quality gates pass

## Quality Gates (Phase 3.1)

All quality gates MUST pass before Phase 3.1 is considered complete.

### Automated Checks (Must Pass)

**Backend:** (updated for Phase 3.1)
- ✅ `pytest` - All backend tests pass (including multi-tenancy, RBAC, audit tests)
- ✅ `mypy` - No type errors (strict mode)
- ✅ `ruff check` - No linting errors
- ✅ `ruff format --check` - Code formatted correctly
- ✅ Test coverage >90% (pytest-cov)

**Frontend:** (unchanged from Phase 4)
- ✅ `npm test` - All frontend tests pass
- ✅ `tsc --noEmit` - No TypeScript errors
- ✅ `eslint` - No linting errors
- ✅ `prettier --check` - Code formatted correctly
- ✅ `npm run build` - Production build succeeds

**Container Validation:** (unchanged from Phase 4)
**Kubernetes Validation:** (unchanged from Phase 4)
**Deployment Validation:** (unchanged from Phase 4)

**Multi-Tenancy Validation (NEW - Phase 3.1):**
- ✅ Organization boundary enforced (no cross-org data leakage)
- ✅ Team boundary enforced (no cross-team access)
- ✅ Project boundary enforced (no cross-project access)
- ✅ RBAC permissions enforced (role-based access control)
- ✅ Invitation flow works end-to-end
- ✅ Audit logs created for all CRUD operations
- ✅ Soft delete works correctly (delete and restore)
- ✅ Data migration completes successfully (single-user → personal org)

### Manual Reviews (Must Confirm)
- ✅ Spec requirements met (all acceptance criteria)
- ✅ Constitution compliance (all 23 principles followed)
- ✅ Database schema designed correctly (all 12 models)
- ✅ RBAC permission matrix implemented correctly
- ✅ Invitation system works end-to-end
- ✅ Audit trail captures all required events
- ✅ Multi-tenant isolation validated (no cross-org leakage)
- ✅ All Phase 4 Kubernetes features still working
- ✅ All Phase 3 chatbot features still working
- ✅ Documentation complete (multi-tenancy, RBAC, invitations, audit)

### Pre-Submission Checklist (Phase 3.1)
- [ ] All Phase 4 Kubernetes features working (containerization, HPA, stateless)
- [ ] All Phase 3 chatbot features working (natural language, MCP tools)
- [ ] All Phase 3.1 multi-tenancy features working (org/team/project management)
- [ ] All quality gates pass (backend + frontend + container + K8s + multi-tenancy)
- [ ] Database schema includes all 12 models (Organization, Team, Project, memberships, Task, Invitation, Conversation, Message, AuditLog)
- [ ] RBAC enforced on all endpoints (permission matrix implemented)
- [ ] Invitation system functional (create, accept, expire, cancel)
- [ ] Audit trail logging all CRUD operations
- [ ] Multi-tenant data isolation validated (no cross-org leakage)
- [ ] Soft delete working (delete and restore organizations/teams/projects/tasks)
- [ ] Data migration completed (existing tasks → personal organization)
- [ ] Frontend UI updated (organization/team/project management screens)
- [ ] README updated with Phase 3.1 features
- [ ] Demo video created (<90 seconds showing multi-tenant collaboration)

## Governance

### Constitution Authority
This constitution supersedes all other practices, preferences, or conventions. When in doubt, the constitution is the tiebreaker.

### Amendment Process
1. Constitution changes require explicit rationale
2. Version increments follow semantic versioning:
   - **MAJOR:** Principle removals or incompatible redefinitions, phase transitions, breaking architectural changes
   - **MINOR:** New principles or significant expansions
   - **PATCH:** Clarifications, typo fixes, non-semantic changes
3. All amendments must update dependent templates (`plan-template.md`, `spec-template.md`, `tasks-template.md`)
4. Sync Impact Report required for all constitution updates

### Compliance Reviews
- **Per-Feature Review:** Verify spec, tests, implementation, docs, RBAC, audit, multi-tenancy against constitution
- **Pre-Submission Review:** Full constitution compliance audit before hackathon submission
- **AI Agent Guidance:** Claude Code must be instructed to validate constitution compliance for all work

### Phase Transition
When transitioning from Phase 3.1 → Phase 5:
1. Update this same `constitution.md` file (do not create separate files)
2. Increment version to 6.0.0 (MAJOR - phase transition with cloud deployment)
3. Update principles to reflect Phase 5 requirements (Kafka, Dapr, cloud deployment, CI/CD)
4. Document breaking changes in Sync Impact Report at top of file
5. Update Last Amended date
6. Update all dependent templates and guidance for Phase 5 stack
7. Git history will preserve Phase 3.1 version for reference

**Note:** This constitution is a living document. All phase updates modify this single file with version increments tracked via git.

**Version:** 5.0.0 | **Ratified:** 2025-12-06 | **Last Amended:** 2025-12-28
