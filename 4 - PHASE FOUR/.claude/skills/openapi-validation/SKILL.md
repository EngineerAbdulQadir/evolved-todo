---
name: openapi-validation
description: OpenAPI schema validation, automatic schema generation from Pydantic models, and API documentation.
---

# OpenAPI Validation

## Instructions

### When to Use

- Generating OpenAPI schemas from FastAPI endpoints
- Validating request/response schemas automatically
- Creating API documentation with Swagger UI
- Enforcing API contracts with Pydantic models
- Versioning API schemas
- Validating OpenAPI specification compliance

## FastAPI OpenAPI Auto-Generation

FastAPI automatically generates OpenAPI schemas from Pydantic models and type hints:

### Basic Endpoint with Schema

```python
# app/api/routes/tasks.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

# Request schema (auto-documented in OpenAPI)
class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    priority: str = Field("medium", pattern="^(low|medium|high)$", description="Task priority level")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "title": "Complete project",
                "description": "Finish the todo app",
                "priority": "high"
            }]
        }
    }

# Response schema (auto-documented in OpenAPI)
class TaskResponse(BaseModel):
    """Schema for task responses."""
    id: int = Field(..., description="Task ID")
    title: str
    description: Optional[str]
    priority: str
    completed: bool
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}

@router.post(
    "/",
    response_model=TaskResponse,
    status_code=201,
    summary="Create a new task",
    description="Create a new task with title, description, and priority",
    responses={
        201: {
            "description": "Task created successfully",
            "model": TaskResponse
        },
        400: {
            "description": "Invalid request data",
            "content": {
                "application/json": {
                    "example": {"detail": "Validation error message"}
                }
            }
        },
        401: {
            "description": "Unauthorized - invalid or missing token"
        }
    }
)
async def create_task(task_data: TaskCreate) -> TaskResponse:
    """
    Create a new task.

    This endpoint accepts a task creation request and returns the created task.
    """
    # Implementation
    pass
```

## Accessing OpenAPI Documentation

FastAPI provides multiple documentation endpoints:

```python
# app/main.py
from fastapi import FastAPI

app = FastAPI(
    title="Evolved Todo API",
    description="Full-stack todo application REST API",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc
    openapi_url="/openapi.json"  # OpenAPI JSON schema
)

# Access documentation at:
# - http://localhost:8000/docs (Swagger UI)
# - http://localhost:8000/redoc (ReDoc)
# - http://localhost:8000/openapi.json (Raw OpenAPI spec)
```

## Custom OpenAPI Schema

### Customizing OpenAPI Generation

```python
# app/main.py
from fastapi.openapi.utils import get_openapi

app = FastAPI()

def custom_openapi():
    """Custom OpenAPI schema generator."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Evolved Todo API",
        version="1.0.0",
        description="Full-stack todo application REST API",
        routes=app.routes,
    )

    # Add custom security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token from Better Auth"
        }
    }

    # Add global security requirement
    openapi_schema["security"] = [{"BearerAuth": []}]

    # Add custom tags
    openapi_schema["tags"] = [
        {
            "name": "tasks",
            "description": "Operations related to tasks"
        },
        {
            "name": "users",
            "description": "Operations related to users"
        }
    ]

    # Add API server info
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.example.com",
            "description": "Production server"
        }
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

## Request Validation

### Automatic Validation with Pydantic

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class TaskCreate(BaseModel):
    """Task creation schema with validation."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: str = Field("medium")

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Validate priority is one of allowed values."""
        allowed = ["low", "medium", "high"]
        if v not in allowed:
            raise ValueError(f"Priority must be one of: {', '.join(allowed)}")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty or whitespace."""
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()

@router.post("/")
async def create_task(task_data: TaskCreate):
    """
    FastAPI automatically validates request body against TaskCreate schema.

    Returns 422 Unprocessable Entity if validation fails.
    """
    # If we reach here, task_data is guaranteed to be valid
    pass
```

### Validation Error Response

When validation fails, FastAPI returns a 422 status with details:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1}
    },
    {
      "type": "value_error",
      "loc": ["body", "priority"],
      "msg": "Value error, Priority must be one of: low, medium, high",
      "input": "urgent"
    }
  ]
}
```

## Response Validation

### Response Model Enforcement

```python
from pydantic import BaseModel

class TaskResponse(BaseModel):
    """Enforced response schema."""
    id: int
    title: str
    completed: bool

    model_config = {"from_attributes": True}

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int):
    """
    FastAPI automatically validates response against TaskResponse schema.

    - Filters out extra fields not in TaskResponse
    - Validates field types
    - Converts SQLModel objects to Pydantic models
    """
    task = await task_service.get_task(task_id)
    return task  # FastAPI converts to TaskResponse automatically
```

### Multiple Response Models

```python
from typing import Union

class TaskResponse(BaseModel):
    id: int
    title: str

class TaskDetailResponse(TaskResponse):
    description: Optional[str]
    created_at: str
    updated_at: str

@router.get(
    "/{task_id}",
    response_model=Union[TaskResponse, TaskDetailResponse],
    responses={
        200: {
            "description": "Task found",
            "model": TaskDetailResponse
        },
        404: {
            "description": "Task not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Task not found"}
                }
            }
        }
    }
)
async def get_task(task_id: int, detailed: bool = False):
    """Return basic or detailed task based on query parameter."""
    task = await task_service.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if detailed:
        return TaskDetailResponse.model_validate(task)
    else:
        return TaskResponse.model_validate(task)
```

## OpenAPI Schema Validation

### Validating Generated Schema

```python
# tests/test_openapi.py
import pytest
from fastapi.testclient import TestClient
from openapi_spec_validator import validate_spec
import json

from app.main import app

def test_openapi_spec_is_valid():
    """Test that generated OpenAPI spec is valid."""
    client = TestClient(app)

    # Get OpenAPI spec
    response = client.get("/openapi.json")
    assert response.status_code == 200

    spec = response.json()

    # Validate against OpenAPI 3.0 specification
    validate_spec(spec)

def test_openapi_has_required_info():
    """Test that OpenAPI spec has required metadata."""
    client = TestClient(app)
    response = client.get("/openapi.json")
    spec = response.json()

    # Check required fields
    assert "openapi" in spec
    assert "info" in spec
    assert "title" in spec["info"]
    assert "version" in spec["info"]
    assert "paths" in spec

def test_openapi_documents_all_endpoints():
    """Test that all endpoints are documented."""
    client = TestClient(app)
    response = client.get("/openapi.json")
    spec = response.json()

    # Check critical endpoints exist
    assert "/api/tasks" in spec["paths"]
    assert "/api/tasks/{task_id}" in spec["paths"]
    assert "get" in spec["paths"]["/api/tasks"]
    assert "post" in spec["paths"]["/api/tasks"]

def test_openapi_schemas_defined():
    """Test that request/response schemas are defined."""
    client = TestClient(app)
    response = client.get("/openapi.json")
    spec = response.json()

    schemas = spec["components"]["schemas"]

    # Check critical schemas exist
    assert "TaskCreate" in schemas
    assert "TaskResponse" in schemas

    # Check schema structure
    task_create = schemas["TaskCreate"]
    assert "properties" in task_create
    assert "title" in task_create["properties"]
    assert "required" in task_create
    assert "title" in task_create["required"]
```

## Exporting OpenAPI Spec

### Save to File

```python
# scripts/export_openapi.py
import json
from app.main import app

def export_openapi_spec(output_file: str = "openapi.json"):
    """Export OpenAPI spec to JSON file."""
    with open(output_file, "w") as f:
        json.dump(app.openapi(), f, indent=2)
    print(f"OpenAPI spec exported to {output_file}")

if __name__ == "__main__":
    export_openapi_spec()
```

```bash
# Export OpenAPI spec
python scripts/export_openapi.py
```

### Generate TypeScript Types

```bash
# Generate TypeScript types from OpenAPI spec
npx openapi-typescript http://localhost:8000/openapi.json -o frontend/lib/api-types.ts
```

## API Versioning

### URL-Based Versioning

```python
# app/api/v1/routes/tasks.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks-v1"])

@router.get("/")
async def list_tasks_v1():
    """Version 1 of list tasks endpoint."""
    pass

# app/api/v2/routes/tasks.py
router = APIRouter(prefix="/api/v2/tasks", tags=["tasks-v2"])

@router.get("/")
async def list_tasks_v2():
    """Version 2 of list tasks endpoint with enhanced features."""
    pass

# app/main.py
from app.api.v1.routes import tasks as tasks_v1
from app.api.v2.routes import tasks as tasks_v2

app.include_router(tasks_v1.router)
app.include_router(tasks_v2.router)
```

## Integration with api-contract-validator Subagent

This skill is primarily used by:
- **api-contract-validator** - For validating OpenAPI schemas
- **backend-api-dev** - For implementing schema-compliant endpoints

### Key Principles

1. **Type Annotations** - Use Pydantic models with proper type hints
2. **Validation** - Let FastAPI handle request/response validation
3. **Documentation** - Add descriptions and examples to schemas
4. **Schema Validation** - Test OpenAPI spec validity
5. **Error Responses** - Document all possible error responses
6. **Versioning** - Plan for API versioning from the start
