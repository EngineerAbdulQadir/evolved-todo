"""
MCP Server Transports for Standalone Hosting

Implements stdio and Streamable HTTP transports for the MCP server,
enabling both local development and remote hosting capabilities.

Reference: https://modelcontextprotocol.io/specification/2025-06-18/basic/transports
Transport Guide: https://docs.roocode.com/features/mcp/server-transports
"""

from typing import Any, Dict, Optional
import asyncio
import json
import logging
from contextlib import asynccontextmanager

from mcp.server import Server
from mcp.server.stdio import stdio_server
from fastapi import FastAPI, Request, Response, HTTPException, Header
from fastapi.responses import StreamingResponse, JSONResponse
from sse_starlette.sse import EventSourceResponse

logger = logging.getLogger(__name__)


class StdioTransport:
    """
    Standard Input/Output transport for local MCP server.

    Use case: Local CLI tools, development, single-client scenarios.
    Communication: stdin/stdout JSON-RPC messages.
    """

    def __init__(self, server: Server):
        self.server = server

    async def run(self) -> None:
        """Run MCP server with stdio transport."""
        logger.info("Starting MCP server with stdio transport")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


class StreamableHTTPTransport:
    """
    Streamable HTTP transport for remote MCP server hosting.

    Use case: Production deployments, multiple clients, cloud hosting.
    Communication: HTTP POST/GET with optional SSE streaming.

    Protocol:
    - POST /mcp/messages - Send messages (JSON-RPC)
    - GET /mcp/messages - Receive streamed responses (SSE)
    - GET /health - Health check endpoint

    Reference: https://mcpcat.io/guides/comparing-stdio-sse-streamablehttp/
    """

    def __init__(
        self,
        server: Server,
        host: str = "0.0.0.0",
        port: int = 8001,
        api_keys: Optional[list[str]] = None,
    ):
        self.server = server
        self.host = host
        self.port = port
        self.api_keys = api_keys or []
        self.app = FastAPI(title="MCP Todo Server", version="1.0.0")
        self._setup_routes()
        self._sessions: Dict[str, Any] = {}

    def _verify_api_key(self, authorization: Optional[str]) -> bool:
        """Verify API key from Authorization header."""
        if not self.api_keys:
            # No API keys configured, allow all (development mode)
            return True

        if not authorization:
            return False

        # Expected format: "Bearer <api_key>"
        if not authorization.startswith("Bearer "):
            return False

        api_key = authorization[7:]  # Remove "Bearer " prefix
        return api_key in self.api_keys

    def _setup_routes(self) -> None:
        """Setup FastAPI routes for MCP protocol."""

        @self.app.post("/mcp/messages")
        async def handle_message(
            request: Request,
            authorization: Optional[str] = Header(None),
        ) -> JSONResponse:
            """
            Handle incoming MCP messages (JSON-RPC).

            Request body: JSON-RPC 2.0 message
            Response: JSON-RPC 2.0 response
            """
            # Verify API key
            if not self._verify_api_key(authorization):
                raise HTTPException(status_code=401, detail="Invalid or missing API key")

            try:
                message = await request.json()
                logger.info(f"Received MCP message: {message.get('method', 'unknown')}")

                # Process message with MCP server
                # Note: This is a simplified implementation
                # Real implementation would use proper JSON-RPC handling
                method = message.get("method")
                params = message.get("params", {})
                msg_id = message.get("id")

                if method == "tools/list":
                    # List available tools
                    tools = await self._list_tools()
                    return JSONResponse({
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {"tools": tools}
                    })

                elif method == "tools/call":
                    # Call a tool
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    result = await self._call_tool(tool_name, arguments)
                    return JSONResponse({
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": result
                    })

                else:
                    return JSONResponse({
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    }, status_code=400)

            except Exception as e:
                logger.error(f"Error handling MCP message: {e}", exc_info=True)
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": message.get("id") if isinstance(message, dict) else None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }, status_code=500)

        @self.app.get("/mcp/messages")
        async def stream_messages(
            request: Request,
            authorization: Optional[str] = Header(None),
        ) -> EventSourceResponse:
            """
            Stream MCP server events via SSE.

            Used for receiving asynchronous notifications and streaming responses.
            """
            # Verify API key
            if not self._verify_api_key(authorization):
                raise HTTPException(status_code=401, detail="Invalid or missing API key")

            async def event_generator():
                """Generate SSE events."""
                try:
                    # This is a placeholder for SSE streaming
                    # Real implementation would yield events from server
                    yield {
                        "event": "connected",
                        "data": json.dumps({"status": "connected"})
                    }

                    # Keep connection alive
                    while True:
                        await asyncio.sleep(30)
                        yield {
                            "event": "ping",
                            "data": json.dumps({"timestamp": asyncio.get_event_loop().time()})
                        }

                except asyncio.CancelledError:
                    logger.info("SSE connection closed")

            return EventSourceResponse(event_generator())

        @self.app.get("/health")
        async def health_check() -> JSONResponse:
            """Health check endpoint for load balancers and monitoring."""
            return JSONResponse({
                "status": "healthy",
                "service": "mcp-todo-server",
                "version": "1.0.0"
            })

        @self.app.get("/")
        async def root() -> JSONResponse:
            """Root endpoint with server information."""
            return JSONResponse({
                "name": "MCP Todo Server",
                "version": "1.0.0",
                "description": "Standalone MCP server for task management",
                "endpoints": {
                    "messages": "/mcp/messages (POST/GET)",
                    "health": "/health",
                    "docs": "/docs"
                },
                "transport": "Streamable HTTP",
                "tools_count": len(getattr(self.server, '_tools', {}))
            })

    async def _list_tools(self) -> list[Dict[str, Any]]:
        """List available tools from MCP server."""
        # Access the server's tool list handler
        # This requires the server to have tools registered
        try:
            # Call the list_tools handler if registered
            if hasattr(self.server, '_list_tools_handler'):
                tools = await self.server._list_tools_handler()
                return [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    }
                    for tool in tools
                ]
            return []
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return []

    async def _call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server."""
        try:
            # Call the tool handler if registered
            if hasattr(self.server, '_call_tool_handler'):
                result = await self.server._call_tool_handler(name, arguments)
                return {
                    "content": [
                        {
                            "type": content.type,
                            "text": content.text
                        }
                        for content in result
                    ]
                }

            return {
                "error": "Tool handler not configured"
            }
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}", exc_info=True)
            return {
                "error": str(e)
            }

    async def run(self) -> None:
        """Run MCP server with HTTP transport."""
        import uvicorn

        logger.info(f"Starting MCP server with Streamable HTTP transport on {self.host}:{self.port}")
        if self.api_keys:
            logger.info(f"API key authentication enabled ({len(self.api_keys)} keys configured)")
        else:
            logger.warning("API key authentication DISABLED - development mode only!")

        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="info",
            access_log=True,
        )
        server = uvicorn.Server(config)
        await server.serve()
