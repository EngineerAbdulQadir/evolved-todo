import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.mcp.server import MCPServer


@pytest.mark.asyncio
async def test_mcp_server_initialization():
    """Test MCP server initialization."""
    server = MCPServer()
    
    assert server.server is not None
    assert server.tools == {}


@pytest.mark.asyncio
async def test_mcp_server_tool_decorator():
    """Test MCP server tool decorator."""
    server = MCPServer()
    
    # Define a mock tool function
    async def mock_tool_func(input_args):
        return {"result": "success"}
    
    # Register the tool using the decorator
    input_schema = {"type": "object", "properties": {"name": {"type": "string"}}}
    output_schema = {"type": "object", "properties": {"result": {"type": "string"}}}
    
    decorated_func = server.tool(
        name="test_tool",
        description="A test tool",
        input_schema=input_schema,
        output_schema=output_schema
    )(mock_tool_func)
    
    # Check that the tool was registered
    assert "test_tool" in server.tools
    assert server.tools["test_tool"] == mock_tool_func


@pytest.mark.asyncio
async def test_mcp_server_run():
    """Test MCP server run method."""
    server = MCPServer()
    
    # Mock the stdio_server context manager
    with patch('app.mcp.server.stdio_server') as mock_stdio_server:
        mock_context_manager = AsyncMock()
        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()
        mock_context_manager.__aenter__.return_value = (mock_read_stream, mock_write_stream)
        mock_stdio_server.return_value = mock_context_manager
        
        # Mock the server methods
        mock_init_opts = MagicMock()
        server.server.create_initialization_options = MagicMock(return_value=mock_init_opts)
        server.server.run = AsyncMock()
        
        # Call run method
        await server.run()
        
        # Verify that run was called
        server.server.run.assert_called_once()