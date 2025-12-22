# ADR-011: Authentication & Authorization Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-11
- **Feature:** 002-phase2-web-app
- **Context:** Phase 2 adds multi-user support, requiring secure authentication and user isolation. The system must prevent users from accessing each other's tasks, maintain session state across requests, and integrate seamlessly with both Next.js frontend and FastAPI backend.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Defines all security boundaries
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - JWT vs session cookies vs OAuth
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all authenticated endpoints
-->

## Decision

Adopt **Better Auth with JWT (HS256)** as the integrated authentication and authorization strategy:

**Authentication Library:**
- **Frontend:** Better Auth (framework-agnostic, JWT-based)
- **Backend:** Custom JWT validation middleware (FastAPI)
- **User Management:** Better Auth creates and manages `users` table in PostgreSQL

**Token Strategy:**
- **Token Type:** JWT (JSON Web Token) with HS256 algorithm
- **Token Storage:** HTTP-only cookies (frontend), secure flag in production
- **Token Expiration:** 7 days (no refresh tokens in Phase 2)
- **Shared Secret:** `BETTER_AUTH_SECRET` environment variable shared between frontend and backend

**JWT Payload:**
```json
{
  "sub": <user_id>,        // User ID (integer)
  "email": "user@example.com",
  "iat": <issued_at>,      // Unix timestamp
  "exp": <expires_at>      // Unix timestamp (iat + 7 days)
}
```

**Frontend Flow:**
1. User registers/logs in via Better Auth forms
2. Better Auth creates user in PostgreSQL and generates JWT
3. JWT stored in HTTP-only cookie
4. All API requests include JWT in `Authorization: Bearer <token>` header

**Backend Flow:**
1. FastAPI middleware extracts JWT from `Authorization` header
2. Validates JWT signature using shared `BETTER_AUTH_SECRET`
3. Extracts `user_id` from token payload (`sub` claim)
4. Injects `user_id` into request context via dependency injection
5. All queries filter by `user_id` to enforce user isolation

**User Isolation:**
- All task API endpoints include `{user_id}` path parameter: `/api/{user_id}/tasks`
- Backend validates path `user_id` matches JWT `sub` claim (403 if mismatch)
- Database queries always filter: `WHERE user_id = <authenticated_user_id>`

**Authorization Pattern:**
```python
# FastAPI dependency
async def get_current_user(
    authorization: str = Header(None),
    session: AsyncSession = Depends(get_session)
) -> User:
    token = authorization.split("Bearer ")[1]
    payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])
    user_id = payload["sub"]
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401)
    return user

# Route usage
@router.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403)
    # Query tasks filtered by user_id
```

**Security Measures:**
- HTTPS only in production (HTTP in local dev)
- Secure, SameSite=Lax cookies
- CORS restricted to frontend origin
- Rate limiting on auth endpoints (optional Phase 2+)

## Consequences

### Positive

- **Stateless Authentication:** JWT enables horizontal scaling (no session store needed)
- **Framework Agnostic:** Better Auth works with any framework (Next.js, Remix, etc.)
- **Simple Integration:** Shared secret approach is straightforward to implement
- **User Isolation:** Path parameter + JWT validation ensures data security
- **Performance:** No database lookup per request (JWT is self-contained)
- **Developer Experience:** Better Auth provides ready-made UI components
- **Frontend Control:** Better Auth manages entire auth flow in frontend
- **Cookie Security:** HTTP-only cookies prevent XSS token theft

### Negative

- **No Refresh Tokens:** 7-day expiration means users re-login weekly (acceptable for Phase 2)
- **Token Size:** JWT in headers increases request size (~1KB)
- **Secret Sharing:** Frontend and backend must share `BETTER_AUTH_SECRET` (deployment complexity)
- **Revocation Challenge:** Cannot revoke JWTs before expiration (7-day window if compromised)
- **Better Auth Maturity:** Newer library, less battle-tested than NextAuth/Clerk
- **Single Device:** No multi-device session management in Phase 2

## Alternatives Considered

**Alternative A: NextAuth (formerly Auth.js) with Session Cookies**
- **Pros:** Mature ecosystem, built-in providers (Google, GitHub), session database
- **Cons:** Tightly coupled to Next.js, requires session database, complex setup
- **Why Rejected:** Better Auth is lighter and doesn't require session storage. Simpler for JWT-only approach.

**Alternative B: Clerk (Auth-as-a-Service)**
- **Pros:** Full-featured, drop-in UI, multi-factor auth, managed service
- **Cons:** Expensive at scale, vendor lock-in, external dependency
- **Why Rejected:** Cost prohibitive for indie project. Adds external service dependency.

**Alternative C: Auth0 (Enterprise Auth Provider)**
- **Pros:** Enterprise-grade security, extensive features, compliance certifications
- **Cons:** Complex setup, expensive, overkill for Phase 2
- **Why Rejected:** Adds unnecessary complexity and cost for simple JWT authentication.

**Alternative D: Session Cookies (server-side sessions in PostgreSQL)**
- **Pros:** Revocable sessions, no JWT complexity, simpler secret management
- **Cons:** Requires session database, stateful (complicates scaling), database lookup per request
- **Why Rejected:** Stateful sessions add database load. JWT is more scalable for API-first design.

**Alternative E: Supabase Auth**
- **Pros:** Integrated with Supabase database, built-in user management, RLS (row-level security)
- **Cons:** Requires Supabase database (we chose Neon), vendor lock-in
- **Why Rejected:** We already selected Neon PostgreSQL. Supabase would require changing ADR-010.

**Alternative F: OAuth-only (Google, GitHub login, no email/password)**
- **Pros:** No password management, improved security, easier for users
- **Cons:** Requires external accounts, more complex setup, privacy concerns
- **Why Rejected:** Email/password is simpler for MVP. Can add OAuth in Phase 3+.

## References

- Feature Spec: `specs/002-phase2-web-app/001-authentication/spec.md`
- Implementation Plan: `specs/002-phase2-web-app/plan.md` (lines 10-15)
- Research: `specs/002-phase2-web-app/research.md` (Better Auth JWT Implementation section)
- Contracts: `specs/002-phase2-web-app/contracts/authentication.md`
- Related ADRs: ADR-008 (Frontend Stack), ADR-009 (Backend Stack), ADR-010 (Database)
- Evaluator Evidence: `history/prompts/002-phase2-web-app/014-create-adrs-phase2.misc.prompt.md`
