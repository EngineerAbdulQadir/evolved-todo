# Deployment Documentation Hub

**Phase 4: Kubernetes Deployment**
**Last Updated:** 2025-12-26

---

## 📚 Documentation Index

This directory contains comprehensive deployment guides for the Evolved Todo application across different environments.

### Quick Navigation

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [Helm Deployment Guide](helm-deployment.md) | **Production-ready Helm charts** | Deploying to Kubernetes clusters |
| [Kubernetes Deployment Guide](kubernetes-deployment.md) | Manual K8s resource deployment | Understanding K8s architecture |
| [Docker Build Guide](docker-build.md) | Container image creation | Building and optimizing images |
| [AIOps Tools Guide](aiops-tools.md) | AI-powered DevOps tools | Optimization and troubleshooting |
| [Troubleshooting Guide](troubleshooting.md) | Common issues and solutions | When things go wrong |
| [kubectl-ai Examples](kubectl-ai-examples.md) | Natural language K8s commands | Learning kubectl operations |
| [Kagent Examples](kagent-examples.md) | Cluster analysis examples | Capacity planning and optimization |
| [Cluster Analysis Report](cluster-analysis-report.md) | Real metrics and recommendations | Resource optimization decisions |
| [AIOps Workflow](aiops-workflow.md) | Integrated AI tooling workflow | Development to production lifecycle |

---

## 🚀 Getting Started

### New to Kubernetes?

**Start here:** [Helm Deployment Guide](helm-deployment.md)

1. Install prerequisites (Docker, Minikube, Helm)
2. Build Docker images
3. Deploy with Helm (one command!)
4. Access your application

**Estimated time:** 30 minutes

### Deploying to Production?

**Recommended path:**

1. **[Docker Build Guide](docker-build.md)** - Optimize your images
   - Multi-stage builds
   - Security scanning
   - Size optimization

2. **[Helm Deployment Guide](helm-deployment.md)** - Production deployment
   - Customize values.yaml
   - Configure secrets
   - Enable autoscaling
   - Setup monitoring

3. **[AIOps Tools Guide](aiops-tools.md)** - Optimize and maintain
   - Docker AI for image optimization
   - kubectl-ai for operations
   - Kagent for capacity planning

4. **[Troubleshooting Guide](troubleshooting.md)** - When issues arise
   - Common problems and solutions
   - Debugging techniques
   - Performance tuning

### Troubleshooting Issues?

**Go directly to:** [Troubleshooting Guide](troubleshooting.md)

Common quick fixes:
- **Pods not starting?** → ImagePullBackOff section
- **Services not accessible?** → LoadBalancer troubleshooting
- **Health checks failing?** → Health probe configuration
- **Out of resources?** → Resource optimization guide

---

## 📖 Documentation Details

### [Helm Deployment Guide](helm-deployment.md)
**Pages:** 850+ lines
**Topics:**
- Installation and prerequisites
- Helm chart structure
- Values customization (dev/prod)
- Upgrade and rollback procedures
- Helm tests and validation
- Best practices and security

**Best for:** Production deployments, automated releases

---

### [Kubernetes Deployment Guide](kubernetes-deployment.md)
**Pages:** 600+ lines
**Topics:**
- Manual K8s manifest deployment
- Service configuration
- HPA setup
- Resource management
- StatefulSets vs Deployments

**Best for:** Understanding Kubernetes internals, custom deployments

---

### [Docker Build Guide](docker-build.md)
**Pages:** 500+ lines
**Topics:**
- Multi-stage Dockerfile patterns
- Image size optimization
- Security best practices
- Build caching strategies
- Health check configuration
- Non-root containers

**Best for:** Image optimization, security hardening

---

### [AIOps Tools Guide](aiops-tools.md)
**Pages:** 4,500+ lines
**Topics:**
- Docker AI (Gordon) for Dockerfile optimization
- kubectl-ai for natural language K8s operations
- Kagent for cluster health and capacity planning
- Tool comparison matrix
- Integration workflows

**Best for:** DevOps automation, learning kubectl, cost optimization

---

### [Troubleshooting Guide](troubleshooting.md)
**Pages:** 400+ lines
**Topics:**
- Pod startup issues (ImagePullBackOff, CrashLoopBackOff)
- Health check failures
- Service connectivity problems
- Resource constraints
- Common error messages and fixes

**Best for:** Diagnosing and fixing issues quickly

---

### [kubectl-ai Examples](kubectl-ai-examples.md)
**Pages:** 650+ lines
**Topics:**
- Natural language kubectl commands
- Manual kubectl equivalents
- Validated examples with real cluster
- Before/after comparisons

**Best for:** Learning kubectl, exploring cluster operations

---

### [Kagent Examples](kagent-examples.md)
**Pages:** 950+ lines
**Topics:**
- Cluster health analysis
- Resource optimization recommendations
- Capacity planning with growth projections
- Cost impact analysis

**Best for:** Monthly optimization, quarterly capacity planning

---

### [Cluster Analysis Report](cluster-analysis-report.md)
**Pages:** 950+ lines
**Topics:**
- Real cluster metrics from production deployment
- Actual resource usage (7m CPU vs 300m allocated!)
- $576/year cost savings identified
- Optimization recommendations with validation

**Best for:** Data-driven optimization decisions

---

### [AIOps Workflow](aiops-workflow.md)
**Pages:** 850+ lines
**Topics:**
- When to use each AIOps tool
- Integrated dev → deploy → operate workflows
- Validation procedures (never auto-apply!)
- ADR templates for AI-driven changes
- Before/after examples with real results

**Best for:** Establishing DevOps best practices

---

## 🎯 Common Workflows

### Workflow 1: First-time Deployment

```bash
# 1. Read prerequisites
cat docs/deployment/helm-deployment.md | grep -A 20 "Prerequisites"

# 2. Build images
# See: docs/deployment/docker-build.md

# 3. Deploy with Helm
helm install evolved-todo ./helm/evolved-todo \
  -f ./helm/evolved-todo/values-dev.yaml \
  --set secrets.DATABASE_URL="$DATABASE_URL"

# 4. Verify deployment
kubectl get pods -l app.kubernetes.io/instance=evolved-todo

# 5. Troubleshoot if needed
# See: docs/deployment/troubleshooting.md
```

### Workflow 2: Optimizing Existing Deployment

```bash
# 1. Run Docker AI analysis
docker ai "optimize backend/Dockerfile for size and security"

# 2. Analyze cluster health
kubectl top pods  # See cluster-analysis-report.md for interpretation

# 3. Get optimization recommendations
# See: docs/deployment/kagent-examples.md

# 4. Apply optimizations
helm upgrade evolved-todo ./helm/evolved-todo \
  --set resources.backend.requests.cpu=20m \
  --reuse-values

# 5. Monitor impact
kubectl top pods --watch
```

### Workflow 3: Troubleshooting Issues

```bash
# 1. Check pod status
kubectl get pods

# 2. Describe failing pod
kubectl describe pod <pod-name>

# 3. Check logs
kubectl logs <pod-name> --tail=50

# 4. Check events
kubectl get events --sort-by='.lastTimestamp' | tail -20

# 5. Consult troubleshooting guide
# See: docs/deployment/troubleshooting.md
```

---

## 📊 Metrics and Benchmarks

### Deployment Success Criteria

✅ **Phase 4 Complete** - All criteria met:

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| **Pods Ready** | <90s | <60s | ✅ Pass |
| **Health Checks** | All passing | ✅ 100% | ✅ Pass |
| **Resource Usage** | <80% | 7% CPU, 43% memory | ✅ Pass |
| **Image Size** | <200MB backend | 185MB | ✅ Pass |
| **Image Size** | <150MB frontend | 142MB | ✅ Pass |
| **Zero Downtime** | Rolling updates | ✅ Verified | ✅ Pass |
| **Autoscaling** | HPA functional | ✅ Configured | ✅ Pass |
| **Security** | Non-root containers | ✅ UID 1000 | ✅ Pass |

### Performance Benchmarks

| Metric | Development | Production Target |
|--------|-------------|-------------------|
| **Pod Startup** | 15-30s | <60s |
| **Health Check Response** | <10ms | <50ms |
| **API Response Time** | <100ms | <200ms |
| **Chat Response Time** | <2s | <3s |
| **Concurrent Users** | 10 | 100+ (with HPA) |
| **Resource Utilization** | 7% CPU | <80% CPU |

---

## 🔧 Tools Reference

### Required Tools

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| **Docker** | 4.53+ | Container runtime | [docker.com](https://docker.com) |
| **Minikube** | 1.28+ | Local K8s cluster | `brew install minikube` |
| **kubectl** | 1.33+ | K8s CLI | `brew install kubectl` |
| **Helm** | 3.x | Package manager | `brew install helm` |

### Optional Tools (AIOps)

| Tool | Purpose | Documentation |
|------|---------|---------------|
| **Docker AI** | Dockerfile optimization | [aiops-tools.md](aiops-tools.md#docker-ai-gordon) |
| **kubectl-ai** | Natural language K8s | [kubectl-ai-examples.md](kubectl-ai-examples.md) |
| **Kagent** | Cluster analysis | [kagent-examples.md](kagent-examples.md) |

---

## 🆘 Getting Help

### Documentation Not Clear?

1. **Check examples** in the specific guide
2. **Search for error message** in [troubleshooting.md](troubleshooting.md)
3. **Review related guides** for context
4. **Check GitHub Issues** for similar problems

### Found a Bug?

1. Verify in [troubleshooting.md](troubleshooting.md) it's not expected behavior
2. Collect diagnostics:
   ```bash
   kubectl get pods
   kubectl describe pod <pod-name>
   kubectl logs <pod-name>
   kubectl get events
   ```
3. Create GitHub issue with diagnostics

### Want to Contribute?

See main [README.md](../../README.md) for contribution guidelines and [AGENTS.md](../../AGENTS.md) for Spec-Driven Development workflow.

---

## 📝 Documentation Maintenance

### Keep Documentation Updated

When making changes to:
- **Dockerfiles** → Update [docker-build.md](docker-build.md)
- **K8s manifests** → Update [kubernetes-deployment.md](kubernetes-deployment.md)
- **Helm charts** → Update [helm-deployment.md](helm-deployment.md)
- **Common issues** → Update [troubleshooting.md](troubleshooting.md)

### Documentation Versioning

- Docs match **Phase 4** implementation (2025-12-26)
- Each guide has "Last Updated" timestamp
- Breaking changes documented with migration guides

---

**Navigation:**
- [← Back to Main README](../../README.md)
- [View All Specifications](../../specs/)
- [Phase 4 Specification](../../specs/004-phase4-k8s-deployment/spec.md)

---

**Last Updated:** 2025-12-26
**Phase:** 4 - Kubernetes Deployment
**Status:** Complete ✅
