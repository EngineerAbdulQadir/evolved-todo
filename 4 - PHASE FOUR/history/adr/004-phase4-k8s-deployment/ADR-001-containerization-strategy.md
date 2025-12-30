# ADR-001: Containerization Strategy with Multi-Stage Builds and Health Checks

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-25
- **Feature:** 004-phase4-k8s-deployment
- **Context:** Phase 4 requires containerizing the Phase 3 AI Chatbot (Next.js frontend + FastAPI backend) for deployment on Kubernetes. Decisions must optimize for image size (<150MB frontend, <200MB backend), security (zero critical vulnerabilities), and Kubernetes integration (health probes for self-healing).

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: ✅ Long-term consequence - all future deployments use these patterns
     2) Alternatives: ✅ Multiple viable options (single-stage, external builds, different base images)
     3) Scope: ✅ Cross-cutting - affects both frontend and backend, build process, deployment, monitoring
-->

## Decision

**Containerization Strategy**:
- **Multi-stage Dockerfiles**: Separate build and production stages for both frontend and backend
- **Base Images**: node:22-alpine (frontend), python:3.13-slim (backend) - pinned to specific versions
- **Health Check Endpoints**: Dedicated `/health` (backend) and `/api/health` (frontend) endpoints for Kubernetes probes
- **Non-root User**: All containers run as UID 1000 (security requirement)
- **Security Scanning**: Trivy scan integrated in CI/CD (zero critical/high vulnerabilities gate)

**Frontend Dockerfile Pattern**:
```dockerfile
# Stage 1: Build
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:22-alpine
RUN addgroup -g 1000 appgroup && adduser -D -u 1000 -G appgroup appuser
WORKDIR /app
COPY --from=builder --chown=appuser:appgroup /app/.next ./.next
COPY --from=builder --chown=appuser:appgroup /app/public ./public
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --chown=appuser:appgroup package.json ./
USER appuser
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"
CMD ["npm", "start"]
```

**Backend Dockerfile Pattern**:
```dockerfile
# Stage 1: Build
FROM python:3.13-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Stage 2: Production
FROM python:3.13-slim
RUN groupadd -g 1000 appgroup && useradd -u 1000 -g appgroup appuser
WORKDIR /app
COPY --from=builder --chown=appuser:appgroup /app/.venv ./.venv
COPY --chown=appuser:appgroup . .
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD [".venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Consequences

### Positive

- **Size Optimization**: Multi-stage builds exclude build tools from final image (30-40% size reduction)
  - Frontend: <150MB target (node_modules pruned to production only)
  - Backend: <200MB target (no pip, uv, build dependencies in final image)
- **Security**:
  - Non-root user prevents privilege escalation attacks
  - Trivy scan catches vulnerabilities before deployment
  - Alpine/slim base images have smaller attack surface than full images
- **Kubernetes Integration**:
  - Health check endpoints enable liveness/readiness/startup probes
  - Self-healing: K8s restarts unhealthy containers automatically
  - Zero-downtime deployments: readiness probes prevent traffic to unhealthy pods
- **Build Speed**: Layer caching optimizes rebuild time (dependencies cached, only app code rebuilt)
- **Reproducibility**: Pinned base image versions ensure consistent builds

### Negative

- **Build Complexity**: Multi-stage Dockerfiles more complex than single-stage (learning curve for team)
- **Image Pull Time**: Alpine uses musl libc (not glibc) - rare compatibility issues possible
- **Health Check Overhead**: HTTP health checks consume minimal resources but add complexity
- **Build Time**: Initial build slower due to multi-stage process (5 minutes vs 3 minutes single-stage)
- **Debugging**: Production images don't contain build tools - must use debug images for troubleshooting

## Alternatives Considered

**Alternative 1: Single-Stage Dockerfiles**
- **Description**: Build and run in same image stage
- **Why Rejected**:
  - Larger image size (300-400MB frontend, 500-600MB backend)
  - Security risk (build tools like npm, pip remain in production image)
  - Slower deployments (larger images take longer to pull)
- **Tradeoff**: Simpler Dockerfile but violates size and security constraints

**Alternative 2: External Build Scripts (CI/CD builds, Docker only for runtime)**
- **Description**: Build artifacts in CI/CD, copy into runtime-only Docker image
- **Why Rejected**:
  - Poor reproducibility (builds depend on CI/CD environment)
  - Complex orchestration (multiple steps, artifact management)
  - Dockerfile doesn't capture full build process
- **Tradeoff**: Simpler Dockerfile but harder to reproduce builds locally

**Alternative 3: Process-Based Health Checks (check if process running)**
- **Description**: Use `ps` or `pidof` for health checks instead of HTTP endpoints
- **Why Rejected**:
  - Process may be running but application unhealthy (e.g., deadlock, database connection lost)
  - K8s prefers HTTP/TCP health checks over exec probes (more reliable)
  - No visibility into application state
- **Tradeoff**: Simpler implementation but less accurate health detection

**Alternative 4: Distroless Base Images**
- **Description**: Use Google's distroless images (minimal, no shell)
- **Why Deferred to Phase 5**:
  - Maximum security (no shell, no package manager)
  - Debugging difficulty (no shell for kubectl exec troubleshooting)
  - Learning curve for team
- **Tradeoff**: Excellent for production but Alpine/slim sufficient for Phase 4

**Alternative 5: Full Base Images (node:22, python:3.13)**
- **Description**: Use full Debian-based images instead of Alpine/slim
- **Why Rejected**:
  - 3-5x larger images (violates size constraints)
  - Larger attack surface (more packages = more vulnerabilities)
  - Slower image pulls
- **Tradeoff**: Better compatibility but fails size requirements

## References

- Feature Spec: `specs/004-phase4-k8s-deployment/spec.md` (FR-001 to FR-010: Containerization requirements)
- Implementation Plan: `specs/004-phase4-k8s-deployment/plan.md`
- Research: `specs/004-phase4-k8s-deployment/research.md` (Sections 1-2: Multi-stage builds, Health checks)
- Related ADRs:
  - ADR-002: Kubernetes Resource & Scaling Strategy
  - ADR-003: Helm Chart Management Approach
- Evaluator Evidence: Will be created in PHR after implementation
