# Data Model: Phase 4 - Local Kubernetes Deployment

**Feature**: Phase 4 - Local Kubernetes Deployment
**Date**: 2025-12-25
**Purpose**: Document data entities and relationships for containerization and Kubernetes deployment

## Overview

Phase 4 does NOT introduce new database models. All database entities (Task, Conversation, Message, User) remain unchanged from Phase 3. This document focuses on infrastructure-related metadata and configuration data required for containerization and Kubernetes deployment.

## Database Models (Unchanged from Phase 3)

### User Model
Managed by Better Auth. No changes from Phase 3.

### Task Model
All 10 Phase 3 task management features preserved. No schema changes.

**Schema** (SQLModel):
```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    status: str = Field(default="pending")  # pending, in_progress, completed
    priority: str | None = Field(default=None)  # low, medium, high
    tags: str | None = Field(default=None)  # Comma-separated
    due_date: datetime | None = Field(default=None)
    recurrence_pattern: str | None = Field(default=None)  # daily, weekly, monthly
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = Field(default=None)
```

### Conversation Model
Conversation state persisted to database (stateless architecture). No changes from Phase 3.

**Schema** (SQLModel):
```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Message Model
Message history for chat interface. No changes from Phase 3.

**Schema** (SQLModel):
```python
class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id", index=True)
    role: str = Field(max_length=20)  # user, assistant, system
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## Infrastructure Configuration Entities

### Kubernetes Secrets (Not in Database)

Stored in Kubernetes Secrets, referenced by pods via environment variables.

**Secret: evolved-todo-secrets**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: evolved-todo-secrets
type: Opaque
stringData:
  database-url: "postgresql://user:pass@neon.tech/dbname"  # External Neon DB
  openai-api-key: "sk-..."                                 # OpenAI API key
  better-auth-secret: "..."                                # Better Auth JWT secret
```

**Pod Environment Injection**:
```yaml
env:
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:
      name: evolved-todo-secrets
      key: database-url
- name: OPENAI_API_KEY
  valueFrom:
    secretKeyRef:
      name: evolved-todo-secrets
      key: openai-api-key
- name: BETTER_AUTH_SECRET
  valueFrom:
    secretKeyRef:
      name: evolved-todo-secrets
      key: better-auth-secret
```

### Kubernetes ConfigMaps (Not in Database)

Non-sensitive configuration data.

**ConfigMap: evolved-todo-config**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: evolved-todo-config
data:
  ENVIRONMENT: "development"  # development | production
  LOG_LEVEL: "info"           # debug | info | warning | error
  CORS_ORIGINS: "*"           # Allowed CORS origins (dev only)
```

**Pod Environment Injection**:
```yaml
envFrom:
- configMapRef:
    name: evolved-todo-config
```

## Health Check Response Schema

**Endpoint**: `GET /health` (backend), `GET /api/health` (frontend)

**Backend Health Response**:
```typescript
interface HealthCheckResponse {
  status: "healthy" | "unhealthy";
  timestamp: string;  // ISO 8601 datetime
  database: "connected" | "error: {message}";
  openai?: "available" | "error: {message}";  // Optional deep check
}
```

**Example Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2025-12-25T10:30:00Z",
  "database": "connected"
}
```

**Example Response** (503 Service Unavailable):
```json
{
  "status": "unhealthy",
  "timestamp": "2025-12-25T10:30:00Z",
  "database": "error: connection timeout"
}
```

**Frontend Health Response**:
```typescript
interface FrontendHealthResponse {
  status: "healthy";
  timestamp: string;
  service: "frontend";
}
```

## Helm Values Schema

**values.yaml Structure**:
```yaml
# Replica counts
replicaCount:
  frontend: <number>
  backend: <number>

# Container images
image:
  frontend:
    repository: <string>
    tag: <string>
    pullPolicy: <IfNotPresent|Always|Never>
  backend:
    repository: <string>
    tag: <string>
    pullPolicy: <IfNotPresent|Always|Never>

# Resource limits
resources:
  frontend:
    requests:
      cpu: <string>     # e.g., "100m"
      memory: <string>  # e.g., "128Mi"
    limits:
      cpu: <string>
      memory: <string>
  backend:
    requests:
      cpu: <string>
      memory: <string>
    limits:
      cpu: <string>
      memory: <string>

# Autoscaling configuration
autoscaling:
  frontend:
    enabled: <boolean>
    minReplicas: <number>
    maxReplicas: <number>
    targetCPUUtilizationPercentage: <number>
  backend:
    enabled: <boolean>
    minReplicas: <number>
    maxReplicas: <number>
    targetCPUUtilizationPercentage: <number>

# Service configuration
service:
  frontend:
    type: <LoadBalancer|NodePort|ClusterIP>
    port: <number>
    nodePort: <number|null>  # Only for NodePort
  backend:
    type: <ClusterIP>
    port: <number>

# Secrets (provided via --set or external secret management)
secrets:
  databaseUrl: <string>
  openaiApiKey: <string>
  betterAuthSecret: <string>
```

## Database Connection Pooling

**Backend Database Configuration** (`backend/app/db.py`):

```python
from sqlmodel import create_engine, Session
import os

# External Neon PostgreSQL (outside Kubernetes cluster)
DATABASE_URL = os.getenv("DATABASE_URL")

# Connection pool configuration for Kubernetes
engine = create_engine(
    DATABASE_URL,
    pool_size=10,              # 10 connections per pod
    max_overflow=5,            # Allow up to 5 extra connections
    pool_timeout=30,           # Wait up to 30s for connection
    pool_recycle=3600,         # Recycle connections every hour
    pool_pre_ping=True,        # Verify connection before checkout
    echo=False,                # Disable SQL logging in production
)

def get_session() -> Session:
    """
    FastAPI dependency for database sessions.
    Used in all endpoints via `session: Session = Depends(get_session)`.
    """
    with Session(engine) as session:
        yield session
```

**Connection Pool Sizing**:
- **Pool Size**: 10 connections per pod
- **Backend Pods**: 3 replicas (default)
- **Total Connections**: 3 pods * 10 connections = 30 concurrent DB connections
- **Max with Overflow**: 3 pods * (10 + 5) = 45 concurrent DB connections
- **Neon Free Tier**: Supports up to 100 concurrent connections (sufficient)

## Data Flow (Unchanged from Phase 3)

**Chat Request Flow**:
```
User → ChatKit UI (Browser)
  → Frontend Container (Next.js, port 3000)
    → Frontend Service (LoadBalancer/NodePort)
      → Backend Service (ClusterIP, port 8000)
        → Backend Pod (any replica, LoadBalancer distributes)
          → FastAPI Chat Endpoint
            → Fetch Conversation History from DB
            → Run OpenAI Agent with MCP Tools
              → MCP Tools query/modify Tasks in DB
            → Store User Message and Assistant Response in DB
            → Return Response
          → Backend Pod responds to Frontend
        → Frontend Container receives response
      → ChatKit UI displays response
    → User sees response
```

**Key Architecture Points**:
- **Stateless Pods**: Any backend pod can handle any request (LoadBalancer distributes)
- **Database Persistence**: Conversation state and tasks stored in external Neon PostgreSQL
- **Horizontal Scaling**: Multiple backend pods share database connection pool
- **Zero Downtime**: Rolling updates replace pods without losing data
- **High Availability**: If one pod fails, others continue serving requests

## Phase 4 Data Model Changes Summary

**Database Schema Changes**: NONE
- All Phase 3 models (Task, Conversation, Message, User) unchanged
- No migrations required for Phase 4
- SQLModel automatic table creation continues to work

**New Configuration Data**:
- Kubernetes Secrets for sensitive data (DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET)
- Kubernetes ConfigMaps for non-sensitive config (ENVIRONMENT, LOG_LEVEL)
- Helm values.yaml for deployment configuration
- Health check response schemas for K8s probes

**Database Connection Changes**:
- Connection pooling configured for Kubernetes (10 connections per pod)
- Pool pre-ping enabled to detect stale connections
- Pool recycle to handle long-lived connections

## Entity Relationship Diagram (Unchanged from Phase 3)

```
┌─────────────┐
│    User     │
│  (Better    │
│   Auth)     │
└──────┬──────┘
       │ 1
       │
       │ N
┌──────▼──────────┐       ┌─────────────────┐
│      Task       │       │  Conversation   │
│                 │       │                 │
│  id (PK)        │       │  id (PK)        │
│  user_id (FK)   │       │  user_id (FK)   │
│  title          │       │  created_at     │
│  description    │       │  updated_at     │
│  status         │       └────────┬────────┘
│  priority       │                │ 1
│  tags           │                │
│  due_date       │                │ N
│  recurrence     │         ┌──────▼─────────┐
│  created_at     │         │    Message     │
│  updated_at     │         │                │
│  completed_at   │         │  id (PK)       │
└─────────────────┘         │  conv_id (FK)  │
                             │  role          │
                             │  content       │
                             │  created_at    │
                             └────────────────┘
```

**Relationships**:
- User (1) → Task (N): One user has many tasks
- User (1) → Conversation (N): One user has many conversations
- Conversation (1) → Message (N): One conversation has many messages

**Storage Location**:
- All entities stored in external Neon PostgreSQL database
- Database accessible from all Kubernetes pods via Secret-injected DATABASE_URL
- No data stored in containers or Kubernetes volumes (stateless architecture)

## Summary

Phase 4 introduces NO database schema changes. The data model remains identical to Phase 3. The primary data-related changes are:
1. **Kubernetes Secrets** for sensitive configuration (not in database)
2. **ConfigMaps** for non-sensitive configuration (not in database)
3. **Health check response schemas** for K8s probes
4. **Helm values schema** for deployment configuration
5. **Connection pooling configuration** for Kubernetes scaling

All business entities (Task, Conversation, Message, User) and their relationships remain unchanged, ensuring 100% feature parity with Phase 3.
