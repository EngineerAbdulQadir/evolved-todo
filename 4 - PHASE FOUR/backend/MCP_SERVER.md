# Standalone MCP Server Documentation

## Overview

The Evolved Todo MCP Server is a **standalone Model Context Protocol server** that exposes task management tools to external MCP clients like Claude Desktop, IDEs, and other AI applications.

### Features

- ✅ **6 Task Management Tools**: add_task, list_tasks, complete_task, update_task, delete_task, search_tasks
- ✅ **Dual Transport Support**: stdio (local) and Streamable HTTP (remote)
- ✅ **API Key Authentication**: Secure access control for HTTP transport
- ✅ **Database-Backed**: Neon PostgreSQL with stateless architecture
- ✅ **Production-Ready**: Docker support, health checks, logging
- ✅ **MCP 2025 Compliant**: Follows latest MCP specification

### Architecture

```
External MCP Clients
(Claude Desktop, IDEs, etc.)
         ↓
   Transport Layer
   (stdio or HTTP)
         ↓
   MCP Protocol Handler
   (JSON-RPC messages)
         ↓
    Tool Registry
    (6 task tools)
         ↓
  Database (Neon PostgreSQL)
```

---

## Quick Start

### 1. Install Dependencies

```bash
cd backend
uv sync
```

### 2. Configure Environment

Create or update `.env` file:

```bash
# Required
DATABASE_URL=postgresql+asyncpg://user:pass@host/db

# Optional (HTTP mode)
MCP_TRANSPORT=http              # stdio or http (default: http)
MCP_HOST=0.0.0.0                # HTTP server host
MCP_PORT=8001                   # HTTP server port
MCP_API_KEYS=key1,key2,key3     # Comma-separated API keys
LOG_LEVEL=INFO                  # Logging level
```

### 3. Run the Server

**Option A: HTTP Transport (Remote Access)**

```bash
uv run python -m app.mcp.standalone
```

Server will start on `http://0.0.0.0:8001`

**Option B: stdio Transport (Local Only)**

```bash
MCP_TRANSPORT=stdio uv run python -m app.mcp.standalone
```

Server will communicate via stdin/stdout

---

## Transport Modes

### stdio Transport

**Use Case**: Local development, CLI tools, single-client scenarios

**Pros:**
- ✅ Simple setup
- ✅ No network configuration
- ✅ Direct process communication

**Cons:**
- ❌ Single client only
- ❌ Cannot host remotely
- ❌ Process must be spawned by client

**Example Usage with Claude Desktop**:

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "evolved-todo": {
      "command": "uv",
      "args": ["run", "python", "-m", "app.mcp.standalone"],
      "cwd": "/path/to/evolved-todo/backend",
      "env": {
        "MCP_TRANSPORT": "stdio",
        "DATABASE_URL": "postgresql+asyncpg://..."
      }
    }
  }
}
```

### Streamable HTTP Transport

**Use Case**: Production deployments, multiple clients, cloud hosting

**Pros:**
- ✅ Multiple concurrent clients
- ✅ Network accessible
- ✅ Works with load balancers
- ✅ Modern standard (MCP 2025)

**Cons:**
- ⚠️ Requires network configuration
- ⚠️ Need API key authentication

**Endpoints:**

```
POST   /mcp/messages       - Send JSON-RPC messages
GET    /mcp/messages       - Receive SSE streamed events
GET    /health             - Health check
GET    /                   - Server info
GET    /docs               - API documentation (FastAPI)
```

**Example Request**:

```bash
# List available tools
curl -X POST http://localhost:8001/mcp/messages \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'

# Call add_task tool
curl -X POST http://localhost:8001/mcp/messages \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "add_task",
      "arguments": {
        "user_id": "user123",
        "title": "Buy groceries",
        "priority": "high"
      }
    }
  }'
```

---

## Available Tools

### 1. add_task

Create a new task.

**Input:**
```json
{
  "user_id": "string (required)",
  "title": "string (required)",
  "description": "string (optional)",
  "priority": "high|medium|low (optional)",
  "tags": ["tag1", "tag2"] (optional),
  "due_date": "YYYY-MM-DD (optional)",
  "due_time": "HH:MM (optional)",
  "recurrence": "daily|weekly|monthly (optional)",
  "recurrence_day": 1-31 (optional)
}
```

**Output:**
```json
{
  "status": "success",
  "task_id": 123,
  "title": "Buy groceries",
  "message": "Task created successfully"
}
```

### 2. list_tasks

Retrieve tasks with filtering and sorting.

**Input:**
```json
{
  "user_id": "string (required)",
  "status": "pending|completed|all (optional)",
  "priority": "high|medium|low (optional)",
  "tag": "string (optional)",
  "sort_by": "created_at|due_date|priority|title (optional)",
  "sort_order": "asc|desc (optional)"
}
```

**Output:**
```json
{
  "status": "success",
  "tasks": [...],
  "count": 5
}
```

### 3. complete_task

Mark task as complete.

**Input:**
```json
{
  "user_id": "string (required)",
  "task_id": 123 (required)
}
```

**Output:**
```json
{
  "status": "success",
  "task_id": 123,
  "title": "Buy groceries",
  "message": "Task completed successfully"
}
```

### 4. update_task

Update task properties.

**Input:**
```json
{
  "user_id": "string (required)",
  "task_id": 123 (required)",
  "title": "string (optional)",
  "description": "string (optional)",
  "priority": "high|medium|low (optional)",
  "tags": "comma,separated,tags (optional)",
  "due_date": "YYYY-MM-DD (optional)",
  "due_time": "HH:MM (optional)"
}
```

### 5. delete_task

Delete a task.

**Input:**
```json
{
  "user_id": "string (required)",
  "task_id": 123 (required)
}
```

### 6. search_tasks

Search tasks by keyword.

**Input:**
```json
{
  "user_id": "string (required)",
  "keyword": "string (required)"
}
```

---

## Docker Deployment

### Build and Run with Docker

```bash
# Build image
docker build -f Dockerfile.mcp -t evolved-todo-mcp-server .

# Run container
docker run -p 8001:8001 \
  -e DATABASE_URL="postgresql+asyncpg://..." \
  -e MCP_API_KEYS="key1,key2" \
  evolved-todo-mcp-server
```

### Docker Compose

```bash
# Start server
docker-compose -f docker-compose.mcp.yml up -d

# View logs
docker-compose -f docker-compose.mcp.yml logs -f

# Stop server
docker-compose -f docker-compose.mcp.yml down
```

---

## Authentication

### API Key Setup

**Generate API Keys:**

```bash
# Generate secure random API keys
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Configure:**

```bash
# .env file
MCP_API_KEYS=key1,key2,key3
```

**Use in Requests:**

```bash
curl -H "Authorization: Bearer key1" http://localhost:8001/mcp/messages
```

### Development Mode (No Auth)

To disable authentication for local development:

```bash
# Leave MCP_API_KEYS empty
MCP_API_KEYS=
```

⚠️ **Warning**: Only use in development. Never deploy without authentication!

---

## Production Deployment

### Recommended Stack

- **Platform**: Railway, Fly.io, or Kubernetes
- **Load Balancer**: Nginx or Traefik
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack or CloudWatch

### Environment Configuration

```bash
# Production .env
MCP_TRANSPORT=http
MCP_HOST=0.0.0.0
MCP_PORT=8001
MCP_API_KEYS=prod-key-1,prod-key-2,prod-key-3
DATABASE_URL=postgresql+asyncpg://prod-db-url
LOG_LEVEL=INFO
```

### Health Checks

The server exposes `/health` endpoint for monitoring:

```bash
curl http://localhost:8001/health
# Returns: {"status": "healthy", "service": "mcp-todo-server", "version": "1.0.0"}
```

### Scaling

The server is **stateless** (all state in database), so you can:

- ✅ Run multiple instances behind load balancer
- ✅ Use horizontal pod autoscaling (Kubernetes)
- ✅ Deploy across multiple regions
- ✅ Handle thousands of concurrent clients

---

## Testing

### Test with curl

```bash
# Health check
curl http://localhost:8001/health

# Server info
curl http://localhost:8001/

# List tools
curl -X POST http://localhost:8001/mcp/messages \
  -H "Authorization: Bearer your-key" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'

# Add a task
curl -X POST http://localhost:8001/mcp/messages \
  -H "Authorization: Bearer your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "add_task",
      "arguments": {
        "user_id": "test-user",
        "title": "Test task from MCP"
      }
    }
  }'
```

### Test with Python Client

```python
import requests
import json

url = "http://localhost:8001/mcp/messages"
headers = {
    "Authorization": "Bearer your-api-key",
    "Content-Type": "application/json"
}

# List tools
response = requests.post(url, headers=headers, json={
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
})
print(json.dumps(response.json(), indent=2))

# Call add_task
response = requests.post(url, headers=headers, json={
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "add_task",
        "arguments": {
            "user_id": "test-user",
            "title": "Buy groceries"
        }
    }
})
print(json.dumps(response.json(), indent=2))
```

---

## Connecting External Clients

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

**HTTP Mode:**
```json
{
  "mcpServers": {
    "evolved-todo-http": {
      "url": "http://your-server:8001/mcp/messages",
      "headers": {
        "Authorization": "Bearer your-api-key"
      }
    }
  }
}
```

**stdio Mode:**
```json
{
  "mcpServers": {
    "evolved-todo-stdio": {
      "command": "uv",
      "args": ["run", "python", "-m", "app.mcp.standalone"],
      "cwd": "/path/to/backend",
      "env": {
        "MCP_TRANSPORT": "stdio",
        "DATABASE_URL": "postgresql+asyncpg://..."
      }
    }
  }
}
```

### VS Code / Cursor

Use MCP extension and configure server URL.

### Custom Applications

Use any HTTP client or MCP SDK to connect:

- Python: Use `requests` or `httpx`
- JavaScript: Use `fetch` or `axios`
- MCP SDK: Use official MCP Python/TypeScript SDK

---

## Troubleshooting

### Server won't start

**Check database connection:**
```bash
python -c "from app.core.database import get_session; import asyncio; asyncio.run(list(get_session()).__anext__())"
```

**Check environment variables:**
```bash
python -c "from app.mcp.config import get_config; print(get_config())"
```

### Authentication errors

**Verify API key format:**
- Must use `Authorization: Bearer <key>` header
- Check MCP_API_KEYS in .env is comma-separated
- No spaces around commas

### Tool execution errors

**Check user_id:**
- All tools require valid `user_id` parameter
- User must exist in database

**Check database permissions:**
- Verify database user has SELECT, INSERT, UPDATE, DELETE permissions

---

## References

- [MCP Specification (2025-06-18)](https://modelcontextprotocol.io/specification/2025-06-18)
- [MCP Best Practices](https://modelcontextprotocol.info/docs/best-practices/)
- [Streamable HTTP Transport Guide](https://mcpcat.io/guides/comparing-stdio-sse-streamablehttp/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

---

## Support

For issues or questions:
- Check logs: `docker-compose logs -f mcp-server`
- Test health endpoint: `curl http://localhost:8001/health`
- Review error responses for details

---

**Version**: 1.0.0
**Last Updated**: 2025-12-25
**License**: MIT
