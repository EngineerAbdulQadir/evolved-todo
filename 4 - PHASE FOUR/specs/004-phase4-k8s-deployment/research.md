# Research: Phase 4 - Local Kubernetes Deployment

**Feature**: Phase 4 - Local Kubernetes Deployment
**Date**: 2025-12-25
**Purpose**: Resolve technical unknowns and document technology choices for containerization and Kubernetes deployment

## Overview

Phase 4 containerizes the Phase 3 AI Chatbot application and deploys it on local Kubernetes (Minikube) using Helm charts and AIOps tools. This research document addresses all technology choices, best practices, and implementation patterns required for successful deployment.

## Research Areas

### 1. Docker Multi-Stage Builds

**Decision**: Use multi-stage Dockerfiles with separate build and production stages

**Rationale**:
- **Size Optimization**: Multi-stage builds exclude build tools and dev dependencies from final image
- **Security**: Production image contains only runtime dependencies, reducing attack surface
- **Performance**: Smaller images = faster pulls, faster deployments
- **Best Practice**: Industry standard for production Docker images

**Alternatives Considered**:
1. **Single-stage Dockerfile**: Simpler but includes unnecessary build tools in production image (rejected due to size/security)
2. **Build scripts outside Docker**: More complex, doesn't leverage Docker layer caching (rejected for complexity)

**Frontend Multi-Stage Build Pattern**:
```dockerfile
# Build stage: Node 22 (full) for build tools
FROM node:22 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage: Node 22-alpine (minimal) for runtime
FROM node:22-alpine
RUN addgroup -g 1000 appgroup && adduser -u 1000 -G appgroup -s /bin/sh -D appuser
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
USER appuser
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1
CMD ["npm", "start"]
```

**Backend Multi-Stage Build Pattern**:
```dockerfile
# Build stage: Python 3.13 (full) for UV and dependencies
FROM python:3.13 AS builder
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Production stage: Python 3.13-slim (minimal) for runtime
FROM python:3.13-slim
RUN useradd -m -u 1000 appuser
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY app/ ./app/
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
CMD ["/app/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Best Practices**:
- Use official base images (node:22-alpine, python:3.13-slim)
- Pin specific versions (no `latest` tags)
- Copy package files first for better layer caching
- Use .dockerignore to exclude dev files (node_modules, .git, tests)
- Run as non-root user (UID 1000)
- Include HEALTHCHECK directive for Docker and K8s health checks

---

### 2. Container Health Checks

**Decision**: Implement dedicated health check endpoints that verify service readiness

**Rationale**:
- **Self-Healing**: Kubernetes uses health checks to automatically restart failed containers
- **Zero-Downtime**: Readiness probes prevent traffic to unhealthy pods
- **Fast Startup**: Startup probes allow slow initialization without false liveness failures
- **Observability**: Health status visible in Kubernetes dashboard and kubectl

**Alternatives Considered**:
1. **No health checks**: Simple but no automatic recovery (rejected for reliability)
2. **Process-based checks**: Check if process is running, not if service is healthy (rejected for accuracy)
3. **External monitoring only**: Requires additional infrastructure (rejected for complexity)

**Backend Health Check Implementation** (`backend/app/health.py`):
```python
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from datetime import datetime
import httpx

from app.db import engine
from app.models import Task

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check endpoint for Kubernetes liveness and readiness probes.

    Checks:
    1. FastAPI is running (implicit - if this code executes)
    2. Database connection is available
    3. OpenAI API is accessible (optional - may add latency)

    Returns:
        200 OK if healthy, 503 Service Unavailable if unhealthy
    """
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "unknown",
        "openai": "unknown"
    }

    # Check database connection
    try:
        with Session(engine) as session:
            # Simple query to verify DB connectivity
            session.exec(select(Task).limit(1))
            status["database"] = "connected"
    except Exception as e:
        status["status"] = "unhealthy"
        status["database"] = f"error: {str(e)}"
        raise HTTPException(status_code=503, detail=status)

    # OpenAI check optional (adds latency to health checks)
    # Can be enabled for deep health checks, disabled for fast liveness

    return status
```

**Frontend Health Check Implementation** (`frontend/app/api/health/route.ts`):
```typescript
// frontend/app/api/health/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  // Simple health check - if Next.js is serving this, it's healthy
  // Optional: Add check for backend connectivity

  return NextResponse.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'frontend',
  });
}
```

**Kubernetes Probe Configuration**:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10      # Wait 10s after container start
  periodSeconds: 10             # Check every 10s
  timeoutSeconds: 5             # Timeout after 5s
  failureThreshold: 3           # Restart after 3 consecutive failures

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 20       # Wait 20s for DB connection
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3           # Remove from service after 3 failures

startupProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 0
  periodSeconds: 5              # Check every 5s
  timeoutSeconds: 5
  failureThreshold: 12          # Allow up to 60s for startup (12 * 5s)
```

---

### 3. Kubernetes Resource Management

**Decision**: Define CPU and memory requests/limits for all pods based on Phase 3 performance data

**Rationale**:
- **Predictable Scheduling**: Requests ensure pods get minimum resources
- **Prevent Starvation**: Limits prevent runaway processes from consuming all cluster resources
- **Cost Optimization**: Right-sizing prevents over-provisioning
- **QoS Classes**: Proper requests/limits enable Guaranteed or Burstable QoS

**Alternatives Considered**:
1. **No limits**: Simple but risks resource starvation (rejected for reliability)
2. **Only requests**: No upper bound on resource usage (rejected for multi-tenant safety)
3. **Only limits**: Scheduler can't make informed decisions (rejected for scheduling efficiency)

**Resource Specifications**:

**Frontend** (Next.js):
```yaml
resources:
  requests:
    cpu: 100m        # 0.1 CPU core minimum
    memory: 128Mi    # 128 MiB minimum
  limits:
    cpu: 200m        # 0.2 CPU core maximum
    memory: 256Mi    # 256 MiB maximum
```

**Backend** (FastAPI + OpenAI Agents SDK + MCP):
```yaml
resources:
  requests:
    cpu: 200m        # 0.2 CPU core minimum
    memory: 256Mi    # 256 MiB minimum
  limits:
    cpu: 500m        # 0.5 CPU core maximum
    memory: 512Mi    # 512 MiB maximum
```

**Rationale for Values**:
- **Frontend**: Lightweight Next.js SSR, primarily I/O bound (waiting on backend)
- **Backend**: Heavier workload (Python runtime, SQLModel ORM, OpenAI API calls, MCP tools)
- **Buffer**: Limits are 2x requests to allow bursts without triggering OOMKilled
- **Tested**: Values based on Phase 3 local testing (100 concurrent requests, <2s response time)

**Quality of Service (QoS) Class**: **Burstable**
- Requests < Limits → Burstable QoS
- Pods can burst above requests but won't be evicted unless node is under pressure
- Better than BestEffort (no guarantees) and more flexible than Guaranteed (requests = limits)

---

### 4. Horizontal Pod Autoscaling (HPA)

**Decision**: Use HPA for backend with CPU-based scaling (2-10 pods), frontend with CPU-based scaling (2-5 pods)

**Rationale**:
- **Elasticity**: Automatically scale pods based on load
- **Cost Efficiency**: Scale down during low usage periods
- **Availability**: Scale up during high usage periods
- **Stateless Architecture**: Phase 3 stateless design enables horizontal scaling

**Alternatives Considered**:
1. **Fixed replicas**: Simple but can't handle load spikes (rejected for scalability)
2. **Manual scaling**: Requires human intervention (rejected for automation)
3. **Memory-based HPA**: Less predictive for request-based workloads (rejected for accuracy)
4. **Custom metrics (request rate)**: More accurate but requires Prometheus + adapter (deferred to Phase 5)

**Backend HPA Configuration**:
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
  minReplicas: 2                # Minimum for high availability
  maxReplicas: 10               # Maximum based on Minikube resources (4 CPU, 8GB RAM)
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70  # Scale up if avg CPU > 70%
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60    # Wait 60s before scaling up
      policies:
      - type: Pods
        value: 2                         # Add 2 pods at a time
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300   # Wait 5min before scaling down
      policies:
      - type: Pods
        value: 1                         # Remove 1 pod at a time
        periodSeconds: 60
```

**Frontend HPA Configuration**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: frontend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: frontend
  minReplicas: 2
  maxReplicas: 5                # Frontend is lightweight, fewer replicas needed
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80  # Higher threshold for frontend
```

**Prerequisites**:
- Metrics server must be installed in Minikube: `minikube addons enable metrics-server`
- Resource requests must be defined (HPA uses requests as baseline)

**Testing HPA**:
```bash
# Generate load to trigger autoscaling
kubectl run -i --tty load-generator --rm --image=busybox --restart=Never -- /bin/sh
# Inside container:
while true; do wget -q -O- http://backend.default.svc.cluster.local:8000/api/health; done

# Watch HPA behavior
kubectl get hpa backend-hpa --watch

# Verify pods scaling
kubectl get pods --watch
```

---

### 5. Helm Chart Structure and Templating

**Decision**: Use standard Helm chart structure with parameterized values for environment-specific configuration

**Rationale**:
- **Templating**: Single chart definition, multiple deployments (dev, prod)
- **Versioning**: Chart version tracks deployment changes
- **Rollback**: Easy rollback to previous chart versions
- **Best Practice**: Helm is industry standard for Kubernetes package management

**Alternatives Considered**:
1. **Raw K8s manifests**: No templating, duplication across environments (rejected for maintainability)
2. **Kustomize**: Patching-based, less intuitive than Helm (rejected for learning curve)
3. **Custom scripts**: Reinventing the wheel (rejected for complexity)

**Chart Structure**:
```
helm/evolved-todo/
├── Chart.yaml              # Metadata (name, version, appVersion)
├── values.yaml             # Default values (production defaults)
├── values-dev.yaml         # Development overrides
├── templates/
│   ├── _helpers.tpl        # Common labels and selectors
│   ├── namespace.yaml
│   ├── secrets.yaml        # Templated secrets (values from values.yaml)
│   ├── configmaps.yaml
│   ├── frontend/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── hpa.yaml
│   └── backend/
│       ├── deployment.yaml
│       ├── service.yaml
│       └── hpa.yaml
└── tests/
    └── test-connection.yaml  # Helm test to verify connectivity
```

**_helpers.tpl** (Common Template Functions):
```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "evolved-todo.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "evolved-todo.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "evolved-todo.labels" -}}
helm.sh/chart: {{ include "evolved-todo.chart" . }}
{{ include "evolved-todo.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "evolved-todo.selectorLabels" -}}
app.kubernetes.io/name: {{ include "evolved-todo.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

**values.yaml** (Production Defaults):
```yaml
# Production defaults
replicaCount:
  frontend: 3
  backend: 3

image:
  frontend:
    repository: evolved-todo-frontend
    tag: "1.0.0"
    pullPolicy: IfNotPresent
  backend:
    repository: evolved-todo-backend
    tag: "1.0.0"
    pullPolicy: IfNotPresent

resources:
  frontend:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 200m
      memory: 256Mi
  backend:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi

autoscaling:
  frontend:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 80
  backend:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70

service:
  frontend:
    type: LoadBalancer
    port: 3000
  backend:
    type: ClusterIP
    port: 8000

secrets:
  databaseUrl: ""  # Must be provided via --set or values override
  openaiApiKey: ""
  betterAuthSecret: ""
```

**values-dev.yaml** (Development Overrides):
```yaml
# Development overrides for Minikube
replicaCount:
  frontend: 1      # Single replica for dev
  backend: 1

service:
  frontend:
    type: NodePort  # NodePort instead of LoadBalancer for Minikube
    port: 3000
    nodePort: 30080

autoscaling:
  frontend:
    enabled: false  # Disable HPA in dev
  backend:
    enabled: false

image:
  frontend:
    tag: "latest"   # Use latest tag in dev
  backend:
    tag: "latest"
```

**Deployment Commands**:
```bash
# Development deployment
helm install evolved-todo ./helm/evolved-todo -f ./helm/evolved-todo/values-dev.yaml \
  --set secrets.databaseUrl="${DATABASE_URL}" \
  --set secrets.openaiApiKey="${OPENAI_API_KEY}" \
  --set secrets.betterAuthSecret="${BETTER_AUTH_SECRET}"

# Production deployment (Phase 5)
helm install evolved-todo ./helm/evolved-todo -f ./helm/evolved-todo/values.yaml \
  --set secrets.databaseUrl="${DATABASE_URL}" \
  --set secrets.openaiApiKey="${OPENAI_API_KEY}" \
  --set secrets.betterAuthSecret="${BETTER_AUTH_SECRET}"

# Upgrade deployment
helm upgrade evolved-todo ./helm/evolved-todo -f ./helm/evolved-todo/values-dev.yaml

# Rollback to previous version
helm rollback evolved-todo

# Test deployment
helm test evolved-todo
```

---

### 6. AIOps Tool Integration

**Decision**: Use Docker AI (Gordon), kubectl-ai, and Kagent for intelligent operations

**Rationale**:
- **Productivity**: Natural language commands reduce learning curve
- **Optimization**: AI suggestions for Dockerfile and resource tuning
- **Troubleshooting**: Automated diagnostics and root cause analysis
- **Best Practice**: Leverage AI for infrastructure operations (emerging trend)

**Docker AI (Gordon) Usage**:
```bash
# Optimize Dockerfile
docker ai "optimize backend/Dockerfile for size and security"

# Security analysis
docker ai "analyze security vulnerabilities in evolved-todo-backend:latest"

# Troubleshoot container issues
docker ai "why does this container keep restarting"

# Best practices
docker ai "review this Dockerfile for production readiness"
```

**kubectl-ai Usage**:
```bash
# Natural language deployments
kubectl-ai "deploy the todo backend with 3 replicas"

# Scaling
kubectl-ai "scale the frontend to handle more load"

# Troubleshooting
kubectl-ai "check why the backend pods are failing"
kubectl-ai "show me error logs from the last hour"

# Diagnostics
kubectl-ai "why is the pod in CrashLoopBackOff"
kubectl-ai "which pods are using the most memory"
```

**Kagent Usage**:
```bash
# Cluster health analysis
kagent "analyze the cluster health and identify issues"

# Resource optimization
kagent "optimize resource allocation for better efficiency"

# Capacity planning
kagent "recommend resource limits based on actual usage"

# Cost optimization
kagent "identify opportunities to reduce resource costs"
```

**Best Practices**:
- Use AIOps tools for exploration and learning, codify decisions in manifests
- Don't rely solely on AI tools - understand underlying kubectl/docker commands
- Document AI-suggested optimizations in ADRs for team review
- Validate AI suggestions before applying to production

---

## Technology Stack Decisions Summary

| Technology | Choice | Rationale | Phase |
|------------|--------|-----------|-------|
| **Container Runtime** | Docker Desktop 4.53+ | Docker AI support, industry standard | 4 |
| **Frontend Base Image** | node:22-alpine | Minimal size, official image | 4 |
| **Backend Base Image** | python:3.13-slim | Smaller than full Python, official | 4 |
| **Build Pattern** | Multi-stage Dockerfiles | Size optimization, security | 4 |
| **Health Checks** | Dedicated /health endpoints | K8s self-healing, observability | 4 |
| **Orchestration** | Kubernetes (Minikube) | Industry standard, horizontal scaling | 4 |
| **Package Manager** | Helm 3.x | Templating, versioning, rollback | 4 |
| **Resource Management** | Requests + Limits | Predictable scheduling, QoS | 4 |
| **Autoscaling** | HPA with CPU metrics | Elasticity, cost efficiency | 4 |
| **AIOps Tools** | Gordon, kubectl-ai, Kagent | Productivity, optimization | 4 |
| **Database** | Neon PostgreSQL (external) | Managed, no cluster complexity | 3 (unchanged) |
| **Backend Framework** | FastAPI + OpenAI Agents SDK | Unchanged from Phase 3 | 3 (unchanged) |
| **Frontend Framework** | Next.js 16+ + ChatKit | Unchanged from Phase 3 | 3 (unchanged) |

---

## Implementation Patterns

### Pattern 1: Stateless Architecture for Horizontal Scaling

**Problem**: How to ensure conversation state persists when pods are added/removed/restarted?

**Solution**: Database-persisted conversation state (Phase 3 architecture)

**Validation**:
1. Deploy backend with 3 replicas
2. Start conversation, get conversation_id
3. Send follow-up message to same conversation_id (may hit different pod)
4. Delete one backend pod
5. Verify conversation history intact and conversation continues

**Key Implementation Points**:
- Every request fetches conversation history from database
- No in-memory state in pods
- Any pod can serve any request
- LoadBalancer distributes requests across pods
- Pod deletion/recreation has zero impact on conversations

---

### Pattern 2: Zero-Downtime Deployments

**Problem**: How to update containers without dropping user requests?

**Solution**: Rolling updates with readiness probes

**Configuration**:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 1  # At most 1 pod down at a time
    maxSurge: 1        # At most 1 extra pod during update

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 20
  periodSeconds: 10
```

**Update Flow**:
1. New pod starts with new image
2. Kubernetes waits for readiness probe to pass (20s initial delay)
3. Once ready, new pod added to Service
4. Old pod removed from Service
5. Old pod terminated
6. Repeat for next pod

**Result**: At least minReplicas pods always available during update

---

### Pattern 3: Container Security Hardening

**Problem**: How to minimize container attack surface?

**Solution**: Non-root user, read-only filesystem, minimal base image, no secrets in image

**Implementation**:
```dockerfile
# Use minimal base image
FROM python:3.13-slim

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy application files
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY app/ ./app/

# Switch to non-root user
USER appuser

# Expose port (informational)
EXPOSE 8000
```

**Kubernetes Security Context**:
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true  # Where possible
  allowPrivilegeEscalation: false
  capabilities:
    drop:
    - ALL
```

**Security Validation**:
```bash
# Scan image for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image evolved-todo-backend:latest

# Verify non-root user
docker run --rm evolved-todo-backend:latest id
# Expected: uid=1000(appuser) gid=1000(appuser)
```

---

## Next Steps (Phase 1: Design & Contracts)

1. **data-model.md**: Document Phase 4 entities (minimal - Phase 3 models unchanged, only add container/deployment metadata if needed)
2. **contracts/docker/**: Dockerfile specifications for frontend and backend
3. **contracts/kubernetes/**: K8s manifest specifications (Deployment, Service, HPA)
4. **contracts/helm/**: Helm chart template specifications
5. **quickstart.md**: Step-by-step deployment guide for Minikube

---

## References

- Docker Multi-Stage Builds: https://docs.docker.com/build/building/multi-stage/
- Kubernetes Best Practices: https://kubernetes.io/docs/concepts/configuration/overview/
- Helm Chart Best Practices: https://helm.sh/docs/chart_best_practices/
- Horizontal Pod Autoscaling: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/
- Container Security: https://kubernetes.io/docs/concepts/security/pod-security-standards/
