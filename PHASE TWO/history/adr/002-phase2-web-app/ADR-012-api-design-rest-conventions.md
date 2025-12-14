# ADR-012: API Design & RESTful Conventions

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-11
- **Feature:** 002-phase2-web-app
- **Context:** Phase 2 requires a well-designed REST API for task CRUD operations with filtering, sorting, and searching. The API must follow HTTP conventions, provide clear error messages, enforce user isolation, and integrate seamlessly with Next.js frontend using Axios.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Defines all API contracts
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - REST vs GraphQL vs tRPC
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all frontend-backend communication
-->

## Decision

Adopt **RESTful API design** with the following conventions and patterns:

**API Pattern:**
- **Style:** RESTful HTTP with resource-based endpoints
- **Base Path:** `/api/{user_id}/tasks` (user_id in path for explicit user isolation)
- **HTTP Methods:** GET (read), POST (create), PUT (update), PATCH (toggle), DELETE (delete)
- **Content Type:** `application/json` for all requests and responses

**Endpoint Structure:**
```
GET    /health                              # Health check (no auth)
GET    /api/{user_id}/tasks                 # List all tasks with filters
POST   /api/{user_id}/tasks                 # Create new task
GET    /api/{user_id}/tasks/{id}            # Get specific task (optional)
PUT    /api/{user_id}/tasks/{id}            # Update task (full replacement)
PATCH  /api/{user_id}/tasks/{id}/complete   # Toggle completion status
DELETE /api/{user_id}/tasks/{id}            # Delete task
```

**Query Parameters (GET /api/{user_id}/tasks):**
- `completed` (boolean): Filter by completion status
- `priority` (string): Filter by priority (low, medium, high)
- `tag` (string): Filter by tag (exact match)
- `search` (string): Full-text search in title and description
- `due_date_filter` (string): overdue, today, this_week
- `sort_by` (string): created_at, due_date, priority, title, completed
- `sort_order` (string): asc, desc

**HTTP Status Codes:**
- `200 OK`: Successful GET/PUT/PATCH
- `201 Created`: Successful POST
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Validation error (missing fields, invalid format)
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: User attempting to access another user's data
- `404 Not Found`: Task ID does not exist
- `422 Unprocessable Entity`: Business logic validation failure
- `500 Internal Server Error`: Unexpected server error

**Request Schema (POST/PUT):**
```json
{
  "title": "string (required, 1-200 chars)",
  "description": "string (optional, max 1000 chars)",
  "priority": "low | medium | high | null",
  "tags": "comma,separated,tags",
  "due_date": "YYYY-MM-DD | null",
  "due_time": "HH:MM:SS | null (only if due_date set)",
  "recurrence_pattern": "daily | weekly | monthly | null",
  "recurrence_day": "1-7 (weekly) | 1-31 (monthly) | null"
}
```

**Response Schema (Task):**
```json
{
  "id": 123,
  "user_id": 1,
  "title": "string",
  "description": "string | null",
  "completed": false,
  "completed_at": "ISO 8601 timestamp | null",
  "priority": "low | medium | high | null",
  "tags": "comma,separated,tags",
  "due_date": "YYYY-MM-DD | null",
  "due_time": "HH:MM:SS | null",
  "recurrence_pattern": "daily | weekly | monthly | null",
  "recurrence_day": 1-31 | null,
  "created_at": "ISO 8601 timestamp",
  "updated_at": "ISO 8601 timestamp"
}
```

**Error Response Schema:**
```json
{
  "detail": "Human-readable error message",
  "field": "field_name (for validation errors)",
  "code": "ERROR_CODE (optional)"
}
```

**Authentication:**
- All endpoints except `/health` require JWT in `Authorization: Bearer <token>` header
- Backend validates token and extracts `user_id`
- Path `{user_id}` must match JWT `sub` claim (403 if mismatch)

**Validation Strategy:**
- Request validation via Pydantic schemas (automatic by FastAPI)
- Business logic validation in service layer
- Database constraints enforce data integrity

## Consequences

### Positive

- **HTTP Conventions:** Standard HTTP methods and status codes make API intuitive
- **User Isolation:** `user_id` in path makes user boundary explicit and auditable
- **Type Safety:** Pydantic schemas validate all inputs automatically
- **Auto-Documentation:** FastAPI generates OpenAPI schema automatically
- **Frontend Integration:** Axios can use standard REST patterns without custom logic
- **Filtering Flexibility:** Query parameters enable complex task filtering without GraphQL
- **Error Clarity:** Structured error responses help frontend display helpful messages
- **Idempotency:** PUT/DELETE are idempotent (safe to retry)
- **Caching:** GET requests cacheable by HTTP layer

### Negative

- **Over-fetching:** REST can return unnecessary fields (mitigated: small task objects)
- **Multiple Requests:** No nested resources (e.g., user + tasks in one request) unlike GraphQL
- **Query Parameter Complexity:** Many filters lead to long query strings
- **Versioning Challenge:** API versioning requires `/v1/` path prefix or header-based versioning
- **Path Parameter Duplication:** `user_id` in path is redundant (already in JWT)
- **N+1 Queries:** REST can lead to multiple round trips for related data

## Alternatives Considered

**Alternative A: GraphQL (Apollo Server + Apollo Client)**
- **Pros:** Flexible queries, no over-fetching, strongly typed schema, single endpoint
- **Cons:** Learning curve, complexity for simple CRUD, caching is harder, larger payload
- **Why Rejected:** Overkill for simple task CRUD. REST is simpler and well-understood by team.

**Alternative B: tRPC (End-to-End TypeScript RPC)**
- **Pros:** Full type safety across frontend/backend, no schema duplication, excellent DX
- **Cons:** TypeScript-only (can't use from mobile apps), monorepo coupling required
- **Why Rejected:** Tightly couples frontend and backend. REST enables independent evolution.

**Alternative C: REST without user_id in path (user_id from JWT only)**
- **Endpoint:** `/api/tasks` (user_id inferred from JWT)
- **Pros:** Cleaner URLs, no redundant path parameter
- **Cons:** Less explicit, harder to audit, path doesn't clearly show user boundary
- **Why Rejected:** Explicit `user_id` in path improves security auditability and makes user isolation obvious.

**Alternative D: JSON:API Specification**
- **Pros:** Standardized structure, relationships, pagination, filtering conventions
- **Cons:** Verbose response format, learning curve, overkill for simple API
- **Why Rejected:** JSON:API adds complexity without significant benefit for task CRUD.

**Alternative E: gRPC + Protobuf**
- **Pros:** Binary protocol, faster than JSON, strongly typed, streaming support
- **Cons:** Not browser-friendly (requires grpc-web), tooling complexity, harder debugging
- **Why Rejected:** Web browsers don't natively support gRPC. REST+JSON is simpler for web apps.

## References

- Feature Spec: `specs/002-phase2-web-app/spec.md`
- Implementation Plan: `specs/002-phase2-web-app/plan.md` (lines 124-127)
- Contracts: `specs/002-phase2-web-app/contracts/api-endpoints.md`
- Request Schemas: `specs/002-phase2-web-app/contracts/request-schemas.md`
- Response Schemas: `specs/002-phase2-web-app/contracts/response-schemas.md`
- Related ADRs: ADR-009 (Backend Stack), ADR-011 (Authentication)
- Evaluator Evidence: `history/prompts/002-phase2-web-app/014-create-adrs-phase2.misc.prompt.md`
