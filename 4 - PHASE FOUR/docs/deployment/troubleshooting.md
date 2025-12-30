# Kubernetes Deployment Troubleshooting Guide

**Phase 4: Kubernetes Deployment**
**Last Updated:** 2025-12-26

---

## Overview

This guide covers common issues encountered when deploying Evolved Todo to Kubernetes (Minikube or cloud) and their solutions.

---

## 🔍 Quick Diagnostic Commands

Before diving into specific issues, run these diagnostics:

```bash
# Check pod status
kubectl get pods -l app.kubernetes.io/instance=evolved-todo

# Describe problematic pod
kubectl describe pod <pod-name>

# View pod logs
kubectl logs <pod-name> --tail=100

# Check recent events
kubectl get events --sort-by='.lastTimestamp' | tail -20

# Check service endpoints
kubectl get svc -l app.kubernetes.io/instance=evolved-todo

# Check resource usage
kubectl top nodes
kubectl top pods
```

---

## 🚨 Common Issues

### Issue 1: ImagePullBackOff

**Symptom:**
```
NAME                             READY   STATUS             RESTARTS   AGE
evolved-todo-backend-xxx         0/1     ImagePullBackOff   0          2m
```

**Diagnosis:**
```bash
kubectl describe pod evolved-todo-backend-xxx | grep -A 10 "Events:"
```

**Output:**
```
Events:
  Warning  Failed     pulling image "evolved-todo-backend:1.0.0": rpc error: code = Unknown
  Warning  Failed     Error: ErrImagePull
  Warning  Failed     Error: ImagePullBackOff
```

**Cause:** Image not available in Minikube's local registry

**Solution 1: Load Images into Minikube**
```bash
# Build images locally first
docker build -t evolved-todo-backend:1.0.0 ./backend
docker build -t evolved-todo-frontend:1.0.0 ./frontend

# Load into Minikube
minikube image load evolved-todo-backend:1.0.0
minikube image load evolved-todo-frontend:1.0.0

# Verify images loaded
minikube image ls | grep evolved-todo
```

**Solution 2: Use imagePullPolicy: Never (Dev Only)**
```yaml
# In helm/evolved-todo/values-dev.yaml
image:
  backend:
    pullPolicy: Never  # Use local images only
  frontend:
    pullPolicy: Never
```

```bash
# Redeploy with updated values
helm upgrade evolved-todo ./helm/evolved-todo \
  -f ./helm/evolved-todo/values-dev.yaml \
  --reuse-values
```

**Verification:**
```bash
# Pod should transition to Running
kubectl get pods -w  # Watch for status change
```

---

### Issue 2: Pods Pending (Insufficient Resources)

**Symptom:**
```
NAME                             READY   STATUS    RESTARTS   AGE
evolved-todo-backend-xxx         0/1     Pending   0          5m
```

**Diagnosis:**
```bash
kubectl describe pod evolved-todo-backend-xxx
```

**Output:**
```
Events:
  Warning  FailedScheduling  pod has unbound immediate PersistentVolumeClaims
  Warning  FailedScheduling  0/1 nodes are available: 1 Insufficient cpu
```

**Cause:** Minikube cluster has insufficient CPU/memory resources

**Solution 1: Increase Minikube Resources**
```bash
# Stop Minikube
minikube stop

# Delete and recreate with more resources
minikube delete
minikube start --cpus=4 --memory=8192  # 4 CPUs, 8GB RAM

# Verify resources
kubectl top nodes
```

**Solution 2: Reduce Resource Requests (Dev Only)**
```yaml
# In helm/evolved-todo/values-dev.yaml
resources:
  backend:
    requests:
      cpu: 50m      # Reduced from 100m
      memory: 128Mi
  frontend:
    requests:
      cpu: 25m      # Reduced from 50m
      memory: 64Mi
```

```bash
# Apply changes
helm upgrade evolved-todo ./helm/evolved-todo \
  -f ./helm/evolved-todo/values-dev.yaml \
  --reuse-values
```

**Verification:**
```bash
# Check node capacity
kubectl describe nodes | grep -A 5 "Allocated resources"

# Pods should schedule
kubectl get pods
```

---

### Issue 3: Health Check Failures

**Symptom:**
```
Events:
  Warning  Unhealthy  Readiness probe failed: Get "http://10.244.0.5:8000/api/health": dial tcp 10.244.0.5:8000: connect: connection refused
  Warning  Unhealthy  Startup probe failed: HTTP probe failed with statuscode: 404
```

**Diagnosis:**
```bash
# Check if container is running
kubectl get pods -l app.kubernetes.io/instance=evolved-todo

# Check container logs for startup errors
kubectl logs evolved-todo-backend-xxx
```

**Cause 1: Wrong Health Endpoint Path**

**Solution:**
```bash
# Backend health endpoint is /api/health (NOT /health)
# Frontend health endpoint is /api/health

# Verify in values.yaml:
probes:
  backend:
    liveness:
      path: /api/health  # Correct
    readiness:
      path: /api/health  # Correct
```

**Cause 2: Database Connection Failure**

**Diagnosis:**
```bash
kubectl logs evolved-todo-backend-xxx | grep -i "database\|connection"
```

**Output:**
```
ERROR: Could not connect to database
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

**Solution:**
```bash
# Verify DATABASE_URL secret is correct
kubectl get secret evolved-todo-secrets -o yaml

# Check actual value (base64 decode)
kubectl get secret evolved-todo-secrets -o jsonpath='{.data.DATABASE_URL}' | base64 --decode
echo ""

# Should be: postgresql+asyncpg://user:pass@host:5432/dbname?ssl=require

# If wrong, update secret
helm upgrade evolved-todo ./helm/evolved-todo \
  --set secrets.DATABASE_URL="postgresql+asyncpg://correct-url" \
  --reuse-values

# Restart pods to pick up new secret
kubectl rollout restart deployment/evolved-todo-backend
```

**Cause 3: Container Taking Too Long to Start**

**Solution: Increase Startup Probe Timeout**
```yaml
# In values.yaml
probes:
  backend:
    startup:
      initialDelaySeconds: 10   # Increased from 0
      periodSeconds: 5
      timeoutSeconds: 5         # Increased from 3
      failureThreshold: 20      # Increased from 12
```

---

### Issue 4: LoadBalancer Service Pending

**Symptom:**
```
NAME                    TYPE           EXTERNAL-IP   PORT(S)
evolved-todo-frontend   LoadBalancer   <pending>     80:30123/TCP
evolved-todo-backend    LoadBalancer   <pending>     8000:30456/TCP
```

**Cause:** Minikube tunnel not running

**Solution:**
```bash
# Start minikube tunnel in separate terminal
# IMPORTANT: Keep this running while using the app
minikube tunnel

# Expected output:
✅  Tunnel successfully started
🏃  Starting tunnel for service evolved-todo-frontend.
🏃  Starting tunnel for service evolved-todo-backend.
```

**Verification:**
```bash
# Check EXTERNAL-IP assigned
kubectl get svc -l app.kubernetes.io/instance=evolved-todo

# Should show:
NAME                    TYPE           EXTERNAL-IP   PORT(S)
evolved-todo-frontend   LoadBalancer   127.0.0.1     80:30123/TCP
evolved-todo-backend    LoadBalancer   127.0.0.1     8000:30456/TCP

# Test access
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1/api/health
```

**Alternative: Use NodePort (if tunnel not available)**
```yaml
# In values-dev.yaml
service:
  backend:
    type: NodePort  # Changed from LoadBalancer
  frontend:
    type: NodePort
```

```bash
# Get NodePort
kubectl get svc evolved-todo-frontend -o jsonpath='{.spec.ports[0].nodePort}'

# Access via Minikube IP
minikube ip  # e.g., 192.168.49.2
# http://192.168.49.2:<nodeport>
```

---

### Issue 5: CrashLoopBackOff

**Symptom:**
```
NAME                             READY   STATUS             RESTARTS   AGE
evolved-todo-backend-xxx         0/1     CrashLoopBackOff   5          10m
```

**Diagnosis:**
```bash
# Check current logs
kubectl logs evolved-todo-backend-xxx

# Check previous container logs (if restarted)
kubectl logs evolved-todo-backend-xxx --previous
```

**Common Causes and Solutions:**

**Cause 1: Missing Environment Variables**
```
KeyError: 'DATABASE_URL'
```

**Solution:**
```bash
# Verify secret exists
kubectl get secret evolved-todo-secrets

# Verify secret has correct keys
kubectl get secret evolved-todo-secrets -o jsonpath='{.data}' | jq

# Should contain: DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET

# If missing, recreate secret
helm upgrade evolved-todo ./helm/evolved-todo \
  --set secrets.DATABASE_URL="$DATABASE_URL" \
  --set secrets.OPENAI_API_KEY="$OPENAI_API_KEY" \
  --set secrets.BETTER_AUTH_SECRET="$BETTER_AUTH_SECRET" \
  --reuse-values
```

**Cause 2: Out of Memory (OOMKilled)**
```bash
kubectl describe pod evolved-todo-backend-xxx | grep -A 5 "Last State"
```

**Output:**
```
Last State:     Terminated
  Reason:       OOMKilled
  Exit Code:    137
```

**Solution: Increase Memory Limits**
```yaml
# In values.yaml
resources:
  backend:
    limits:
      memory: 512Mi  # Increased from 256Mi
```

**Cause 3: Application Crash**
```
Traceback (most recent call last):
  File "app/main.py", line 10, in <module>
    raise Exception("Configuration error")
```

**Solution:** Fix application code and rebuild image

---

### Issue 6: Pods Running but Service Not Accessible

**Symptom:**
```
curl: (7) Failed to connect to 127.0.0.1 port 8000: Connection refused
```

**Diagnosis:**
```bash
# Check pod status
kubectl get pods -l app.kubernetes.io/instance=evolved-todo

# Check service endpoints
kubectl get endpoints -l app.kubernetes.io/instance=evolved-todo

# Should show pod IPs:
NAME                    ENDPOINTS
evolved-todo-backend    10.244.0.5:8000,10.244.0.6:8000
evolved-todo-frontend   10.244.0.7:3000
```

**Cause 1: Service Selector Mismatch**
```bash
kubectl describe svc evolved-todo-backend | grep Selector
```

**Output:**
```
Selector:  app.kubernetes.io/instance=evolved-todo,app.kubernetes.io/component=backend
```

**Solution:** Verify pod labels match selector
```bash
kubectl get pods -l app.kubernetes.io/instance=evolved-todo --show-labels

# Labels should include both:
# app.kubernetes.io/instance=evolved-todo
# app.kubernetes.io/component=backend
```

**Cause 2: Wrong Port Configuration**
```bash
# Check service port
kubectl get svc evolved-todo-backend -o jsonpath='{.spec.ports[0]}'

# Output:
{"name":"http","port":8000,"protocol":"TCP","targetPort":8000}

# Verify container is listening on targetPort
kubectl exec -it evolved-todo-backend-xxx -- netstat -tlnp | grep 8000
```

**Cause 3: Minikube Tunnel Not Running**

See [Issue 4: LoadBalancer Service Pending](#issue-4-loadbalancer-service-pending)

---

### Issue 7: Helm Install Fails with Timeout

**Symptom:**
```
Error: INSTALLATION FAILED: timed out waiting for the condition
```

**Diagnosis:**
```bash
# Check what's preventing readiness
kubectl get pods -l app.kubernetes.io/instance=evolved-todo
kubectl describe pod <pod-name> | grep -A 10 "Events:"
```

**Common Causes:**
1. Health probes failing (see Issue 3)
2. Image pull issues (see Issue 1)
3. Resource constraints (see Issue 2)

**Quick Fix: Increase Timeout**
```bash
helm install evolved-todo ./helm/evolved-todo \
  -f ./helm/evolved-todo/values-dev.yaml \
  --wait --timeout=10m  # Increased from 5m
```

---

### Issue 8: HPA Not Scaling

**Symptom:**
```
kubectl get hpa
NAME                     REFERENCE                       TARGETS    MINPODS   MAXPODS   REPLICAS
evolved-todo-backend-hpa Deployment/evolved-todo-backend <unknown>  2         10        0
```

**Cause:** Metrics server not running

**Diagnosis:**
```bash
kubectl get deployment metrics-server -n kube-system
```

**Solution: Enable Metrics Server**
```bash
# For Minikube
minikube addons enable metrics-server

# Verify metrics available
kubectl top nodes
kubectl top pods
```

**Verification:**
```bash
# HPA should show CPU metrics
kubectl get hpa
# TARGETS should show: 5%/70% (current/target)
```

---

### Issue 9: Secrets Not Found

**Symptom:**
```
Error from server (NotFound): secrets "evolved-todo-secrets" not found
```

**Cause:** Secrets not created during Helm install

**Solution:**
```bash
# Verify secrets were provided
helm get values evolved-todo | grep -A 5 "secrets:"

# If missing, upgrade with secrets
helm upgrade evolved-todo ./helm/evolved-todo \
  --set secrets.DATABASE_URL="${DATABASE_URL}" \
  --set secrets.OPENAI_API_KEY="${OPENAI_API_KEY}" \
  --set secrets.BETTER_AUTH_SECRET="${BETTER_AUTH_SECRET}" \
  --reuse-values
```

---

### Issue 10: Rolling Update Stuck

**Symptom:**
```
kubectl rollout status deployment/evolved-todo-backend
Waiting for deployment "evolved-todo-backend" rollout to finish: 1 old replicas are pending termination...
```

**Diagnosis:**
```bash
# Check deployment status
kubectl describe deployment evolved-todo-backend

# Check pod events
kubectl get events --field-selector involvedObject.kind=Pod --sort-by='.lastTimestamp' | tail -20
```

**Cause:** New pods failing readiness check

**Solution:**
```bash
# Check new pod logs
kubectl logs <new-pod-name>

# If health checks failing, see Issue 3

# Force rollback if needed
helm rollback evolved-todo
```

---

## 🛠️ Advanced Troubleshooting

### Debug Pod with Shell Access

```bash
# Get shell in running pod
kubectl exec -it evolved-todo-backend-xxx -- /bin/sh

# Inside pod:
# Check environment variables
env | grep DATABASE

# Test database connection
python -c "from app.core.database import engine; print(engine.url)"

# Check listening ports
netstat -tlnp

# Test health endpoint internally
curl http://localhost:8000/api/health
```

### Network Connectivity Testing

```bash
# Create debug pod
kubectl run debug --rm -it --image=busybox -- sh

# Inside debug pod:
# Test backend service DNS
nslookup evolved-todo-backend

# Test backend connectivity
wget -O- http://evolved-todo-backend:8000/api/health

# Test frontend
wget -O- http://evolved-todo-frontend/api/health
```

### Check Resource Quotas

```bash
# Check if namespace has resource quotas
kubectl get resourcequota

# Check limit ranges
kubectl get limitrange

# View detailed quota usage
kubectl describe resourcequota
```

---

## 📊 Performance Issues

### Slow Response Times

**Diagnosis:**
```bash
# Check pod resource usage
kubectl top pods -l app.kubernetes.io/instance=evolved-todo

# Check for CPU throttling
kubectl get pods -o yaml | grep -A 5 "throttling"

# Check database connection pool
kubectl logs evolved-todo-backend-xxx | grep "pool"
```

**Solutions:**
1. Increase CPU limits
2. Increase HPA replicas
3. Optimize database queries
4. Add database indexes

### High Memory Usage

**Diagnosis:**
```bash
# Check memory usage trend
kubectl top pods --watch

# Check for memory leaks in logs
kubectl logs evolved-todo-backend-xxx | grep -i "memory\|oom"
```

**Solutions:**
1. Increase memory limits
2. Review application for memory leaks
3. Adjust connection pool size
4. Enable garbage collection logging

---

## 🔐 Security Issues

### Non-root User Not Working

**Symptom:**
```
Error: container has runAsNonRoot and image has non-numeric user
```

**Solution:** Verify Dockerfile sets numeric UID
```dockerfile
# In Dockerfile
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser

USER 1000:1000  # Use numeric UID, not username
```

### Secret Values Not Updated

**Problem:** Changed secrets but pods still use old values

**Solution:**
```bash
# Secrets are mounted at pod creation time
# Must restart pods to pick up new secrets

kubectl rollout restart deployment/evolved-todo-backend
kubectl rollout restart deployment/evolved-todo-frontend

# Verify new pods are using updated secrets
kubectl exec -it evolved-todo-backend-xxx -- env | grep DATABASE_URL
```

---

## 🆘 When All Else Fails

### Complete Clean and Redeploy

```bash
# 1. Uninstall Helm release
helm uninstall evolved-todo

# 2. Delete all resources
kubectl delete all -l app.kubernetes.io/instance=evolved-todo
kubectl delete secret evolved-todo-secrets

# 3. Restart Minikube (if local)
minikube stop
minikube start --cpus=4 --memory=8192

# 4. Reload images
minikube image load evolved-todo-backend:1.0.0
minikube image load evolved-todo-frontend:1.0.0

# 5. Fresh install
helm install evolved-todo ./helm/evolved-todo \
  -f ./helm/evolved-todo/values-dev.yaml \
  --set secrets.DATABASE_URL="${DATABASE_URL}" \
  --set secrets.OPENAI_API_KEY="${OPENAI_API_KEY}" \
  --set secrets.BETTER_AUTH_SECRET="${BETTER_AUTH_SECRET}" \
  --wait --timeout=5m

# 6. Start tunnel
minikube tunnel
```

---

## 📚 Additional Resources

- [Kubernetes Debugging Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/)
- [Helm Troubleshooting](https://helm.sh/docs/faq/troubleshooting/)
- [Minikube Docs](https://minikube.sigs.k8s.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

---

**Last Updated:** 2025-12-26
**Phase:** 4 - Kubernetes Deployment
**For More Help:** See [docs/deployment/README.md](README.md)
