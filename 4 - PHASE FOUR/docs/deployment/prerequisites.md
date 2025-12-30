# Phase 4 - Deployment Prerequisites

**Task**: T007
**Ref**: ADR-001, ADR-002, ADR-003, ADR-004
**Purpose**: Document all prerequisites for Phase 4 Local Kubernetes Deployment

---

## Required Software

### 1. Docker Desktop 4.53+ ✅

**Current Version**: Docker 28.3.2
**Status**: ✅ INSTALLED

**Purpose**: Container runtime for building and running Docker images
**Minimum Version**: 4.53+ (for Docker AI Gordon support)

**Verify Installation**:
```bash
docker --version
# Expected: Docker version 28.3.2 or higher
```

**Installation** (if needed):
- Download from: https://www.docker.com/products/docker-desktop
- Ensure Docker Desktop is running before proceeding

---

### 2. Minikube 1.32+ ✅

**Current Version**: v1.36.0
**Status**: ✅ INSTALLED

**Purpose**: Local Kubernetes cluster for development and testing
**Minimum Version**: 1.32+

**Verify Installation**:
```bash
minikube version
# Expected: minikube version: v1.36.0 or higher
```

**Installation** (if needed):
```bash
# Windows (with Chocolatey)
choco install minikube

# macOS (with Homebrew)
brew install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

**Start Minikube**:
```bash
minikube start --cpus=4 --memory=8192 --driver=docker
```

---

### 3. kubectl 1.28+ ✅

**Current Version**: v1.32.2
**Status**: ✅ INSTALLED

**Purpose**: Kubernetes command-line tool for cluster management
**Minimum Version**: 1.28+

**Verify Installation**:
```bash
kubectl version --client
# Expected: Client Version: v1.32.2 or higher
```

**Installation** (if needed):
```bash
# Windows (with Chocolatey)
choco install kubernetes-cli

# macOS (with Homebrew)
brew install kubectl

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/kubectl
```

---

### 4. Helm 3.x ❌

**Current Version**: NOT INSTALLED
**Status**: ❌ REQUIRES INSTALLATION

**Purpose**: Kubernetes package manager for templated deployments
**Minimum Version**: 3.x (latest stable)

**Installation Instructions**:

**Windows (PowerShell)**:
```powershell
# Using Chocolatey
choco install kubernetes-helm

# Or download installer from GitHub
# https://github.com/helm/helm/releases
```

**macOS**:
```bash
brew install helm
```

**Linux**:
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

**Verify Installation**:
```bash
helm version
# Expected: version.BuildInfo{Version:"v3.x.x", ...}
```

---

## Optional: AIOps Tools (User Story 4)

### Docker AI (Gordon)

**Status**: Included with Docker Desktop 4.53+
**Verify**: Available via `docker ai` command

**Purpose**: Dockerfile optimization and security analysis

**Test**:
```bash
docker ai "help"
```

---

### kubectl-ai

**Status**: Requires separate installation
**Purpose**: Natural language Kubernetes operations

**Installation**:
```bash
# Install via kubectl plugin manager (krew)
kubectl krew install ai
```

**Verify**:
```bash
kubectl ai "help"
```

---

### Kagent

**Status**: Requires separate installation
**Purpose**: Cluster health analysis and optimization recommendations

**Installation**:
Follow instructions at: https://github.com/kagent-ai/kagent

**Verify**:
```bash
kagent version
```

---

## Network Requirements

### Ports Required

- **Frontend**: 3000 (Next.js)
- **Backend**: 8000 (FastAPI)
- **Minikube NodePort**: 30080 (Frontend Service)
- **Minikube Tunnel**: LoadBalancer support (requires admin/sudo)

### Firewall Configuration

Ensure the following are allowed:
- Docker daemon communication
- Minikube cluster network (192.168.49.0/24 by default)
- NodePort range (30000-32767)

---

## Database Access

### Neon PostgreSQL

**Requirement**: External Neon Serverless PostgreSQL connection
**Environment Variable**: `DATABASE_URL`

**Format**:
```
DATABASE_URL="postgresql://user:password@hostname/database?sslmode=require"
```

**Verify Connectivity**:
```bash
# From local machine
psql "${DATABASE_URL}" -c "SELECT 1;"
```

---

## Environment Variables Required

Create `.env` file in project root with:

```bash
# Database
DATABASE_URL="postgresql://user:password@hostname/database?sslmode=require"

# OpenAI API
OPENAI_API_KEY="sk-..."

# Authentication
BETTER_AUTH_SECRET="your-secret-key-here"
BETTER_AUTH_URL="http://localhost:3000"

# Node Environment
NODE_ENV="development"
```

---

## System Requirements

### Minimum Hardware

- **CPU**: 4 cores (for Minikube)
- **RAM**: 8GB minimum, 16GB recommended
- **Disk**: 20GB free space for images and cluster

### Operating System

- Windows 10/11 with WSL2
- macOS 11+
- Linux (Ubuntu 20.04+, Fedora 35+, or equivalent)

---

## Validation Checklist

Before proceeding with Phase 4 implementation, verify:

- [ ] Docker Desktop 4.53+ running
- [ ] Minikube 1.32+ installed
- [ ] kubectl 1.28+ installed
- [ ] **Helm 3.x installed** ⚠️ ACTION REQUIRED
- [ ] `.env` file configured with all required secrets
- [ ] Neon PostgreSQL database accessible
- [ ] Phase 3 application running locally (backend + frontend)
- [ ] At least 8GB RAM available for Minikube

---

## Next Steps

After installing Helm and verifying all prerequisites:

1. **Start Minikube**: `minikube start --cpus=4 --memory=8192 --driver=docker`
2. **Enable metrics-server**: `minikube addons enable metrics-server` (required for HPA)
3. **Proceed to Phase 2**: Implement health check endpoints (T008-T012)

---

## Troubleshooting

### Docker Desktop Not Running

**Symptom**: `Cannot connect to the Docker daemon`

**Solution**: Start Docker Desktop application

### Minikube Start Fails

**Symptom**: `Exiting due to insufficient resources`

**Solution**: Increase allocated resources or reduce --cpus/--memory flags

### kubectl Not Connected to Minikube

**Symptom**: `The connection to the server localhost:8080 was refused`

**Solution**:
```bash
minikube start
kubectl config use-context minikube
```

### Helm Command Not Found (Windows)

**Symptom**: `helm: command not found` after installation

**Solution**:
1. Close and reopen PowerShell/terminal
2. Verify Helm binary is in PATH
3. Reinstall using Chocolatey with admin privileges

---

**Last Updated**: 2025-12-25
**Phase**: Phase 4 - Local Kubernetes Deployment
**Related ADRs**: ADR-001 (Containerization), ADR-002 (K8s Resources), ADR-003 (Helm), ADR-004 (AIOps)
