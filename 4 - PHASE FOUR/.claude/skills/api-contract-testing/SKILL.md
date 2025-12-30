# API Contract Testing

**Skill**: api-contract-testing
**Version**: 1.0.0
**Primary Users**: backend-api-developer, api-contract-validator
**Prerequisites**: Pydantic, FastAPI, pytest

## Purpose
Implement contract-first API development with OpenAPI schemas, request/response validation, and contract testing between frontend and backend.

## Core Patterns

### Pydantic Schemas for MCP Tools
```python
from pydantic import BaseModel, Field

class AddTaskInput(BaseModel):
    user_id: str = Field(..., description="User ID from JWT token")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str | None = Field(None, max_length=1000)
    priority: str | None = Field(None, pattern="^(high|medium|low)$")
    tags: str | None = Field(None, max_length=500)
    due_date: str | None = Field(None, description="ISO 8601 date")
    due_time: str | None = Field(None, pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    recurrence: str | None = Field(None, pattern="^(daily|weekly|monthly)$")
    recurrence_day: int | None = Field(None, ge=1, le=31)

class AddTaskOutput(BaseModel):
    task_id: int = Field(..., description="ID of created task")
    status: str = Field(..., pattern="^(created|error)$")
    title: str
    message: str | None = None
```

### MCP Tool Implementation
```python
from mcp import MCPServer

server = MCPServer()

@server.tool(
    name="add_task",
    description="Create a new task for the user",
    input_schema=AddTaskInput.schema(),
    output_schema=AddTaskOutput.schema()
)
async def add_task(input: AddTaskInput) -> AddTaskOutput:
    # Pydantic automatically validates input
    task = Task(
        user_id=input.user_id,
        title=input.title,
        description=input.description,
        priority=input.priority,
        tags=input.tags
    )
    session.add(task)
    await session.commit()
    
    return AddTaskOutput(
        task_id=task.id,
        status="created",
        title=task.title
    )
```

### Contract Testing with pytest
```python
import pytest
from pydantic import ValidationError

def test_add_task_input_validation():
    # Valid input
    valid_input = AddTaskInput(
        user_id="user123",
        title="Buy groceries",
        priority="high"
    )
    assert valid_input.title == "Buy groceries"

def test_add_task_input_validation_errors():
    # Invalid: title too short
    with pytest.raises(ValidationError) as exc_info:
        AddTaskInput(user_id="user123", title="")
    assert "min_length" in str(exc_info.value)

    # Invalid: priority not in enum
    with pytest.raises(ValidationError) as exc_info:
        AddTaskInput(user_id="user123", title="Task", priority="urgent")
    assert "pattern" in str(exc_info.value)

def test_add_task_output_schema():
    # Valid output
    output = AddTaskOutput(
        task_id=1,
        status="created",
        title="Task title"
    )
    assert output.status == "created"

    # Invalid: status not in enum
    with pytest.raises(ValidationError):
        AddTaskOutput(task_id=1, status="invalid", title="Task")
```

### Integration Contract Test
```python
@pytest.mark.asyncio
async def test_add_task_contract():
    # Arrange: Create valid input
    input_data = {
        "user_id": "test_user",
        "title": "Test task",
        "priority": "high",
        "tags": "work,important"
    }
    
    # Act: Call MCP tool
    result = await add_task(AddTaskInput(**input_data))
    
    # Assert: Validate output schema
    assert isinstance(result, AddTaskOutput)
    assert result.status == "created"
    assert result.task_id > 0
    assert result.title == "Test task"
```

### FastAPI Request/Response Validation
```python
from fastapi import FastAPI, Body
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    conversation_id: int | None = None
    message: str = Field(..., min_length=1, max_length=5000)

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: list[str] = []

@app.post("/api/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest = Body(...)
):
    # FastAPI automatically validates request against ChatRequest schema
    # and serializes response to ChatResponse schema
    return ChatResponse(
        conversation_id=1,
        response="Task created",
        tool_calls=["add_task"]
    )
```

### Frontend TypeScript Types from Schemas
```typescript
// frontend/types/chat.ts
export interface ChatRequest {
  conversation_id?: number;
  message: string;
}

export interface ChatResponse {
  conversation_id: number;
  response: string;
  tool_calls: string[];
}

export interface AddTaskInput {
  user_id: string;
  title: string;
  description?: string;
  priority?: 'high' | 'medium' | 'low';
  tags?: string;
  due_date?: string;
  due_time?: string;
  recurrence?: 'daily' | 'weekly' | 'monthly';
  recurrence_day?: number;
}
```

## Best Practices
- Define schemas before implementation (contract-first)
- Use Field() for constraints (min_length, max_length, pattern)
- Test schema validation with pytest
- Document schemas with description field
- Use Literal or pattern for enums
- Generate TypeScript types from Pydantic schemas
- Write contract tests before implementation (TDD)

## Contract Documentation
```python
# Document in contracts/mcp-tools.md
# Tool: add_task

**Input Schema:**
- user_id (str, required): User ID from JWT token
- title (str, required): Task title (1-200 chars)
- priority (str, optional): "high" | "medium" | "low"

**Output Schema:**
- task_id (int): ID of created task
- status (str): "created" | "error"
- title (str): Task title

**Example:**
Input: {"user_id": "user123", "title": "Buy milk", "priority": "high"}
Output: {"task_id": 5, "status": "created", "title": "Buy milk"}
```

## Contract Validation Workflow
1. Define Pydantic schemas (Input/Output)
2. Write contract tests (validate schemas)
3. Document in contracts/ directory
4. Implement MCP tool using schemas
5. Run contract tests (ensure compliance)
6. Generate TypeScript types for frontend

## Related Skills
fastapi-sqlmodel, type-safety, testing-patterns, openapi-validation

See examples.md for complete contract testing workflows.
