# Helm Chart Deployment Guide

**Task:** T102 - Helm deployment documentation
**Phase:** Phase 4 - Kubernetes Deployment
**Version:** 1.0.0

## Overview

This guide covers deploying the Evolved Todo application to Kubernetes using Helm charts. The Helm chart templates all Kubernetes resources (Deployments, Services, HPAs, Secrets) and supports environment-specific configurations.

---

## Prerequisites

- **Kubernetes Cluster:** Minikube 1.28+ (local) or production cluster
- **Helm:** Version 3.x installed (`helm version`)
- **kubectl:** Configured to access your cluster
- **Docker Images:** Backend and frontend images loaded into cluster
- **Database:** Neon Serverless PostgreSQL connection string
- **API Keys:** OpenAI API key for AI agent

### Verify Prerequisites

```bash
# Check Helm version
helm version

# Check Kubernetes cluster connection
kubectl cluster-info

# Check Minikube status (local only)
minikube status

# Load Docker images into Minikube (local only)
minikube image load evolved-todo-backend:1.0.0
minikube image load evolved-todo-frontend:1.0.0
```

---

## Helm Chart Structure

```
helm/evolved-todo/
├── Chart.yaml                          # Chart metadata
├── values.yaml                         # Production defaults
├── values-dev.yaml                     # Development overrides
├── values-test.yaml                    # Test secrets (gitignored)
└── templates/
    ├── _helpers.tpl                    # Template functions
    ├── secrets.yaml                    # Secrets template
    ├── tests/
    │   └── test-connection.yaml        # Helm connectivity test
    ├── backend/
    │   ├── deployment.yaml             # Backend Deployment
    │   ├── service.yaml                # Backend Service (ClusterIP/LoadBalancer)
    │   └── hpa.yaml                    # Backend HPA (conditional)
    └── frontend/
        ├── deployment.yaml             # Frontend Deployment
        ├── service.yaml                # Frontend Service (LoadBalancer)
        └── hpa.yaml                    # Frontend HPA (conditional)
```

---

## Installation

### 1. Prepare Secrets

Create a `values-secrets.yaml` file (DO NOT commit to git):

```yaml
secrets:
  DATABASE_URL: "postgresql+asyncpg://user:password@host:5432/dbname?ssl=require"
  OPENAI_API_KEY: "sk-proj-your-api-key-here"
  BETTER_AUTH_SECRET: "your-32-character-secret-here"
```

### 2. Install Helm Chart

#### Development Environment (Minikube)

```bash
# Install with dev values
helm install evolved-todo ./helm/evolved-todo \
  -f ./helm/evolved-todo/values-dev.yaml \
  -f ./helm/evolved-todo/values-secrets.yaml \
  --wait \
  --timeout=5m

# Or use --set for secrets
helm install evolved-todo ./helm/evolved-todo \
  -f ./helm/evolved-todo/values-dev.yaml \
  --set secrets.DATABASE_URL="${DATABASE_URL}" \
  --set secrets.OPENAI_API_KEY="${OPENAI_API_KEY}" \
  --set secrets.BETTER_AUTH_SECRET="${BETTER_AUTH_SECRET}" \
  --wait \
  --timeout=5m
```

#### Production Environment

```bash
# Install with production values
helm install evolved-todo ./helm/evolved-todo \
  -f ./helm/evolved-todo/values.yaml \
  -f ./helm/evolved-todo/values-secrets.yaml \
  --wait \
  --timeout=5m
```

### 3. Verify Installation

```bash
# Check Helm release status
helm status evolved-todo

# Check all resources created
kubectl get all -l app.kubernetes.io/instance=evolved-todo

# Wait for pods to be ready
kubectl wait --for=condition=Ready pod -l app.kubernetes.io/instance=evolved-todo --timeout=90s

# Check pod logs
kubectl logs -l app.kubernetes.io/component=backend --tail=50
kubectl logs -l app.kubernetes.io/component=frontend --tail=50
```

### 4. Access Services (Minikube)

```bash
# Start Minikube tunnel (in separate terminal - KEEP RUNNING)
minikube tunnel

# Access services
# Frontend: http://127.0.0.1
# Backend:  http://127.0.0.1:8000

# Verify health endpoints
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1/api/health
```

---

## Upgrade

### Modify Configuration

Update `values-dev.yaml` or `values.yaml` with desired changes:

```yaml
# Example: Increase backend replicas
replicaCount:
  backend: 3
  frontend: 2
```

### Apply Upgrade

```bash
# Upgrade with modified values
helm upgrade evolved-todo ./helm/evolved-todo \
  -f ./helm/evolved-todo/values-dev.yaml \
  -f ./helm/evolved-todo/values-secrets.yaml \
  --wait

# Check upgrade status
helm status evolved-todo

# Verify rolling update completed
kubectl get deployments -l app.kubernetes.io/instance=evolved-todo
kubectl get pods -l app.kubernetes.io/instance=evolved-todo
```

### Verify Zero Downtime

```bash
# Monitor rollout status
kubectl rollout status deployment/evolved-todo-backend
kubectl rollout status deployment/evolved-todo-frontend

# Test application during upgrade
while true; do curl -s http://127.0.0.1:8000/api/health | grep -o "healthy"; sleep 1; done
```

---

## Rollback

### View Release History

```bash
# List all revisions
helm history evolved-todo

# Output:
# REVISION  UPDATED                   STATUS      CHART               DESCRIPTION
# 1         Fri Dec 26 18:46:24 2025  superseded  evolved-todo-1.0.0  Install complete
# 2         Fri Dec 26 18:51:59 2025  superseded  evolved-todo-1.0.0  Upgrade complete
# 3         Fri Dec 26 18:55:55 2025  deployed    evolved-todo-1.0.0  Rollback to 1
```

### Rollback to Previous Revision

```bash
# Rollback to previous revision
helm rollback evolved-todo --wait

# Or rollback to specific revision
helm rollback evolved-todo 1 --wait

# Verify rollback succeeded
helm status evolved-todo
kubectl get deployments -l app.kubernetes.io/instance=evolved-todo
```

---

## Helm Tests

### Run Connectivity Tests

```bash
# Run Helm test suite (verifies frontend→backend connectivity)
helm test evolved-todo

# Output:
# TEST SUITE:     evolved-todo-test-connection
# Last Started:   Fri Dec 26 19:08:18 2025
# Last Completed: Fri Dec 26 19:08:22 2025
# Phase:          Succeeded
```

The test pod verifies:
- Frontend health endpoint accessible (`/api/health`)
- Backend health endpoint accessible (`/api/health`)
- Inter-service connectivity within cluster

---

## Values Customization

### Production Values (`values.yaml`)

```yaml
# Replica counts (with HPA enabled, these are initial counts)
replicaCount:
  backend: 2
  frontend: 2

# Autoscaling (enabled in production)
autoscaling:
  backend:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
  frontend:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 80

# Service types (LoadBalancer for cloud, NodePort for on-prem)
service:
  backend:
    type: LoadBalancer
    port: 8000
  frontend:
    type: LoadBalancer
    port: 80
    targetPort: 3000

# Resource limits
resources:
  backend:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
  frontend:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 200m
      memory: 256Mi
```

### Development Values (`values-dev.yaml`)

```yaml
# Single replica (no autoscaling)
replicaCount:
  backend: 1
  frontend: 1

# Autoscaling disabled
autoscaling:
  backend:
    enabled: false
  frontend:
    enabled: false

# Use local images (Never pull from registry)
image:
  backend:
    pullPolicy: Never
  frontend:
    pullPolicy: Never

# Lower resource limits for local dev
resources:
  backend:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 300m
      memory: 256Mi
  frontend:
    requests:
      cpu: 50m
      memory: 64Mi
    limits:
      cpu: 150m
      memory: 128Mi
```

### Custom Environment Variables

```yaml
# Custom backend environment
env:
  backend:
    ENVIRONMENT: "staging"
    DEBUG: "true"
    FRONTEND_URL: "https://staging.example.com"

# Custom frontend environment
  frontend:
    NEXT_PUBLIC_BACKEND_URL: "https://api-staging.example.com"
    BETTER_AUTH_URL: "https://staging.example.com"
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -l app.kubernetes.io/instance=evolved-todo

# Describe pod for events
kubectl describe pod <pod-name>

# Check pod logs
kubectl logs <pod-name>

# Common issues:
# - Image pull errors: Ensure images loaded into Minikube (minikube image load)
# - Health check failures: Verify /api/health endpoint returns 200
# - Database connection: Check DATABASE_URL secret is correct
```

### Health Probes Failing

```bash
# Test health endpoints directly from within pod
kubectl exec <pod-name> -- curl -s http://localhost:8000/api/health  # Backend
kubectl exec <pod-name> -- curl -s http://localhost:3000/api/health  # Frontend

# Common issues:
# - Backend: Health endpoint is /api/health (not /health)
# - Frontend: Next.js may take 10-30s to start (startup probe allows 60s)
# - Database: Connection string must include ssl=require for Neon
```

### Services Not Accessible (Minikube)

```bash
# Check service status
kubectl get svc -l app.kubernetes.io/instance=evolved-todo

# If EXTERNAL-IP shows <pending>:
# - Start minikube tunnel in separate terminal: minikube tunnel
# - Keep tunnel running while accessing services
# - Frontend: http://127.0.0.1
# - Backend: http://127.0.0.1:8000

# Alternative: Use NodePort
kubectl port-forward svc/evolved-todo-frontend 3000:80
kubectl port-forward svc/evolved-todo-backend 8000:8000
```

### HPA Not Scaling

```bash
# Check HPA status
kubectl get hpa -l app.kubernetes.io/instance=evolved-todo

# Check metrics server (required for HPA)
kubectl get deployment metrics-server -n kube-system

# View HPA events
kubectl describe hpa evolved-todo-backend-hpa

# Common issues:
# - Metrics server not running: minikube addons enable metrics-server
# - Resource requests not set: HPA requires requests.cpu defined
# - Low traffic: Generate load to trigger scaling
```

### Helm Install/Upgrade Failures

```bash
# Check Helm release status
helm status evolved-todo

# View Helm release history
helm history evolved-todo

# If stuck in "pending-upgrade" state:
helm rollback evolved-todo <previous-revision>

# Or uninstall and reinstall
helm uninstall evolved-todo
helm install evolved-todo ./helm/evolved-todo -f values-dev.yaml

# Validate chart before installing
helm lint ./helm/evolved-todo
helm install --dry-run --debug evolved-todo ./helm/evolved-todo -f values-dev.yaml
```

### Secrets Not Found

```bash
# Check if secrets created
kubectl get secrets | grep evolved-todo

# Describe secret (shows keys but not values)
kubectl describe secret evolved-todo-secrets

# Verify secret values (base64 encoded)
kubectl get secret evolved-todo-secrets -o yaml

# Common issues:
# - Secrets not provided during install: Use --set or -f values-secrets.yaml
# - Wrong secret keys: Must be DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET
# - Secrets not base64 encoded in template: Check templates/secrets.yaml uses {{ .Values.secrets.* | b64enc }}
```

### Rolling Update Stuck

```bash
# Check deployment rollout status
kubectl rollout status deployment/evolved-todo-backend

# View deployment events
kubectl describe deployment/evolved-todo-backend

# Check pod readiness
kubectl get pods -l app.kubernetes.io/component=backend -o wide

# If update stuck:
# - Check new pods failing readiness probe
# - Verify resource limits not exceeded
# - Rollback if needed: helm rollback evolved-todo
```

---

## Cleanup

### Uninstall Helm Release

```bash
# Uninstall release (deletes all resources)
helm uninstall evolved-todo

# Verify all resources deleted
kubectl get all -l app.kubernetes.io/instance=evolved-todo

# Secrets are also deleted automatically
kubectl get secrets | grep evolved-todo
```

### Delete Persistent Data

```bash
# If using PersistentVolumeClaims (not in this deployment)
kubectl delete pvc -l app.kubernetes.io/instance=evolved-todo
```

---

## Security Best Practices

### Secrets Management

1. **Never commit secrets to git:**
   ```bash
   # Add to .gitignore
   echo "helm/evolved-todo/values-secrets.yaml" >> .gitignore
   echo "helm/evolved-todo/values-test.yaml" >> .gitignore
   ```

2. **Use external secrets management** (production):
   - Kubernetes External Secrets Operator
   - HashiCorp Vault
   - AWS Secrets Manager / Azure Key Vault / GCP Secret Manager

3. **Rotate secrets regularly:**
   ```bash
   # Update secrets
   helm upgrade evolved-todo ./helm/evolved-todo \
     --set secrets.OPENAI_API_KEY="new-key" \
     --reuse-values

   # Restart pods to load new secrets
   kubectl rollout restart deployment/evolved-todo-backend
   kubectl rollout restart deployment/evolved-todo-frontend
   ```

### Network Security

1. **Backend should be ClusterIP** (internal only in production)
2. **Frontend should be behind Ingress** (not direct LoadBalancer)
3. **Use NetworkPolicies** to restrict pod-to-pod communication
4. **Enable TLS** for external services

---

## Monitoring and Observability

### Check Application Logs

```bash
# Stream backend logs
kubectl logs -f -l app.kubernetes.io/component=backend

# Stream frontend logs
kubectl logs -f -l app.kubernetes.io/component=frontend

# View logs from all pods
kubectl logs -l app.kubernetes.io/instance=evolved-todo --all-containers=true
```

### Monitor Resource Usage

```bash
# Check pod resource usage
kubectl top pods -l app.kubernetes.io/instance=evolved-todo

# Check node resource usage
kubectl top nodes

# Check HPA metrics
kubectl get hpa evolved-todo-backend-hpa -o yaml
```

### Health Checks

```bash
# Backend health
curl http://127.0.0.1:8000/api/health

# Frontend health
curl http://127.0.0.1/api/health

# Expected response:
# Backend:  {"status":"healthy","api":"ok","database":"ok"}
# Frontend: {"status":"healthy","service":"evolved-todo-frontend"}
```

---

## Advanced Configuration

### Custom Image Tags

```bash
# Use custom image versions
helm upgrade evolved-todo ./helm/evolved-todo \
  --set image.backend.tag="v2.0.0" \
  --set image.frontend.tag="v2.0.0" \
  --reuse-values
```

### Resource Tuning

```bash
# Adjust resource limits based on actual usage
helm upgrade evolved-todo ./helm/evolved-todo \
  --set resources.backend.requests.cpu="300m" \
  --set resources.backend.limits.memory="768Mi" \
  --reuse-values
```

### Enable/Disable Autoscaling

```bash
# Disable autoscaling (use fixed replicas)
helm upgrade evolved-todo ./helm/evolved-todo \
  --set autoscaling.backend.enabled=false \
  --set replicaCount.backend=3 \
  --reuse-values
```

---

## References

- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Project Constitution](../../.specify/memory/constitution.md)
- [Phase 4 Specification](../../specs/004-phase4-k8s-deployment/spec.md)

---

**Last Updated:** 2025-12-26
**Document Version:** 1.0.0
**Maintained By:** Evolved Todo Team
