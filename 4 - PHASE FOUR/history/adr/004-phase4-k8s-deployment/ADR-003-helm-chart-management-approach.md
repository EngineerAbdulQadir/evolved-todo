# ADR-003: Helm Chart Management Approach with Environment-Specific Values

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-25
- **Feature:** 004-phase4-k8s-deployment
- **Context:** Phase 4 requires templated Kubernetes manifests for development (Minikube) and future production deployments (Phase 5 cloud). Must support environment-specific configuration (replicas, service types, resource limits), versioning for rollback, and consistent deployment workflows. Helm is industry standard but adds complexity vs raw manifests.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: ✅ Long-term consequence - affects deployment process, environment management, Phase 5 cloud deployment
     2) Alternatives: ✅ Multiple viable options (raw manifests, Kustomize, custom scripts)
     3) Scope: ✅ Cross-cutting - affects deployment, configuration management, versioning, rollback
-->

## Decision

**Helm Chart Management Strategy**:
- **Chart Structure**: Standard Helm chart layout with templates/ directory and _helpers.tpl
- **Values Files**: values.yaml (production defaults), values-dev.yaml (development overrides)
- **Templating**: Parameterize replicas, image tags, resources, service types, secrets
- **Versioning**: Chart.yaml tracks chart version (semver) and appVersion (application version)
- **Environment-Specific Deployment**: Use `-f values-dev.yaml` for Minikube, default values.yaml for production

**Chart Structure**:
```
helm/evolved-todo/
├── Chart.yaml              # Metadata (name: evolved-todo, version: 1.0.0, appVersion: 1.0.0)
├── values.yaml             # Production defaults (LoadBalancer, 3 replicas, HPA enabled)
├── values-dev.yaml         # Development overrides (NodePort, 1 replica, HPA disabled)
├── templates/
│   ├── _helpers.tpl        # Common labels, selectors, names
│   ├── namespace.yaml      # Optional namespace
│   ├── secrets.yaml        # Templated secrets (DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET)
│   ├── configmaps.yaml     # Application configuration
│   ├── frontend/
│   │   ├── deployment.yaml # Frontend Deployment (templated resources, replicas, image)
│   │   ├── service.yaml    # Frontend Service (templated type: LoadBalancer vs NodePort)
│   │   └── hpa.yaml        # Frontend HPA (conditional: {{ if .Values.autoscaling.frontend.enabled }})
│   └── backend/
│       ├── deployment.yaml # Backend Deployment
│       ├── service.yaml    # Backend Service (ClusterIP - internal only)
│       └── hpa.yaml        # Backend HPA (conditional)
└── tests/
    └── test-connection.yaml  # Helm test to verify frontend→backend connectivity
```

**values.yaml** (Production Defaults):
```yaml
# Production defaults for Phase 5 cloud deployment
replicaCount:
  frontend: 3
  backend: 3

image:
  frontend:
    repository: evolved-todo-frontend
    tag: "1.0.0"              # Pin specific version
    pullPolicy: IfNotPresent
  backend:
    repository: evolved-todo-backend
    tag: "1.0.0"
    pullPolicy: IfNotPresent

resources:
  frontend:
    requests: { cpu: 100m, memory: 128Mi }
    limits: { cpu: 200m, memory: 256Mi }
  backend:
    requests: { cpu: 200m, memory: 256Mi }
    limits: { cpu: 500m, memory: 512Mi }

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
    type: LoadBalancer        # External access
    port: 3000
  backend:
    type: ClusterIP           # Internal only
    port: 8000

secrets:
  databaseUrl: ""             # Must be provided via --set or values override
  openaiApiKey: ""
  betterAuthSecret: ""
```

**values-dev.yaml** (Development Overrides for Minikube):
```yaml
# Development overrides for local Minikube deployment
replicaCount:
  frontend: 1                 # Single replica for dev
  backend: 1

service:
  frontend:
    type: NodePort            # NodePort instead of LoadBalancer for Minikube
    port: 3000
    nodePort: 30080           # Fixed port for consistency

autoscaling:
  frontend:
    enabled: false            # Disable HPA in dev
  backend:
    enabled: false

image:
  frontend:
    tag: "latest"             # Use latest tag in dev (rebuilt frequently)
  backend:
    tag: "latest"
```

**_helpers.tpl** (Common Template Functions):
```yaml
{{- define "evolved-todo.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "evolved-todo.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "evolved-todo.name" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "evolved-todo.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/name: {{ include "evolved-todo.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "evolved-todo.selectorLabels" -}}
app.kubernetes.io/name: {{ include "evolved-todo.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

**Deployment Commands**:
```bash
# Development deployment (Minikube)
helm install evolved-todo ./helm/evolved-todo \
  -f ./helm/evolved-todo/values-dev.yaml \
  --set secrets.databaseUrl="${DATABASE_URL}" \
  --set secrets.openaiApiKey="${OPENAI_API_KEY}" \
  --set secrets.betterAuthSecret="${BETTER_AUTH_SECRET}"

# Validate before install
helm lint ./helm/evolved-todo
helm install --dry-run --debug evolved-todo ./helm/evolved-todo -f values-dev.yaml

# Upgrade deployment
helm upgrade evolved-todo ./helm/evolved-todo -f values-dev.yaml --wait

# Rollback to previous version
helm rollback evolved-todo

# Test deployment
helm test evolved-todo
```

## Consequences

### Positive

- **Templating**: Single chart definition, multiple environments (dev, staging, prod)
- **Version Control**: Chart.yaml version tracks deployment changes, easy rollback
- **Consistency**: Standard labels, selectors, naming via _helpers.tpl (no duplication)
- **Environment-Specific Config**: values-dev.yaml overrides production defaults without modifying templates
- **Upgrade/Rollback**: `helm upgrade` for rolling updates, `helm rollback` for quick revert
- **Validation**: `helm lint` catches template errors, `--dry-run` previews changes before apply
- **Industry Standard**: Helm is Kubernetes package manager (widely adopted, strong ecosystem)
- **Phase 5 Ready**: Same chart structure will work for cloud deployment (only change values files)

### Negative

- **Learning Curve**: Helm templating syntax (Go templates) more complex than raw YAML
- **Abstraction Layer**: Templates hide underlying Kubernetes manifests (debugging requires `helm template`)
- **Tooling Dependency**: Requires Helm 3.x installed (additional prerequisite)
- **Chart Maintenance**: Values files and templates must stay synchronized (risk of drift)
- **Secret Management**: Secrets still passed via --set (not ideal, Sealed Secrets deferred to Phase 5)

## Alternatives Considered

**Alternative 1: Raw Kubernetes Manifests**
- **Description**: Use kubectl apply -f k8s/ with separate manifest files per environment
- **Why Rejected**:
  - Duplication across environments (k8s/dev/, k8s/prod/ with 80% identical manifests)
  - No built-in versioning or rollback (must use git tags)
  - Manual parameter substitution (envsubst or sed scripts)
  - No validation before apply (syntax errors discovered at runtime)
- **Tradeoff**: Simpler (no templating) but poor maintainability and no rollback

**Alternative 2: Kustomize**
- **Description**: Use Kustomize for patching-based configuration (base/ + overlays/dev/, overlays/prod/)
- **Why Rejected**:
  - Patching model less intuitive than value substitution (harder to reason about final manifest)
  - No versioning or rollback built-in (still need external tooling)
  - Limited templating capabilities vs Helm (no loops, conditionals)
  - Less ecosystem support than Helm (fewer public charts)
- **Tradeoff**: Native kubectl integration but less powerful than Helm

**Alternative 3: Custom Deployment Scripts**
- **Description**: Write bash/PowerShell scripts to generate manifests from templates (envsubst, sed)
- **Why Rejected**:
  - Reinventing the wheel (Helm already solves this)
  - Poor error handling (scripts fail silently)
  - No community support or best practices
  - Maintenance burden (custom tooling)
- **Tradeoff**: Full control but high complexity and maintenance cost

**Alternative 4: Helm + External Secrets Operator**
- **Description**: Use Helm with External Secrets Operator to sync secrets from external vault
- **Why Deferred to Phase 5**:
  - Better secret management (no --set for sensitive data)
  - Requires external secret store (AWS Secrets Manager, HashiCorp Vault)
  - Additional infrastructure complexity for Phase 4 Minikube
- **Tradeoff**: Production-ready secret management but overkill for local development

**Alternative 5: Helmfile (Declarative Helm Releases)**
- **Description**: Use Helmfile to manage multiple Helm releases declaratively
- **Why Deferred to Phase 5**:
  - Excellent for multi-chart deployments (microservices)
  - Phase 4 has single chart (evolved-todo) - no multi-release complexity
  - Additional tooling dependency
- **Tradeoff**: Better for complex deployments but unnecessary for single chart

## References

- Feature Spec: `specs/004-phase4-k8s-deployment/spec.md` (FR-029 to FR-036: Helm requirements, SC-018 to SC-023: Helm success criteria)
- Implementation Plan: `specs/004-phase4-k8s-deployment/plan.md`
- Research: `specs/004-phase4-k8s-deployment/research.md` (Section 5: Helm chart structure)
- Quickstart: `specs/004-phase4-k8s-deployment/quickstart.md` (Helm deployment commands)
- Related ADRs:
  - ADR-001: Containerization Strategy
  - ADR-002: Kubernetes Resource & Scaling Strategy
  - ADR-004: AIOps Tool Integration
- Evaluator Evidence: Will be created in PHR after implementation
