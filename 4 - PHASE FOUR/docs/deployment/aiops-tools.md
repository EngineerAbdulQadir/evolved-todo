# AIOps Tools Guide

**Task:** T103-T118 - AIOps tool integration and documentation
**Phase:** Phase 4 - Kubernetes Deployment
**Version:** 1.0.0

## Overview

This guide demonstrates using AI-powered operations (AIOps) tools for Docker, Kubernetes, and cluster management:

- **Docker AI (Gordon):** AI assistant for Dockerfile optimization and security analysis
- **kubectl-ai:** Natural language interface for Kubernetes operations
- **Kagent:** AI-powered cluster health analysis and optimization

These tools enhance developer productivity by providing intelligent suggestions, automated analysis, and natural language commands.

---

## Docker AI (Gordon)

**Docker AI** is an AI-powered assistant integrated into Docker Desktop that helps optimize Dockerfiles, analyze security vulnerabilities, and provide best practice recommendations.

### Prerequisites

- Docker Desktop 4.53+ with Docker AI enabled
- Docker images built locally or available in registry

### Installation & Setup

Docker AI (Gordon) is included with Docker Desktop 4.53+:

```bash
# Verify Docker Desktop version
docker --version
# Docker version 28.1.1 or higher

# Check Docker AI availability
docker ai --help
```

### Use Cases

#### 1. Optimize Dockerfile for Size and Security

**Command:**
```bash
docker ai "optimize backend/Dockerfile for size and security"
```

**Example Usage:**
```bash
# Analyze and get optimization suggestions for backend Dockerfile
docker ai "optimize backend/Dockerfile for size and security"
```

**Expected Suggestions:**
- Use multi-stage builds to reduce final image size
- Pin base image versions (avoid `latest` tags)
- Run as non-root user for security
- Minimize layers by combining RUN commands
- Remove unnecessary dependencies
- Use `.dockerignore` to exclude dev files
- Scan for vulnerabilities with `docker scout`

**Sample Output Analysis:**
```
I analyzed your backend/Dockerfile and found several optimization opportunities:

1. Image Size Reduction:
   - Current size: 1.2GB
   - Use python:3.13-slim instead of python:3.13 (saves ~800MB)
   - Use multi-stage build to separate build dependencies
   - Estimated final size: ~200MB

2. Security Improvements:
   - Pin base image to specific version: python:3.13.1-slim
   - Run as non-root user (UID 1000)
   - 3 high-severity vulnerabilities detected
   - Update dependencies: pip install --upgrade package

3. Build Optimization:
   - Combine RUN commands to reduce layers
   - Use COPY --chown to avoid extra chown layer
   - Order commands by frequency of change (cache optimization)
```

#### 2. Analyze Security Vulnerabilities

**Command:**
```bash
docker ai "analyze security issues in evolved-todo-backend:1.0.0"
```

**Example Usage:**
```bash
# Get security vulnerability report for backend image
docker ai "analyze security issues in evolved-todo-backend:1.0.0"
```

**Expected Analysis:**
- CVE vulnerabilities in base image and dependencies
- Severity levels (Critical, High, Medium, Low)
- Recommended fixes and package updates
- Compliance checks (CIS benchmarks)

**Sample Output:**
```
Security Analysis for evolved-todo-backend:1.0.0:

Critical Vulnerabilities: 0
High Severity: 3
Medium Severity: 12
Low Severity: 45

Top Issues:
1. [HIGH] CVE-2024-XXXX in openssl 3.0.1
   Fix: Update to openssl 3.0.14

2. [HIGH] CVE-2024-YYYY in libssl
   Fix: apt-get update && apt-get upgrade libssl

3. [MEDIUM] Container running as root user
   Fix: Add USER 1000 in Dockerfile

Recommendations:
- Scan regularly: docker scout cves evolved-todo-backend:1.0.0
- Enable Docker Scout continuous monitoring
- Update base image to python:3.13-slim-bookworm
```

#### 3. Best Practices Validation

**Command:**
```bash
docker ai "review frontend/Dockerfile for production best practices"
```

**Expected Guidance:**
- Health check instructions
- Environment variable handling
- Port exposure security
- Layer caching optimization
- Build-time vs runtime dependencies

### When to Use Docker AI

✅ **Use Docker AI when:**
- Optimizing Dockerfiles for production deployment
- Investigating security vulnerabilities
- Learning Docker best practices
- Troubleshooting build issues
- Reviewing Dockerfiles from new team members

❌ **Don't use Docker AI for:**
- Critical production decisions without validation
- Automated deployment pipelines (requires human review)
- Sensitive security issues (consult security team)

### Validating AI Suggestions

**IMPORTANT:** Always validate AI suggestions before applying:

1. **Test in development first:**
   ```bash
   # Build optimized image
   docker build -t evolved-todo-backend:optimized -f backend/Dockerfile.optimized backend/

   # Test functionality
   docker run --rm evolved-todo-backend:optimized python -c "import app; print('OK')"

   # Compare image sizes
   docker images | grep evolved-todo-backend
   ```

2. **Review security implications:**
   ```bash
   # Run security scan
   docker scout cves evolved-todo-backend:optimized

   # Compare with original
   docker scout compare evolved-todo-backend:1.0.0 evolved-todo-backend:optimized
   ```

3. **Document changes in ADR:**
   - Create Architecture Decision Record for significant Dockerfile changes
   - Document rationale and AI suggestions considered
   - Track impact on image size, build time, security

### Codifying AI Suggestions

After validating suggestions, update your Dockerfile:

```dockerfile
# Example: Apply Docker AI optimization suggestions
# ADR-XXX: Optimized Dockerfile based on Docker AI recommendations

# Multi-stage build (AI suggestion #1)
FROM python:3.13-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage (AI suggestion #2 - minimize size)
FROM python:3.13-slim
WORKDIR /app

# Security: Run as non-root user (AI suggestion #3)
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 appuser

# Copy only runtime dependencies
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --chown=appuser:appuser . .

USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## kubectl-ai

**kubectl-ai** provides a natural language interface for Kubernetes operations, translating English commands into kubectl commands.

### Prerequisites

- Kubernetes cluster (Minikube or production)
- kubectl configured
- kubectl-ai plugin installed

### Installation

```bash
# Install kubectl-ai (example - check official docs for latest method)
# Option 1: Using krew
kubectl krew install ai

# Option 2: Download binary
# Visit: https://github.com/sozercan/kubectl-ai
```

### Use Cases

#### 1. Deploy Resources with Natural Language

**Command:**
```bash
kubectl-ai "deploy the backend with 3 replicas"
```

**Expected Translation:**
```bash
kubectl scale deployment evolved-todo-backend --replicas=3
```

**Example Usage:**
```bash
# Let AI generate the kubectl command
kubectl-ai "deploy the backend with 3 replicas"

# Review the suggested command before executing
# Execute if correct, or modify as needed
```

#### 2. Scale for Load Handling

**Command:**
```bash
kubectl-ai "scale the frontend to handle more load"
```

**Expected Suggestions:**
- Increase replica count
- Adjust HPA settings
- Update resource limits
- Enable autoscaling

**Sample Output:**
```bash
# Suggested commands:
kubectl scale deployment evolved-todo-frontend --replicas=5
kubectl autoscale deployment evolved-todo-frontend --min=3 --max=10 --cpu-percent=70
kubectl set resources deployment evolved-todo-frontend --limits=cpu=400m,memory=512Mi
```

#### 3. Troubleshoot Pod Failures

**Command:**
```bash
kubectl-ai "check why the pods are failing"
```

**Expected Diagnostics:**
```bash
# Suggested diagnostic commands:
kubectl get pods --all-namespaces | grep -E 'Error|CrashLoopBackOff|ImagePullBackOff'
kubectl describe pod <failing-pod-name>
kubectl logs <failing-pod-name> --previous
kubectl get events --sort-by='.lastTimestamp'
```

#### 4. Analyze Error Logs

**Command:**
```bash
kubectl-ai "show me error logs from the last hour"
```

**Expected Log Queries:**
```bash
# Suggested commands:
kubectl logs --since=1h --all-containers=true -l app.kubernetes.io/instance=evolved-todo | grep -i error
kubectl logs --since=1h -l app.kubernetes.io/component=backend --tail=100
kubectl get events --field-selector type=Warning --sort-by='.lastTimestamp'
```

### When to Use kubectl-ai

✅ **Use kubectl-ai when:**
- Learning Kubernetes commands
- Exploring cluster operations
- Quick troubleshooting
- Generating complex kubectl syntax
- Training new team members

❌ **Don't use kubectl-ai for:**
- Production deployments (use validated manifests/Helm)
- Automated scripts (commands may vary)
- Critical operations (review before executing)

### Best Practices

1. **Always review generated commands** before executing
2. **Test in development** environment first
3. **Document useful patterns** in runbooks
4. **Combine with traditional kubectl** for verification

---

## Kagent

**Kagent** is an AI-powered Kubernetes agent that analyzes cluster health, recommends optimizations, and provides capacity planning insights.

### Prerequisites

- Kubernetes cluster with metrics-server enabled
- kubectl access with appropriate permissions
- Kagent CLI or web interface

### Installation

```bash
# Install Kagent (example - check official docs)
# Visit: https://github.com/kagent/kagent for latest installation
```

### Use Cases

#### 1. Cluster Health Analysis

**Command:**
```bash
kagent "analyze the cluster health and identify issues"
```

**Expected Health Assessment:**
```
Cluster Health Report:

Overall Status: Healthy ⚠️ (2 warnings)

Node Health:
✅ minikube - Ready
   CPU: 45% (4 cores available)
   Memory: 68% (8GB available)
   Disk: 32% (60GB available)

Resource Utilization:
⚠️  Backend pods CPU throttling detected (95% usage)
✅ Frontend within normal range (25% usage)
⚠️  Database connection pool nearing limit (85/100)

Recommendations:
1. Increase backend CPU limits from 500m to 800m
2. Scale backend replicas from 2 to 4 during peak hours
3. Review database query performance
```

#### 2. Resource Optimization

**Command:**
```bash
kagent "optimize resource allocation for better efficiency"
```

**Expected Optimization Recommendations:**
```
Resource Optimization Report:

Over-Provisioned Resources:
- Frontend deployment: Allocated 200m CPU, using avg 50m (75% waste)
  Recommendation: Reduce limits to 100m, requests to 50m
  Estimated savings: $15/month

- Backend memory: Allocated 512Mi, using avg 256Mi (50% waste)
  Recommendation: Reduce limits to 384Mi, requests to 256Mi

Under-Provisioned Resources:
- Backend CPU: Throttling 15% of time
  Recommendation: Increase limits from 500m to 800m
  Cost impact: +$8/month

HPA Tuning:
- Backend HPA triggers at 70% CPU, avg load is 65%
  Recommendation: Reduce threshold to 60% for proactive scaling

Network Optimization:
- ClusterIP sufficient for backend (currently LoadBalancer)
  Estimated savings: $20/month
```

#### 3. Capacity Planning

**Command:**
```bash
kagent "recommend resource limits based on actual usage"
```

**Expected Capacity Recommendations:**
```
Capacity Planning Report (based on 7-day analysis):

Backend Deployment:
Current Configuration:
  Requests: 200m CPU, 256Mi memory
  Limits: 500m CPU, 512Mi memory

Actual Usage (P95):
  CPU: 350m (70% of limit)
  Memory: 384Mi (75% of limit)

Recommended Configuration:
  Requests: 300m CPU, 320Mi memory
  Limits: 600m CPU, 512Mi memory
  Reasoning:
    - P95 CPU usage at 350m, add 250m headroom
    - P95 memory stable, current limit sufficient
    - Prevents CPU throttling during traffic spikes

Frontend Deployment:
Current: 100m/200m CPU, 128Mi/256Mi memory
Actual P95: 75m CPU, 96Mi memory
Recommended: 80m/150m CPU, 100Mi/200Mi memory

Cost Impact:
- Backend: +$5/month (improved performance worth it)
- Frontend: -$10/month (reduced waste)
- Net savings: -$5/month with better performance
```

### When to Use Kagent

✅ **Use Kagent when:**
- Planning capacity for new features
- Investigating performance issues
- Right-sizing resource allocations
- Reducing cloud costs
- Annual infrastructure reviews

❌ **Don't use Kagent for:**
- Real-time incident response (use monitoring tools)
- Automated resource changes (requires validation)
- Short-term metrics (needs 7+ days data)

### Best Practices

1. **Collect metrics for 7+ days** before optimization
2. **Validate recommendations in staging** first
3. **Document decisions in ADRs**
4. **Re-analyze quarterly** to catch drift
5. **Combine with cost monitoring tools**

---

## Comparison Matrix

| Feature | Docker AI (Gordon) | kubectl-ai | Kagent |
|---------|-------------------|------------|--------|
| **Focus** | Container optimization | Kubernetes operations | Cluster health & capacity |
| **Use Phase** | Build time | Runtime operations | Planning & optimization |
| **Skill Level** | Beginner-friendly | Intermediate | Advanced |
| **Automation** | Suggestions only | Command generation | Analysis & recommendations |
| **Cost Impact** | Build optimization | Operational efficiency | Resource right-sizing |
| **Best For** | Dockerfile review | Learning kubectl | Cost reduction |

---

## Integration Workflow

### Development Phase
1. **Docker AI:** Optimize Dockerfiles before committing
2. **Build:** Create optimized images
3. **Test:** Validate functionality unchanged

### Deployment Phase
4. **kubectl-ai:** Generate deployment commands (review first)
5. **Deploy:** Apply to cluster
6. **Monitor:** Collect metrics for 7+ days

### Optimization Phase
7. **Kagent:** Analyze cluster health and usage
8. **Right-size:** Apply resource recommendations
9. **Document:** Create ADR for significant changes

---

## Safety Guidelines

### Never Auto-Apply AI Suggestions

```bash
# ❌ DANGEROUS - Don't do this
docker ai "fix Dockerfile" | bash

# ✅ SAFE - Review and validate
docker ai "suggest Dockerfile improvements" > suggestions.txt
# Review suggestions.txt
# Apply manually after validation
```

### Always Test Before Production

```bash
# 1. Test in development
docker build -f Dockerfile.optimized .
docker run --rm optimized-image npm test

# 2. Deploy to staging
kubectl apply -f optimized-deployment.yaml --dry-run=client
kubectl apply -f optimized-deployment.yaml -n staging

# 3. Monitor for issues
kubectl logs -n staging -l app=myapp --tail=100

# 4. Only then deploy to production
```

### Document AI-Driven Changes

Create ADR for significant changes:
```markdown
# ADR-XXX: Optimize Backend Dockerfile Based on Docker AI Analysis

## Context
Docker AI suggested reducing image size from 1.2GB to 200MB using multi-stage builds.

## Decision
Implement multi-stage build with python:3.13-slim base.

## Consequences
- Positive: 83% image size reduction, faster deployments
- Negative: Slightly more complex Dockerfile
- Validated: All tests pass, no functionality change
```

---

## Troubleshooting

### Docker AI Not Responding
```bash
# Check Docker Desktop is running
docker ps

# Restart Docker Desktop
# GUI: Docker Desktop > Restart

# Check AI service status
docker info | grep ai
```

### kubectl-ai Commands Fail
```bash
# Verify kubectl context
kubectl config current-context

# Check cluster connection
kubectl cluster-info

# Review suggested command before running
kubectl-ai "scale deployment" --dry-run
```

### Kagent Analysis Incomplete
```bash
# Ensure metrics-server running
kubectl get deployment metrics-server -n kube-system

# Collect sufficient metrics (7+ days)
kubectl top pods  # Should show CPU/Memory usage

# Check Kagent has permissions
kubectl auth can-i get pods --all-namespaces
```

---

## References

- [Docker AI Documentation](https://docs.docker.com/desktop/ai/)
- [kubectl-ai GitHub](https://github.com/sozercan/kubectl-ai)
- [Kagent Documentation](https://github.com/kagent/kagent)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)

---

**Last Updated:** 2025-12-26
**Document Version:** 1.0.0
**Maintained By:** Evolved Todo Team
