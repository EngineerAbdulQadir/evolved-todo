# Quickstart: Phase 4 - Local Kubernetes Deployment

**Feature**: Phase 4 - Local Kubernetes Deployment
**Date**: 2025-12-25
**Target**: Deploy Phase 3 AI Chatbot on local Minikube cluster

## Prerequisites

### Required Tools

1. **Docker Desktop 4.53+**
   - Includes Docker AI (Gordon) support
   - Download: https://www.docker.com/products/docker-desktop

2. **Minikube 1.32+**
   - Local Kubernetes cluster
   - Install: `curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-windows-amd64.exe`
   - Rename to `minikube.exe` and add to PATH

3. **kubectl 1.28+**
   - Kubernetes CLI
   - Install: `minikube kubectl -- version` (bundled with Minikube)

4. **Helm 3.x**
   - Kubernetes package manager
   - Download: https://helm.sh/docs/intro/install/

5. **kubectl-ai (Optional)**
   - Natural language Kubernetes operations
   - Install: Follow instructions at kubectl-ai repository

6. **Kagent (Optional)**
   - Cluster analysis and optimization
   - Install: Follow instructions at Kagent repository

### System Requirements

- **CPU**: 4 cores minimum (8 cores recommended)
- **RAM**: 8GB minimum (16GB recommended)
- **Disk**: 20GB free space
- **OS**: Windows 10/11 with WSL2, macOS 11+, or Linux

### Environment Variables

Create a `.env` file with:

```bash
DATABASE_URL=postgresql://user:pass@neon.tech/evolved_todo
OPENAI_API_KEY=sk-...
BETTER_AUTH_SECRET=your-secret-key
```

## Quick Deploy (30 Minutes)

### Step 1: Start Minikube (5 minutes)

```bash
# Start Minikube with Docker driver
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable metrics server for HPA
minikube addons enable metrics-server

# Enable LoadBalancer support
minikube tunnel  # Run in separate terminal, requires sudo/admin
```

**Verify**:
```bash
kubectl cluster-info
kubectl get nodes
```

Expected output: 1 node in Ready state

### Step 2: Build Docker Images (10 minutes)

```bash
# Navigate to project root
cd evolved-todo

# Build frontend image
docker build -t evolved-todo-frontend:1.0.0 ./frontend

# Build backend image
docker build -t evolved-todo-backend:1.0.0 ./backend

# Verify images
docker images | grep evolved-todo
```

Expected: 2 images <150MB (frontend), <200MB (backend)

### Step 3: Load Images to Minikube (2 minutes)

```bash
# Load images into Minikube's Docker daemon
minikube image load evolved-todo-frontend:1.0.0
minikube image load evolved-todo-backend:1.0.0

# Verify
minikube ssh "docker images | grep evolved-todo"
```

### Step 4: Create Kubernetes Secrets (1 minute)

```bash
# Source environment variables
source .env  # or `set -a; source .env; set +a` on Linux

# Create secrets
kubectl create secret generic evolved-todo-secrets \
  --from-literal=database-url="${DATABASE_URL}" \
  --from-literal=openai-api-key="${OPENAI_API_KEY}" \
  --from-literal=better-auth-secret="${BETTER_AUTH_SECRET}"

# Verify
kubectl get secrets evolved-todo-secrets
```

### Step 5: Deploy with Helm (5 minutes)

```bash
# Create secrets configuration file (DO NOT commit to git)
cat > helm/evolved-todo/values-secrets.yaml <<EOF
secrets:
  DATABASE_URL: "${DATABASE_URL}"
  OPENAI_API_KEY: "${OPENAI_API_KEY}"
  BETTER_AUTH_SECRET: "${BETTER_AUTH_SECRET}"
EOF

# Install Helm chart
helm install evolved-todo ./helm/evolved-todo \
  -f ./helm/evolved-todo/values-dev.yaml \
  -f ./helm/evolved-todo/values-secrets.yaml \
  --wait --timeout=5m

# Watch pods start
kubectl get pods -l app.kubernetes.io/instance=evolved-todo --watch
```

Expected: All pods reach Running state within 60 seconds

### Step 6: Access Application (2 minutes)

```bash
# Start minikube tunnel in separate terminal (required for LoadBalancer)
minikube tunnel

# Get service external IPs
kubectl get svc -l app.kubernetes.io/instance=evolved-todo
```

Access URLs:
- **Frontend**: http://127.0.0.1 (port 80)
- **Backend API**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs

### Step 7: Verify Deployment (5 minutes)

```bash
# Check pod status
kubectl get pods -l app.kubernetes.io/instance=evolved-todo

# Check services
kubectl get svc -l app.kubernetes.io/instance=evolved-todo

# Check HPA status
kubectl get hpa

# Test health checks
kubectl exec -it <backend-pod-name> -- curl localhost:8000/api/health

# View logs
kubectl logs -l app.kubernetes.io/component=backend --tail=50
```

## Alternative: Deploy Using Raw Manifests

If you prefer not to use Helm, you can render the templates and apply them manually:

```bash
# Step 1-3: Same as Quick Deploy above

# Step 4: Create secrets file
cat > helm/evolved-todo/values-secrets.yaml <<EOF
secrets:
  DATABASE_URL: "${DATABASE_URL}"
  OPENAI_API_KEY: "${OPENAI_API_KEY}"
  BETTER_AUTH_SECRET: "${BETTER_AUTH_SECRET}"
EOF

# Step 5: Render Helm templates to YAML
helm template evolved-todo ./helm/evolved-todo \
  -f ./helm/evolved-todo/values-dev.yaml \
  -f ./helm/evolved-todo/values-secrets.yaml \
  > k8s-manifests.yaml

# Step 6: Apply rendered manifests
kubectl apply -f k8s-manifests.yaml

# Step 7: Wait for rollout
kubectl rollout status deployment/evolved-todo-backend
kubectl rollout status deployment/evolved-todo-frontend
```

**Note:** Using Helm is recommended for easier upgrades and rollbacks.

## Testing Phase 4 Features

### Test 1: Container Health Checks

```bash
# Backend health
kubectl exec -it <backend-pod-name> -- curl http://localhost:8000/api/health

# Frontend health
kubectl exec -it <frontend-pod-name> -- curl http://localhost:3000/api/health
```

Expected: 200 OK with JSON status ({"status":"healthy","database":"ok"} for backend)

### Test 2: Horizontal Pod Autoscaling

```bash
# Generate load on backend
kubectl run -i --tty load-generator --rm --image=busybox --restart=Never -- /bin/sh
# Inside container:
while true; do wget -q -O- http://evolved-todo-backend:8000/api/health; done

# Watch HPA behavior (in another terminal)
kubectl get hpa evolved-todo-backend --watch

# Watch pods scale
kubectl get pods -l app.kubernetes.io/component=backend --watch
```

Expected: Backend pods scale from 2 to 10 as CPU increases above 70%

### Test 3: Stateless Architecture

```bash
# Start conversation in chatbot UI
# Get conversation_id from browser dev tools

# Delete one backend pod
kubectl delete pod <backend-pod-name>

# Continue conversation with same conversation_id
# Verify conversation history intact
```

Expected: Conversation history persists, new pod handles request

### Test 4: Zero-Downtime Updates

```bash
# Update backend image (build new version first)
kubectl set image deployment/evolved-todo-backend backend=evolved-todo-backend:1.0.1

# Watch rolling update
kubectl rollout status deployment/evolved-todo-backend

# Verify no dropped requests during update
# Test health endpoint during rollout:
while true; do curl -s http://127.0.0.1:8000/api/health; sleep 1; done
```

Expected: Rolling update with readiness gates, zero failed requests

### Test 5: All Phase 3 Features Work

Test all 10 Phase 3 task management features via chatbot:

1. Add task: "Add task to buy groceries"
2. List tasks: "Show all my tasks"
3. Search tasks: "Find tasks about groceries"
4. Update task: "Update task 1 description to buy organic groceries"
5. Complete task: "Mark task 1 as complete"
6. Delete task: "Delete task 1"
7. Priorities: "Add high priority task to finish report"
8. Tags: "Add task tagged work to review PR"
9. Due dates: "Add task to call mom due tomorrow"
10. Recurring tasks: "Add daily task to exercise"

Expected: All features work identically to Phase 3

## AIOps Tools Usage

### Docker AI (Gordon)

```bash
# Optimize Dockerfile
docker ai "optimize backend/Dockerfile for size and security"

# Security analysis
docker ai "analyze security vulnerabilities in evolved-todo-backend:1.0.0"

# Troubleshoot
docker ai "why does this container keep restarting"
```

### kubectl-ai

```bash
# Deploy with natural language
kubectl-ai "deploy the todo backend with 3 replicas"

# Troubleshoot
kubectl-ai "check why the backend pods are failing"
kubectl-ai "show me error logs from the last hour"

# Scale
kubectl-ai "scale the frontend to handle more load"
```

### Kagent

```bash
# Cluster health
kagent "analyze the cluster health and identify issues"

# Resource optimization
kagent "optimize resource allocation for better efficiency"

# Capacity planning
kagent "recommend resource limits based on actual usage"
```

## Troubleshooting

### Issue: Pods stuck in ImagePullBackOff

**Cause**: Images not loaded into Minikube

**Solution**:
```bash
minikube image load evolved-todo-frontend:1.0.0
minikube image load evolved-todo-backend:1.0.0
```

### Issue: Pods stuck in Pending

**Cause**: Insufficient cluster resources

**Solution**:
```bash
# Check node resources
kubectl describe nodes

# Increase Minikube resources
minikube stop
minikube start --cpus=8 --memory=16384
```

### Issue: Health check failures

**Cause**: Database connection issues

**Solution**:
```bash
# Check secret
kubectl get secret evolved-todo-secrets -o yaml

# Verify DATABASE_URL is correct
kubectl exec -it <backend-pod-name> -- env | grep DATABASE_URL

# Check backend logs
kubectl logs <backend-pod-name>
```

### Issue: LoadBalancer service pending

**Cause**: minikube tunnel not running

**Solution**:
```bash
# Start tunnel (separate terminal)
minikube tunnel  # Requires sudo/admin
```

### Issue: HPA shows <unknown>/70%

**Cause**: Metrics server not enabled

**Solution**:
```bash
minikube addons enable metrics-server
kubectl get pods -n kube-system | grep metrics-server
```

## Cleanup

```bash
# Delete Helm release
helm uninstall evolved-todo

# Or delete K8s resources
kubectl delete -f k8s/

# Delete secrets
kubectl delete secret evolved-todo-secrets

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

## Next Steps

1. **Explore AIOps Tools**: Use Gordon, kubectl-ai, and Kagent for optimization
2. **Test Scaling**: Simulate load and observe HPA behavior
3. **Experiment with Helm**: Try upgrading with different values, rollback
4. **Monitor Logs**: Use `kubectl logs` and `kubectl logs -f` for real-time monitoring
5. **Phase 5 Preparation**: Plan cloud deployment (DigitalOcean, GCP, Azure) with Kafka/Dapr

## Reference Commands

```bash
# Minikube
minikube start --cpus=4 --memory=8192
minikube stop
minikube delete
minikube status
minikube dashboard

# kubectl
kubectl get pods
kubectl get svc
kubectl get hpa
kubectl describe pod <pod-name>
kubectl logs <pod-name> --tail=100 -f
kubectl exec -it <pod-name> -- /bin/sh
kubectl port-forward service/<service-name> <local-port>:<service-port>

# Helm
helm install <release-name> <chart-path>
helm upgrade <release-name> <chart-path>
helm rollback <release-name>
helm uninstall <release-name>
helm list
helm test <release-name>

# Docker
docker build -t <image-name>:<tag> <path>
docker images
docker ps
docker logs <container-id>
```

## Time Estimates

- **First Time Setup**: 30-45 minutes (includes tool installation)
- **Subsequent Deployments**: 10-15 minutes (images cached, Minikube running)
- **Helm Upgrade**: 2-3 minutes
- **Rollback**: 1-2 minutes

---

**Total Time for Complete Deployment**: 30 minutes (as specified in success criteria SC-032)
