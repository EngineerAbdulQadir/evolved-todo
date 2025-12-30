# AIOps Workflow Guide

**Task:** T116-T118 - AIOps workflow documentation
**Phase:** Phase 4 - Kubernetes Deployment
**Version:** 1.0.0

## Overview

This guide demonstrates when and how to use AI-powered operations (AIOps) tools throughout the development lifecycle. It provides a systematic workflow for integrating Docker AI (Gordon), kubectl-ai, and Kagent into your daily operations.

---

## AIOps Tool Selection Matrix

| Phase | Tool | Primary Use Case | Frequency |
|-------|------|------------------|-----------|
| **Build Time** | Docker AI (Gordon) | Dockerfile optimization, security scanning | Per commit / PR review |
| **Deploy Time** | kubectl-ai | Learning kubectl, exploring operations | Daily (learning phase) |
| **Runtime** | Kagent | Cluster health, resource optimization | Weekly / Monthly |
| **Incident** | kubectl-ai | Quick troubleshooting commands | As needed |
| **Planning** | Kagent | Capacity planning, cost optimization | Quarterly |

---

## When to Use Each Tool

### Docker AI (Gordon)

**Use During:**
- ✅ Writing new Dockerfiles
- ✅ Code review (PR approval process)
- ✅ Before production deployments
- ✅ Security audits
- ✅ Image size optimization sprints

**Don't Use For:**
- ❌ Automated CI/CD pipelines (requires human review)
- ❌ Real-time deployments (too slow)
- ❌ Emergency hotfixes (no time for optimization)

**Example Workflow:**
```bash
# Step 1: Developer writes Dockerfile
vim backend/Dockerfile

# Step 2: Run Docker AI optimization check
docker ai "optimize backend/Dockerfile for size and security"

# Step 3: Review suggestions, apply valid ones
# (Manual review required - see validation section)

# Step 4: Rebuild and test
docker build -t backend:optimized .
docker run --rm backend:optimized npm test

# Step 5: Run security scan
docker ai "analyze security issues in backend:optimized"

# Step 6: If passing, commit changes
git add backend/Dockerfile
git commit -m "Optimize Dockerfile based on Docker AI suggestions"
```

### kubectl-ai

**Use During:**
- ✅ Learning Kubernetes (first 3-6 months)
- ✅ Exploring new cluster features
- ✅ Quick troubleshooting sessions
- ✅ Generating kubectl command templates

**Don't Use For:**
- ❌ Production automation (use tested scripts)
- ❌ CI/CD pipelines (non-deterministic)
- ❌ Critical operations (need exact control)

**Example Workflow:**
```bash
# Step 1: Natural language query
kubectl-ai "show me all failing pods"

# Step 2: Review generated command
# Example output: kubectl get pods --all-namespaces | grep -v Running

# Step 3: Validate command is safe
# (Check for destructive operations like delete, scale down)

# Step 4: Execute manually (copy/paste)
kubectl get pods --all-namespaces | grep -v Running

# Step 5: Save useful commands to runbook
echo "kubectl get pods --all-namespaces | grep -v Running" >> runbooks/troubleshooting.md
```

### Kagent

**Use During:**
- ✅ Weekly operational reviews
- ✅ Monthly cost optimization
- ✅ Quarterly capacity planning
- ✅ Annual infrastructure audits
- ✅ Post-incident analysis

**Don't Use For:**
- ❌ Real-time monitoring (use Prometheus)
- ❌ Immediate incident response (too slow)
- ❌ Short-term metrics (needs 7+ days data)

**Example Workflow:**
```bash
# Step 1: Collect metrics for 7+ days
kubectl top pods > metrics/$(date +%Y%m%d).txt

# Step 2: Run Kagent analysis
kagent "analyze cluster health and recommend optimizations"

# Step 3: Review recommendations with team
# (Schedule 30min meeting to discuss findings)

# Step 4: Prioritize recommendations
# High impact + low effort = do first
# High impact + high effort = plan sprint
# Low impact = backlog

# Step 5: Implement in staging first
helm upgrade myapp --set resources.backend.requests.cpu=50m

# Step 6: Monitor for 48 hours
kubectl top pods -l app=myapp --watch

# Step 7: If stable, promote to production
helm upgrade myapp -f values-prod.yaml

# Step 8: Document in ADR
# Create ADR-XXX-optimize-backend-resources.md
```

---

## Integrated AIOps Workflow

### Development Phase (New Feature)

```
1. Write Dockerfile
   ├─> docker ai "optimize for size and security"
   ├─> Apply validated suggestions
   └─> Build and test locally

2. Write Kubernetes manifests
   ├─> kubectl-ai "create deployment with 3 replicas"
   ├─> Review generated YAML
   └─> Customize and commit

3. Create Helm chart (if not exists)
   ├─> helm create myapp
   ├─> Customize templates
   └─> Validate: helm lint myapp
```

### Build & Test Phase

```
4. Security scanning
   ├─> docker ai "analyze security in myapp:v1.0.0"
   ├─> Review CVE reports
   ├─> Fix high/critical vulnerabilities
   └─> Document in security.md

5. Image optimization validation
   ├─> Compare image sizes (before/after)
   ├─> Verify functionality unchanged
   └─> Run integration tests
```

### Deployment Phase

```
6. Deploy to staging
   ├─> kubectl-ai "deploy myapp to staging namespace" (learn command)
   ├─> Actually use: helm install myapp ./charts/myapp -n staging
   └─> Verify: kubectl get pods -n staging

7. Collect baseline metrics (7 days minimum)
   ├─> kubectl top pods -n staging > metrics/baseline.txt
   ├─> Set up monitoring alerts
   └─> Document expected resource usage
```

### Operations Phase

```
8. Weekly health check
   ├─> kagent "analyze staging cluster health"
   ├─> Review warnings and issues
   └─> Create tickets for action items

9. Monthly optimization
   ├─> kagent "recommend resource optimizations"
   ├─> Calculate cost impact
   ├─> Prioritize high-ROI changes
   └─> Implement in staging, then prod

10. Quarterly capacity planning
    ├─> kagent "project capacity needs for 6 months"
    ├─> Review with architecture team
    ├─> Budget for infrastructure growth
    └─> Schedule upgrades if needed
```

---

## Validation Workflow

**CRITICAL:** Never blindly apply AI suggestions. Always validate.

### Validating Docker AI Suggestions

```bash
# 1. Create test branch
git checkout -b optimize-dockerfile

# 2. Apply Docker AI suggestions to Dockerfile.optimized
# (Manual edit with human judgment)

# 3. Build both versions
docker build -t myapp:current -f Dockerfile .
docker build -t myapp:optimized -f Dockerfile.optimized .

# 4. Compare image sizes
docker images | grep myapp
# Verify optimized is smaller

# 5. Compare functionality
docker run --rm myapp:current npm test
docker run --rm myapp:optimized npm test
# Both should pass identical tests

# 6. Compare startup time
time docker run --rm myapp:current node --version
time docker run --rm myapp:optimized node --version
# Optimized should be similar or faster

# 7. Security scan comparison
docker scout cves myapp:current > current-cves.txt
docker scout cves myapp:optimized > optimized-cves.txt
diff current-cves.txt optimized-cves.txt
# Optimized should have fewer CVEs

# 8. If all validations pass, merge
git add Dockerfile.optimized
git commit -m "Optimize Dockerfile (Docker AI suggestions validated)"
git push origin optimize-dockerfile
# Create PR for team review
```

### Validating kubectl-ai Commands

```bash
# 1. Generate command with kubectl-ai
kubectl-ai "scale backend to handle 2x traffic"
# Output: kubectl scale deployment backend --replicas=6

# 2. Check current state
kubectl get deployment backend
# Current: 3 replicas

# 3. Validate command is safe
# ✅ scale is non-destructive (reversible)
# ✅ increasing replicas (not deleting)
# ✅ targeting correct deployment

# 4. Dry-run first (if command supports it)
kubectl scale deployment backend --replicas=6 --dry-run=client
# No errors = safe to proceed

# 5. Execute in staging
kubectl scale deployment backend --replicas=6 -n staging

# 6. Monitor impact
kubectl get pods -n staging -w
kubectl top pods -n staging -l app=backend

# 7. If successful, apply to prod
kubectl scale deployment backend --replicas=6 -n production

# 8. Document in runbook
echo "# Scale backend for 2x traffic" >> runbooks/scaling.md
echo "kubectl scale deployment backend --replicas=6" >> runbooks/scaling.md
```

### Validating Kagent Recommendations

```bash
# 1. Kagent recommends: Reduce frontend CPU from 200m to 100m

# 2. Review recommendation rationale
# - Current: 200m requested, 45m actual usage
# - Waste: 77.5% over-provisioned
# - Recommendation: 100m (2x actual + headroom)

# 3. Check historical data (7+ days)
kubectl top pods -l app=frontend | tee -a metrics-history.txt
# Verify 45m is consistent, not a temporary dip

# 4. Test in staging first
helm upgrade myapp --set resources.frontend.requests.cpu=100m -n staging

# 5. Monitor for 48 hours
watch kubectl top pods -n staging -l app=frontend
# Ensure no CPU throttling occurs

# 6. Load test (if applicable)
kubectl run load-test --rm -it --image=busybox -- sh -c "while true; do wget -q -O- http://frontend; done"
# Monitor CPU usage under load

# 7. Check for throttling indicators
kubectl get events -n staging | grep -i throttl
# No throttling events = safe to proceed

# 8. If validation passes, promote to prod
helm upgrade myapp --set resources.frontend.requests.cpu=100m -n production

# 9. Document in ADR
# ADR-XXX: Reduce frontend CPU based on Kagent analysis
# - Validated in staging for 48h
# - No performance degradation observed
# - Saves $12/month in cloud costs
```

---

## Documenting AI-Suggested Changes in ADRs

When implementing significant AI suggestions, document in Architecture Decision Records:

### ADR Template for AI-Driven Changes

```markdown
# ADR-XXX: [Title - e.g., Optimize Backend Dockerfile Using Docker AI]

## Status
Proposed / Accepted / Implemented / Deprecated

## Context
- **Tool Used:** Docker AI (Gordon) / kubectl-ai / Kagent
- **Analysis Date:** 2025-12-26
- **Current State:** [Describe problem AI identified]
- **AI Recommendation:** [Quote the suggestion]

## AI Analysis Summary
[Paste relevant AI output]

Example:
```
Docker AI identified 3 optimization opportunities:
1. Use multi-stage build (saves 800MB)
2. Run as non-root user (security improvement)
3. Pin base image version (reproducibility)
```

## Validation Performed
- [ ] Tested in local development
- [ ] Deployed to staging environment
- [ ] Monitored for 48 hours minimum
- [ ] Load tested (if applicable)
- [ ] Security scanned
- [ ] Reviewed by team
- [ ] Documented impact metrics

## Decision
[Accept / Reject / Modify the AI suggestion]

We decided to accept recommendations #1 and #2, but reject #3 because [reason].

## Implementation Details
[What changes were made]

```dockerfile
# Before (1.2GB):
FROM node:18
COPY . .
RUN npm install
CMD ["npm", "start"]

# After (200MB - Docker AI optimized):
FROM node:18-alpine AS builder
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine
RUN addgroup -S appuser && adduser -S appuser -G appuser
USER appuser
COPY --from=builder /app/node_modules ./node_modules
COPY . .
CMD ["npm", "start"]
```

## Consequences

### Positive
- Image size reduced 83% (1.2GB → 200MB)
- Deployment time reduced from 90s to 15s
- Security improved (non-root user)
- Estimated cost savings: $15/month on cloud storage

### Negative
- Dockerfile complexity increased
- Build time increased by 10s (multi-stage build)

### Neutral
- Team needs brief training on multi-stage builds

## Validation Results

### Testing Summary
```
Functionality Tests: ✅ All 150 tests passed
Performance Tests:  ✅ Response time unchanged (45ms avg)
Security Scan:      ✅ 12 fewer vulnerabilities
Load Test:          ✅ Handles 1000 req/s (same as before)
```

### Metrics Before/After
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Image Size | 1.2GB | 200MB | 83% reduction |
| Deploy Time | 90s | 15s | 83% faster |
| Vulnerabilities | 31 | 19 | 39% reduction |
| Monthly Cost | $45 | $30 | $15 savings |

## Compliance
- [ ] Security review completed
- [ ] Performance benchmarks passed
- [ ] Documentation updated
- [ ] Team notified of changes

## References
- Docker AI analysis output: [Link to saved output]
- Validation test results: [Link to test report]
- Related ADRs: ADR-001 (Container Security Policy)

## Notes
[Any additional context, gotchas, or lessons learned]

Example: "Docker AI suggested using `distroless` base image, but we chose Alpine instead because our team has more experience with it and troubleshooting is easier."

---

**Author:** [Your name]
**Date:** 2025-12-26
**Reviewers:** [Team members who reviewed]
**Last Updated:** 2025-12-26
```

---

## Before/After Examples

### Example 1: Dockerfile Optimization

**Before (No AI Assistance):**
```dockerfile
FROM python:3.13
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]

# Issues:
# - Large base image (1GB+)
# - Running as root
# - No health check
# - Build cache not optimized
```

**After (Docker AI Suggestions Applied):**
```dockerfile
# Multi-stage build (Docker AI recommendation #1)
FROM python:3.13-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.13-slim
WORKDIR /app

# Non-root user (Docker AI recommendation #2)
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 appuser

# Copy only runtime dependencies
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --chown=appuser:appuser . .

USER appuser
EXPOSE 8000

# Health check (Docker AI recommendation #3)
HEALTHCHECK --interval=30s --timeout=5s \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

CMD ["python", "app.py"]

# Results:
# ✅ Image size: 1.2GB → 250MB (79% reduction)
# ✅ Security: Now runs as non-root
# ✅ Reliability: Health checks enabled
# ✅ Build time: Optimized layer caching
```

### Example 2: Resource Optimization

**Before (No Kagent Analysis):**
```yaml
# Guessed resource limits
resources:
  requests:
    cpu: 500m      # "Should be enough"
    memory: 1Gi    # "Better safe than sorry"
  limits:
    cpu: 2000m     # "Just in case"
    memory: 4Gi    # "Maximum we can afford"

# Issues:
# - Massively over-provisioned (90% waste)
# - High cloud costs ($80/month per pod)
# - Poor cluster utilization
```

**After (Kagent Recommendations Applied):**
```yaml
# Based on 30-day actual usage analysis
resources:
  requests:
    cpu: 100m      # 2x P95 usage (50m observed)
    memory: 256Mi  # 1.5x P95 usage (170Mi observed)
  limits:
    cpu: 300m      # 6x P95 for spike handling
    memory: 512Mi  # 3x P95 for safety margin

# Results:
# ✅ Cost: $80/month → $15/month (81% reduction)
# ✅ Performance: No degradation observed
# ✅ Cluster utilization: 15% → 65%
# ✅ Can run 5x more pods on same nodes
```

### Example 3: Troubleshooting Workflow

**Before (Manual kubectl):**
```bash
# Developer struggling to find issue (30 minutes)
kubectl get pods
kubectl describe pod myapp-xyz
kubectl logs myapp-xyz
kubectl logs myapp-xyz --previous
kubectl get events
# ... 20 more commands ...
# Finally found: ImagePullBackOff due to typo in image tag
```

**After (kubectl-ai Assisted):**
```bash
# Developer asks natural language question
kubectl-ai "why is my pod failing to start"

# AI suggests diagnostic sequence:
kubectl get pods | grep -v Running
kubectl describe pod myapp-xyz | grep -A 10 "Events:"
kubectl logs myapp-xyz --tail=50

# Issue found in 2 minutes:
# Events: Failed to pull image "myapp:v1.0.0" → should be "myapp:v1.0"

# Developer fixes and documents
echo "Common issue: Always verify image tag exists" >> runbooks/troubleshooting.md
```

---

## Troubleshooting AI Tools

### Docker AI Not Working

```bash
# Check Docker Desktop version
docker --version
# Need 4.53+ for Docker AI

# Verify Docker AI enabled
docker ai --help
# If error, restart Docker Desktop

# Check network connectivity
curl -I https://api.docker.com
# AI requires internet connection
```

### kubectl-ai Commands Failing

```bash
# Verify kubectl context
kubectl config current-context

# Check API server connectivity
kubectl cluster-info

# Update kubectl-ai plugin
kubectl krew upgrade ai

# Fall back to manual kubectl
kubectl get pods  # Always works
```

### Kagent Analysis Incomplete

```bash
# Ensure metrics-server running
kubectl get deployment metrics-server -n kube-system

# Enable if missing
minikube addons enable metrics-server

# Verify metrics available
kubectl top nodes
kubectl top pods

# Wait for sufficient data (7+ days recommended)
```

---

## Best Practices Summary

### ✅ Do This

1. **Always validate AI suggestions** before applying
2. **Test in development/staging** before production
3. **Document significant changes** in ADRs
4. **Monitor impact** after implementing changes
5. **Combine AI tools** with human expertise
6. **Save useful commands** to runbooks
7. **Review AI suggestions with team** before major changes

### ❌ Don't Do This

1. **Never auto-apply** AI suggestions without review
2. **Don't use in CI/CD** without extensive testing
3. **Don't trust blindly** - AI can make mistakes
4. **Don't skip validation** steps to save time
5. **Don't use for critical production operations** without approval
6. **Don't ignore team expertise** in favor of AI
7. **Don't forget to document** what you learned

---

## Measuring Success

### Metrics to Track

**Docker AI Impact:**
- Image size reduction (target: >50%)
- Build time change (acceptable: ±20%)
- Security vulnerabilities fixed (target: 100% critical/high)
- Deployment time improvement (target: >30%)

**kubectl-ai Impact:**
- Time saved on kubectl learning (estimated hours)
- Commands discovered and saved to runbooks
- Troubleshooting time reduction (target: >40%)

**Kagent Impact:**
- Cloud cost reduction (target: >20%)
- Resource utilization improvement (target: <80% waste)
- Capacity planning accuracy (prevent outages)
- Cluster health score improvement

### Example Dashboard

```markdown
## AIOps Impact Report - Q1 2025

### Docker AI
- Images optimized: 12
- Average size reduction: 68%
- Vulnerabilities fixed: 47 high/critical
- Estimated cost savings: $180/month

### kubectl-ai
- Commands learned: 35
- Runbooks created: 8
- Avg troubleshooting time: 15min → 4min (73% faster)

### Kagent
- Clusters analyzed: 3
- Resources right-sized: 24 deployments
- Cost reduction: $540/month (32%)
- Prevented capacity issues: 2 (would have caused outages)

**Total Value:** $720/month savings + 15hrs/week time saved
**ROI:** 450% (AI tool costs vs. savings + productivity gains)
```

---

## References

- [Docker AI Documentation](https://docs.docker.com/desktop/ai/)
- [kubectl-ai GitHub](https://github.com/sozercan/kubectl-ai)
- [Kagent Documentation](https://github.com/kagent/kagent)
- [AIOps Best Practices](https://kubernetes.io/docs/concepts/cluster-administration/manage-deployment/)

---

**Last Updated:** 2025-12-26
**Document Version:** 1.0.0
**Maintained By:** Evolved Todo Team
