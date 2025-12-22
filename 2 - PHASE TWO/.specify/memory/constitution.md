<!--
Sync Impact Report:
Version: 2.0.0 (MAJOR - Phase 2 Transition with Breaking Architectural Changes)
Previous Version: 1.1.0
Changes in v2.0.0:
  - MAJOR PHASE TRANSITION: Phase 1 (CLI, in-memory) → Phase 2 (Full-Stack Web, Database)
  - BREAKING: Removed in-memory constraint, now requires Neon PostgreSQL database
  - BREAKING: Removed CLI-only constraint, now requires Next.js web interface
  - BREAKING: Added multi-user requirement with Better Auth JWT authentication
  - ADDED Technology Stack: Next.js 16+, FastAPI, SQLModel, Neon PostgreSQL, Better Auth
  - ADDED Principle IX: Multi-User Data Isolation & Security
  - ADDED Principle X: Database Schema & Migration Management
  - ADDED Principle XI: API Design & RESTful Conventions
  - ADDED Monorepo Structure requirement (frontend/ + backend/ folders)
  - MAINTAINED all 10 features from Phase 1 (Basic + Intermediate + Advanced levels)
  - UPDATED YAGNI Principle to maintain comprehensive 10-feature scope
  - UPDATED Project Structure to monorepo organization
  - UPDATED Quality Gates to include API security checks
Principles (Updated):
  - I. Spec-First Development (unchanged)
  - II. Test-First (TDD - NON-NEGOTIABLE) (unchanged - now applies to both backend and frontend)
  - III. YAGNI Principle (MAINTAINED - still 10 features, now as web app)
  - IV. Technology Stack Requirements (BREAKING - complete stack overhaul for Phase 2)
  - V. Clean Code & Modularity (UPDATED - now covers monorepo structure)
  - VI. Type Safety (UPDATED - now covers both Python and TypeScript)
  - VII. Comprehensive Documentation (UPDATED - includes API documentation)
  - VIII. Error Handling (UPDATED - includes HTTP error responses)
  - IX. Multi-User Data Isolation & Security (NEW)
  - X. Database Schema & Migration Management (NEW)
  - XI. API Design & RESTful Conventions (NEW)
Templates Requiring Updates:
  - ✅ plan-template.md (updated for Phase 2 architecture)
  - ✅ spec-template.md (updated for API + UI specifications)
  - ✅ tasks-template.md (updated for full-stack task types)
Follow-up TODOs:
  - Create Phase 2 feature specifications for all 10 features
  - Set up monorepo structure (frontend/ and backend/ folders)
  - Configure Neon PostgreSQL database
  - Set up Better Auth with JWT in both frontend and backend
Ratification Date: 2025-12-06
Last Amended: 2025-12-10
-->

# Evolved Todo - Phase 2 Constitution

## Core Principles

### I. Spec-First Development
Every feature MUST have a specification written and approved before implementation begins. Specifications are the single source of truth for requirements, acceptance criteria, and implementation guidance.

**Rules:**
- Feature specs live in `specs/<feature>/spec.md`
- All specs follow the spec-template structure
- Specs must define clear acceptance criteria for both API and UI
- Specs must include API endpoint definitions and UI wireframes/requirements
- Implementation must not begin until spec is approved
- Code that doesn't match spec is incorrect, regardless of functionality

**Rationale:** Spec-first ensures alignment between architect (human or AI), developer (Claude Code), and stakeholder expectations before any code is written. In Phase 2, this applies to both frontend and backend components.

### II. Test-First (TDD - NON-NEGOTIABLE)
Test-Driven Development is mandatory for both backend and frontend. Tests MUST be written, reviewed, and approved before implementation code.

**Red-Green-Refactor Cycle (Strictly Enforced):**
1. **Red:** Write failing tests that capture acceptance criteria
2. **Green:** Implement minimal code to pass tests
3. **Refactor:** Improve code while keeping tests green

**Rules:**
- **Backend (FastAPI):** pytest for unit and integration tests
  - All API endpoints must have integration tests
  - All service layer functions must have unit tests
  - All database models must have validation tests
- **Frontend (Next.js):** Jest + React Testing Library for component tests
  - All UI components must have rendering tests
  - All user interactions must have behavior tests
  - All API client functions must have mock tests
- Tests written first → User approved → Tests fail → Then implement
- Edge cases and error paths must have tests
- Tests must be deterministic and isolated

**Rationale:** TDD ensures correctness, prevents regression, and serves as executable documentation for both backend and frontend.

### III. YAGNI Principle (Phase 2 Scope - All Features from Phase 1)
"You Aren't Gonna Need It" - Implement ALL 10 features from Phase 1, now as a web application with database persistence and multi-user support. No additional features beyond this list, no premature optimization, no speculative functionality.

**Phase 2 Features - Basic Level (Core Essentials):**
1. Add Task – Create new todo items via web UI
2. Delete Task – Remove tasks from the list
3. Update Task – Modify existing task details
4. View Task List – Display all tasks with filtering
5. Mark as Complete – Toggle task completion status

**Phase 2 Features - Intermediate Level (Organization & Usability):**
6. Priorities & Tags/Categories – Assign levels (high/medium/low) or labels (work/home)
7. Search & Filter – Search by keyword; filter by status, priority, or date
8. Sort Tasks – Reorder by due date, priority, or alphabetically

**Phase 2 Features - Advanced Level (Intelligent Features):**
9. Recurring Tasks – Auto-reschedule repeating tasks (e.g., "weekly meeting")
10. Due Dates & Time Reminders – Set deadlines with date/time pickers; notifications

**Still Forbidden in Phase 2:**
- ❌ AI chatbot interface (Phase III)
- ❌ Kubernetes deployment (Phase IV)
- ❌ Event-driven architecture with Kafka (Phase V)
- ❌ Any feature not in the above 10-feature list

**Rationale:** Maintain the comprehensive 10-feature scope from Phase 1, now delivered as a production-ready multi-user web application with persistent storage. All features must work together as a cohesive system before transitioning to Phase III (AI chatbot).

### IV. Technology Stack Requirements (Phase 2)
Phase 2 MUST use the specified technology stack. No substitutions.

**Mandatory Stack:**

**Frontend:**
- **Framework:** Next.js 16+ (App Router - not Pages Router)
- **Language:** TypeScript (strict mode)
- **Styling:** Tailwind CSS
- **Authentication:** Better Auth with JWT

**Backend:**
- **Framework:** Python FastAPI
- **Language:** Python 3.13+
- **ORM:** SQLModel
- **Database:** Neon Serverless PostgreSQL
- **Package Manager:** UV (not pip, not poetry)

**Testing & Quality:**
- **Backend Testing:** pytest, pytest-cov
- **Frontend Testing:** Jest, React Testing Library
- **Type Checking:** mypy (Python), TypeScript compiler
- **Linting:** ruff (Python), ESLint (TypeScript)
- **Formatting:** ruff format (Python), Prettier (TypeScript)

**Deployment (Optional for Phase 2):**
- **Frontend Hosting:** Vercel
- **Backend Hosting:** Any Python-compatible platform
- **Database:** Neon Serverless PostgreSQL (managed)

**Rules:**
- All dependencies managed via `pyproject.toml` (backend) and `package.json` (frontend)
- Must use monorepo structure with `frontend/` and `backend/` folders
- JWT tokens for authentication between frontend and backend
- Shared `BETTER_AUTH_SECRET` environment variable for JWT signing
- RESTful API design (no GraphQL, no gRPC in Phase 2)

**Rationale:** Standardization ensures consistency across all hackathon submissions and prepares for Phase III (AI chatbot) migration.

### V. Clean Code & Modularity (Phase 2 - Monorepo Structure)
Code MUST be well-organized, modular, and follow clean code principles. Phase 2 uses a monorepo structure with clear separation between frontend and backend.

**Organization Requirements:**
- Separation of concerns (data models, business logic, API routes, UI components)
- Single Responsibility Principle for all functions, classes, and components
- Clear, descriptive naming (no abbreviations like `td`, `lst`, `mgr`)
- Maximum function length: 20 lines (excluding docstrings)
- Maximum file length: 200 lines (300 for complex API routes)

**Monorepo Project Structure:**
```
evolved-todo/
├── .spec-kit/
│   └── config.yaml
├── specs/
│   ├── overview.md
│   ├── architecture.md
│   ├── features/          # Feature specifications
│   ├── api/               # API specifications
│   ├── database/          # Database schema
│   └── ui/                # UI component specs
├── frontend/
│   ├── CLAUDE.md
│   ├── app/               # Next.js App Router pages
│   ├── components/        # Reusable UI components
│   ├── lib/               # API client, utilities
│   ├── types/             # TypeScript types
│   └── __tests__/         # Frontend tests
├── backend/
│   ├── CLAUDE.md
│   ├── app/
│   │   ├── main.py        # FastAPI entry point
│   │   ├── models.py      # SQLModel database models
│   │   ├── routes/        # API route handlers
│   │   ├── services/      # Business logic
│   │   ├── auth.py        # JWT authentication
│   │   └── db.py          # Database connection
│   └── tests/             # Backend tests
├── docker-compose.yml
├── CLAUDE.md
└── README.md
```

**Rationale:** Monorepo structure enables unified development experience with Claude Code while maintaining clear separation between frontend and backend concerns.

### VI. Type Safety (Phase 2 - Python & TypeScript)
All functions MUST have complete type annotations. Type checking MUST pass without errors for both Python and TypeScript.

**Backend (Python) Requirements:**
- Function signatures: parameters and return types fully annotated
- Class attributes: type annotations required
- No `Any` types unless explicitly justified
- Use generic types (`list[Task]`, not `list`)
- Enable strict mypy mode
- SQLModel models with proper type hints

**Frontend (TypeScript) Requirements:**
- Enable strict mode in `tsconfig.json`
- All component props fully typed (no implicit `any`)
- API response types defined and validated
- Use TypeScript generics where appropriate
- Avoid type assertions (`as`) unless necessary

**Example (Backend):**
```python
from sqlmodel import Field, SQLModel

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(max_length=200)
    description: str | None = None
    completed: bool = False
```

**Example (Frontend):**
```typescript
interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
}

async function getTasks(userId: string): Promise<Task[]> {
  const response = await fetch(`/api/${userId}/tasks`);
  return response.json();
}
```

**Rationale:** Type safety catches bugs at compile time, improves IDE support, and serves as inline documentation for both backend and frontend.

### VII. Comprehensive Documentation (Phase 2 - API & UI)
Documentation MUST be thorough, clear, and maintained alongside code. Phase 2 includes API documentation and UI component documentation.

**Required Documentation:**

1. **README.md:**
   - Project overview and Phase 2 scope
   - Setup instructions (frontend and backend)
   - Environment variables (BETTER_AUTH_SECRET, DATABASE_URL, etc.)
   - Running locally (frontend, backend, database)
   - Running tests (backend and frontend)
   - Deployment instructions

2. **API Documentation:**
   - All API endpoints documented in `specs/api/rest-endpoints.md`
   - Request/response schemas with examples
   - Authentication requirements (JWT token header)
   - Error response formats

3. **Database Schema Documentation:**
   - Schema documented in `specs/database/schema.md`
   - All tables, columns, relationships, indexes
   - Migration strategy (SQLModel automatic migrations)

4. **Docstrings/Comments (Backend):**
   - All public functions, classes, methods (Google style)
   - Include Args, Returns, Raises sections
   - FastAPI route handlers with OpenAPI descriptions

5. **Component Documentation (Frontend):**
   - All reusable components documented with props
   - Usage examples for complex components
   - Storybook documentation (optional but recommended)

6. **Architecture Documentation:**
   - `specs/architecture.md` explaining monorepo organization
   - Data flow: Frontend → API → Database
   - Authentication flow: Better Auth → JWT → FastAPI
   - Design decisions and rationale

**Rationale:** Comprehensive docs enable onboarding, facilitate review, and prepare for Phase III (AI chatbot) handoff.

### VIII. Error Handling (Phase 2 - HTTP Errors)
Errors MUST be handled explicitly and gracefully. No silent failures. Phase 2 includes HTTP error responses with proper status codes.

**Backend (FastAPI) Requirements:**
- Validate all inputs with Pydantic models
- Use HTTPException with appropriate status codes
- Return structured error responses with `detail` field
- Handle database errors (connection, constraints, etc.)
- Log errors for debugging

**Frontend (Next.js) Requirements:**
- Handle API errors gracefully (network errors, 4xx, 5xx)
- Display user-friendly error messages
- Validate user inputs before API calls
- Use error boundaries for React component errors
- Provide fallback UI for error states

**HTTP Status Codes:**
- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid input validation
- `401 Unauthorized` - Missing or invalid JWT token
- `403 Forbidden` - User doesn't have access to resource
- `404 Not Found` - Resource doesn't exist
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

**Example (Backend):**
```python
from fastapi import HTTPException, status

@app.get("/api/{user_id}/tasks/{task_id}")
async def get_task(user_id: str, task_id: int):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this task"
        )
    return task
```

**Example (Frontend):**
```typescript
async function getTasks(userId: string): Promise<Task[]> {
  try {
    const response = await fetch(`/api/${userId}/tasks`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch tasks');
    }
    return response.json();
  } catch (error) {
    console.error('Error fetching tasks:', error);
    toast.error('Failed to load tasks. Please try again.');
    return [];
  }
}
```

**Rationale:** Explicit error handling with proper HTTP semantics prevents undefined behavior and improves user experience in web applications.

### IX. Multi-User Data Isolation & Security (NEW - Phase 2)
Every user MUST only see and modify their own data. Authentication and authorization are mandatory for all API endpoints.

**Authentication Requirements:**
- **Better Auth** on Next.js frontend for user signup/signin
- JWT tokens issued by Better Auth upon successful login
- JWT tokens include `user_id` claim for identification
- Tokens expire after 7 days (configurable)
- Refresh tokens supported for seamless re-authentication

**Authorization Requirements:**
- All API endpoints require valid JWT token in `Authorization: Bearer <token>` header
- Requests without token receive `401 Unauthorized`
- Backend extracts `user_id` from JWT token
- All database queries filtered by `user_id`
- Task ownership enforced: users can only access their own tasks
- Path parameter `{user_id}` MUST match JWT token `user_id` claim

**Security Rules:**
- Shared `BETTER_AUTH_SECRET` between frontend and backend
- Secret stored in environment variables (never committed to git)
- JWT signature verified on every request
- No SQL injection (use parameterized queries via SQLModel)
- No XSS (escape all user inputs in UI)
- HTTPS required for production (enforced by Vercel/hosting)

**Example (Backend Middleware):**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.BETTER_AUTH_SECRET, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@app.get("/api/{user_id}/tasks")
async def list_tasks(user_id: str, authenticated_user_id: str = Depends(verify_token)):
    if user_id != authenticated_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()
    return tasks
```

**Rationale:** Multi-user data isolation ensures privacy, security, and prevents unauthorized access in a production web application.

### X. Database Schema & Migration Management (NEW - Phase 2)
Database schema MUST be versioned, documented, and managed through migrations. SQLModel provides automatic schema management.

**Database Requirements:**
- **Provider:** Neon Serverless PostgreSQL (managed, no local setup)
- **ORM:** SQLModel (combines SQLAlchemy + Pydantic)
- **Migrations:** SQLModel automatic table creation (Phase 2 only - manual migrations in Phase 3+)
- **Connection:** Connection string from `DATABASE_URL` environment variable

**Schema Design Rules:**
- All tables include `created_at` and `updated_at` timestamps
- Use appropriate indexes for query performance (`user_id`, `completed`, etc.)
- Foreign keys for relationships (users → tasks)
- NOT NULL constraints for required fields
- VARCHAR limits for text fields (prevent abuse)

**Phase 2 Database Models:**

**Users Table (Managed by Better Auth):**
```python
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)  # UUID from Better Auth
    email: str = Field(unique=True, index=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Tasks Table:**
```python
from datetime import datetime, date, time
from sqlmodel import Field, SQLModel

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)

    # Intermediate Level (Priorities & Tags)
    priority: str | None = Field(default=None)  # "high", "medium", "low"
    tags: str | None = Field(default=None)  # Comma-separated tags

    # Advanced Level (Recurring & Due Dates)
    due_date: date | None = Field(default=None)
    due_time: time | None = Field(default=None)
    recurrence: str | None = Field(default=None)  # "daily", "weekly", "monthly"
    recurrence_day: int | None = Field(default=None)  # Day of week/month

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Migration Strategy (Phase 2):**
- SQLModel creates tables automatically on first run
- Use `create_db_and_tables()` in `app/db.py`
- No manual migrations needed for Phase 2
- Schema documented in `specs/database/schema.md`

**Rationale:** Structured schema management ensures data integrity, query performance, and smooth evolution as features are added.

### XI. API Design & RESTful Conventions (NEW - Phase 2)
All API endpoints MUST follow RESTful conventions and return consistent, predictable responses.

**RESTful Endpoint Design:**

| Method | Endpoint | Description | Request Body | Success Response |
|--------|----------|-------------|--------------|------------------|
| GET | `/api/{user_id}/tasks` | List all tasks | None | `200 OK` + Task[] |
| POST | `/api/{user_id}/tasks` | Create task | Task data | `201 Created` + Task |
| GET | `/api/{user_id}/tasks/{id}` | Get task | None | `200 OK` + Task |
| PUT | `/api/{user_id}/tasks/{id}` | Update task | Task data | `200 OK` + Task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task | None | `204 No Content` |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle complete | None | `200 OK` + Task |

**API Conventions:**
- All endpoints prefixed with `/api`
- User-scoped endpoints include `{user_id}` path parameter
- Use plural nouns for resources (`/tasks`, not `/task`)
- Use HTTP methods semantically (GET = read, POST = create, PUT = update, DELETE = delete, PATCH = partial update)
- Return appropriate status codes (2xx success, 4xx client error, 5xx server error)
- Return JSON responses with consistent structure

**Request/Response Format:**

**List Tasks (with filters):**
```
GET /api/{user_id}/tasks?status=pending&sort=due_date
Response: 200 OK
[
  {
    "id": 1,
    "user_id": "user123",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "priority": "high",
    "tags": "shopping,urgent",
    "due_date": "2025-12-15",
    "due_time": "18:00:00",
    "recurrence": null,
    "recurrence_day": null,
    "created_at": "2025-12-10T10:00:00Z",
    "updated_at": "2025-12-10T10:00:00Z"
  }
]
```

**Create Task:**
```
POST /api/{user_id}/tasks
{
  "title": "Call dentist",
  "description": "Schedule checkup",
  "priority": "medium",
  "tags": "health",
  "due_date": "2025-12-12"
}
Response: 201 Created
{
  "id": 2,
  "user_id": "user123",
  "title": "Call dentist",
  ...
}
```

**Error Response Format:**
```
Response: 404 Not Found
{
  "detail": "Task with ID 999 not found"
}
```

**Query Parameters (List Endpoint):**
- `status`: Filter by completion status (`all`, `pending`, `completed`)
- `priority`: Filter by priority (`high`, `medium`, `low`)
- `tag`: Filter by tag (exact match)
- `sort`: Sort field (`id`, `title`, `priority`, `due_date`, `created_at`)
- `order`: Sort order (`asc`, `desc`)

**Rationale:** RESTful conventions ensure predictable, discoverable APIs that follow industry standards and integrate seamlessly with frontend frameworks.

## Phase 2 Scope Constraints

### In-Scope
- **Frontend:** Next.js web interface with all 10 features
- **Backend:** FastAPI REST API with JWT authentication
- **Database:** Neon PostgreSQL with SQLModel ORM
- **Authentication:** Better Auth with JWT tokens
- **Multi-User:** Complete user isolation and data privacy
- **All 10 Features:** Basic (1-5), Intermediate (6-8), Advanced (9-10)
- **Testing:** Comprehensive test coverage (>90%) for backend and frontend
- **Deployment:** Frontend on Vercel, backend on any platform

### Out-of-Scope (Future Phases)
- ❌ AI chatbot interface (Phase III)
- ❌ MCP server architecture (Phase III)
- ❌ Kubernetes deployment (Phase IV)
- ❌ Event-driven architecture with Kafka (Phase V)
- ❌ Dapr distributed runtime (Phase V)

## Development Workflow (Phase 2)

### Feature Development Process
1. **Specification:** Write feature spec in `specs/features/<feature>/spec.md`
   - Include API endpoint definitions
   - Include UI component requirements
   - Include database schema changes
2. **Review Spec:** Ensure alignment with constitution and acceptance criteria
3. **Database First:** Update database models in `backend/app/models.py`
4. **Write Backend Tests:** Create failing tests for API endpoints
5. **Implement Backend:** Write FastAPI routes and service logic (Red → Green)
6. **Write Frontend Tests:** Create failing tests for UI components
7. **Implement Frontend:** Write React components and API client (Red → Green)
8. **Integration Testing:** Test full stack (frontend → API → database)
9. **Refactor:** Improve code quality while keeping tests green
10. **Documentation:** Update README, API docs, component docs
11. **Final Review:** Verify all quality gates pass

### Iteration Cycle
- Each feature is a single iteration
- Complete backend + frontend for one feature before starting next
- Order: Add → View → Update → Mark Complete → Delete → Priorities/Tags → Search/Filter → Sort → Recurring → Due Dates

## Quality Gates (Phase 2)

All quality gates MUST pass before a feature is considered complete.

### Automated Checks (Must Pass)

**Backend:**
- ✅ `pytest` - All backend tests pass
- ✅ `mypy` - No type errors (strict mode)
- ✅ `ruff check` - No linting errors
- ✅ `ruff format --check` - Code formatted correctly
- ✅ Test coverage >90% (pytest-cov)

**Frontend:**
- ✅ `npm test` - All frontend tests pass
- ✅ `tsc --noEmit` - No TypeScript errors
- ✅ `eslint` - No linting errors
- ✅ `prettier --check` - Code formatted correctly
- ✅ `npm run build` - Production build succeeds

**Integration:**
- ✅ API endpoints return correct responses
- ✅ JWT authentication works end-to-end
- ✅ Database queries are optimized (no N+1 queries)

### Manual Reviews (Must Confirm)
- ✅ Spec requirements met (all acceptance criteria)
- ✅ Constitution compliance (all principles followed)
- ✅ API documentation complete
- ✅ UI/UX is responsive and accessible
- ✅ Error handling for all edge cases
- ✅ Multi-user data isolation verified
- ✅ Security: JWT tokens, HTTPS, no SQL injection/XSS

### Pre-Submission Checklist
- [ ] All 10 features implemented (Basic + Intermediate + Advanced)
- [ ] All quality gates pass (backend + frontend)
- [ ] Better Auth configured with JWT
- [ ] Neon database connected and working
- [ ] All API endpoints secured with JWT middleware
- [ ] README includes setup instructions for both frontend and backend
- [ ] Architecture documentation explains monorepo and data flow
- [ ] Frontend deployed to Vercel
- [ ] Backend deployed and accessible
- [ ] Demo video created (<90 seconds)

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
When transitioning from Phase 2 → Phase 3:
1. Update this same `constitution.md` file (do not create separate files)
2. Increment version to 3.0.0 (MAJOR - phase transition with breaking changes)
3. Update principles to reflect Phase 3 requirements (AI chatbot, MCP, etc.)
4. Document breaking changes in Sync Impact Report at top of file
5. Update Last Amended date
6. Update all dependent templates and guidance for Phase 3 stack
7. Git history will preserve Phase 2 version for reference

**Note:** This constitution is a living document. All phase updates modify this single file with version increments tracked via git.

**Version:** 2.0.0 | **Ratified:** 2025-12-06 | **Last Amended:** 2025-12-10
