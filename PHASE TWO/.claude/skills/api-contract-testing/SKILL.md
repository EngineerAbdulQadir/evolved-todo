---
name: api-contract-testing
description: Contract-first API development with OpenAPI schemas, request/response validation, and contract testing between frontend and backend.
---

# API Contract Testing

## Instructions

### When to Use

- Validating API endpoints match OpenAPI specification
- Ensuring request/response schemas are correct
- Testing frontend-backend contract compatibility
- Implementing contract-first development
- Validating error response structures
- Preventing API breaking changes

## What is Contract Testing?

Contract testing verifies that:
- **Backend** implements the API contract (OpenAPI spec)
- **Frontend** consumes the API according to the contract
- **Both** agree on request/response schemas and error formats

**Benefits:**
- Catch integration issues early
- Safe API changes (detect breaking changes)
- Documentation is always up-to-date
- Frontend and backend can develop independently

## API Contract Example

```yaml
# openapi.yaml
openapi: 3.0.0
info:
  title: Evolved Todo API
  version: 1.0.0

paths:
  /api/{user_id}/tasks:
    get:
      summary: List tasks
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: integer
        - name: completed
          in: query
          schema:
            type: boolean
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Task'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '403':
          $ref: '#/components/responses/Forbidden'

    post:
      summary: Create task
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TaskCreate'
      responses:
        '201':
          description: Created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'

components:
  schemas:
    Task:
      type: object
      required:
        - id
        - user_id
        - title
        - completed
        - priority
        - created_at
        - updated_at
      properties:
        id:
          type: integer
        user_id:
          type: integer
        title:
          type: string
          maxLength: 200
        description:
          type: string
          maxLength: 1000
        completed:
          type: boolean
        priority:
          type: string
          enum: [low, medium, high]
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time

    TaskCreate:
      type: object
      required:
        - title
      properties:
        title:
          type: string
          minLength: 1
          maxLength: 200
        description:
          type: string
          maxLength: 1000
        priority:
          type: string
          enum: [low, medium, high]
          default: medium

  responses:
    Unauthorized:
      description: Unauthorized
      content:
        application/json:
          schema:
            type: object
            properties:
              detail:
                type: string
                example: "Invalid or expired token"

    Forbidden:
      description: Forbidden
      content:
        application/json:
          schema:
            type: object
            properties:
              detail:
                type: string
                example: "Not authorized to access this resource"

    BadRequest:
      description: Bad Request
      content:
        application/json:
          schema:
            type: object
            properties:
              detail:
                type: array
                items:
                  type: object
                  properties:
                    loc:
                      type: array
                    msg:
                      type: string
                    type:
                      type: string
```

## Backend: OpenAPI Auto-Generation (FastAPI)

FastAPI automatically generates OpenAPI schemas from Pydantic models:

```python
# app/main.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Evolved Todo API",
    version="1.0.0",
    description="Full-stack todo application API",
)

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Evolved Todo API",
        version="1.0.0",
        description="Full-stack todo application API",
        routes=app.routes,
    )

    # Add custom extensions or modify schema here
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Access OpenAPI spec at: http://localhost:8000/openapi.json
# Swagger UI at: http://localhost:8000/docs
# ReDoc at: http://localhost:8000/redoc
```

## Backend: Contract Testing with pytest

```python
# tests/test_contract.py
import pytest
from fastapi.testclient import TestClient
from openapi_spec_validator import validate_spec
from openapi_spec_validator.readers import read_from_filename
import json

from app.main import app

@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)

def test_openapi_spec_is_valid(client):
    """Test that OpenAPI spec is valid."""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    spec = response.json()

    # Validate OpenAPI spec
    validate_spec(spec)

def test_list_tasks_contract(client, auth_headers):
    """Test that list tasks endpoint matches contract."""
    response = client.get("/api/1/tasks", headers=auth_headers)

    # Response status
    assert response.status_code == 200

    # Response schema
    data = response.json()
    assert isinstance(data, list)

    if len(data) > 0:
        task = data[0]
        # Required fields
        assert "id" in task
        assert "user_id" in task
        assert "title" in task
        assert "completed" in task
        assert "priority" in task
        assert "created_at" in task
        assert "updated_at" in task

        # Field types
        assert isinstance(task["id"], int)
        assert isinstance(task["user_id"], int)
        assert isinstance(task["title"], str)
        assert isinstance(task["completed"], bool)
        assert task["priority"] in ["low", "medium", "high"]

def test_create_task_contract(client, auth_headers):
    """Test that create task endpoint matches contract."""
    # Valid request
    payload = {
        "title": "Test task",
        "description": "Test description",
        "priority": "high"
    }

    response = client.post("/api/1/tasks", json=payload, headers=auth_headers)

    # Response status
    assert response.status_code == 201

    # Response schema
    task = response.json()
    assert "id" in task
    assert task["title"] == payload["title"]
    assert task["description"] == payload["description"]
    assert task["priority"] == payload["priority"]

def test_create_task_validation_contract(client, auth_headers):
    """Test that validation errors match contract."""
    # Invalid request (missing title)
    payload = {
        "description": "Test description"
    }

    response = client.post("/api/1/tasks", json=payload, headers=auth_headers)

    # Response status
    assert response.status_code == 422

    # Error response schema
    error = response.json()
    assert "detail" in error
    assert isinstance(error["detail"], list)

    # Validation error structure
    validation_error = error["detail"][0]
    assert "loc" in validation_error
    assert "msg" in validation_error
    assert "type" in validation_error
```

## Frontend: TypeScript Types from OpenAPI

### Using openapi-typescript

```bash
cd frontend
pnpm add -D openapi-typescript
```

```json
// package.json
{
  "scripts": {
    "generate-types": "openapi-typescript http://localhost:8000/openapi.json -o lib/api-types.ts"
  }
}
```

```bash
# Generate TypeScript types from OpenAPI spec
pnpm generate-types
```

```typescript
// lib/api-types.ts (auto-generated)
export interface paths {
  "/api/{user_id}/tasks": {
    get: operations["list_tasks"]
    post: operations["create_task"]
  }
  "/api/{user_id}/tasks/{task_id}": {
    get: operations["get_task"]
    put: operations["update_task"]
    delete: operations["delete_task"]
  }
}

export interface components {
  schemas: {
    Task: {
      id: number
      user_id: number
      title: string
      description?: string | null
      completed: boolean
      priority: "low" | "medium" | "high"
      created_at: string
      updated_at: string
    }
    TaskCreate: {
      title: string
      description?: string | null
      priority?: "low" | "medium" | "high"
    }
  }
}

export type Task = components["schemas"]["Task"]
export type TaskCreate = components["schemas"]["TaskCreate"]
```

### Type-Safe API Client

```typescript
// lib/api-client.ts
import axios from 'axios'
import type { Task, TaskCreate } from './api-types'

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
})

export const tasksApi = {
  async list(userId: number, completed?: boolean): Promise<Task[]> {
    const response = await apiClient.get<Task[]>(`/api/${userId}/tasks`, {
      params: { completed },
    })
    return response.data
  },

  async create(userId: number, data: TaskCreate): Promise<Task> {
    const response = await apiClient.post<Task>(`/api/${userId}/tasks`, data)
    return response.data
  },

  async get(userId: number, taskId: number): Promise<Task> {
    const response = await apiClient.get<Task>(`/api/${userId}/tasks/${taskId}`)
    return response.data
  },

  async update(userId: number, taskId: number, data: Partial<TaskCreate>): Promise<Task> {
    const response = await apiClient.put<Task>(`/api/${userId}/tasks/${taskId}`, data)
    return response.data
  },

  async delete(userId: number, taskId: number): Promise<void> {
    await apiClient.delete(`/api/${userId}/tasks/${taskId}`)
  },
}
```

## Frontend: Contract Testing with Jest

```typescript
// __tests__/api-contract.test.ts
import { tasksApi } from '@/lib/api-client'
import type { Task, TaskCreate } from '@/lib/api-types'

describe('API Contract Tests', () => {
  const userId = 1

  test('list tasks returns array of Task objects', async () => {
    const tasks = await tasksApi.list(userId)

    expect(Array.isArray(tasks)).toBe(true)

    if (tasks.length > 0) {
      const task = tasks[0]

      // Required fields
      expect(task).toHaveProperty('id')
      expect(task).toHaveProperty('user_id')
      expect(task).toHaveProperty('title')
      expect(task).toHaveProperty('completed')
      expect(task).toHaveProperty('priority')
      expect(task).toHaveProperty('created_at')
      expect(task).toHaveProperty('updated_at')

      // Field types
      expect(typeof task.id).toBe('number')
      expect(typeof task.user_id).toBe('number')
      expect(typeof task.title).toBe('string')
      expect(typeof task.completed).toBe('boolean')
      expect(['low', 'medium', 'high']).toContain(task.priority)
    }
  })

  test('create task accepts TaskCreate and returns Task', async () => {
    const taskData: TaskCreate = {
      title: 'Test task',
      description: 'Test description',
      priority: 'high',
    }

    const task = await tasksApi.create(userId, taskData)

    expect(task).toHaveProperty('id')
    expect(task.title).toBe(taskData.title)
    expect(task.description).toBe(taskData.description)
    expect(task.priority).toBe(taskData.priority)
  })

  test('create task validates required fields', async () => {
    // @ts-expect-error - Testing invalid data
    const taskData: TaskCreate = {
      description: 'Missing title',
    }

    await expect(tasksApi.create(userId, taskData)).rejects.toThrow()
  })
})
```

## Contract Evolution

### Non-Breaking Changes (Safe)

```yaml
# ✅ Adding optional fields
TaskCreate:
  properties:
    title: string
    priority: string
    tags: string[]  # NEW optional field
```

### Breaking Changes (Require Versioning)

```yaml
# ❌ Removing required fields
Task:
  properties:
    # id: integer  # REMOVED - BREAKING!
    title: string

# ❌ Changing field types
Task:
  properties:
    priority: integer  # Changed from string - BREAKING!

# ❌ Renaming fields
Task:
  properties:
    task_title: string  # Renamed from "title" - BREAKING!
```

## Continuous Contract Validation

### GitHub Actions

```yaml
# .github/workflows/contract-test.yml
name: API Contract Tests

on: [push, pull_request]

jobs:
  contract-test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Start backend
        run: |
          cd backend
          uv sync
          uv run uvicorn app.main:app &
          sleep 5

      - name: Validate OpenAPI spec
        run: |
          curl http://localhost:8000/openapi.json > openapi.json
          npx @openapitools/openapi-generator-cli validate -i openapi.json

      - name: Run backend contract tests
        run: |
          cd backend
          uv run pytest tests/test_contract.py

      - name: Generate TypeScript types
        run: |
          cd frontend
          pnpm install
          pnpm generate-types

      - name: Run frontend contract tests
        run: |
          cd frontend
          pnpm test __tests__/api-contract.test.ts
```

## Integration with api-contract-validator Subagent

This skill is primarily used by:
- **api-contract-validator** - For validating API contracts
- **backend-api-dev** - For implementing contract-compliant endpoints
- **frontend-react-dev** - For consuming APIs according to contract

### Key Principles

1. **Contract-First Development** - Define OpenAPI spec before implementation
2. **Auto-Generation** - Generate TypeScript types from OpenAPI spec
3. **Continuous Validation** - Run contract tests on every commit
4. **Type Safety** - Use generated types in frontend for compile-time safety
5. **Error Structures** - Standardize error response formats
6. **Versioning** - Plan for API versioning when breaking changes needed
