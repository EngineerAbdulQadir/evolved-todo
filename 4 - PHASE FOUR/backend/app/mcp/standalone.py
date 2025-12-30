"""
MCP Standalone Server Entry Point

Runs the MCP server as a standalone service that can be accessed
by external MCP clients like Claude Desktop, IDEs, or other tools.

Usage:
    # HTTP transport (default):
    uv run python -m app.mcp.standalone

    # stdio transport:
    MCP_TRANSPORT=stdio uv run python -m app.mcp.standalone

    # With API keys:
    MCP_API_KEYS="key1,key2,key3" uv run python -m app.mcp.standalone

Environment Variables:
    MCP_TRANSPORT - Transport mode: stdio or http (default: http)
    MCP_HOST - HTTP server host (default: 0.0.0.0)
    MCP_PORT - HTTP server port (default: 8001)
    MCP_API_KEYS - Comma-separated API keys for authentication
    DATABASE_URL - PostgreSQL connection string (required)
    LOG_LEVEL - Logging level (default: INFO)
"""

import asyncio
import logging
import sys
from typing import Any, Dict

from mcp.server import Server
from mcp import types

from app.mcp.config import get_config
from app.mcp.transports import StdioTransport, StreamableHTTPTransport
from app.mcp.tools.registry import get_all_tool_definitions

# Import tool implementations
from app.mcp.tools.add_task import add_task, AddTaskInput
from app.mcp.tools.list_tasks import list_tasks, ListTasksInput
from app.mcp.tools.complete_task import complete_task, CompleteTaskInput
from app.mcp.tools.update_task import update_task, UpdateTaskInput
from app.mcp.tools.delete_task import delete_task, DeleteTaskInput
from app.mcp.tools.search_tasks import search_tasks, SearchTasksInput


logger = logging.getLogger(__name__)


class StandaloneMCPServer:
    """
    Standalone MCP server for task management.

    Features:
    - 6 task management tools (add, list, complete, update, delete, search)
    - Supports stdio and HTTP transports
    - API key authentication for HTTP
    - Database-backed (Neon PostgreSQL)
    - Stateless architecture
    """

    def __init__(self):
        self.config = get_config()
        self.server = Server("todo-mcp-server")
        self.tools: Dict[str, Any] = {}

        # Store handlers for HTTP transport access
        self.server._list_tools_handler = None
        self.server._call_tool_handler = None

        self._register_tools()
        self._configure_logging()

    def _configure_logging(self) -> None:
        """Configure logging based on config."""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)]
        )

    def _register_tools(self) -> None:
        """Register all MCP tools with the server."""
        # Tool definitions
        tool_defs = get_all_tool_definitions()

        # Map tool names to implementations
        tool_implementations = {
            "add_task": add_task,
            "list_tasks": list_tasks,
            "complete_task": complete_task,
            "update_task": update_task,
            "delete_task": delete_task,
            "search_tasks": search_tasks,
        }

        # Register tools with server
        for tool_name, tool_func in tool_implementations.items():
            self.tools[tool_name] = tool_func
            logger.info(f"Registered tool: {tool_name}")

        # Setup MCP server handlers
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List all available tools."""
            logger.info("Listing tools")
            return [
                types.Tool(
                    name=tool_def["function"]["name"],
                    description=tool_def["function"]["description"],
                    inputSchema=tool_def["function"]["parameters"],
                )
                for tool_def in tool_defs
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> list[types.TextContent]:
            """Execute a tool with given arguments."""
            logger.info(f"Calling tool: {name} with arguments: {arguments}")

            if name not in self.tools:
                raise ValueError(f"Unknown tool: {name}")

            try:
                tool_func = self.tools[name]
                result = await tool_func(arguments)

                # Convert result to JSON string for MCP response
                import json
                result_text = json.dumps(result, default=str)

                return [
                    types.TextContent(
                        type="text",
                        text=result_text
                    )
                ]

            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}", exc_info=True)
                import json
                error_response = json.dumps({
                    "status": "error",
                    "error_code": "TOOL_EXECUTION_ERROR",
                    "message": str(e)
                })
                return [
                    types.TextContent(
                        type="text",
                        text=error_response
                    )
                ]

        # Store handlers for HTTP transport
        self.server._list_tools_handler = handle_list_tools
        self.server._call_tool_handler = handle_call_tool

        logger.info(f"Registered {len(self.tools)} tools with MCP server")

    async def run(self) -> None:
        """Run the MCP server with configured transport."""
        logger.info("=" * 60)
        logger.info("MCP TODO SERVER - STANDALONE MODE")
        logger.info("=" * 60)
        logger.info(f"Transport: {self.config.mcp_transport.upper()}")
        logger.info(f"Database: {self.config.database_url.split('@')[-1]}")  # Hide credentials
        logger.info(f"Tools: {len(self.tools)}")
        logger.info("=" * 60)

        if self.config.is_stdio_transport:
            # Run with stdio transport
            logger.info("Starting stdio transport (single client, local)")
            logger.info("Connect via stdin/stdout JSON-RPC")
            transport = StdioTransport(self.server)
            await transport.run()

        elif self.config.is_http_transport:
            # Run with HTTP transport
            logger.info(f"Starting HTTP transport on {self.config.mcp_host}:{self.config.mcp_port}")
            if self.config.api_keys_list:
                logger.info(f"API authentication: ENABLED ({len(self.config.api_keys_list)} keys)")
            else:
                logger.warning("API authentication: DISABLED (development mode only!)")

            logger.info("")
            logger.info("Endpoints:")
            logger.info(f"  POST http://{self.config.mcp_host}:{self.config.mcp_port}/mcp/messages")
            logger.info(f"  GET  http://{self.config.mcp_host}:{self.config.mcp_port}/mcp/messages")
            logger.info(f"  GET  http://{self.config.mcp_host}:{self.config.mcp_port}/health")
            logger.info("")

            transport = StreamableHTTPTransport(
                self.server,
                host=self.config.mcp_host,
                port=self.config.mcp_port,
                api_keys=self.config.api_keys_list,
            )
            await transport.run()

        else:
            raise ValueError(f"Invalid transport: {self.config.mcp_transport}")


async def main() -> None:
    """Main entry point for standalone MCP server."""
    try:
        server = StandaloneMCPServer()
        await server.run()
    except KeyboardInterrupt:
        logger.info("\nShutting down MCP server...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
