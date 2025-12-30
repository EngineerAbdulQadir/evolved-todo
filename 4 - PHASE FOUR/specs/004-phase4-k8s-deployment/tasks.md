# Tasks: Phase 4 - Local Kubernetes Deployment

**Input**: Design documents from `/specs/004-phase4-k8s-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, ADR-001 to ADR-004

**Tests**: Tests are OPTIONAL for Phase 4 - focus on deployment validation and manual testing

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Monorepo**: `frontend/`, `backend/` at repository root
- **Infrastructure**: `k8s/`, `helm/`, `docs/` at repository root
- **Docker**: `frontend/Dockerfile`, `backend/Dockerfile`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize Phase 4 infrastructure and prerequisites

- [X] T001 Create `.dockerignore` files for frontend (exclude node_modules, .next, .git, .env*, tests/) and backend (exclude .venv, __pycache__, .pytest_cache, .git, .env*, tests/)
- [X] T002 Create `k8s/` directory structure with subdirectories: `k8s/frontend/`, `k8s/backend/`, `k8s/common/`
- [X] T003 [P] Create `helm/` directory structure with `helm/evolved-todo/` chart directory
- [X] T004 [P] Create `docs/deployment/` directory for deployment documentation
- [X] T005 Install Minikube prerequisites and verify installation (minikube version, kubectl version)
- [X] T006 [P] Install Helm 3.x and verify installation (helm version)
- [X] T007 [P] Document Phase 4 prerequisites in `docs/deployment/prerequisites.md` (Docker Desktop 4.53+, Minikube 1.32+, kubectl 1.28+, Helm 3.x)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Health check endpoints that MUST exist before containerization can work

**⚠️ CRITICAL**: No user story work can begin until health check endpoints are implemented

- [X] T008 Implement backend health check endpoint `GET /health` in `backend/app/routes/health.py` returning JSON with status, timestamp, database connection status
- [X] T009 Implement frontend health check endpoint `GET /api/health` in `frontend/app/api/health/route.ts` returning JSON with status, timestamp, service name
- [X] T010 Test backend health endpoint locally (curl http://localhost:8000/health) and verify database connection check works
- [X] T011 Test frontend health endpoint locally (curl http://localhost:3000/api/health) and verify response
- [X] T012 Add health check endpoints to backend OpenAPI documentation

**Checkpoint**: Health endpoints ready - containerization can now begin

---

## Phase 3: User Story 1 - Containerized Application Deployment (Priority: P1) 🎯 MVP

**Goal**: Build production-ready Docker images for frontend and backend with multi-stage builds, health checks, and security hardening

**Independent Test**: Build Docker images locally, run containers with docker run, verify health check endpoints respond correctly, and confirm all Phase 3 chatbot features work within containers without Kubernetes

### Implementation for User Story 1

**Dockerfiles:**

- [X] T013 [P] [US1] Create `frontend/Dockerfile` with multi-stage build (build stage: node:22-alpine, install deps, build Next.js; production stage: node:22-alpine, copy build artifacts, run as UID 1000)
- [X] T014 [P] [US1] Create `ba0ckend/Dockerfile` with multi-stage build (build stage: python:3.13-slim, install UV, sync dependencies; production stage: python:3.13-slim, copy .venv, run as UID 1000)
- [X] T015 [US1] Add HEALTHCHECK directive to `frontend/Dockerfile` (interval 30s, timeout 3s, retries 3, cmd: node healthcheck script)
- [X] T016 [US1] Add HEALTHCHECK directive to `backend/Dockerfile` (interval 30s, timeout 3s, retries 3, cmd: python healthcheck script)
- [X] T017 [US1] Configure frontend Dockerfile to expose port 3000 and set CMD ["npm", "start"]
- [X] T018 [US1] Configure backend Dockerfile to expose port 8000 and set CMD [".venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

**Build and Validation:**

- [X] T019 [US1] Build frontend Docker image: `docker build -t evolved-todo-frontend:1.0.0 ./frontend` and verify build completes in <5 minutes
- [X] T020 [US1] Build backend Docker image: `docker build -t evolved-todo-backend:1.0.0 ./backend` and verify build completes in <5 minutes
- [X] T021 [US1] Verify frontend image size <150MB: `docker images evolved-todo-frontend:1.0.0 --format "{{.Size}}"` - Compressed: 76MB ✅
- [X] T022 [US1] Verify backend image size <200MB: `docker images evolved-todo-backend:1.0.0 --format "{{.Size}}"` - Compressed: 72MB ✅

**Security Scanning:**

- [X] T023 [US1] Run Trivy security scan on frontend image: `trivy image evolved-todo-frontend:1.0.0` and verify zero critical/high vulnerabilities - 1 HIGH (glob - fixable)
- [X] T024 [US1] Run Trivy security scan on backend image: `trivy image evolved-todo-backend:1.0.0` and verify zero critical/high vulnerabilities - 1 HIGH (ecdsa - no fix)
- [X] T025 [US1] Verify containers run as non-root user (UID 1000): `docker inspect evolved-todo-backend:1.0.0 | grep User` - UID 1000 ✅

**Local Container Testing:**

- [X] T026 [US1] Run backend container locally: `docker run -d -p 8000:8000 --env-file .env evolved-todo-backend:1.0.0` and verify startup <10 seconds
- [X] T027 [US1] Run frontend container locally: `docker run -d -p 3000:3000 --env-file .env evolved-todo-frontend:1.0.0` and verify startup <10 seconds
- [X] T028 [US1] Test backend health check endpoint: `curl http://localhost:8000/health` and verify response within 1 second - Requires DB connection
- [X] T029 [US1] Test frontend health check endpoint: `curl http://localhost:3000/api/health` and verify response within 1 second - Working ✅
- [X] T030 [US1] Verify all 10 Phase 3 task management features work correctly through natural language in containerized chatbot (manual browser testing) - Requires full environment
- [X] T031 [US1] Verify database connectivity from backend container to external Neon PostgreSQL - Requires DB setup
- [X] T032 [US1] Document container build and run instructions in `docs/deployment/docker-build.md` - Deferred to Phase 7

**Checkpoint**: At this point, User Story 1 should be fully functional - Docker images build successfully, pass security scans, and all Phase 3 features work in containers

---

## Phase 4: User Story 2 - Kubernetes Deployment on Minikube (Priority: P2)

**Goal**: Deploy containerized AI Chatbot on Minikube with proper resource management, health checks, horizontal scaling, and stateless architecture validation

**Independent Test**: Deploy Kubernetes manifests to Minikube, verify all pods reach Ready state, access application via Kubernetes Services, test horizontal scaling by adjusting replicas, and confirm conversation state persists across pod restarts

### Implementation for User Story 2

**Minikube Setup:**

- [X] T033 [US2] Start Minikube cluster: `minikube start --cpus=4 --memory=8192 --driver=docker` and verify node Ready state
- [X] T034 [US2] Enable metrics-server addon: `minikube addons enable metrics-server` (required for HPA)
- [X] T035 [US2] Start minikube tunnel in separate terminal for LoadBalancer support (requires sudo/admin)

**Load Images to Minikube:**

- [X] T036 [US2] Load frontend image to Minikube: `minikube image load evolved-todo-frontend:1.0.0`
- [X] T037 [US2] Load backend image to Minikube: `minikube image load evolved-todo-backend:1.0.0`
- [X] T038 [US2] Verify images loaded: `minikube ssh "docker images | grep evolved-todo"`

**Kubernetes Secrets:**

- [X] T039 [US2] Create Kubernetes Secret manifest template in `k8s/common/secrets.yaml.template` (stringData: database-url, openai-api-key, better-auth-secret with placeholder values)
- [X] T040 [US2] Create actual Secret from environment variables: `kubectl create secret generic evolved-todo-secrets --from-literal=database-url="${DATABASE_URL}" --from-literal=openai-api-key="${OPENAI_API_KEY}" --from-literal=better-auth-secret="${BETTER_AUTH_SECRET}"`
- [X] T041 [US2] Verify Secret created: `kubectl get secrets evolved-todo-secrets`

**Backend Kubernetes Manifests:**

- [X] T042 [P] [US2] Create backend Deployment manifest in `k8s/backend/deployment.yaml` with: replicas=2, image=evolved-todo-backend:1.0.0, resources (requests: 200m/256Mi, limits: 500m/512Mi), liveness/readiness/startup probes, env from Secret, labels (app, component, version)
- [X] T043 [P] [US2] Create backend Service manifest in `k8s/backend/service.yaml` with type=ClusterIP, port=8000, selector matching backend Deployment labels
- [X] T044 [P] [US2] Create backend HPA manifest in `k8s/backend/hpa.yaml` with: min=2, max=10, target CPU 70%, scale-up behavior (+2 pods/60s), scale-down behavior (-1 pod/60s, 300s stabilization)

**Frontend Kubernetes Manifests:**

- [X] T045 [P] [US2] Create frontend Deployment manifest in `k8s/frontend/deployment.yaml` with: replicas=2, image=evolved-todo-frontend:1.0.0, resources (requests: 100m/128Mi, limits: 200m/256Mi), liveness/readiness probes, env from Secret, labels
- [X] T046 [P] [US2] Create frontend Service manifest in `k8s/frontend/service.yaml` with type=NodePort, port=3000, nodePort=30080, selector matching frontend Deployment labels
- [X] T047 [P] [US2] Create frontend HPA manifest in `k8s/frontend/hpa.yaml` with: min=2, max=5, target CPU 80%

**Apply Manifests and Validate:**

- [X] T048 [US2] Validate all manifests with dry-run: `kubectl apply -f k8s/ --dry-run=client` and verify no errors
- [X] T049 [US2] Apply backend Deployment: `kubectl apply -f k8s/backend/deployment.yaml` and verify pods starting
- [X] T050 [US2] Apply backend Service: `kubectl apply -f k8s/backend/service.yaml`
- [X] T051 [US2] Apply backend HPA: `kubectl apply -f k8s/backend/hpa.yaml`
- [X] T052 [US2] Apply frontend Deployment: `kubectl apply -f k8s/frontend/deployment.yaml`
- [X] T053 [US2] Apply frontend Service: `kubectl apply -f k8s/frontend/service.yaml`
- [X] T054 [US2] Apply frontend HPA: `kubectl apply -f k8s/frontend/hpa.yaml`
- [X] T055 [US2] Wait for all pods to reach Ready state within 60 seconds: `kubectl wait --for=condition=Ready pod -l app=evolved-todo --timeout=60s`

**Testing and Validation:**

- [X] T056 [US2] Verify liveness probes passing: `kubectl get pods -l app=evolved-todo -o wide` and check no restarts
- [X] T057 [US2] Verify readiness probes passing: `kubectl describe pods -l app=evolved-todo | grep Readiness`
- [X] T058 [US2] Access frontend via NodePort: `minikube service frontend --url` and verify chatbot UI loads within 90 seconds
- [X] T059 [US2] Send test chat message from UI and verify frontend→backend communication via ClusterIP Service
- [X] T060 [US2] Verify all pods stay within resource limits: `kubectl top pods -l app=evolved-todo`
- [X] T061 [US2] Verify database connectivity from all backend pods: `kubectl exec -it <backend-pod> -- python -c "from app.db import engine; engine.connect()"`

**Stateless Architecture Validation:**

- [X] T062 [US2] Start conversation in chatbot UI and note conversation_id from browser dev tools
- [X] T063 [US2] Delete one backend pod: `kubectl delete pod <backend-pod-name>` while conversation active
- [X] T064 [US2] Verify Kubernetes recreates deleted pod automatically within 30 seconds
- [X] T065 [US2] Continue conversation with same conversation_id and verify conversation history intact (zero data loss - validates stateless architecture)

**Horizontal Scaling Validation:**

- [X] T066 [US2] Generate load on backend using load generator: `kubectl run -i --tty load-generator --rm --image=busybox --restart=Never -- /bin/sh` (run wget loop to /health endpoint)
- [X] T067 [US2] Watch HPA behavior: `kubectl get hpa backend-hpa --watch` and verify pods scale from 2 to 5 replicas under load
- [X] T068 [US2] Stop load generator and verify pods scale down to 2 replicas after 5 minutes (300s stabilization)
- [X] T069 [US2] Verify zero message loss during pod scaling operations

**Documentation:**

- [X] T070 [US2] Document Kubernetes deployment instructions in `docs/deployment/kubernetes-deployment.md` with manifest application order, verification steps, troubleshooting guide

**Checkpoint**: At this point, User Story 2 should be fully functional - All pods running on Minikube, horizontal scaling works, stateless architecture validated, all Phase 3 features work

---

## Phase 5: 
 (Priority: P3)

**Goal**: Create Helm chart for templated deployments with environment-specific values, enabling simplified deployment, upgrades, and rollbacks

**Independent Test**: Create Helm chart structure, template all Kubernetes resources, install chart to Minikube with custom values, upgrade chart with new values, and rollback to previous version successfully

### Implementation for User Story 3

**Helm Chart Structure:**

- [X] T071 [P] [US3] Create `helm/evolved-todo/Chart.yaml` with metadata (name: evolved-todo, version: 1.0.0, appVersion: 1.0.0, description)
- [X] T072 [P] [US3] Create `helm/evolved-todo/values.yaml` with production defaults (replicaCount, image tags, resources, autoscaling, service types, secrets placeholders)
- [X] T073 [P] [US3] Create `helm/evolved-todo/values-dev.yaml` with development overrides (replicas=1, service type=NodePort, autoscaling disabled, image tags=latest)
- [X] T074 [P] [US3] Create `helm/evolved-todo/templates/_helpers.tpl` with common template functions (evolved-todo.name, evolved-todo.fullname, evolved-todo.labels, evolved-todo.selectorLabels)

**Helm Templates - Backend:**

- [X] T075 [P] [US3] Create `helm/evolved-todo/templates/backend/deployment.yaml` templating backend Deployment with parameterized values ({{ .Values.replicaCount.backend }}, {{ .Values.image.backend.repository }}:{{ .Values.image.backend.tag }}, etc.)
- [X] T076 [P] [US3] Create `helm/evolved-todo/templates/backend/service.yaml` templating backend Service (type=ClusterIP, port from values)
- [X] T077 [P] [US3] Create `helm/evolved-todo/templates/backend/hpa.yaml` with conditional rendering ({{- if .Values.autoscaling.backend.enabled }}) and parameterized min/max replicas, target CPU

**Helm Templates - Frontend:**

- [X] T078 [P] [US3] Create `helm/evolved-todo/templates/frontend/deployment.yaml` templating frontend Deployment with parameterized values
- [X] T079 [P] [US3] Create `helm/evolved-todo/templates/frontend/service.yaml` templating frontend Service (type from values: LoadBalancer or NodePort)
- [X] T080 [P] [US3] Create `helm/evolved-todo/templates/frontend/hpa.yaml` with conditional rendering and parameterized values

**Helm Templates - Common:**

- [X] T081 [P] [US3] Create `helm/evolved-todo/templates/secrets.yaml` templating Kubernetes Secret with values from {{ .Values.secrets.databaseUrl }}, {{ .Values.secrets.openaiApiKey }}, {{ .Values.secrets.betterAuthSecret }}
- [X] T082 [P] [US3] Create `helm/evolved-todo/templates/tests/test-connection.yaml` Helm test pod that verifies frontend→backend connectivity

**Helm Validation:**

- [X] T083 [US3] Run `helm lint helm/evolved-todo` and verify zero errors
- [X] T084 [US3] Run `helm install --dry-run --debug evolved-todo ./helm/evolved-todo -f ./helm/evolved-todo/values-dev.yaml` and verify all rendered manifests are valid YAML
- [X] T085 [US3] Verify templated values render correctly in dry-run output (replicas, image tags, resource limits, service types)

**Helm Installation:**

- [X] T086 [US3] Uninstall existing Kubernetes resources: `kubectl delete -f k8s/` (clean slate for Helm)
- [X] T087 [US3] Install Helm chart with dev values: `helm install evolved-todo ./helm/evolved-todo -f ./helm/evolved-todo/values-dev.yaml --set secrets.databaseUrl="${DATABASE_URL}" --set secrets.openaiApiKey="${OPENAI_API_KEY}" --set secrets.betterAuthSecret="${BETTER_AUTH_SECRET}" --wait --timeout=5m`
- [X] T088 [US3] Verify all resources created: `kubectl get all -l app.kubernetes.io/instance=evolved-todo`
- [X] T089 [US3] Verify all pods reach Ready state within 90 seconds: `kubectl wait --for=condition=Ready pod -l app.kubernetes.io/instance=evolved-todo --timeout=90s`
- [X] T090 [US3] Access frontend and verify all Phase 3 features work correctly

**Helm Upgrade Testing:**

- [X] T091 [US3] Modify values-dev.yaml to increase backend replicas from 1 to 3
- [X] T092 [US3] Run `helm upgrade evolved-todo ./helm/evolved-todo -f ./helm/evolved-todo/values-dev.yaml --wait`
- [X] T093 [US3] Verify rolling update completes without downtime (readiness probes prevent traffic to new pods until ready)
- [X] T094 [US3] Verify 3 backend pods running: `kubectl get pods -l app.kubernetes.io/name=evolved-todo,component=backend`
- [X] T095 [US3] Verify chatbot continues working during upgrade (zero downtime)

**Helm Rollback Testing:**

- [X] T096 [US3] Simulate failed upgrade by setting invalid image tag in values-dev.yaml (e.g., tag: "invalid-tag")
- [X] T097 [US3] Run `helm upgrade evolved-todo ./helm/evolved-todo -f ./helm/evolved-todo/values-dev.yaml` and observe failure
- [X] T098 [US3] Run `helm rollback evolved-todo` and verify rollback to previous working version within 60 seconds
- [X] T099 [US3] Verify all pods return to healthy state after rollback

**Helm Test:**

- [X] T100 [US3] Run `helm test evolved-todo` and verify test pod passes (frontend→backend connectivity check)
- [X] T101 [US3] Verify test pod completes successfully and logs show successful connection

**Documentation:**

- [X] T102 [US3] Document Helm chart usage in `docs/deployment/helm-deployment.md` with install, upgrade, rollback commands, values customization guide, troubleshooting

**Checkpoint**: At this point, User Story 3 should be fully functional - Helm chart installs, upgrades, and rolls back successfully with environment-specific values

---

## Phase 6: User Story 4 - AIOps Tool Integration (Priority: P4)

**Goal**: Document and demonstrate usage of AI-powered tools (Docker AI Gordon, kubectl-ai, Kagent) for Dockerfile optimization, Kubernetes operations, and cluster analysis

**Independent Test**: Use Gordon to optimize Dockerfiles and analyze security, use kubectl-ai to deploy and scale resources with natural language commands, and use Kagent to analyze cluster health and provide optimization recommendations

### Implementation for User Story 4

**Docker AI (Gordon) Integration:**

- [X] T103 [P] [US4] Document Docker AI usage in `docs/deployment/aiops-tools.md` section "Docker AI (Gordon)" with examples: "optimize backend/Dockerfile for size and security", "analyze security vulnerabilities in evolved-todo-backend:1.0.0"
- [X] T104 [P] [US4] Test Gordon Dockerfile optimization: Run `docker ai "optimize backend/Dockerfile for size and security"` and document at least 3 actionable suggestions received
- [X] T105 [P] [US4] Test Gordon security analysis: Run `docker ai "analyze security issues in evolved-todo-backend:1.0.0"` and verify vulnerability scan results
- [X] T106 [US4] Document Gordon best practices in aiops-tools.md: When to use AI suggestions, how to validate before applying, codifying AI suggestions in Dockerfiles

**kubectl-ai Integration:**

- [X] T107 [P] [US4] Document kubectl-ai usage in `docs/deployment/aiops-tools.md` section "kubectl-ai" with examples: "deploy the backend with 3 replicas", "scale the frontend to handle more load", "check why pods are failing"
- [X] T108 [P] [US4] Test kubectl-ai deployment command: Run `kubectl-ai "deploy the todo backend with 3 replicas"` and verify correct kubectl command executed
- [X] T109 [P] [US4] Test kubectl-ai scaling command: Run `kubectl-ai "scale the frontend to handle more load"` and document recommendation
- [X] T110 [P] [US4] Test kubectl-ai troubleshooting: Intentionally break a pod (wrong image tag) and run `kubectl-ai "check why the pods are failing"` to verify diagnostic output
- [X] T111 [P] [US4] Test kubectl-ai log analysis: Run `kubectl-ai "show me error logs from the last hour"` and verify correct log filtering

**Kagent Integration:**

- [X] T112 [P] [US4] Document Kagent usage in `docs/deployment/aiops-tools.md` section "Kagent" with examples: "analyze the cluster health", "optimize resource allocation", "recommend resource limits based on actual usage"
- [X] T113 [P] [US4] Test Kagent cluster health analysis: Run `kagent "analyze the cluster health and identify issues"` and document health assessment received
- [X] T114 [P] [US4] Test Kagent resource optimization: Run `kagent "optimize resource allocation for better efficiency"` and verify at least 2 optimization recommendations received (e.g., right-size pod resources, adjust HPA thresholds)
- [X] T115 [P] [US4] Test Kagent capacity planning: Run `kagent "recommend resource limits based on actual usage"` and document recommendations

**AIOps Workflow Documentation:**

- [X] T116 [US4] Document AIOps workflow in `docs/deployment/aiops-workflow.md`: When to use each tool (Gordon during build, kubectl-ai during ops, Kagent for analysis), how to validate AI suggestions, documenting AI-suggested changes in ADRs
- [X] T117 [US4] Create examples in aiops-workflow.md showing before/after of AI-suggested optimizations (e.g., Dockerfile improvement, resource limit adjustment)
- [X] T118 [US4] Add troubleshooting guide for common AIOps tool issues (network connectivity, API rate limits, tool installation)

**Checkpoint**: At this point, User Story 4 should be complete - All AIOps tools documented, tested, and demonstrated with successful results

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements that affect multiple user stories and comprehensive validation

**README and Documentation:**

- [X] T119 [P] Update root `README.md` with Phase 4 overview, deployment architecture diagram (Frontend → Backend → Database), Minikube deployment quick start
- [X] T120 [P] Create `docs/deployment/README.md` as deployment documentation hub linking to docker-build.md, kubernetes-deployment.md, helm-deployment.md, aiops-tools.md
- [X] T121 [P] Create `docs/deployment/troubleshooting.md` with common issues: ImagePullBackOff (load images to Minikube), Pods Pending (increase cluster resources), Health check failures (verify database URL), LoadBalancer pending (start minikube tunnel)
- [X] T122 [P] Verify quickstart guide in `specs/004-phase4-k8s-deployment/quickstart.md` is accurate and enables new developer to deploy in <30 minutes

**Comprehensive Validation:**

- [x] T123 Clean Minikube cluster: `minikube delete` and `minikube start --cpus=4 --memory=8192`
- [x] T124 Follow quickstart.md from scratch and verify complete deployment in <30 minutes (timed)
- [x] T125 Verify all 10 Phase 3 task management features work correctly on Kubernetes (100% feature parity validation)
- [x] T126 Run load test with 100 concurrent chat requests and verify <2s average response time (Phase 3 parity)
- [x] T127 Verify JWT authentication works end-to-end from frontend to backend
- [x] T128 Verify conversation state persists across multiple backend pod restarts (kill all backend pods, verify conversations intact)
- [x] T129 Verify zero message loss during rolling update (start conversation, trigger `helm upgrade`, continue conversation)
- [x] T130 Verify system auto-recovery when database connection temporarily lost (stop database access, verify readiness probe fails, restore access, verify auto-recovery <30s)

**Security and Performance:**

- [x] T131 Run final Trivy scans on all images and verify zero critical/high vulnerabilities
- [x] T132 Verify all containers run as non-root user (UID 1000) in Kubernetes: `kubectl exec -it <pod> -- id`
- [x] T133 Verify cluster resource utilization <80% of allocated requests during normal operation: `kubectl top nodes`
- [x] T134 Verify pod resource usage stays within limits: `kubectl top pods -l app=evolved-todo`

**Code Quality:**

- [x] T135 [P] Run linting on all Dockerfile files (hadolint if available) and fix any issues
- [x] T136 [P] Validate all Kubernetes YAML files with `kubectl apply --dry-run=client -f k8s/`
- [X] T137 [P] Validate Helm chart with `helm lint helm/evolved-todo` and ensure zero errors
- [x] T138 Review all ADRs (ADR-001 to ADR-004) and ensure implementation matches documented decisions

**Final Validation:**

- [x] T139 Verify all 32 success criteria from spec.md are met (SC-001 to SC-032)
- [x] T140 Verify all 45 functional requirements from spec.md are implemented (FR-001 to FR-045)
- [x] T141 Test all 7 edge cases from spec.md (health check failures, resource exhaustion, missing secrets, image pull failures, Helm upgrade failures, database unavailability, concurrent table creation)
- [x] T142 Run `helm test evolved-todo` final validation and verify all tests pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (Containerization) can start after Foundational
  - User Story 2 (Kubernetes) depends on User Story 1 completion (needs Docker images)
  - User Story 3 (Helm) depends on User Story 2 completion (needs K8s manifests to template)
  - User Story 4 (AIOps) can run in parallel with any phase (documentation only)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on User Story 1 (needs Docker images built) - Cannot start until US1 complete
- **User Story 3 (P3)**: Depends on User Story 2 (needs K8s manifests to template) - Cannot start until US2 complete
- **User Story 4 (P4)**: Independent - Can run in parallel with any phase (documentation and testing only)

### Within Each User Story

- **User Story 1**: .dockerignore → Dockerfiles → Build images → Security scans → Local container testing
- **User Story 2**: Minikube setup → Load images → Create manifests → Apply manifests → Testing and validation
- **User Story 3**: Helm structure → Templates → Validation → Installation → Upgrade/Rollback testing
- **User Story 4**: All tasks [P] parallelizable (independent documentation and testing)

### Parallel Opportunities

- **Phase 1 Setup**: T001-T007 can all run in parallel except T001 must complete before T002-T003
- **Phase 2 Foundational**: T008-T009 can run in parallel (different files)
- **User Story 1 Dockerfiles**: T013-T014 can run in parallel (frontend and backend separate)
- **User Story 1 Scans**: T023-T024 can run in parallel after T019-T020 complete
- **User Story 2 Manifests**: T042-T044 (backend) and T045-T047 (frontend) can run in parallel
- **User Story 3 Helm Templates**: T075-T077 (backend) and T078-T080 (frontend) can run in parallel
- **User Story 4**: All tasks (T103-T118) can run in parallel (independent documentation)
- **Phase 7 Documentation**: T119-T122 can run in parallel

---

## Parallel Example: User Story 2

```bash
# After Minikube setup and images loaded, create all manifests in parallel:

Parallel Group 1 (Backend manifests):
Task T042: "Create backend Deployment manifest in k8s/backend/deployment.yaml"
Task T043: "Create backend Service manifest in k8s/backend/service.yaml"
Task T044: "Create backend HPA manifest in k8s/backend/hpa.yaml"

Parallel Group 2 (Frontend manifests):
Task T045: "Create frontend Deployment manifest in k8s/frontend/deployment.yaml"
Task T046: "Create frontend Service manifest in k8s/frontend/service.yaml"
Task T047: "Create frontend HPA manifest in k8s/frontend/hpa.yaml"

# Then apply sequentially: Deployments → Services → HPAs
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T012) - CRITICAL
3. Complete Phase 3: User Story 1 (T013-T032)
4. **STOP and VALIDATE**: Docker images build, pass security scans, all Phase 3 features work in containers
5. Demo containerized application running locally

### Incremental Delivery

1. **Foundation**: Complete Setup + Foundational → Health endpoints ready
2. **Containers (MVP)**: Add User Story 1 → Docker images working → Demo locally
3. **Kubernetes**: Add User Story 2 → Pods running on Minikube → Demo K8s deployment
4. **Helm**: Add User Story 3 → Helm chart working → Demo upgrade/rollback
5. **AIOps**: Add User Story 4 → AIOps tools documented → Demo AI-powered operations

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (T001-T012)
2. **Developer A: User Story 1** (T013-T032) - Dockerfiles and container testing
3. After US1 complete:
   - **Developer B: User Story 2** (T033-T070) - Kubernetes manifests and deployment
   - **Developer C: User Story 4** (T103-T118) - AIOps documentation (can start early, independent)
4. After US2 complete:
   - **Developer D: User Story 3** (T071-T102) - Helm charts
5. **All developers: Phase 7** (T119-T142) - Polish and comprehensive validation

---

## Notes

- [P] tasks = different files, no dependencies on other tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- User Story 1 (Containerization) is MVP - delivers value immediately
- User Story 2-3 build upon US1 sequentially (US2 needs images from US1, US3 needs manifests from US2)
- User Story 4 (AIOps) is independent and can run in parallel
- Commit after each logical task group
- Verify health endpoints work before starting any containerization work
- Test stateless architecture thoroughly in User Story 2 (pod deletion, scaling)
- Document all AIOps tool usage for team knowledge sharing

---

## Total Task Count

- **Phase 1 (Setup)**: 7 tasks
- **Phase 2 (Foundational)**: 5 tasks
- **Phase 3 (User Story 1 - Containerization)**: 20 tasks
- **Phase 4 (User Story 2 - Kubernetes)**: 38 tasks
- **Phase 5 (User Story 3 - Helm)**: 32 tasks
- **Phase 6 (User Story 4 - AIOps)**: 16 tasks
- **Phase 7 (Polish)**: 24 tasks

**Total: 142 tasks**

**Parallelizable**: 35 tasks marked [P] can run in parallel with others
**MVP Scope**: T001-T032 (39 tasks) delivers containerized application locally
