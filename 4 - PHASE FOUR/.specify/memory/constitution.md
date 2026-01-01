<!--
Sync Impact Report:
Version: 4.0.0 (MAJOR - Phase 4 Transition: AI Chatbot → Local Kubernetes Deployment)
Previous Version: 3.0.0
Changes in v4.0.0:
  - MAJOR PHASE TRANSITION: Phase 3 (AI Chatbot) → Phase 4 (Local Kubernetes Deployment)
  - ADDED Technology Stack: Docker Desktop 4.53+, Docker AI (Gordon), Kubernetes (Minikube 1.28+), Helm 3.x, kubectl-ai, Kagent
  - ADDED Principle XV: Containerization & Docker Best Practices
  - ADDED Principle XVI: Kubernetes Deployment & Orchestration
  - ADDED Principle XVII: Helm Chart Management
  - ADDED Principle XVIII: AIOps & Infrastructure as Code
  - UPDATED Principle III: YAGNI (Phase 4 scope - containerization, K8s local deployment)
  - UPDATED Principle IV: Technology Stack Requirements (added Docker, K8s, Helm, AIOps tools)
  - UPDATED Principle V: Clean Code & Modularity (added helm/, k8s/, docker/ folders)
  - UPDATED Principle XIII: Stateless Architecture (CRITICAL for K8s horizontal scaling)
  - UPDATED Quality Gates: Added containerization gates, Kubernetes deployment gates, Helm validation gates
  - MAINTAINED all 14 principles from Phase 3 (I-XIV unchanged in spirit, updated for Phase 4 context)
  - MAINTAINED All 10 features from Phase 3 (Basic + Intermediate + Advanced via chatbot)
  - MAINTAINED Phase 3.1 features (multi-tenant collaboration, RBAC, audit trails, invitations)
  - UPDATED Scope: Kubernetes deployment in-scope (Minikube local), cloud deployment still out-of-scope (Phase V)
Principles (Updated):
  - I. Spec-First Development (unchanged - applies to Helm charts and K8s manifests)
  - II. Test-First (TDD - NON-NEGOTIABLE) (updated - includes container tests, K8s validation tests)
  - III. YAGNI Principle (UPDATED - Phase 4 implements containerization + local K8s deployment)
  - IV. Technology Stack Requirements (BREAKING - added Docker, Kubernetes, Helm, AIOps tools)
  - V. Clean Code & Modularity (UPDATED - added helm/, k8s/ folders for infrastructure code)
  - VI. Type Safety (unchanged - still applies to Python + TypeScript)
  - VII. Comprehensive Documentation (UPDATED - includes Dockerfile docs, K8s manifest docs, Helm chart docs)
  - VIII. Error Handling (unchanged - still applies to all services)
  - IX. Multi-User Data Isolation & Security (UPDATED - K8s secrets for sensitive data)
  - X. Database Schema & Migration Management (unchanged - Neon DB external to K8s cluster)
  - XI. API Design & RESTful Conventions (unchanged - APIs remain the same)
  - XII. AI Agent Development & MCP Server Architecture (unchanged - deployed in K8s pods)
  - XIII. Stateless Architecture & Conversation State Management (CRITICAL UPDATE - required for K8s HPA)
  - XIV. Natural Language Understanding & Intent Recognition (unchanged - NLU in K8s pods)
  - XV. Containerization & Docker Best Practices (NEW)
  - XVI. Kubernetes Deployment & Orchestration (NEW)
  - XVII. Helm Chart Management (NEW)
  - XVIII. AIOps & Infrastructure as Code (NEW)
Templates Requiring Updates:
  - ⚠ plan-template.md (requires Phase 4 architecture patterns: Docker, K8s, Helm)
  - ⚠ spec-template.md (requires containerization acceptance criteria, K8s deployment validation)
  - ⚠ tasks-template.md (requires Dockerfile tasks, K8s manifest tasks, Helm chart tasks)
Follow-up TODOs:
  - Create Phase 4 feature specification for containerization and K8s deployment
  - Write Dockerfiles for frontend and backend with multi-stage builds
  - Create Kubernetes manifests for all services (deployments, services, HPA, secrets)
  - Create Helm chart for full application deployment
  - Set up Minikube local cluster
  - Configure kubectl-ai and kagent for intelligent K8s operations
  - Validate all Phase 3 features work in containerized environment (100% feature parity)
  - Validate stateless architecture with pod restarts and horizontal scaling
Ratification Date: 2025-12-06
Last Amended: 2026-01-01
-->

# Evolved Todo - Phase 4 Constitution

## Core Principles

### I. Spec-First Development
Every feature MUST have a specification written and approved before implementation begins. Specifications are the single source of truth for requirements, acceptance criteria, and implementation guidance.

**Rules:**
- Feature specs live in `specs/<feature>/spec.md`
- All specs follow the spec-template structure
- Specs must define clear acceptance criteria for chatbot interactions, MCP tools, conversation flows, containerization, and Kubernetes deployment
- Specs must include natural language examples, MCP tool schemas, expected AI behavior, Dockerfile requirements, and K8s manifest specifications
- Implementation must not begin until spec is approved
- Code that doesn't match spec is incorrect, regardless of functionality

**Phase 4 Additions:**
- Containerization specifications must define base images, build stages, security requirements, and health checks
- Kubernetes specifications must define resource limits, probes, scaling policies, and secrets management
- Helm chart specifications must define templates, values, and deployment strategies

**Rationale:** Spec-first ensures alignment between architect (human or AI), developer (Claude Code), and stakeholder expectations before any code is written. In Phase 4, this extends to infrastructure as code (Dockerfiles, K8s manifests, Helm charts).

### II. Test-First (TDD - NON-NEGOTIABLE)
Test-Driven Development is mandatory for backend, MCP tools, conversation flows, containerization, and Kubernetes deployment. Tests MUST be written, reviewed, and approved before implementation code.

**Red-Green-Refactor Cycle (Strictly Enforced):**
1. **Red:** Write failing tests that capture acceptance criteria
2. **Green:** Implement minimal code to pass tests
3. **Refactor:** Improve code while keeping tests green

**Rules:**
- **Backend (FastAPI):** pytest for unit and integration tests
  - All API endpoints must have integration tests (including chat endpoint)
  - All service layer functions must have unit tests
  - All database models must have validation tests
- **MCP Tools:** pytest for MCP tool tests
  - All MCP tools must have unit tests with mock database
  - All MCP tool schemas must be validated
  - All MCP tool error paths must be tested
- **Conversation Flows:** pytest for conversation integration tests
  - All conversation flows must have end-to-end tests
  - All natural language intents must be tested
  - All conversation state persistence must be tested
- **Containerization:** Container validation tests
  - All containers must have health check tests
  - All containers must have security scan tests (Trivy)
  - All containers must have startup time tests (<10 seconds)
- **Kubernetes:** K8s deployment validation tests
  - All pods must reach Ready state within 60 seconds
  - All health checks must pass for all pods
  - All services must be accessible (frontend externally, backend internally)
  - Stateless architecture tests (conversation state persists across pod restarts)
  - Horizontal scaling tests (HPA scales pods based on load)
- Tests written first → User approved → Tests fail → Then implement
- Edge cases and error paths must have tests
- Tests must be deterministic and isolated

**Rationale:** TDD ensures correctness, prevents regression, and serves as executable documentation for backend, MCP tools, AI agent behavior, containerization, and Kubernetes deployment.

### III. YAGNI Principle (Phase 4 Scope - Containerization + Local K8s Deployment)
"You Aren't Gonna Need It" - Implement ALL 10 features from Phase 3 (Basic + Intermediate + Advanced) via AI chatbot interface deployed on local Kubernetes (Minikube). No cloud deployment, no Kafka, no Dapr.

**Phase 4 Features - All Phase 3 Features Maintained (100% Parity):**

**Basic Level (Core Essentials via Natural Language):**
1. Add Task – "Add a task to buy groceries"
2. Delete Task – "Delete task 3"
3. Update Task – "Change task 1 to 'Call mom tonight'"
4. View Task List – "Show me all my tasks"
5. Mark as Complete – "Mark task 2 as complete"

**Intermediate Level (Organization & Usability):**
6. Priorities & Tags – "Add a high priority task" / "Tag this with work"
7. Search & Filter – "Show me high priority tasks" / "Filter by work tag"
8. Sort Tasks – "Sort my tasks by due date"

**Advanced Level (Intelligent Features):**
9. Recurring Tasks – "Add a weekly meeting task every Monday"
10. Due Dates & Reminders – "Set due date to Friday 5 PM for task 3"

**Phase 4 Implementation Requirements - Infrastructure:**
- Containerize frontend and backend applications using Docker
- Multi-stage Dockerfiles for optimized image sizes (Frontend <150MB, Backend <200MB)
- Deploy on local Kubernetes cluster (Minikube 1.28+)
- Create Helm charts for deployment automation
- Use kubectl-ai and kagent for intelligent K8s operations
- Use Docker AI (Gordon) for intelligent Docker operations
- Configure resource requests and limits for all pods
- Configure liveness, readiness, and startup probes
- Configure Horizontal Pod Autoscaler (HPA) for backend (2-10 pods at 70% CPU)
- Store sensitive data in Kubernetes secrets (DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET)
- Services: ClusterIP for backend (internal only), LoadBalancer/NodePort for frontend (external access)
- Maintain stateless architecture (CRITICAL for K8s horizontal scaling)
- All Phase 3.1 features maintained (multi-tenant collaboration, RBAC, audit trails, invitations)

**Forbidden in Phase 4:**
- ❌ Cloud Kubernetes deployment (GKE, AKS, EKS, DOKS - Phase V)
- ❌ Event-driven architecture with Kafka (Phase V)
- ❌ Dapr distributed runtime (Phase V)
- ❌ CI/CD pipelines (Phase V)
- ❌ Any feature beyond the 10-feature list

**Rationale:** Phase 4 focuses on containerization and local Kubernetes deployment while maintaining 100% feature parity with Phase 3. All 10 features via natural language chatbot, now running in containers on Minikube.

### IV. Technology Stack Requirements (Phase 4)
Phase 4 MUST use the specified technology stack. No substitutions.

**Mandatory Stack:**

**Containerization:**
- **Container Engine:** Docker Desktop 4.53+ (includes Kubernetes support)
- **Docker AI:** Docker AI Agent (Gordon) for intelligent Docker operations
- **Base Images:** node:22-alpine (frontend), python:3.13-slim (backend)
- **Security:** Trivy for vulnerability scanning (zero critical/high vulnerabilities)
- **Registry:** Docker Hub or local registry for image storage

**Orchestration:**
- **Kubernetes:** Minikube 1.28+ (local cluster with 2+ nodes recommended)
- **Package Manager:** Helm 3.x for deployment automation
- **AIOps:** kubectl-ai (AI-assisted K8s operations), Kagent (cluster health analysis)
- **Monitoring:** Kubernetes built-in metrics (kubectl top, describe)

**Frontend (Unchanged from Phase 3):**
- **Framework:** OpenAI ChatKit (hosted or self-hosted)
- **Language:** TypeScript (strict mode)
- **Styling:** Tailwind CSS (for custom UI around ChatKit)
- **Authentication:** Better Auth with JWT

**Backend (Unchanged from Phase 3):**
- **Framework:** Python FastAPI
- **Language:** Python 3.13+
- **AI Framework:** OpenAI Agents SDK (for agent orchestration)
- **MCP Server:** Official MCP SDK (Python implementation)
- **ORM:** SQLModel
- **Database:** Neon Serverless PostgreSQL (external to K8s cluster)
- **Package Manager:** UV (not pip, not poetry)

**Testing & Quality:**
- **Backend Testing:** pytest, pytest-cov
- **MCP Testing:** pytest with mock tools
- **Conversation Testing:** pytest with mock OpenAI responses
- **Container Testing:** Trivy security scanning, docker run health checks
- **K8s Testing:** kubectl --dry-run=client validation, helm lint, integration tests
- **Type Checking:** mypy (Python), TypeScript compiler
- **Linting:** ruff (Python), ESLint (TypeScript)
- **Formatting:** ruff format (Python), Prettier (TypeScript)

**Deployment (Phase 4):**
- **Local K8s:** Minikube cluster with Helm charts
- **External Database:** Neon Serverless PostgreSQL (not in cluster)
- **Secrets Management:** Kubernetes Secrets for DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET

**Rules:**
- All dependencies managed via `pyproject.toml` (backend) and `package.json` (frontend)
- Must use monorepo structure with `frontend/`, `backend/`, `helm/`, `.docker/` folders
- Dockerfiles must use multi-stage builds (build + production stages)
- Container images must be scanned with Trivy (zero critical/high vulnerabilities)
- All K8s manifests validated with `kubectl --dry-run=client`
- Helm charts must pass `helm lint` validation
- JWT tokens for authentication between frontend and backend
- Shared `BETTER_AUTH_SECRET` environment variable for JWT signing (stored in K8s secret)
- MCP server runs within FastAPI backend container
- OpenAI API key required for Agents SDK (`OPENAI_API_KEY` stored in K8s secret)
- Database connection string from `DATABASE_URL` K8s secret

**Rationale:** Standardization ensures consistency across containerization and Kubernetes deployment. Docker + K8s chosen for industry-standard containerization and orchestration. Minikube provides local development environment before cloud deployment in Phase V.

### V. Clean Code & Modularity (Phase 4 - Monorepo with K8s Infrastructure)
Code MUST be well-organized, modular, and follow clean code principles. Phase 4 extends monorepo structure with Kubernetes manifests, Helm charts, and Docker configurations.

**Organization Requirements:**
- Separation of concerns (data models, business logic, API routes, MCP tools, AI agents, infrastructure)
- Single Responsibility Principle for all functions, classes, components, MCP tools, and infrastructure configs
- Clear, descriptive naming (no abbreviations like `td`, `lst`, `mgr`)
- Maximum function length: 20 lines (excluding docstrings)
- Maximum file length: 200 lines (300 for complex API routes or K8s manifests)

**Phase 4 Project Structure:**
```
evolved-todo/
├── .specify/
│   ├── memory/
│   │   └── constitution.md
│   ├── templates/
│   └── scripts/
├── specs/
│   ├── overview.md
│   ├── architecture.md
│   ├── features/          # Feature specifications
│   ├── api/               # API specifications (including chat endpoint)
│   ├── database/          # Database schema (including Conversation, Message)
│   ├── mcp/               # MCP tool specifications
│   ├── ui/                # ChatKit UI specs
│   └── k8s/               # Kubernetes deployment specs (NEW)
├── frontend/
│   ├── CLAUDE.md
│   ├── Dockerfile         # Multi-stage Dockerfile (NEW)
│   ├── .dockerignore      # Docker ignore file (NEW)
│   ├── app/               # Next.js App Router pages
│   ├── components/        # ChatKit integration
│   ├── lib/               # API client for chat endpoint
│   ├── types/             # TypeScript types
│   └── __tests__/         # Frontend tests
├── backend/
│   ├── CLAUDE.md
│   ├── Dockerfile         # Multi-stage Dockerfile (NEW)
│   ├── .dockerignore      # Docker ignore file (NEW)
│   ├── app/
│   │   ├── main.py        # FastAPI entry point with health check endpoint
│   │   ├── models.py      # SQLModel database models (Task, Conversation, Message)
│   │   ├── routes/        # API route handlers (including chat.py)
│   │   ├── services/      # Business logic
│   │   ├── mcp/           # MCP server and tools
│   │   │   ├── server.py  # MCP server setup
│   │   │   └── tools/     # MCP tool implementations (add_task, list_tasks, etc.)
│   │   ├── agents/        # OpenAI Agents SDK configuration
│   │   │   ├── todo_agent.py  # Main todo agent
│   │   │   └── prompts.py     # System prompts and instructions
│   │   ├── auth.py        # JWT authentication
│   │   └── db.py          # Database connection
│   └── tests/             # Backend tests (including MCP tool tests)
├── helm/                  # Helm chart (NEW)
│   └── evolved-todo/
│       ├── Chart.yaml     # Helm chart metadata
│       ├── values.yaml    # Default configuration values
│       ├── templates/
│       │   ├── frontend-deployment.yaml
│       │   ├── frontend-service.yaml
│       │   ├── backend-deployment.yaml
│       │   ├── backend-service.yaml
│       │   ├── backend-hpa.yaml
│       │   ├── secrets.yaml
│       │   └── configmap.yaml
│       └── README.md      # Helm chart documentation
├── k8s/                   # Raw K8s manifests (optional, for learning) (NEW)
│   ├── frontend/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── backend/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── hpa.yaml
│   └── secrets/
│       └── app-secrets.yaml
├── docker-compose.yml     # Local development (optional)
├── .github/               # GitHub workflows (Phase V)
├── AGENTS.md
├── CLAUDE.md
└── README.md
```

**Rationale:** Clear structure separates application code (frontend, backend) from infrastructure code (helm, k8s, docker), making Phase 4 architecture easy to understand, maintain, and deploy.

### VI. Type Safety (Phase 4 - Python & TypeScript)
All functions MUST have complete type annotations. Type checking MUST pass without errors for both Python and TypeScript.

**Backend (Python) Requirements:**
- Function signatures: parameters and return types fully annotated
- Class attributes: type annotations required
- No `Any` types unless explicitly justified
- Use generic types (`list[Task]`, not `list`)
- Enable strict mypy mode
- SQLModel models with proper type hints
- MCP tool input/output schemas fully typed

**Frontend (TypeScript) Requirements:**
- Enable strict mode in `tsconfig.json`
- All component props fully typed (no implicit `any`)
- API response types defined and validated
- ChatKit props and event handlers fully typed
- Use TypeScript generics where appropriate
- Avoid type assertions (`as`) unless necessary

**Rationale:** Type safety catches bugs at compile time, improves IDE support, and serves as inline documentation for backend, MCP tools, and frontend. Unchanged from Phase 3.

### VII. Comprehensive Documentation (Phase 4 - Added K8s & Docker Docs)
Documentation MUST be thorough, clear, and maintained alongside code. Phase 4 includes Dockerfile documentation, Kubernetes manifest documentation, Helm chart documentation, and deployment guides.

**Required Documentation:**

1. **README.md:**
   - Project overview and Phase 4 scope
   - Prerequisites (Docker Desktop 4.53+, Minikube 1.28+, Helm 3.x, kubectl-ai, kagent)
   - Setup instructions (frontend, backend, MCP server, OpenAI API key, Minikube cluster)
   - Environment variables (OPENAI_API_KEY, BETTER_AUTH_SECRET, DATABASE_URL)
   - Running locally (Docker Compose for development, Minikube for K8s deployment)
   - Running tests (backend, MCP tools, conversation flows, container tests, K8s tests)
   - Deployment instructions (Minikube + Helm)
   - Troubleshooting common issues (pod restarts, image pull errors, health check failures)

2. **API Documentation:**
   - All API endpoints documented in `specs/api/rest-endpoints.md`
   - Chat endpoint specification (POST /api/{user_id}/chat)
   - Health check endpoints (/health for backend, /api/health for frontend)
   - Request/response schemas with examples
   - Authentication requirements (JWT token header)
   - Error response formats

3. **MCP Tool Documentation:**
   - All MCP tools documented in `specs/mcp/tools.md`
   - Tool schemas (input parameters, output format)
   - Tool behavior and side effects
   - Error handling for each tool
   - Usage examples with natural language triggers

4. **AI Agent Documentation:**
   - Agent behavior documented in `specs/mcp/agent-behavior.md`
   - System prompts and instructions
   - Intent recognition patterns
   - Conversation flow examples
   - Tool invocation logic

5. **Database Schema Documentation:**
   - Schema documented in `specs/database/schema.md`
   - All tables: Task, Conversation, Message
   - All columns, relationships, indexes
   - Migration strategy

6. **Dockerfile Documentation (NEW):**
   - Each Dockerfile documented in `specs/k8s/docker.md`
   - Multi-stage build strategy explained
   - Base image selection rationale
   - Security considerations (non-root user, minimal attack surface)
   - Build optimization techniques
   - Health check implementation

7. **Kubernetes Manifest Documentation (NEW):**
   - All K8s manifests documented in `specs/k8s/manifests.md`
   - Resource requests and limits explained
   - Probe configuration (liveness, readiness, startup)
   - HPA configuration and scaling policies
   - Secret management strategy
   - Service types and networking

8. **Helm Chart Documentation (NEW):**
   - Helm chart documented in `helm/evolved-todo/README.md`
   - Chart structure and templates explained
   - Values.yaml configuration options
   - Installation and upgrade procedures
   - Rollback strategies
   - Customization examples

9. **Deployment Guide (NEW):**
   - Step-by-step deployment guide in `docs/deployment.md`
   - Minikube setup and configuration
   - Helm installation and chart deployment
   - Verifying deployment health
   - Accessing services (frontend, backend)
   - Scaling and monitoring

10. **Docstrings/Comments (Backend):**
    - All public functions, classes, methods (Google style)
    - Include Args, Returns, Raises sections
    - FastAPI route handlers with OpenAPI descriptions
    - MCP tools with schema documentation

11. **Architecture Documentation:**
    - `specs/architecture.md` explaining Phase 4 architecture
    - Data flow: ChatKit → Frontend Pod → Backend Pod → OpenAI Agents SDK → MCP Tools → Database
    - Stateless architecture explanation (CRITICAL for K8s)
    - Conversation state persistence strategy
    - Containerization strategy
    - Kubernetes deployment architecture
    - Design decisions and rationale

**Rationale:** Comprehensive docs enable onboarding, facilitate review, and prepare for Phase V (cloud deployment) handoff. Docker and Kubernetes documentation critical for understanding infrastructure architecture and deployment strategies.

### VIII. Error Handling (Phase 4 - Added Container & K8s Errors)
Errors MUST be handled explicitly and gracefully. No silent failures. Phase 4 includes container error handling and Kubernetes deployment error handling.

**Backend (FastAPI) Requirements:**
- Validate all inputs with Pydantic models
- Use HTTPException with appropriate status codes
- Return structured error responses with `detail` field
- Handle database errors (connection, constraints, etc.)
- Handle OpenAI API errors (rate limits, timeouts, etc.)
- Handle MCP tool errors (invalid input, tool failure, etc.)
- Log errors for debugging

**MCP Tool Requirements:**
- Validate all tool inputs with Pydantic schemas
- Return structured error responses
- Handle missing tasks gracefully ("Task not found")
- Handle permission errors ("Access denied to task")
- Never crash the agent on tool errors

**Frontend (ChatKit) Requirements:**
- Handle API errors gracefully (network errors, 4xx, 5xx)
- Display user-friendly error messages in chat interface
- Retry on transient failures (network timeout)
- Provide fallback responses for errors
- Never leave user without feedback

**Container Error Handling (NEW):**
- Health check endpoints must return appropriate status codes
- Container startup failures must be logged clearly
- Image build failures must fail fast with clear error messages
- Security scan failures must block deployment

**Kubernetes Error Handling (NEW):**
- Pod startup failures must be debugged via `kubectl describe pod`
- Service unavailability must be detected via readiness probes
- Resource limit errors must be logged and alerted
- HPA scaling failures must be investigated and resolved
- Secret mounting errors must fail fast with clear messages

**Rationale:** Explicit error handling prevents undefined behavior and improves debugging. Container and Kubernetes error handling critical for reliable deployments.

### IX. Multi-User Data Isolation & Security (Phase 4 - K8s Secrets)
Every user MUST only see and modify their own data. Authentication and authorization are mandatory for all API endpoints. Sensitive data MUST be stored in Kubernetes secrets.

**Authentication Requirements:**
- **Better Auth** on Next.js frontend for user signup/signin
- JWT tokens issued by Better Auth upon successful login
- JWT tokens include `user_id` claim for identification
- Tokens expire after 7 days (configurable)
- Refresh tokens supported for seamless re-authentication

**Authorization Requirements:**
- All API endpoints require valid JWT token in `Authorization: Bearer <token>` header
- Chat endpoint requires valid JWT token
- Requests without token receive `401 Unauthorized`
- Backend extracts `user_id` from JWT token
- All database queries filtered by `user_id`
- Task ownership enforced: users can only access their own tasks
- Conversation ownership enforced: users can only access their own conversations
- Path parameter `{user_id}` MUST match JWT token `user_id` claim

**MCP Tool Security:**
- All MCP tools receive `user_id` parameter
- All MCP tools filter database queries by `user_id`
- MCP tools never expose data from other users
- Agent cannot override user isolation

**Kubernetes Secrets Management (NEW):**
- All sensitive data stored in Kubernetes secrets
- `BETTER_AUTH_SECRET` - JWT signing secret
- `OPENAI_API_KEY` - OpenAI API key for Agents SDK
- `DATABASE_URL` - Neon PostgreSQL connection string
- Secrets mounted as environment variables in pods
- Secrets never committed to git
- Secrets created via `kubectl create secret` or Helm templates

**Security Rules:**
- Shared `BETTER_AUTH_SECRET` between frontend and backend (stored in K8s secret)
- JWT signature verified on every request
- No SQL injection (use parameterized queries via SQLModel)
- No XSS (escape all user inputs in UI)
- HTTPS required for production (enforced by K8s ingress)
- OpenAI API key stored securely in K8s secret
- Containers run as non-root user (UID 1000)
- Container images scanned for vulnerabilities (Trivy)

**Rationale:** Multi-user data isolation ensures privacy and security. Kubernetes secrets provide secure storage for sensitive data in containerized environments.

### X. Database Schema & Migration Management (Phase 4 - Unchanged)
Database schema MUST be versioned, documented, and managed through migrations. SQLModel provides automatic schema management. Database remains external to Kubernetes cluster.

**Database Requirements:**
- **Provider:** Neon Serverless PostgreSQL (managed, external to K8s cluster)
- **ORM:** SQLModel (combines SQLAlchemy + Pydantic)
- **Migrations:** SQLModel automatic table creation (Phase 4 only - Alembic in Phase V)
- **Connection:** Connection string from `DATABASE_URL` Kubernetes secret

**Schema Design Rules:**
- All tables include `created_at` and `updated_at` timestamps
- Use appropriate indexes for query performance (`user_id`, `completed`, `conversation_id`, etc.)
- Foreign keys for relationships (users → tasks, users → conversations, conversations → messages)
- NOT NULL constraints for required fields
- VARCHAR limits for text fields (prevent abuse)

**Phase 4 Database Models (Unchanged from Phase 3):**
- User table (managed by Better Auth)
- Task table (with priority, tags, due dates, recurrence)
- Conversation table (for chat history)
- Message table (for chat messages)

**Migration Strategy (Phase 4):**
- SQLModel creates tables automatically on first run
- Use `create_db_and_tables()` in `app/db.py`
- No manual migrations needed for Phase 4
- Schema documented in `specs/database/schema.md`
- Database connection string stored in K8s secret (DATABASE_URL)

**Rationale:** External database (Neon) simplifies Phase 4 deployment. Pods can restart without losing data. Kubernetes StatefulSets not required.

### XI. API Design & RESTful Conventions (Phase 4 - Added Health Check Endpoints)
All API endpoints MUST follow RESTful conventions and return consistent, predictable responses. Phase 4 adds health check endpoints for Kubernetes probes.

**RESTful Endpoint Design:**

| Method | Endpoint | Description | Request Body | Success Response |
|--------|----------|-------------|--------------|------------------|
| GET | `/api/{user_id}/tasks` | List all tasks | None | `200 OK` + Task[] |
| POST | `/api/{user_id}/tasks` | Create task | Task data | `201 Created` + Task |
| GET | `/api/{user_id}/tasks/{id}` | Get task | None | `200 OK` + Task |
| PUT | `/api/{user_id}/tasks/{id}` | Update task | Task data | `200 OK` + Task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task | None | `204 No Content` |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle complete | None | `200 OK` + Task |
| POST | `/api/{user_id}/chat` | Send chat message | Chat message | `200 OK` + Response |
| **GET** | **`/health`** | **Backend health check** | **None** | **`200 OK` + Health status** |
| **GET** | **`/api/health`** | **Frontend health check** | **None** | **`200 OK` + Health status** |

**Health Check Endpoints (NEW):**

**Backend Health Check:**
```json
GET /health
Response: {"status": "healthy", "database": "connected"}
```

**Frontend Health Check:**
```json
GET /api/health
Response: {"status": "healthy"}
```

**API Conventions:**
- All endpoints prefixed with `/api` (except health checks)
- User-scoped endpoints include `{user_id}` path parameter
- Use plural nouns for resources (`/tasks`, not `/task`)
- Use HTTP methods semantically (GET = read, POST = create, PUT = update, DELETE = delete, PATCH = partial update)
- Return appropriate status codes (2xx success, 4xx client error, 5xx server error)
- Return JSON responses with consistent structure
- Health check endpoints for Kubernetes probes (liveness, readiness)

**Rationale:** RESTful conventions ensure predictable APIs. Health check endpoints enable Kubernetes to monitor pod health and restart failed containers.

### XII. AI Agent Development & MCP Server Architecture (Phase 4 - Deployed in K8s Pods)
AI agents and MCP tools MUST be developed with clear separation of concerns, testability, and deterministic behavior. Phase 4 deploys agents in Kubernetes pods.

**MCP Server Requirements:**
- MCP server runs within FastAPI backend (inside backend pod)
- Official MCP SDK (Python) for tool registration
- All tools registered with schemas (input/output types)
- Tools are stateless: receive input, return output, no side effects beyond database
- Tools never maintain internal state (all state in database)

**MCP Tool Design Rules:**
- Each tool is a single-purpose function
- Clear input schema with Pydantic models
- Clear output schema with Pydantic models
- Error responses are part of output schema (status: "success" | "error")
- Tools validate inputs before execution
- Tools handle errors gracefully (no crashes)
- Tools are fully testable with mock database

**Phase 4 MCP Tools (All 10 Features - Unchanged from Phase 3):**

**Basic Level Tools:**
1. **add_task** - Create new task
2. **list_tasks** - Retrieve tasks with filtering and sorting
3. **complete_task** - Mark task complete (handles recurring task logic)
4. **delete_task** - Remove task
5. **update_task** - Modify task (all fields)

**Intermediate Level Tools:**
6. **search_tasks** - Search tasks by keyword

**OpenAI Agents SDK Integration:**
- Agent initialized with system prompt defining behavior
- Agent has access to MCP tools via tool definitions
- Agent decides which tools to call based on user message
- Agent can chain multiple tool calls in single turn
- Agent provides conversational responses wrapping tool outputs
- Agent runs in backend pod (containerized)

**Kubernetes Deployment Considerations (NEW):**
- Backend pod contains both FastAPI server and MCP server
- Agent state persisted to database (conversation history)
- Pods can be killed and recreated without losing agent capability
- Horizontal scaling supported (any pod can handle any request)

**Rationale:** Clear MCP architecture separates AI logic (agent) from task operations (tools), enabling testability, maintainability, and scalability in Kubernetes environment.

### XIII. Stateless Architecture & Conversation State Management (Phase 4 - CRITICAL for K8s)
The chat endpoint MUST be stateless. All conversation state MUST be persisted to database. Server restarts MUST NOT lose conversation history. **This is CRITICAL for Kubernetes horizontal scaling and pod restarts.**

**Stateless Server Requirements (CRITICAL for K8s HPA):**
- Chat endpoint does not maintain in-memory state
- Every request is independent
- Server can be restarted without losing conversations
- Horizontally scalable (any pod can handle any request)
- **Pods can be killed and recreated by Kubernetes without data loss**
- **Load balancer can route to any backend pod**
- **HPA can scale pods up and down based on CPU/memory**

**Conversation State Persistence:**
- Conversation history stored in `conversations` and `messages` tables
- Each request fetches conversation history from database
- Each request stores new user message and assistant response
- Conversation history passed to OpenAI Agents SDK on every request

**Request Cycle (Stateless):**
1. Receive user message + optional conversation_id
2. If conversation_id provided, fetch conversation history from database
3. If no conversation_id, create new conversation record
4. Store user message in messages table
5. Build message array for agent (history + new message)
6. Run agent with MCP tools (agent decides which tools to call)
7. Agent generates response
8. Store assistant response in messages table
9. Return response to client
10. **Server forgets everything (ready for next request - any pod can handle it)**

**Kubernetes Benefits of Stateless Architecture:**
- **Horizontal Pod Autoscaler (HPA):** Can scale backend pods from 2 to 10 based on CPU load
- **Rolling Updates:** Can update pods one at a time without downtime
- **Pod Restarts:** Kubernetes can restart failed pods without losing conversation state
- **Load Balancing:** Any pod can handle any request (no sticky sessions required)
- **Resilience:** System survives pod crashes and node failures

**Validation Tests (CRITICAL for Phase 4):**
- Conversation state persists across pod restarts
- No message loss during pod kills
- HPA scales pods without conversation disruption
- Rolling updates complete without data loss

**Rationale:** Stateless architecture is mandatory for Kubernetes. Pods are ephemeral and can be killed/recreated at any time. All state must be in database to enable horizontal scaling, rolling updates, and resilience.

### XIV. Natural Language Understanding & Intent Recognition (Phase 4 - Unchanged)
The AI agent MUST understand natural language commands and map them to appropriate MCP tool calls. Intent recognition MUST be robust and user-friendly.

**Natural Language Command Examples:**

| User Says | Agent Should |
|-----------|-------------|
| "Add a task to buy groceries" | Call add_task with title "Buy groceries" |
| "Add a high priority task to call dentist" | Call add_task with title "Call dentist", priority "high" |
| "Create a work task for the presentation" | Call add_task with title "Presentation", tags "work" |
| "Show me all my tasks" | Call list_tasks with status "all" |
| "Mark task 3 as complete" | Call complete_task with task_id 3 |

**Intent Recognition Rules:**
- Agent must recognize various phrasings for same intent
- Agent must extract entities (task ID, title, description, status)
- Agent must handle ambiguous requests by asking clarification
- Agent must handle multi-step requests

**Rationale:** Robust NLU ensures users can interact naturally with chatbot. Unchanged from Phase 3 - deployed in Kubernetes pods.

### XV. Containerization & Docker Best Practices (NEW - Phase 4)
All applications MUST be containerized using Docker with multi-stage builds, security best practices, and optimized image sizes.

**Dockerfile Requirements:**

**Multi-Stage Builds (MANDATORY):**
- **Build Stage:** Install dependencies, compile code, run tests
- **Production Stage:** Copy only runtime artifacts, minimal image size
- Example structure:
  ```dockerfile
  # Build stage
  FROM node:22-alpine AS build
  WORKDIR /app
  COPY package*.json ./
  RUN npm ci
  COPY . .
  RUN npm run build

  # Production stage
  FROM node:22-alpine
  WORKDIR /app
  COPY --from=build /app/.next ./.next
  COPY --from=build /app/node_modules ./node_modules
  COPY --from=build /app/package.json ./package.json
  USER 1000
  EXPOSE 3000
  CMD ["npm", "start"]
  ```

**Image Size Limits:**
- **Frontend:** <150MB (compressed)
- **Backend:** <200MB (compressed)
- Use alpine base images where possible
- Exclude dev dependencies from production images
- Use .dockerignore to exclude unnecessary files

**Security Requirements:**
- **Non-Root User:** Containers MUST run as non-root user (UID 1000)
- **Vulnerability Scanning:** All images MUST be scanned with Trivy
- **Zero Critical/High Vulnerabilities:** No critical or high severity vulnerabilities allowed
- **Minimal Attack Surface:** Only include necessary runtime dependencies
- **No Secrets in Images:** Never commit secrets to Dockerfiles

**Health Check Endpoints (MANDATORY):**
- **Backend:** GET /health (returns 200 OK + {"status": "healthy"})
- **Frontend:** GET /api/health (returns 200 OK + {"status": "healthy"})
- Health checks MUST complete in <1 second
- Health checks MUST verify critical dependencies (database connection for backend)

**Base Image Selection:**
- **Frontend:** node:22-alpine (small, secure, official)
- **Backend:** python:3.13-slim (small, secure, official)
- Pin specific image versions (no `latest` tags)
- Use official images from Docker Hub

**.dockerignore Files (MANDATORY):**
- Exclude development files (node_modules, .git, tests)
- Exclude documentation files (README.md, docs/)
- Exclude environment files (.env, .env.local)
- Example:
  ```
  node_modules/
  .git/
  .env*
  README.md
  docs/
  tests/
  __tests__/
  *.md
  ```

**Build Optimization:**
- Layer caching: Copy dependency files before source code
- Multi-stage builds: Separate build and runtime stages
- Minimize layer count: Combine RUN commands where appropriate
- Use build arguments for environment-specific configuration

**Container Startup Requirements:**
- Containers MUST start in <10 seconds locally
- Containers MUST expose correct ports (3000 for frontend, 8000 for backend)
- Containers MUST handle SIGTERM gracefully (shutdown within 30 seconds)

**Rationale:** Multi-stage builds reduce image size and attack surface. Security scanning prevents deployment of vulnerable images. Health checks enable Kubernetes to monitor container health. Non-root users improve security posture.

### XVI. Kubernetes Deployment & Orchestration (NEW - Phase 4)
All applications MUST be deployed on Kubernetes (Minikube local cluster) with proper resource management, health probes, horizontal scaling, and secrets management.

**Kubernetes Requirements:**

**Cluster Setup:**
- **Platform:** Minikube 1.28+ (local Kubernetes cluster)
- **Nodes:** Minimum 2 nodes recommended for realistic testing
- **CPU:** Minimum 4 CPUs allocated to Minikube
- **Memory:** Minimum 8GB RAM allocated to Minikube

**Resource Requests and Limits (MANDATORY):**

**Frontend Pods:**
```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 200m
    memory: 256Mi
```

**Backend Pods:**
```yaml
resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

**Probes Configuration (MANDATORY):**

**Liveness Probe (Restart on Failure):**
- **Purpose:** Detect if container is running but broken (restart it)
- **Endpoint:** GET /health (backend), GET /api/health (frontend)
- **Initial Delay:** 15 seconds (allow startup time)
- **Period:** 10 seconds (check every 10 seconds)
- **Timeout:** 2 seconds (fail if no response in 2 seconds)
- **Failure Threshold:** 3 (restart after 3 consecutive failures)

**Readiness Probe (Remove from Load Balancer on Failure):**
- **Purpose:** Detect if container is ready to serve traffic (remove from service if not)
- **Endpoint:** GET /health (backend), GET /api/health (frontend)
- **Initial Delay:** 5 seconds (shorter than liveness)
- **Period:** 5 seconds (check more frequently)
- **Timeout:** 2 seconds
- **Failure Threshold:** 3 (remove from service after 3 consecutive failures)

**Startup Probe (Allow Slow Startup):**
- **Purpose:** Give containers extra time to start (disable liveness during startup)
- **Endpoint:** GET /health (backend), GET /api/health (frontend)
- **Initial Delay:** 0 seconds
- **Period:** 5 seconds
- **Timeout:** 2 seconds
- **Failure Threshold:** 12 (allow 60 seconds total startup time)

**Replica Configuration:**
- **Minimum Replicas:** 2 (high availability)
- **Maximum Replicas:** 10 (HPA limit for backend)
- **Frontend:** 2-5 replicas (static, HPA optional)
- **Backend:** 2-10 replicas (dynamic, HPA required)

**Horizontal Pod Autoscaler (HPA) - Backend (MANDATORY):**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**Secrets Management (MANDATORY):**
- **All sensitive data in Kubernetes secrets**
- **Secrets:**
  - `DATABASE_URL` - Neon PostgreSQL connection string
  - `OPENAI_API_KEY` - OpenAI API key
  - `BETTER_AUTH_SECRET` - JWT signing secret
- **Mounting:** Secrets mounted as environment variables
- **Creation:** `kubectl create secret generic app-secrets --from-literal=DATABASE_URL=... --from-literal=OPENAI_API_KEY=... --from-literal=BETTER_AUTH_SECRET=...`
- **Never commit secrets to git**

**Service Configuration:**

**Backend Service (ClusterIP - Internal Only):**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend
spec:
  type: ClusterIP
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
```

**Frontend Service (LoadBalancer/NodePort - External Access):**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
spec:
  type: LoadBalancer  # or NodePort for Minikube
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 3000
```

**Deployment Labels (MANDATORY):**
- **app:** Application name (frontend, backend)
- **component:** Component type (web, api, agent)
- **version:** Semantic version (v1.0.0)

**Deployment Strategy:**
- **Type:** RollingUpdate (zero downtime)
- **Max Surge:** 1 (one extra pod during update)
- **Max Unavailable:** 0 (no downtime)

**Validation Requirements:**
- All manifests MUST pass `kubectl --dry-run=client -f manifest.yaml`
- All pods MUST reach Ready state within 60 seconds
- All health checks MUST pass for all pods
- Services MUST be accessible (frontend externally, backend internally)
- HPA MUST scale pods up/down based on CPU load

**Rationale:** Resource limits prevent resource exhaustion. Probes enable Kubernetes to monitor pod health and restart failures. HPA enables automatic scaling based on load. Secrets enable secure credential management.

### XVII. Helm Chart Management (NEW - Phase 4)
Kubernetes deployments MUST be managed via Helm charts for reusability, versioning, and deployment automation.

**Helm Chart Requirements:**

**Chart Structure:**
```
helm/evolved-todo/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration
├── templates/
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── backend-hpa.yaml
│   ├── secrets.yaml
│   ├── configmap.yaml
│   └── _helpers.tpl       # Template helpers
└── README.md               # Chart documentation
```

**Chart.yaml (Metadata):**
```yaml
apiVersion: v2
name: evolved-todo
description: AI-powered todo application with chatbot interface
version: 4.0.0
appVersion: "4.0.0"
keywords:
  - todo
  - chatbot
  - ai
  - openai
maintainers:
  - name: Your Name
    email: your.email@example.com
```

**values.yaml (Configuration):**
```yaml
frontend:
  image:
    repository: evolved-todo/frontend
    tag: "4.0.0"
    pullPolicy: IfNotPresent
  replicaCount: 2
  service:
    type: LoadBalancer
    port: 80
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 200m
      memory: 256Mi

backend:
  image:
    repository: evolved-todo/backend
    tag: "4.0.0"
    pullPolicy: IfNotPresent
  replicaCount: 2
  service:
    type: ClusterIP
    port: 8000
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
  hpa:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70

secrets:
  databaseUrl: ""  # Set via --set or values override
  openaiApiKey: ""  # Set via --set or values override
  betterAuthSecret: ""  # Set via --set or values override
```

**Template Best Practices:**
- Use `{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}` for images
- Use `{{ .Release.Name }}-frontend` for resource names
- Use `{{ include "evolved-todo.fullname" . }}` helper for consistent naming
- Parameterize all configuration (replicas, resources, image tags)
- Use `{{ .Values.secrets.databaseUrl | b64enc }}` for secret encoding

**Helm Commands:**

**Install:**
```bash
helm install evolved-todo ./helm/evolved-todo \
  --set secrets.databaseUrl="postgresql://..." \
  --set secrets.openaiApiKey="sk-..." \
  --set secrets.betterAuthSecret="..."
```

**Upgrade:**
```bash
helm upgrade evolved-todo ./helm/evolved-todo \
  --set backend.image.tag="4.1.0"
```

**Rollback:**
```bash
helm rollback evolved-todo 1
```

**Lint:**
```bash
helm lint ./helm/evolved-todo
```

**Validation Requirements:**
- Chart MUST pass `helm lint` with zero errors
- Chart MUST install successfully on Minikube
- Chart MUST support customization via values.yaml
- Chart MUST support upgrades without downtime
- Chart MUST support rollbacks to previous versions

**Versioning:**
- Chart version increments with application version (semantic versioning)
- Use `appVersion` for application version tracking
- Tag releases with chart version

**Rationale:** Helm charts enable reusable, versioned deployments. Configuration via values.yaml supports environment-specific customization. Helm supports upgrades and rollbacks for safe deployments.

### XVIII. AIOps & Infrastructure as Code (NEW - Phase 4)
Kubernetes operations SHOULD leverage AI-assisted tools (kubectl-ai, kagent, Gordon) for intelligent cluster management and Docker operations.

**kubectl-ai (AI-Assisted Kubernetes Operations):**

**Purpose:** Natural language interface to Kubernetes

**Example Commands:**
```bash
kubectl-ai "deploy the todo frontend with 2 replicas"
kubectl-ai "scale the backend to handle more load"
kubectl-ai "check why the pods are failing"
kubectl-ai "show me resource usage across the cluster"
kubectl-ai "troubleshoot backend pod errors"
```

**Use Cases:**
- Deploying applications with natural language
- Scaling resources based on load
- Troubleshooting pod failures
- Monitoring resource usage
- Debugging network issues

**Kagent (Kubernetes Agent for Cluster Health):**

**Purpose:** AI-powered cluster health analysis and optimization

**Example Commands:**
```bash
kagent "analyze the cluster health"
kagent "optimize resource allocation"
kagent "identify performance bottlenecks"
kagent "suggest cost optimizations"
```

**Use Cases:**
- Cluster health monitoring
- Resource optimization recommendations
- Performance bottleneck identification
- Cost analysis and optimization
- Security posture assessment

**Docker AI (Gordon) - AI-Assisted Docker Operations:**

**Purpose:** Natural language interface to Docker

**Example Commands:**
```bash
docker ai "build a multi-stage Dockerfile for Python app"
docker ai "optimize this image size"
docker ai "scan this image for vulnerabilities"
docker ai "troubleshoot container startup failure"
```

**Use Cases:**
- Dockerfile generation and optimization
- Image size reduction
- Security vulnerability analysis
- Container troubleshooting
- Build optimization

**Infrastructure as Code Principles:**
- All infrastructure defined in code (Dockerfiles, K8s manifests, Helm charts)
- Version control for all infrastructure code
- Declarative configuration (desired state, not imperative steps)
- Automated deployments via Helm
- Reproducible environments (dev, staging, prod)

**AIOps Benefits:**
- Faster troubleshooting with natural language queries
- Intelligent resource optimization
- Automated health monitoring
- Reduced learning curve for Kubernetes
- Faster time to resolution for issues

**Validation Requirements:**
- kubectl-ai installed and configured
- Kagent installed and configured (optional)
- Docker AI (Gordon) enabled in Docker Desktop 4.53+
- All infrastructure code committed to git
- Deployments reproducible from code

**Rationale:** AIOps tools accelerate Kubernetes learning and operations. Infrastructure as code ensures reproducibility and version control. AI-assisted tools reduce cognitive load and speed up troubleshooting.

## Phase 4 Scope Constraints

### In-Scope
- **Frontend:** OpenAI ChatKit conversational interface (containerized)
- **Backend:** FastAPI with OpenAI Agents SDK + MCP server (containerized)
- **Database:** Neon PostgreSQL (external to K8s cluster)
- **Authentication:** Better Auth with JWT tokens (stored in K8s secrets)
- **Multi-User:** Complete user isolation and data privacy
- **All 10 Features:** Basic (1-5), Intermediate (6-8), Advanced (9-10) via natural language
- **MCP Tools:** 6 stateless tools supporting all task operations (CRUD, priorities, tags, filtering, sorting, recurrence, due dates)
- **Stateless Architecture:** Database-persisted conversation state (CRITICAL for K8s)
- **Containerization:** Docker multi-stage builds, security scanning, image optimization
- **Kubernetes:** Minikube deployment, resource limits, probes, HPA, secrets, services
- **Helm Charts:** Deployment automation, versioning, upgrades, rollbacks
- **AIOps:** kubectl-ai, kagent, Gordon for intelligent operations
- **Testing:** Comprehensive test coverage (>90%) for backend, MCP tools, conversation flows, containers, K8s deployment
- **Deployment:** Local Minikube cluster with Helm charts

### Out-of-Scope (Future Phases)
- ❌ Cloud Kubernetes deployment (GKE, AKS, EKS, DOKS - Phase V)
- ❌ Event-driven architecture with Kafka (Phase V)
- ❌ Dapr distributed runtime (Phase V)
- ❌ CI/CD pipelines (Phase V)
- ❌ Monitoring and observability (Prometheus, Grafana - Phase V)
- ❌ Production-grade ingress controllers (Phase V)

## Development Workflow (Phase 4)

### Feature Development Process
1. **Specification:** Write feature spec in `specs/features/<feature>/spec.md`
   - Include natural language examples
   - Include MCP tool specifications
   - Include agent behavior requirements
   - Include conversation flow examples
   - Include containerization requirements
   - Include Kubernetes deployment specifications
2. **Review Spec:** Ensure alignment with constitution and acceptance criteria
3. **Database First:** Update database models in `backend/app/models.py` (if needed)
4. **Write MCP Tool Tests:** Create failing tests for each MCP tool (if adding new tools)
5. **Implement MCP Tools:** Write tool functions with schemas (Red → Green)
6. **Write Agent Tests:** Create failing tests for agent behavior
7. **Implement Agent:** Configure OpenAI Agents SDK with system prompt and tools
8. **Write Chat Endpoint Tests:** Create failing tests for stateless chat endpoint
9. **Implement Chat Endpoint:** Write FastAPI route with conversation persistence
10. **Write Frontend Tests:** Create failing tests for ChatKit integration
11. **Implement Frontend:** Integrate ChatKit with chat endpoint
12. **Write Dockerfile Tests:** Create failing tests for container builds and health checks
13. **Implement Dockerfiles:** Write multi-stage Dockerfiles for frontend and backend
14. **Write K8s Tests:** Create failing tests for K8s deployment validation
15. **Implement K8s Manifests:** Write deployments, services, HPA, secrets
16. **Implement Helm Chart:** Create Helm templates and values.yaml
17. **Integration Testing:** Test full flow (ChatKit → Frontend Pod → Backend Pod → Agent → MCP Tools → Database)
18. **Refactor:** Improve code quality while keeping tests green
19. **Documentation:** Update README, Dockerfile docs, K8s docs, Helm docs
20. **Final Review:** Verify all quality gates pass (application + infrastructure)

### Iteration Cycle
- Implement all 10 features (Basic + Intermediate + Advanced) via natural language chatbot
- Containerize both frontend and backend with Docker
- Deploy on Minikube with Kubernetes manifests
- Automate deployment with Helm charts
- Validate stateless architecture with pod restarts
- Validate horizontal scaling with HPA
- Use kubectl-ai and kagent for cluster operations

## Quality Gates (Phase 4)

All quality gates MUST pass before Phase 4 is considered complete.

### Automated Checks (Must Pass)

**Backend:**
- ✅ `pytest` - All backend tests pass
- ✅ `mypy` - No type errors (strict mode)
- ✅ `ruff check` - No linting errors
- ✅ `ruff format --check` - Code formatted correctly
- ✅ Test coverage >90% (pytest-cov)

**MCP Tools:**
- ✅ All 6 MCP tools have unit tests
- ✅ All MCP tool schemas validated
- ✅ All MCP tool error paths tested
- ✅ All MCP tools tested with mock database

**Conversation Flows:**
- ✅ All natural language examples have integration tests
- ✅ All conversation flows tested end-to-end
- ✅ All error recovery scenarios tested
- ✅ Stateless architecture validated (no in-memory state)

**Frontend:**
- ✅ `npm test` - All frontend tests pass
- ✅ `tsc --noEmit` - No TypeScript errors
- ✅ `eslint` - No linting errors
- ✅ `prettier --check` - Code formatted correctly
- ✅ `npm run build` - Production build succeeds

**Containerization (NEW):**
- ✅ Dockerfiles use multi-stage builds (build + production stages)
- ✅ Base images pinned to specific versions (no `latest` tags)
- ✅ .dockerignore files exclude dev files (node_modules, .git, tests)
- ✅ Health check endpoints implemented (`/health` backend, `/api/health` frontend)
- ✅ Container images scanned with Trivy (zero critical/high vulnerabilities)
- ✅ Containers run as non-root user (UID 1000)
- ✅ Image size targets met (Frontend <150MB, Backend <200MB)
- ✅ Containers start in <10 seconds locally

**Kubernetes (NEW):**
- ✅ Resource requests and limits defined for all pods
- ✅ Liveness, Readiness, and Startup probes configured
- ✅ Multiple replicas configured for high availability (minimum 2)
- ✅ HPA configured for backend autoscaling (2-10 pods, CPU 70%)
- ✅ Secrets created for sensitive data (DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET)
- ✅ Services configured (ClusterIP for backend, LoadBalancer/NodePort for frontend)
- ✅ All manifests validated with `kubectl --dry-run=client`
- ✅ Labels present on all resources (app, component, version)
- ✅ All pods reach Ready state within 60 seconds
- ✅ Health checks pass for all pods
- ✅ Services accessible (frontend externally, backend internally)

**Helm (NEW):**
- ✅ Helm chart passes `helm lint` validation
- ✅ Helm install succeeds on Minikube
- ✅ Helm upgrade succeeds without downtime
- ✅ Helm rollback works correctly
- ✅ Chart documented in README.md

**Integration:**
- ✅ Chat endpoint returns correct responses in K8s
- ✅ JWT authentication works end-to-end in K8s
- ✅ Conversation state persisted to database (external to K8s)
- ✅ Agent correctly invokes MCP tools in K8s pods
- ✅ Database queries are optimized (no N+1 queries)

### Manual Reviews (Must Confirm)
- ✅ Spec requirements met (all acceptance criteria)
- ✅ Constitution compliance (all 18 principles followed)
- ✅ MCP tool documentation complete
- ✅ Agent behavior documented with examples
- ✅ ChatKit UI works smoothly in K8s
- ✅ Error handling for all edge cases
- ✅ Multi-user data isolation verified
- ✅ Conversation history survives server restart (stateless validated)
- ✅ Natural language understanding is robust
- ✅ Security: JWT tokens, HTTPS, no SQL injection/XSS, K8s secrets
- ✅ Dockerfile documentation complete
- ✅ Kubernetes manifest documentation complete
- ✅ Helm chart documentation complete

### Deployment Validation (NEW - Phase 4)
- ✅ Conversation state persists across pod restarts (stateless architecture verified)
- ✅ Horizontal scaling tested (HPA scales pods up/down based on load)
- ✅ Zero message loss during pod restarts or deletions
- ✅ All 10 Phase 3 features work correctly in containers (100% feature parity)
- ✅ Rolling updates complete without downtime
- ✅ Helm chart installs, upgrades, and rolls back successfully

### Pre-Submission Checklist (Phase 4)
- [ ] All 10 features (Basic + Intermediate + Advanced) work via natural language in K8s
- [ ] All quality gates pass (backend + MCP + frontend + containers + K8s)
- [ ] OpenAI ChatKit configured
- [ ] OpenAI Agents SDK integrated with MCP server (running in backend pod)
- [ ] All 6 MCP tools implemented and tested (supporting all 10 features)
- [ ] Stateless chat endpoint with database persistence (validated in K8s)
- [ ] Better Auth configured with JWT (secrets in K8s)
- [ ] Neon database connected with Conversation and Message tables (external to K8s)
- [ ] Chat endpoint secured with JWT middleware
- [ ] Dockerfiles created for frontend and backend (multi-stage builds)
- [ ] Container images scanned with Trivy (zero critical/high)
- [ ] Kubernetes manifests created for all services
- [ ] Helm chart created and tested
- [ ] Minikube cluster set up and running
- [ ] All pods healthy and ready in Minikube
- [ ] Services accessible (frontend externally via LoadBalancer/NodePort, backend internally)
- [ ] kubectl-ai and kagent installed and configured
- [ ] README includes setup instructions (Docker, Minikube, Helm, kubectl-ai, OpenAI API key)
- [ ] Architecture documentation explains containerization and K8s deployment
- [ ] Dockerfile documentation complete
- [ ] Kubernetes manifest documentation complete
- [ ] Helm chart documentation complete
- [ ] Demo video created (<90 seconds) showing containerized deployment

## Governance

### Constitution Authority
This constitution supersedes all other practices, preferences, or conventions. When in doubt, the constitution is the tiebreaker.

### Amendment Process
1. Constitution changes require explicit rationale
2. Version increments follow semantic versioning:
   - **MAJOR:** Principle removals or incompatible redefinitions, phase transitions
   - **MINOR:** New principles or significant expansions
   - **PATCH:** Clarifications, typo fixes, non-semantic changes
3. All amendments must update dependent templates (`plan-template.md`, `spec-template.md`, `tasks-template.md`)
4. Sync Impact Report required for all constitution updates

### Compliance Reviews
- **Per-Feature Review:** Verify spec, tests, implementation, docs against constitution
- **Pre-Submission Review:** Full constitution compliance audit before hackathon submission
- **AI Agent Guidance:** Claude Code must be instructed to validate constitution compliance for all work

### Phase Transition
When transitioning from Phase 4 → Phase 5:
1. Update this same `constitution.md` file (do not create separate files)
2. Increment version to 5.0.0 (MAJOR - phase transition with breaking changes)
3. Update principles to reflect Phase 5 requirements (Kafka, Dapr, cloud K8s, CI/CD, etc.)
4. Document breaking changes in Sync Impact Report at top of file
5. Update Last Amended date
6. Update all dependent templates and guidance for Phase 5 stack
7. Git history will preserve Phase 4 version for reference

**Note:** This constitution is a living document. All phase updates modify this single file with version increments tracked via git.

**Version:** 4.0.0 | **Ratified:** 2025-12-06 | **Last Amended:** 2026-01-01
