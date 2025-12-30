TO RUN TEST SUITE OF FRONTEND:
cd frontend && npm test

TO RUN TEST SUITE OF BACKEND:
cd backend && uv run pytest

TO RUN THE BACKEND SERVER:
cd backend && uv run uvicorn app.main:app --reload

TO RUN THE FRONTEND SERVER:
cd frontend && npm run dev

TO RUN THE MCP SERVER:
cd backend && uv run python -m app.mcp.standalone

TO BUILD DOCKER IMAGES:
docker build -t evolved-todo-backend:1.0.0 ./backend
docker build -t evolved-todo-frontend:1.0.0 ./frontend

TO START MINIKUBE CLUSTER:
minikube start --cpus=4 --memory=8192

TO LOAD IMAGES TO MINIKUBE:
minikube image load evolved-todo-backend:1.0.0
minikube image load evolved-todo-frontend:1.0.0

TO CREATE KUBERNETES SECRETS:
kubectl create secret generic database-secret --from-literal=DATABASE_URL='your-database-url'
kubectl create secret generic openai-secret --from-literal=OPENAI_API_KEY='your-openai-key'
kubectl create secret generic auth-secret --from-literal=BETTER_AUTH_SECRET='your-auth-secret'

TO INSTALL WITH HELM (DEVELOPMENT):
helm install evolved-todo ./helm/evolved-todo -f ./helm/evolved-todo/values-dev.yaml --set secrets.DATABASE_URL='your-database-url' --set secrets.OPENAI_API_KEY='your-openai-key' --set secrets.BETTER_AUTH_SECRET='your-auth-secret'

TO UPGRADE HELM RELEASE:
helm upgrade evolved-todo ./helm/evolved-todo -f ./helm/evolved-todo/values-dev.yaml

TO CHECK DEPLOYMENT STATUS:
kubectl get pods
kubectl get services

TO ACCESS SERVICES (START TUNNEL):
minikube tunnel

TO RUN HELM TESTS:
helm test evolved-todo

TO VIEW APPLICATION LOGS:
kubectl logs -l app.kubernetes.io/component=backend --tail=100
kubectl logs -l app.kubernetes.io/component=frontend --tail=100

TO UNINSTALL HELM RELEASE:
helm uninstall evolved-todo

TO STOP MINIKUBE CLUSTER:
minikube stop

TO DELETE MINIKUBE CLUSTER:
minikube delete

--- HOW TO START THE APPLICATION ---

LOCAL DEVELOPMENT (WITHOUT KUBERNETES):
# Terminal 1 - Backend
cd backend && uv run uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend && npm run dev

# Access application at http://localhost:3000

KUBERNETES DEPLOYMENT (WITH MINIKUBE):
# Start Minikube and tunnel (in separate terminal)
minikube start --cpus=4 --memory=8192
minikube tunnel

# Access application at http://127.0.0.1

--- HOW TO UPDATE BACKEND CODE ---

WHEN YOU CHANGE BACKEND CODE (*.py files):

OPTION 1: LOCAL DEVELOPMENT (FASTEST FOR TESTING)
cd backend && uv run uvicorn app.main:app --reload
# Server auto-restarts on file changes

OPTION 2: UPDATE KUBERNETES DEPLOYMENT
# Step 1: Point Docker to Minikube
minikube docker-env --shell powershell | Invoke-Expression

# Step 2: Rebuild backend image with new version tag
docker build -t evolved-todo-backend:1.0.1 ./backend

# Step 3: Update deployment to use new image
kubectl set image deployment/evolved-todo-backend backend=evolved-todo-backend:1.0.1 -n default

# Step 4: Watch rollout progress
kubectl rollout status deployment/evolved-todo-backend -n default

# Step 5: Verify pods are running
kubectl get pods -n default -l app.kubernetes.io/component=backend

OPTION 3: REBUILD AND RESTART (ALTERNATIVE)
# Point Docker to Minikube
minikube docker-env --shell powershell | Invoke-Expression

# Rebuild image
docker build -t evolved-todo-backend:1.0.0 ./backend

# Restart deployment (forces pull of latest image)
kubectl rollout restart deployment/evolved-todo-backend -n default

--- HOW TO UPDATE FRONTEND CODE ---

WHEN YOU CHANGE FRONTEND CODE (*.ts, *.tsx files):

OPTION 1: LOCAL DEVELOPMENT (FASTEST FOR TESTING)
cd frontend && npm run dev
# Server auto-restarts on file changes

OPTION 2: UPDATE KUBERNETES DEPLOYMENT
# Step 1: Point Docker to Minikube
minikube docker-env --shell powershell | Invoke-Expression

# Step 2: Rebuild frontend image with new version tag
docker build -t evolved-todo-frontend:1.0.1 ./frontend

# Step 3: Update deployment to use new image
kubectl set image deployment/evolved-todo-frontend frontend=evolved-todo-frontend:1.0.1 -n default

# Step 4: Watch rollout progress
kubectl rollout status deployment/evolved-todo-frontend -n default

# Step 5: Verify pods are running
kubectl get pods -n default -l app.kubernetes.io/component=frontend

OPTION 3: REBUILD AND RESTART (ALTERNATIVE)
# Point Docker to Minikube
minikube docker-env --shell powershell | Invoke-Expression

# Rebuild image
docker build -t evolved-todo-frontend:1.0.0 ./frontend

# Restart deployment
kubectl rollout restart deployment/evolved-todo-frontend -n default

--- COMPLETE DEPLOYMENT WORKFLOW ---

FRESH DEPLOYMENT FROM SCRATCH:
# 1. Start Minikube
minikube start --cpus=4 --memory=8192

# 2. Point Docker to Minikube
minikube docker-env --shell powershell | Invoke-Expression

# 3. Build both images
docker build -t evolved-todo-backend:1.0.0 ./backend
docker build -t evolved-todo-frontend:1.0.0 ./frontend

# 4. Verify images in Minikube
minikube ssh docker images | grep evolved-todo

# 5. Create secrets (replace with your actual values)
kubectl create secret generic database-secret --from-literal=DATABASE_URL='postgresql+asyncpg://user:pass@host/db'
kubectl create secret generic openai-secret --from-literal=OPENAI_API_KEY='sk-...'
kubectl create secret generic auth-secret --from-literal=BETTER_AUTH_SECRET='your-secret'

# 6. Install with Helm
helm install evolved-todo ./helm/evolved-todo -f ./helm/evolved-todo/values-dev.yaml

# 7. Wait for pods to be ready
kubectl get pods -n default -w

# 8. Start tunnel (in separate terminal)
minikube tunnel

# 9. Access application
# Frontend: http://127.0.0.1
# Backend API: http://127.0.0.1:8000
# API Docs: http://127.0.0.1:8000/api/docs

--- TROUBLESHOOTING ---

IF PODS SHOW 'ErrImageNeverPull':
# Make sure you built image in Minikube's Docker daemon
minikube docker-env --shell powershell | Invoke-Expression
docker build -t evolved-todo-backend:1.0.0 ./backend
kubectl rollout restart deployment/evolved-todo-backend -n default

IF PODS SHOW 'CrashLoopBackOff':
# Check pod logs for errors
kubectl logs <pod-name> -n default --previous

IF MINIKUBE TUNNEL DOESN'T WORK:
# Check tunnel status
minikube tunnel --cleanup
# Restart tunnel
minikube tunnel

TO VIEW REAL-TIME LOGS:
kubectl logs -f deployment/evolved-todo-backend -n default
kubectl logs -f deployment/evolved-todo-frontend -n default


Quick Start Guide - Next Session

  Run these commands in order:

  # 1. Start Minikube cluster
  minikube start --cpus=4 --memory=8192

  # 2. Point Docker to Minikube
  eval $(minikube docker-env)

  # 3. Deploy with Helm (images already built in Minikube)
  helm install evolved-todo ./helm/evolved-todo \
    -f ./helm/evolved-todo/values-debug.yaml \
    --set backend.image.tag=1.0.1 \
    --set frontend.image.tag=1.0.3 \
    --set secrets.DATABASE_URL='postgresql+asyncpg://neondb_owner:npg_piYDtzkE2vH5@ep-solitary-shape-a1uj62mx.ap-southeast-1.aws.neon.tech/neondb?ssl=require' \
    --set secrets.OPENAI_API_KEY='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' \
    --set secrets.BETTER_AUTH_SECRET='OP_aCndvbZrj2G0xQN3syhnAhfOH6zHcnV2glEqheWcg3Fk6spxK9cnHknBWo3wU'

  # 4. Wait for pods to be ready (2-3 minutes)
  kubectl get pods -w

  # 5. In a SEPARATE terminal, start the tunnel
  minikube tunnel

  # 6. Access the application
  # Frontend: http://127.0.0.1
  # Backend API: http://127.0.0.1:8000
  # API Docs: http://127.0.0.1:8000/api/docs

  If deployment already exists, use upgrade instead:
  helm upgrade evolved-todo ./helm/evolved-todo \
    -f ./helm/evolved-todo/values-debug.yaml \
    --set backend.image.tag=1.0.1 \
    --set frontend.image.tag=1.0.3 \
    --set secrets.DATABASE_URL='postgresql+asyncpg://neondb_owner:npg_piYDtzkE2vH5@ep-solitary-shape-a1uj62mx.ap-southeast-1.aws.neon.tech/neondb?ssl=require' \
    --set secrets.OPENAI_API_KEY='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' \
    --set secrets.BETTER_AUTH_SECRET='OP_aCndvbZrj2G0xQN3syhnAhfOH6zHcnV2glEqheWcg3Fk6spxK9cnHknBWo3wU'

  Useful Commands:
  kubectl get pods              # Check pod status
  kubectl logs <pod-name>       # View logs
  helm list                     # List deployments
  minikube status              # Check cluster status
  minikube stop                # Stop cluster when done
