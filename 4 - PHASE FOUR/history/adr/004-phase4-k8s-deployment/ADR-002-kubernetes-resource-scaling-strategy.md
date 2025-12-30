# ADR-002: Kubernetes Resource Management and Horizontal Pod Autoscaling Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-25
- **Feature:** 004-phase4-k8s-deployment
- **Context:** Kubernetes deployment requires explicit resource requests/limits for predictable scheduling and cost control. Phase 3's stateless architecture enables horizontal scaling. Must balance availability (minimum 2 replicas), cost (maximize pod density), and performance (<2s response time under load).

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: ✅ Long-term consequence - affects cluster sizing, cost, reliability for all future phases
     2) Alternatives: ✅ Multiple viable options (fixed replicas, manual scaling, memory-based HPA, custom metrics)
     3) Scope: ✅ Cross-cutting - affects deployment, monitoring, cost, performance, reliability
-->

## Decision

**Resource Management Strategy**:
- **Requests + Limits**: Define both for all pods (Burstable QoS class)
- **Frontend Resources**: 100m/128Mi requests → 200m/256Mi limits (2x buffer for bursts)
- **Backend Resources**: 200m/256Mi requests → 500m/512Mi limits (2x buffer for bursts)
- **Quality of Service**: Burstable QoS (requests < limits) for flexibility

**Horizontal Pod Autoscaling (HPA) Strategy**:
- **Backend HPA**: 2-10 pods, CPU-based scaling at 70% utilization
- **Frontend HPA**: 2-5 pods, CPU-based scaling at 80% utilization
- **Metrics Source**: Kubernetes metrics-server (Minikube addon)
- **Scaling Behavior**: Conservative scale-up (60s stabilization, +2 pods), slow scale-down (300s stabilization, -1 pod)

**Frontend Deployment Resources**:
```yaml
resources:
  requests:
    cpu: 100m        # 0.1 CPU core minimum (Next.js SSR, I/O bound)
    memory: 128Mi    # 128 MiB minimum
  limits:
    cpu: 200m        # 0.2 CPU core maximum
    memory: 256Mi    # 256 MiB maximum
```

**Backend Deployment Resources**:
```yaml
resources:
  requests:
    cpu: 200m        # 0.2 CPU core minimum (Python runtime, SQLModel ORM, OpenAI API calls)
    memory: 256Mi    # 256 MiB minimum
  limits:
    cpu: 500m        # 0.5 CPU core maximum
    memory: 512Mi    # 512 MiB maximum
```

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
      stabilizationWindowSeconds: 60    # Wait 60s before scaling up (avoid flapping)
      policies:
      - type: Pods
        value: 2                         # Add 2 pods at a time
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300   # Wait 5min before scaling down (traffic spikes)
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
        averageUtilization: 80  # Higher threshold for frontend (I/O bound)
```

**Rationale for Resource Values**:
- **Frontend**: Lightweight Next.js SSR, primarily I/O bound (waiting on backend API calls)
- **Backend**: Heavier workload (Python runtime, SQLModel ORM, OpenAI API calls, MCP tools)
- **2x Buffer**: Limits are 2x requests to allow bursts without triggering OOMKilled
- **Tested Values**: Based on Phase 3 local testing (100 concurrent requests, <2s response time)

## Consequences

### Positive

- **Predictable Scheduling**: Requests guarantee minimum resources, scheduler makes informed placement decisions
- **Cost Optimization**: Right-sizing prevents over-provisioning, HPA scales down during low usage
- **Prevent Starvation**: Limits prevent runaway processes from consuming all cluster resources
- **High Availability**: Minimum 2 replicas ensures no single point of failure
- **Elasticity**: HPA automatically scales pods based on load (2→10 backend, 2→5 frontend within 2 minutes)
- **Stateless Architecture Enabler**: Phase 3's database-persisted state enables seamless horizontal scaling
- **Quality of Service**: Burstable QoS allows bursts above requests without eviction (unless node pressure)

### Negative

- **Resource Overhead**: Minimum 2 replicas consume resources even during zero load
- **HPA Lag**: 60s stabilization window delays scale-up response (acceptable for Phase 4, optimize in Phase 5)
- **Metrics Server Dependency**: HPA requires metrics-server addon (must enable in Minikube)
- **CPU-Only Metrics**: CPU-based scaling may not reflect request-based load accurately (custom metrics deferred to Phase 5)
- **Configuration Complexity**: HPA behavior tuning (stabilization, policies) requires expertise
- **Minikube Constraints**: 10 max backend replicas limited by local resources (4 CPU, 8GB RAM)

## Alternatives Considered

**Alternative 1: Fixed Replicas (No HPA)**
- **Description**: Deploy with fixed replica count (e.g., 3 frontend, 3 backend)
- **Why Rejected**:
  - Cannot handle load spikes (503 errors during high traffic)
  - Wastes resources during low usage periods
  - Manual scaling requires human intervention
- **Tradeoff**: Simpler configuration but poor elasticity

**Alternative 2: Manual Scaling**
- **Description**: Manually run `kubectl scale deployment backend --replicas=10` during high load
- **Why Rejected**:
  - Requires human monitoring and intervention
  - Slow response time (minutes to hours)
  - Not suitable for unpredictable traffic patterns
- **Tradeoff**: Full control but poor automation

**Alternative 3: Memory-Based HPA**
- **Description**: Scale based on memory utilization instead of CPU
- **Why Rejected**:
  - Memory usage less predictive for request-based workloads
  - Backend memory usage stable (Python process size doesn't correlate with load)
  - CPU better proxy for concurrent request processing
- **Tradeoff**: Simpler metric but less accurate for our workload

**Alternative 4: Custom Metrics HPA (Request Rate via Prometheus)**
- **Description**: Scale based on HTTP request rate (e.g., scale up if >100 req/s per pod)
- **Why Deferred to Phase 5**:
  - More accurate scaling trigger for request-based workloads
  - Requires Prometheus operator + custom metrics adapter (complexity)
  - CPU-based HPA sufficient for Phase 4 Minikube deployment
- **Tradeoff**: Better accuracy but significant infrastructure complexity

**Alternative 5: No Resource Limits (Only Requests)**
- **Description**: Define requests but omit limits to allow unlimited burst
- **Why Rejected**:
  - Pods can consume unlimited CPU/memory (risk of node resource starvation)
  - Multi-tenant cluster safety requires limits
  - No protection against memory leaks or runaway processes
- **Tradeoff**: Simpler config but unsafe for production

**Alternative 6: Guaranteed QoS (Requests = Limits)**
- **Description**: Set requests equal to limits (e.g., 500m/512Mi for both)
- **Why Rejected**:
  - Wastes resources (pods can't burst above requests)
  - Requires accurate capacity planning upfront (over-provision to avoid OOMKilled)
  - Less flexible than Burstable QoS
- **Tradeoff**: Maximum predictability but poor resource utilization

## References

- Feature Spec: `specs/004-phase4-k8s-deployment/spec.md` (FR-011 to FR-028: Kubernetes deployment requirements, SC-008 to SC-017: Success criteria)
- Implementation Plan: `specs/004-phase4-k8s-deployment/plan.md`
- Research: `specs/004-phase4-k8s-deployment/research.md` (Sections 3-4: Resource management, HPA)
- Related ADRs:
  - ADR-001: Containerization Strategy
  - ADR-003: Helm Chart Management Approach
- Evaluator Evidence: Will be created in PHR after implementation
