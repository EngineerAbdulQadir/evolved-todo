# API Contracts: Phase 4 - Local Kubernetes Deployment

**Feature**: Phase 4 - Local Kubernetes Deployment
**Date**: 2025-12-25
**Purpose**: Define contracts for Docker images, Kubernetes resources, and Helm templates

## Directory Structure

```
contracts/
├── README.md (this file)
├── docker/
│   ├── frontend-dockerfile-spec.md   # Frontend Dockerfile specification
│   └── backend-dockerfile-spec.md    # Backend Dockerfile specification
├── kubernetes/
│   ├── deployment-spec.md            # Deployment resource specification
│   ├── service-spec.md               # Service resource specification
│   └── hpa-spec.md                   # HorizontalPodAutoscaler specification
└── helm/
    └── chart-spec.md                 # Helm chart structure specification
```

## Contract Overview

### Docker Contracts

**Purpose**: Define multi-stage Dockerfile structure, base images, security hardening, and health checks

**Key Specifications**:
- Multi-stage builds (build + production stages)
- Base images: node:22-alpine (frontend), python:3.13-slim (backend)
- Non-root user (UID 1000)
- Health check directives
- Image size targets: <150MB (frontend), <200MB (backend)

### Kubernetes Contracts

**Purpose**: Define Kubernetes resource specifications for Deployments, Services, and HPA

**Key Specifications**:
- Resource requests and limits for all pods
- Liveness, Readiness, and Startup probes
- Rolling update strategy
- Service types (ClusterIP for backend, LoadBalancer/NodePort for frontend)
- HPA configuration (CPU-based autoscaling)

### Helm Contracts

**Purpose**: Define Helm chart structure, templating patterns, and values schema

**Key Specifications**:
- Chart.yaml metadata structure
- values.yaml schema for parameterization
- Template organization (frontend/, backend/, _helpers.tpl)
- Environment-specific value files (values-dev.yaml)
- Helm test templates for connectivity validation

## Implementation Notes

All contract specifications reference the technical decisions documented in `research.md` and align with the constitution principles in `.specify/memory/constitution.md` (v4.0.0).

Detailed specifications for each contract type are available in subdirectories.
