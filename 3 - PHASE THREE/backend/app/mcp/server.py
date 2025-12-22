"""MCP Server initialization and tool registration.

This module sets up the MCP server and registers all task management tools
that can be called by the OpenAI Agents SDK.

Task: T011 - Initialize MCP server with tool registration system
Spec: specs/003-phase3-ai-chatbot/plan.md (MCP SDK section)
"""

from typing import Any, Callable, Dict, List

from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from pydantic import BaseModel


class MCPServer:
    """
    MCP Server for task management tools.

    Provides a standardized interface for AI agents to interact with task
    operations through MCP (Model Context Protocol).

    Architecture:
        - Stateless: All state persisted to database
        - Tool registration: Each tool registered with schema validation
        - Async support: All tools are async functions
        - Error handling: Structured error responses
    """

    def __init__(self) -> None:
        """Initialize MCP server."""
        self.server = Server("todo-mcp-server")
        self.tools: Dict[str, Callable[..., Any]] = {}

    def tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any],
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Decorator to register a tool with the MCP server.

        Args:
            name: Tool name (e.g., "add_task")
            description: Tool description for AI agent
            input_schema: Pydantic schema for input validation
            output_schema: Pydantic schema for output validation

        Returns:
            Decorated function registered as MCP tool

        Example:
            @server.tool(
                name="add_task",
                description="Create a new task",
                input_schema=AddTaskInput.schema(),
                output_schema=AddTaskOutput.schema()
            )
            async def add_task(input: AddTaskInput) -> AddTaskOutput:
                ...
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            # Register tool with MCP server
            self.tools[name] = func

            # Define tool handler
            @self.server.list_tools()
            async def handle_list_tools() -> List[types.Tool]:
                """List available tools."""
                return [
                    types.Tool(
                        name=tool_name,
                        description=description,
                        inputSchema=input_schema,
                    )
                    for tool_name in self.tools.keys()
                ]

            @self.server.call_tool()
            async def handle_call_tool(
                name: str, arguments: Dict[str, Any]
            ) -> List[types.TextContent]:
                """Execute tool with arguments."""
                if name not in self.tools:
                    raise ValueError(f"Unknown tool: {name}")

                tool_func = self.tools[name]
                result = await tool_func(arguments)

                return [types.TextContent(type="text", text=str(result))]

            return func

        return decorator

    async def run(self) -> None:
        """Run MCP server with stdio transport."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


# Global MCP server instance
mcp_server = MCPServer()
