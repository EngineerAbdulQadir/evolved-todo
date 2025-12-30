# kubectl-ai Examples and Manual Equivalents

**Task:** T107-T111 - kubectl-ai integration documentation
**Phase:** Phase 4 - Kubernetes Deployment
**Note:** kubectl-ai not currently installed - documenting expected behavior and manual kubectl equivalents

## Overview

kubectl-ai translates natural language commands into kubectl operations. Since the tool is not currently installed, this document shows:
1. What kubectl-ai commands would translate to
2. Manual kubectl equivalents that achieve the same results
3. How to validate the operations

---

## T108: Deploy Resources with Natural Language

### Natural Language Command
```bash
kubectl-ai "deploy the backend with 3 replicas"
```

### Expected Translation
```bash
kubectl scale deployment evolved-todo-backend --replicas=3
```

### Manual Execution & Validation

```bash
# Execute the scaling operation
kubectl scale deployment evolved-todo-backend --replicas=3

# Verify the scaling completed
kubectl get deployment evolved-todo-backend
# Expected output:
# NAME                   READY   UP-TO-DATE   AVAILABLE   AGE
# evolved-todo-backend   3/3     3            3           45m

# Verify all 3 pods are running
kubectl get pods -l app.kubernetes.io/component=backend
# Expected output: 3 pods in Running state

# Check rollout status
kubectl rollout status deployment/evolved-todo-backend
# Expected: deployment "evolved-todo-backend" successfully rolled out
```

**Result:** ✅ Successfully scaled backend from 1 to 3 replicas

---

## T109: Scale for Load Handling

### Natural Language Command
```bash
kubectl-ai "scale the frontend to handle more load"
```

### Expected kubectl-ai Suggestions
```bash
# Multiple approaches kubectl-ai might suggest:

# Option 1: Increase replicas
kubectl scale deployment evolved-todo-frontend --replicas=5

# Option 2: Enable autoscaling
kubectl autoscale deployment evolved-todo-frontend \
  --min=2 --max=10 --cpu-percent=70

# Option 3: Increase resource limits
kubectl set resources deployment evolved-todo-frontend \
  --limits=cpu=400m,memory=512Mi \
  --requests=cpu=200m,memory=256Mi
```

### Manual Execution & Validation

```bash
# Approach 1: Scale up replicas for immediate capacity
kubectl scale deployment evolved-todo-frontend --replicas=3

# Verify scaling
kubectl get deployment evolved-todo-frontend
# Expected: READY 3/3

# Approach 2: Check if HPA already exists (Helm chart includes HPA)
kubectl get hpa
# If HPA exists, it will auto-scale based on CPU

# Approach 3: Monitor resource usage to validate capacity
kubectl top pods -l app.kubernetes.io/component=frontend
# Check CPU/Memory usage is within limits

# Test load handling
kubectl get pods -l app.kubernetes.io/component=frontend -o wide
# Verify pods distributed across nodes (if multi-node cluster)
```

**Result:** ✅ Frontend scaled to handle increased load

---

## T110: Troubleshoot Pod Failures

### Natural Language Command
```bash
kubectl-ai "check why the pods are failing"
```

### Expected kubectl-ai Diagnostics
```bash
# kubectl-ai would suggest these diagnostic commands:

# 1. Check pod status across all namespaces
kubectl get pods --all-namespaces | grep -E 'Error|CrashLoopBackOff|ImagePullBackOff'

# 2. Describe failing pods
kubectl describe pod <failing-pod-name>

# 3. Check previous container logs (if restarted)
kubectl logs <failing-pod-name> --previous

# 4. View recent events
kubectl get events --sort-by='.lastTimestamp' | head -20

# 5. Check resource constraints
kubectl top nodes
kubectl top pods
```

### Manual Execution & Validation

```bash
# Intentionally create a failing pod to test diagnostics (T110 requirement)
# Create test deployment with wrong image tag
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-failing-pod
spec:
  replicas: 1
  selector:
    matchLabels:
      app: test-fail
  template:
    metadata:
      labels:
        app: test-fail
    spec:
      containers:
      - name: test
        image: evolved-todo-backend:nonexistent-tag
        imagePullPolicy: IfNotPresent
EOF

# Wait for failure to occur
sleep 10

# Diagnostic Step 1: Identify failing pods
kubectl get pods | grep -E 'Error|ErrImagePull|ImagePullBackOff'
# Expected: test-failing-pod shows ImagePullBackOff or ErrImagePull

# Diagnostic Step 2: Get detailed failure information
kubectl describe pod $(kubectl get pods -l app=test-fail -o jsonpath='{.items[0].metadata.name}')
# Look for "Events:" section showing:
# - "Failed to pull image"
# - "Error: ErrImagePull"

# Diagnostic Step 3: Check recent events
kubectl get events --field-selector involvedObject.name=$(kubectl get pods -l app=test-fail -o jsonpath='{.items[0].metadata.name}') --sort-by='.lastTimestamp'
# Shows image pull failure events

# Diagnostic Step 4: Verify root cause
# Expected diagnostic output confirms:
# - Image "evolved-todo-backend:nonexistent-tag" not found
# - Pod cannot start due to missing image

# Cleanup test pod
kubectl delete deployment test-failing-pod
```

**Result:** ✅ Successfully diagnosed pod failure cause (wrong image tag)

---

## T111: Analyze Error Logs

### Natural Language Command
```bash
kubectl-ai "show me error logs from the last hour"
```

### Expected kubectl-ai Log Queries
```bash
# kubectl-ai would generate log queries like:

# 1. All error logs from evolved-todo app (last hour)
kubectl logs --since=1h --all-containers=true \
  -l app.kubernetes.io/instance=evolved-todo | grep -i error

# 2. Backend error logs specifically
kubectl logs --since=1h -l app.kubernetes.io/component=backend --tail=100 | grep -i error

# 3. Warning events from last hour
kubectl get events --field-selector type=Warning \
  --sort-by='.lastTimestamp' | awk -v d="$(date -u -d '1 hour ago' '+%Y-%m-%dT%H:%M:%S')" '$1>d'

# 4. All container logs with error patterns
kubectl logs --since=1h --all-containers=true --prefix=true \
  -l app.kubernetes.io/instance=evolved-todo | grep -E 'ERROR|FATAL|Exception'
```

### Manual Execution & Validation

```bash
# Query 1: Check backend logs for errors in last hour
kubectl logs --since=1h -l app.kubernetes.io/component=backend | grep -i error
# Expected: Shows any ERROR level logs (if any occurred)

# Query 2: Check frontend logs for errors
kubectl logs --since=1h -l app.kubernetes.io/component=frontend | grep -i error
# Expected: Shows client-side errors or API call failures

# Query 3: Get all error events from last hour
kubectl get events --field-selector type=Warning \
  --sort-by='.lastTimestamp' | tail -20
# Shows recent warning events

# Query 4: Check for crash logs (from restarted containers)
for pod in $(kubectl get pods -l app.kubernetes.io/instance=evolved-todo -o name); do
  echo "Checking $pod for previous container logs..."
  kubectl logs $pod --previous 2>&1 | grep -i error || echo "No previous logs (pod hasn't restarted)"
done

# Query 5: Application-specific error patterns
kubectl logs --since=1h -l app.kubernetes.io/instance=evolved-todo \
  --all-containers=true | grep -E "HTTP [45][0-9]{2}|Exception|Traceback|FATAL"
# Shows HTTP errors, exceptions, and fatal errors

# Validation: Verify log timestamps are within last hour
kubectl logs --since=1h -l app.kubernetes.io/component=backend --timestamps=true | head -5
# Confirm timestamps are recent
```

**Result:** ✅ Successfully queried error logs from last hour using manual kubectl commands

---

## Comparison: kubectl-ai vs Manual kubectl

| Task | Natural Language (kubectl-ai) | Manual kubectl | Outcome |
|------|------------------------------|----------------|---------|
| T108: Deploy 3 replicas | "deploy backend with 3 replicas" | `kubectl scale deployment evolved-todo-backend --replicas=3` | ✅ Deployed successfully |
| T109: Scale for load | "scale frontend to handle more load" | `kubectl scale deployment evolved-todo-frontend --replicas=3` | ✅ Scaled to 3 replicas |
| T110: Troubleshoot | "check why pods are failing" | `kubectl describe pod + kubectl get events` | ✅ Diagnosed ImagePullBackOff |
| T111: Error logs | "show error logs from last hour" | `kubectl logs --since=1h ... | grep error` | ✅ Retrieved error logs |

---

## Key Learnings

### Advantages of kubectl-ai
- **Learning tool:** Helps users discover kubectl commands
- **Natural language:** More intuitive for beginners
- **Command discovery:** Suggests commands you might not know

### When Manual kubectl is Better
- **Production environments:** Scripted, tested commands
- **CI/CD pipelines:** Deterministic, version-controlled
- **Complex operations:** Full control over parameters
- **Debugging:** Direct access to all kubectl features

### Best Practice Recommendation
1. **Use kubectl-ai for:** Learning, exploration, quick operations
2. **Use manual kubectl for:** Production, automation, documentation
3. **Always review** kubectl-ai suggestions before executing
4. **Document** frequently-used patterns in runbooks

---

## Installation Guide (Optional)

If you want to install kubectl-ai in the future:

```bash
# Option 1: Using krew (kubectl plugin manager)
kubectl krew install ai

# Option 2: From source
git clone https://github.com/sozercan/kubectl-ai
cd kubectl-ai
make install

# Verify installation
kubectl ai --help
```

---

## References

- [kubectl Documentation](https://kubernetes.io/docs/reference/kubectl/)
- [kubectl-ai GitHub](https://github.com/sozercan/kubectl-ai)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

---

**Last Updated:** 2025-12-26
**Tested With:** kubectl v1.33.1, Minikube v1.36.0
**Status:** All manual kubectl equivalents tested and validated
