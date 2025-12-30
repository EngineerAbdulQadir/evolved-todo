---
id: 002
title: Update AGENTS.md for Phase 4
stage: misc
date: 2025-12-25
surface: agent
model: claude-sonnet-4-5-20250929
feature: 004-phase4-k8s-deployment
branch: 004-phase4-k8s-deployment
user: AQI
command: manual
labels: ["phase-4", "agents-md", "documentation", "update"]
links:
  spec: specs/004-phase4-k8s-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - AGENTS.md
tests:
  - None (documentation update)
---

## Prompt

User requested: "now update @AGENTS.md in accordance with phase 4"

**Context**: After completing Phase 4 implementation planning (`/sp.plan`), user requested updating the AGENTS.md file to reflect Phase 4 containerization and Kubernetes deployment requirements. The file previously documented Phase 3 (AI Chatbot Development) and needed to be updated for Phase 4 (Local Kubernetes Deployment).

**Intent**: Update agent behavior guidelines, technology stack, constraints, quality gates, and workflow examples to reflect Phase 4 scope and requirements.

## Response snapshot

Successfully updated AGENTS.md from v1.0.0 (Phase 3) to v2.0.0 (Phase 4):

**Phase Context Updated:**
- Changed "Phase 3 Specific Context" → "Phase 4 Specific Context"
- Updated current phase: Phase III → Phase IV - Local Kubernetes Deployment
- Added comprehensive technology stack for containerization and orchestration

**Technology Stack Expanded (+7 new tools):**
- **Containerization**: Docker Desktop 4.53+, Docker AI (Gordon)
- **Orchestration**: Kubernetes (Minikube 1.28+), Helm 3.x
- **AIOps Tools**: kubectl-ai, Kagent
- **Base Images**: node:22-alpine (frontend), python:3.13-slim (backend)
- **Preserved Phase 3 Stack**: FastAPI, OpenAI Agents SDK, MCP SDK, Next.js 16+, ChatKit, Better Auth, Neon PostgreSQL

**Key Constraints Added (3 categories):**

1. **Containerization Constraints:**
   - Multi-stage Dockerfiles required (build + production stages)
   - Image size limits: Frontend <150MB, Backend <200MB (compressed)
   - Non-root containers (UID 1000)
   - Health check endpoints mandatory (`/health` backend, `/api/health` frontend)
   - Zero critical/high vulnerabilities (Trivy security scan)

2. **Kubernetes Deployment Constraints:**
   - Resource requests and limits defined (Frontend: 100m/128Mi → 200m/256Mi, Backend: 200m/256Mi → 500m/512Mi)
   - Liveness, Readiness, and Startup probes configured
   - Minimum 2 replicas per service for high availability
   - HPA for autoscaling (Backend: 2-10 pods @ 70% CPU, Frontend: 2-5 pods @ 80% CPU)
   - Kubernetes Secrets for sensitive data (DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET)
   - Services: ClusterIP for backend (internal only), LoadBalancer/NodePort for frontend (external)

3. **Stateless Architecture (CRITICAL for K8s):**
   - All MCP tools stateless (database persistence only)
   - Chat endpoint fetches conversation history from DB on each request
   - Any backend pod can handle any request (LoadBalancer distribution)
   - Pods can be killed/recreated without data loss
   - Conversation state persisted to database

**"Agent Must Not" Rules Expanded (+7 new rules):**
- ❌ Use `latest` tags for Docker images (pin specific versions)
- ❌ Run containers as root user (security requirement)
- ❌ Include secrets in Dockerfiles or commit to git
- ❌ Create containers without health checks
- ❌ Skip resource requests/limits in K8s manifests
- ❌ Deploy without validation (`kubectl --dry-run=client`, `helm lint`)
- ❌ Modify Phase 3 database schema (Task, Conversation, Message, User unchanged)

**Quality Gates Expanded (+30 new gates, 15 → 45 total):**

1. **Before Writing Code**: Added Docker/Kubernetes prerequisites check
2. **After Implementation - Containerization (8 gates)**: Dockerfiles, .dockerignore, health checks, Trivy scans, non-root user, image size, startup time
3. **After Implementation - Kubernetes (11 gates)**: Resources, probes, replicas, HPA, Secrets, Services, manifest validation, labels, pod ready time, health checks, service accessibility
4. **After Implementation - Deployment Validation (7 gates)**: State persistence, horizontal scaling, zero message loss, 100% feature parity, rolling updates, Helm validation

**Workflow Example Updated:**
- Changed from generic "Implement AI chatbot" to specific Phase 4 example: "Containerize Phase 3 AI Chatbot and deploy on Minikube with Helm"
- Updated workflow steps: `/sp.specify` (4 user stories) → `/sp.plan` (Docker, K8s, Helm) → `/sp.tasks` (Dockerfiles, resources, templates) → `/sp.implement` (TDD approach) → validation (18 principles)
- Updated human-in-the-loop examples with Phase 4 decisions (multi-stage builds, HPA config, LoadBalancer vs NodePort)

**Version & Change Log:**
- Version: 1.0.0 → 2.0.0 (MAJOR version bump - new phase, new capabilities)
- Last Updated: 2025-12-17 → 2025-12-25
- Added comprehensive change log documenting v1.0.0 → v2.0.0 transition

**Phase 3 Feature Preservation Section Added:**
- Explicitly documented that all 10 Phase 3 task management features MUST work in containers (100% feature parity)
- Natural language understanding unchanged
- JWT authentication preserved
- MCP tools and OpenAI Agents SDK integration unchanged

## Outcome

- ✅ Impact: AGENTS.md updated to v2.0.0 with comprehensive Phase 4 containerization and Kubernetes deployment guidance for all AI agents
- 🧪 Tests: None required (documentation update)
- 📁 Files: 1 file modified (AGENTS.md)
- 🔁 Next prompts:
  - Execute `/sp.tasks` to generate atomic implementation tasks for Phase 4
  - Create Dockerfiles for frontend and backend following multi-stage build pattern
  - Set up Minikube local cluster with metrics-server addon
  - Create Kubernetes manifests (Deployments, Services, Secrets, HPA)
  - Create Helm charts with templates and values files
  - Implement container tests (health checks, security scans, startup time)
- 🧠 Reflection: Successfully updated agent guidance from Phase 3 (AI Chatbot) to Phase 4 (Containerization & K8s). Key achievement: Maintained all Phase 3 requirements while adding comprehensive containerization and orchestration constraints. The 30 new quality gates ensure production-ready deployments with security, reliability, and scalability. Stateless architecture emphasis is CRITICAL - enables horizontal scaling without code changes. Version 2.0.0 reflects MAJOR transition to cloud-native deployment patterns.

## Evaluation notes (flywheel)

- Failure modes observed: None - all sections updated consistently and comprehensively
- Graders run and results (PASS/FAIL): PASS - AGENTS.md follows structure, all Phase 4 technologies documented, constraints clearly defined, quality gates comprehensive, workflow examples realistic
- Prompt variant (if applicable): Standard documentation update workflow (read → analyze → update → validate)
- Next experiment (smallest change to try): Proceed to `/sp.tasks` to generate atomic implementation tasks with TDD test cases for Dockerfiles, K8s manifests, Helm charts, and deployment validation
