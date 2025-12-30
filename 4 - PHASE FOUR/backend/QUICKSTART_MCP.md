# MCP Server Quick Start Guide

## Get Your MCP Server Running in 5 Minutes

### Step 1: Install Dependencies

```bash
cd backend
uv sync
uv add sse-starlette
```

### Step 2: Configure Environment

Copy the example configuration:

```bash
cp .env.mcp.example .env
```

Edit `.env` and update:

```bash
# Required: Your Neon PostgreSQL URL
DATABASE_URL=postgresql+asyncpg://neondb_owner:your_password@your-host.aws.neon.tech/neondb?ssl=require

# Optional: API Keys (comma-separated)
MCP_API_KEYS=my-secure-key-1,my-secure-key-2
```

### Step 3: Start the Server

**HTTP Mode (Recommended):**

```bash
uv run python -m app.mcp.standalone
```

The server will start on `http://0.0.0.0:8001`

**stdio Mode (Local Only):**

```bash
MCP_TRANSPORT=stdio uv run python -m app.mcp.standalone
```

### Step 4: Test It

**Health Check:**

```bash
curl http://localhost:8001/health
```

**List Available Tools:**

```bash
curl -X POST http://localhost:8001/mcp/messages \
  -H "Authorization: Bearer my-secure-key-1" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

**Create a Task:**

```bash
curl -X POST http://localhost:8001/mcp/messages \
  -H "Authorization: Bearer my-secure-key-1" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "add_task",
      "arguments": {
        "user_id": "test-user",
        "title": "My first MCP task!"
      }
    }
  }'
```

---

## Connect External Clients

### Claude Desktop (HTTP Mode)

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "evolved-todo": {
      "url": "http://localhost:8001/mcp/messages",
      "headers": {
        "Authorization": "Bearer my-secure-key-1"
      }
    }
  }
}
```

Restart Claude Desktop and you'll see "evolved-todo" server with 6 tools!

### Claude Desktop (stdio Mode)

```json
{
  "mcpServers": {
    "evolved-todo": {
      "command": "uv",
      "args": ["run", "python", "-m", "app.mcp.standalone"],
      "cwd": "C:/path/to/evolved-todo/backend",
      "env": {
        "MCP_TRANSPORT": "stdio",
        "DATABASE_URL": "postgresql+asyncpg://..."
      }
    }
  }
}
```

---

## Docker Deployment

```bash
# Build image
docker build -f Dockerfile.mcp -t evolved-todo-mcp .

# Run container
docker run -p 8001:8001 \
  -e DATABASE_URL="your-db-url" \
  -e MCP_API_KEYS="key1,key2" \
  evolved-todo-mcp

# Or use docker-compose
docker-compose -f docker-compose.mcp.yml up -d
```

---

## Available Tools

Your MCP server exposes **6 task management tools**:

1. **add_task** - Create new tasks
2. **list_tasks** - View tasks with filters
3. **complete_task** - Mark tasks complete
4. **update_task** - Modify task properties
5. **delete_task** - Remove tasks
6. **search_tasks** - Find tasks by keyword

All tools require `user_id` parameter for data isolation.

---

## Troubleshooting

**Server won't start?**

Check your `.env` file has valid `DATABASE_URL`

**Authentication errors?**

Make sure you're using the correct API key in the `Authorization: Bearer <key>` header

**Can't connect from Claude Desktop?**

- HTTP mode: Make sure server is running and URL is correct
- stdio mode: Check `cwd` path is absolute and points to backend directory

---

## Next Steps

- Read full documentation: [MCP_SERVER.md](./MCP_SERVER.md)
- Deploy to production: See Docker/Kubernetes sections
- Add custom tools: Extend the tool registry
- Monitor usage: Add logging and metrics

**Questions?** Check the [MCP specification](https://modelcontextprotocol.io/) or open an issue.
