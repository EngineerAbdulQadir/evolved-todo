# Feature Specification: Phase 4 - Local Kubernetes Deployment

**Feature Branch**: `004-phase4-k8s-deployment`
**Created**: 2025-12-25
**Status**: Draft
**Input**: User description: "Phase 4: Local Kubernetes Deployment - Containerize Phase 3 AI Chatbot with Docker and deploy on Minikube using Helm charts with AIOps tools (Gordon, kubectl-ai, Kagent)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Containerized Application Deployment (Priority: P1)

As a DevOps engineer, I want to containerize the Phase 3 AI Chatbot application (frontend and backend) so that it runs consistently across different environments and can be deployed on Kubernetes.

**Why this priority**: Containerization is the foundation for all subsequent Kubernetes deployment work. Without properly containerized applications with health checks and security hardening, none of the orchestration benefits can be realized.

**Independent Test**: Can be fully tested by building Docker images locally, running containers with docker run, verifying health check endpoints respond correctly, and confirming all Phase 3 chatbot features work within containers without Kubernetes.

**Acceptance Scenarios**:

1. **Given** Phase 3 frontend and backend code exists, **When** Dockerfiles are created with multi-stage builds, **Then** both images build successfully and are smaller than 150MB (frontend) and 200MB (backend)
2. **Given** Docker images are built, **When** containers are started locally, **Then** health check endpoints respond within 1 second and return healthy status
3. **Given** containers are running, **When** security scan is performed with Trivy, **Then** no critical or high vulnerabilities are found
4. **Given** frontend and backend containers are running, **When** user accesses chatbot via browser, **Then** all 10 Phase 3 task management features work correctly through natural language
5. **Given** backend container is running, **When** database connection is tested, **Then** backend successfully connects to external Neon PostgreSQL database
6. **Given** containers are running as non-root user, **When** container security context is inspected, **Then** containers run with user ID 1000 and read-only root filesystem where possible

---

### User Story 2 - Kubernetes Deployment on Minikube (Priority: P2)

As a DevOps engineer, I want to deploy the containerized AI Chatbot on a local Minikube Kubernetes cluster with proper resource management, health checks, and horizontal scaling so that I can validate cloud-native architecture before production deployment.

**Why this priority**: Once containers are working, Kubernetes deployment provides orchestration, self-healing, and horizontal scaling capabilities. This is the core deliverable for Phase 4 and validates the stateless architecture.

**Independent Test**: Can be fully tested by deploying Kubernetes manifests to Minikube, verifying all pods reach Ready state, accessing the application via Kubernetes Services, testing horizontal scaling by adjusting replicas, and confirming conversation state persists across pod restarts.

**Acceptance Scenarios**:

1. **Given** Minikube cluster is running, **When** Kubernetes manifests are applied, **Then** all pods (frontend and backend) reach Ready state within 60 seconds
2. **Given** pods are running, **When** liveness probes are checked, **Then** all probes pass and pods are not restarted
3. **Given** pods are running, **When** readiness probes are checked, **Then** all probes pass and pods are added to Services
4. **Given** Services are created, **When** frontend Service is accessed via NodePort or LoadBalancer, **Then** chatbot UI loads successfully
5. **Given** frontend and backend Services exist, **When** user sends chat message, **Then** frontend communicates with backend via ClusterIP Service and receives response
6. **Given** backend has 3 replicas running, **When** one pod is deleted, **Then** Kubernetes automatically recreates it and conversation state is not lost
7. **Given** backend deployment exists, **When** HPA (Horizontal Pod Autoscaler) is configured, **Then** pods scale up under load (simulated with load generator) and scale down when load decreases
8. **Given** Kubernetes Secrets exist, **When** pods are inspected, **Then** environment variables for DATABASE_URL, OPENAI_API_KEY, and BETTER_AUTH_SECRET are correctly injected from Secrets
9. **Given** pods are running, **When** resource usage is checked, **Then** all pods stay within defined CPU and memory limits
10. **Given** backend pods are running, **When** database connectivity is tested, **Then** all pods successfully connect to external Neon PostgreSQL database

---

### User Story 3 - Helm Chart Deployment (Priority: P3)

As a DevOps engineer, I want to manage Kubernetes deployments using Helm charts with environment-specific values so that I can simplify deployment, upgrades, and rollbacks across different environments.

**Why this priority**: Helm charts provide templating, versioning, and configuration management. While Kubernetes manifests work for Phase 4, Helm charts prepare for Phase 5 cloud deployment with environment-specific configurations.

**Independent Test**: Can be fully tested by creating Helm chart structure, templating all Kubernetes resources, installing chart to Minikube with custom values, upgrading chart with new values, and rolling back to previous version successfully.

**Acceptance Scenarios**:

1. **Given** Helm chart structure is created, **When** helm lint is run, **Then** chart passes all validation checks without errors
2. **Given** Helm chart is valid, **When** helm install --dry-run is executed, **Then** all rendered manifests are valid Kubernetes YAML
3. **Given** Helm chart is ready, **When** helm install is executed with values-dev.yaml, **Then** all resources are created and pods reach Ready state
4. **Given** Helm release is installed, **When** values are modified (e.g., increase replicas), **Then** helm upgrade applies changes without downtime
5. **Given** Helm release is upgraded, **When** issue is detected, **Then** helm rollback restores previous working version
6. **Given** Helm chart includes test templates, **When** helm test is executed, **Then** test pods verify frontend and backend connectivity and pass
7. **Given** Helm chart uses parameterized values, **When** different environment values are used (dev vs prod), **Then** chart deploys with appropriate resource limits, replica counts, and service types

---

### User Story 4 - AIOps Tool Integration (Priority: P4)

As a DevOps engineer, I want to use AI-powered tools (Docker AI Gordon, kubectl-ai, Kagent) to optimize Dockerfiles, troubleshoot deployments, and analyze cluster health so that I can accelerate development and reduce manual troubleshooting effort.

**Why this priority**: AIOps tools enhance productivity and provide intelligent insights, but the core deployment must work without them. This is a nice-to-have enhancement rather than a blocker.

**Independent Test**: Can be fully tested by using Gordon to optimize Dockerfiles and analyze security, using kubectl-ai to deploy and scale resources with natural language commands, and using Kagent to analyze cluster health and provide optimization recommendations.

**Acceptance Scenarios**:

1. **Given** Dockerfiles exist, **When** docker ai "optimize this Dockerfile for size and security" is run, **Then** Gordon provides actionable optimization suggestions
2. **Given** Dockerfiles exist, **When** docker ai "analyze security issues in this image" is run, **Then** Gordon identifies security vulnerabilities and provides remediation steps
3. **Given** Minikube cluster is running, **When** kubectl-ai "deploy the backend with 3 replicas" is executed, **Then** backend deployment is created with 3 replicas successfully
4. **Given** deployments are running, **When** kubectl-ai "scale the frontend to handle more load" is executed, **Then** frontend replicas are increased appropriately
5. **Given** pods are failing, **When** kubectl-ai "check why the pods are failing" is executed, **Then** kubectl-ai provides diagnostic information and root cause analysis
6. **Given** cluster is running, **When** kagent "analyze the cluster health" is executed, **Then** Kagent provides health assessment and identifies potential issues
7. **Given** cluster is running, **When** kagent "optimize resource allocation" is executed, **Then** Kagent provides resource optimization recommendations based on actual usage

---

### Edge Cases

- What happens when container health check fails repeatedly (e.g., database connection lost)?
  - Kubernetes liveness probe should restart the container after 3 consecutive failures
  - Readiness probe should remove pod from Service until health check passes
  - Users should see no impact if multiple replicas are running (failover to healthy pods)

- What happens when Minikube cluster runs out of resources (CPU or memory)?
  - Pods should enter Pending state with clear error message indicating insufficient resources
  - Existing pods should continue running within their resource limits
  - HPA should not scale beyond available cluster resources

- What happens when Kubernetes Secret is missing or corrupted?
  - Pods should fail to start with clear error message indicating missing Secret
  - Deployment should not proceed until Secret is created
  - Health check should fail if required environment variables are not set

- What happens when Docker image pull fails (network issue or wrong tag)?
  - Pods should enter ImagePullBackOff state with clear error message
  - Kubernetes should retry image pull with exponential backoff
  - Deployment should not mark as successful until all pods are running

- What happens when Helm upgrade fails mid-deployment?
  - Helm should automatically rollback to previous revision
  - Users should experience minimal downtime if rolling update strategy is used
  - Helm status should clearly indicate failed upgrade and provide rollback steps

- What happens when database is temporarily unavailable?
  - Backend health check should fail (readiness probe)
  - Pods should be removed from Service until database is reachable
  - Kubernetes should not restart pods (liveness probe should still pass if app is running)
  - Users should see service unavailable message until database is back

- What happens when multiple pods try to create database tables simultaneously on first run?
  - SQLModel automatic table creation should use database-level locking to prevent race conditions
  - First pod to acquire lock creates tables, others wait and verify tables exist
  - All pods should eventually reach healthy state

## Requirements *(mandatory)*

### Functional Requirements

**Containerization:**

- **FR-001**: System MUST provide Dockerfiles for frontend and backend using multi-stage builds with separate build and production stages
- **FR-002**: Frontend container MUST use node:22-alpine base image and produce image smaller than 150MB
- **FR-003**: Backend container MUST use python:3.13-slim base image and produce image smaller than 200MB
- **FR-004**: All containers MUST include health check endpoints that respond within 1 second
- **FR-005**: All containers MUST run as non-root user (UID 1000)
- **FR-006**: All containers MUST include HEALTHCHECK directive in Dockerfile with 30s interval, 10s timeout, 3 retries
- **FR-007**: All container images MUST pass security scan with zero critical or high vulnerabilities (Trivy scan)
- **FR-008**: Dockerfiles MUST use .dockerignore to exclude node_modules, .git, tests, and other development files
- **FR-009**: Backend container MUST successfully connect to external Neon PostgreSQL database using DATABASE_URL from environment variable
- **FR-010**: Frontend container MUST serve Next.js production build with optimized static assets

**Kubernetes Deployment:**

- **FR-011**: System MUST provide Kubernetes Deployment manifests for frontend and backend with resource requests and limits defined
- **FR-012**: Frontend Deployment MUST request 100m CPU and 128Mi memory, with limits of 200m CPU and 256Mi memory
- **FR-013**: Backend Deployment MUST request 200m CPU and 256Mi memory, with limits of 500m CPU and 512Mi memory
- **FR-014**: All Deployments MUST include liveness probes (httpGet /health every 10s, failureThreshold 3)
- **FR-015**: All Deployments MUST include readiness probes (httpGet /health every 10s, initialDelaySeconds 20, failureThreshold 3)
- **FR-016**: Backend Deployment MUST include startup probe (httpGet /health every 5s for up to 60s)
- **FR-017**: All Deployments MUST use rolling update strategy with maxUnavailable 1 and maxSurge 1
- **FR-018**: Backend Deployment MUST have minimum 2 replicas for high availability
- **FR-019**: Frontend Deployment MUST have minimum 2 replicas for high availability
- **FR-020**: System MUST provide Kubernetes Service manifests for frontend (LoadBalancer or NodePort) and backend (ClusterIP)
- **FR-021**: Backend Service MUST only be accessible within cluster (ClusterIP type)
- **FR-022**: Frontend Service MUST be externally accessible via NodePort or LoadBalancer on Minikube
- **FR-023**: System MUST provide Kubernetes Secret manifest template for DATABASE_URL, OPENAI_API_KEY, and BETTER_AUTH_SECRET
- **FR-024**: Secrets MUST be mounted as environment variables in backend pods
- **FR-025**: System MUST provide Horizontal Pod Autoscaler for backend scaling from 2 to 10 pods based on CPU (target 70%)
- **FR-026**: All Kubernetes resources MUST include labels: app, component, version
- **FR-027**: All pods MUST reach Ready state within 60 seconds of deployment
- **FR-028**: Conversation state MUST persist across pod restarts and deletions

**Helm Charts:**

- **FR-029**: System MUST provide Helm chart structure with Chart.yaml, values.yaml, values-dev.yaml, and templates/
- **FR-030**: Helm chart MUST pass helm lint validation without errors
- **FR-031**: Helm chart MUST support environment-specific values (dev, prod) via separate values files
- **FR-032**: Helm chart MUST parameterize replica counts, image tags, resource limits, and service types
- **FR-033**: Helm chart MUST include _helpers.tpl for common labels and selectors
- **FR-034**: Helm chart MUST support dry-run installation for validation before deployment
- **FR-035**: Helm chart MUST support upgrade and rollback operations without data loss
- **FR-036**: Helm chart MUST include test templates to verify frontend and backend connectivity

**AIOps Integration:**

- **FR-037**: System MUST document usage of Docker AI (Gordon) for Dockerfile optimization and security analysis
- **FR-038**: System MUST document usage of kubectl-ai for natural language Kubernetes operations
- **FR-039**: System MUST document usage of Kagent for cluster health analysis and optimization

**Phase 3 Feature Preservation:**

- **FR-040**: All 10 Phase 3 task management features MUST work correctly when deployed on Kubernetes (no regression)
- **FR-041**: Natural language chatbot interface MUST function identically in containerized environment
- **FR-042**: JWT authentication MUST work end-to-end from frontend to backend within Kubernetes cluster
- **FR-043**: Conversation state MUST persist correctly to external database from any backend pod
- **FR-044**: All MCP tools MUST execute correctly in containerized backend environment
- **FR-045**: OpenAI Agents SDK MUST function correctly with environment variables from Kubernetes Secrets

### Key Entities

- **Docker Image**: Containerized application artifact containing application code, dependencies, and runtime. Frontend and backend each have separate images with specific base images, build stages, and health checks.

- **Kubernetes Deployment**: Declarative configuration for desired application state including replica count, container specifications, resource limits, health checks, and update strategy.

- **Kubernetes Service**: Network abstraction providing stable endpoint for accessing pods, with different types (ClusterIP for internal, LoadBalancer/NodePort for external).

- **Kubernetes Secret**: Secure storage for sensitive configuration data (database credentials, API keys) mounted as environment variables in pods.

- **Horizontal Pod Autoscaler**: Automatic scaling policy that adjusts pod replica count based on CPU/memory utilization metrics.

- **Helm Chart**: Packaged collection of Kubernetes resource templates with parameterized values for environment-specific deployment configuration.

- **Health Check Endpoint**: HTTP endpoint exposed by containers that returns service health status for Kubernetes liveness and readiness probes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Containerization Success:**

- **SC-001**: Docker images for frontend and backend build successfully in under 5 minutes each
- **SC-002**: Frontend container image size is under 150MB when compressed
- **SC-003**: Backend container image size is under 200MB when compressed
- **SC-004**: Containers start and become healthy within 10 seconds of docker run
- **SC-005**: Health check endpoints respond within 1 second when container is running
- **SC-006**: Zero critical or high security vulnerabilities detected in container images by Trivy scan
- **SC-007**: All Phase 3 chatbot features work correctly when running in containers locally (100% feature parity)

**Kubernetes Deployment Success:**

- **SC-008**: All Kubernetes manifests apply successfully without errors on fresh Minikube cluster
- **SC-009**: All pods reach Ready state within 60 seconds of deployment
- **SC-010**: Liveness and readiness probes pass for all running pods (100% probe success rate)
- **SC-011**: Frontend application is accessible via browser within 90 seconds of helm install
- **SC-012**: Backend application responds to API requests from frontend within cluster
- **SC-013**: Conversation state persists correctly when backend pod is deleted and recreated (zero data loss)
- **SC-014**: All Phase 3 chatbot features work correctly when deployed on Kubernetes (100% feature parity with Phase 3)
- **SC-015**: Horizontal Pod Autoscaler scales backend from 2 to 5 replicas under simulated load within 2 minutes
- **SC-016**: Database connectivity works from all backend pods simultaneously
- **SC-017**: JWT authentication works end-to-end with zero authentication failures

**Helm Chart Success:**

- **SC-018**: Helm chart passes helm lint validation with zero errors
- **SC-019**: Helm dry-run installation completes without errors and renders valid Kubernetes YAML
- **SC-020**: Helm install completes successfully and all pods become ready within 90 seconds
- **SC-021**: Helm upgrade applies configuration changes without downtime (rolling update)
- **SC-022**: Helm rollback restores previous version within 60 seconds
- **SC-023**: Helm test passes with all test pods completing successfully

**Performance & Reliability:**

- **SC-024**: System handles 100 concurrent chat requests without errors (same as Phase 3)
- **SC-025**: Average chat response time remains under 2 seconds (same as Phase 3)
- **SC-026**: Zero message loss when backend pods are killed and recreated during active conversations
- **SC-027**: System recovers automatically within 30 seconds when database connection is temporarily lost
- **SC-028**: Cluster resource utilization stays within 80% of allocated requests during normal operation

**Documentation & Tooling:**

- **SC-029**: Docker AI (Gordon) provides at least 3 actionable Dockerfile optimizations when consulted
- **SC-030**: kubectl-ai successfully executes at least 5 different natural language Kubernetes operations
- **SC-031**: Kagent provides cluster health report and at least 2 optimization recommendations
- **SC-032**: README documentation enables new developer to deploy entire system to Minikube in under 30 minutes

### Assumptions

- Minikube will be installed and configured with Docker driver on developer machines
- Developers have Docker Desktop installed with sufficient resources (4 CPU, 8GB RAM minimum)
- Neon PostgreSQL database remains accessible from Minikube cluster (external to cluster)
- OpenAI API key is available for OpenAI Agents SDK and ChatKit integration
- Better Auth secret is configured and shared between frontend and backend
- Docker AI (Gordon) is available in Docker Desktop 4.53+ (or standard Docker CLI used if unavailable)
- kubectl-ai and Kagent are installed and configured locally
- Helm 3.x is installed on developer machines
- All Phase 3 chatbot features are working correctly before starting Phase 4 containerization
- Windows developers use WSL 2 for Docker and Kubernetes development
- Load balancer functionality in Minikube is configured (minikube tunnel for LoadBalancer services)
