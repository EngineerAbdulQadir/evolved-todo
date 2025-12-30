import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.agents.todo_agent import TodoAgent, initialize_agent, get_agent


def test_todo_agent_initialization():
    """Test TodoAgent initialization."""
    agent = TodoAgent(api_key="test_key", model="gpt-4o-mini")
    
    assert agent.model == "gpt-4o-mini"
    assert agent.temperature == 0.7
    assert agent.max_tokens == 500
    assert agent.tools == []
    assert agent.mcp_tools == {}


def test_register_tool():
    """Test registering a tool with the agent."""
    agent = TodoAgent(api_key="test_key")
    
    tool_definition = {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task",
            "parameters": {"type": "object"}
        }
    }
    
    agent.register_tool(tool_definition)
    
    assert len(agent.tools) == 1
    assert agent.tools[0] == tool_definition


@pytest.mark.asyncio
async def test_process_message_success():
    """Test successful message processing."""
    agent = TodoAgent(api_key="test_key")

    # Mock the OpenAI client response
    mock_response = AsyncMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_choice.message = mock_message
    mock_choice.finish_reason = "stop"
    mock_response.choices = [mock_choice]
    mock_message.content = "Hello, how can I help you?"
    mock_message.tool_calls = None

    with patch.object(agent.client.chat.completions, 'create', return_value=mock_response):
        result = await agent.process_message(
            user_message="Hello",
            conversation_history=[],
            user_id="test_user"
        )

        assert result["content"] == "Hello, how can I help you?"
        assert result["tool_calls"] == []
        assert result["finish_reason"] == "stop"


@pytest.mark.asyncio
async def test_process_message_with_tool_calls():
    """Test message processing with tool calls."""
    agent = TodoAgent(api_key="test_key")

    # Mock tool call in response
    mock_tool_call = MagicMock()
    mock_tool_call.id = "call_123"
    mock_tool_call.function.name = "add_task"
    mock_tool_call.function.arguments = '{"title": "Test task"}'

    mock_response = AsyncMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_choice.message = mock_message
    mock_choice.finish_reason = "tool_calls"
    mock_response.choices = [mock_choice]
    mock_message.content = None
    mock_message.tool_calls = [mock_tool_call]

    with patch.object(agent.client.chat.completions, 'create', return_value=mock_response):
        result = await agent.process_message(
            user_message="Add a task",
            conversation_history=[],
            user_id="test_user"
        )

        assert result["content"] == ""
        assert len(result["tool_calls"]) == 1
        assert result["tool_calls"][0]["name"] == "add_task"
        assert result["finish_reason"] == "tool_calls"


@pytest.mark.asyncio
async def test_process_message_error():
    """Test message processing with OpenAI API error."""
    agent = TodoAgent(api_key="test_key")
    
    with patch.object(agent.client.chat.completions, 'create', side_effect=Exception("API Error")):
        result = await agent.process_message(
            user_message="Hello",
            conversation_history=[],
            user_id="test_user"
        )
        
        assert "I'm having trouble processing your request" in result["content"]
        assert result["finish_reason"] == "error"


@pytest.mark.asyncio
async def test_execute_tool_calls_success():
    """Test successful tool call execution."""
    agent = TodoAgent(api_key="test_key")
    
    tool_calls = [
        {
            "id": "call_123",
            "name": "add_task",
            "arguments": '{"title": "Test task", "user_id": "test_user"}'
        }
    ]
    
    mock_mcp_tools = {
        "add_task": AsyncMock(return_value={"status": "success", "message": "Task created"})
    }
    
    results = await agent.execute_tool_calls(tool_calls, mock_mcp_tools)
    
    assert len(results) == 1
    assert results[0]["tool_call_id"] == "call_123"
    assert results[0]["name"] == "add_task"
    assert "Task created" in results[0]["content"]


@pytest.mark.asyncio
async def test_execute_tool_calls_tool_not_found():
    """Test tool call execution with unknown tool."""
    agent = TodoAgent(api_key="test_key")
    
    tool_calls = [
        {
            "id": "call_123",
            "name": "unknown_tool",
            "arguments": "{}"
        }
    ]
    
    results = await agent.execute_tool_calls(tool_calls, {})
    
    assert len(results) == 1
    assert results[0]["tool_call_id"] == "call_123"
    assert results[0]["name"] == "unknown_tool"
    assert "not found" in results[0]["content"]


@pytest.mark.asyncio
async def test_execute_tool_calls_error():
    """Test tool call execution with error."""
    agent = TodoAgent(api_key="test_key")
    
    tool_calls = [
        {
            "id": "call_123",
            "name": "add_task",
            "arguments": '{"title": "Test task", "user_id": "test_user"}'
        }
    ]
    
    mock_mcp_tools = {
        "add_task": AsyncMock(side_effect=Exception("Tool execution error"))
    }
    
    results = await agent.execute_tool_calls(tool_calls, mock_mcp_tools)
    
    assert len(results) == 1
    assert results[0]["tool_call_id"] == "call_123"
    assert results[0]["name"] == "add_task"
    assert "Error executing tool" in results[0]["content"]


def test_initialize_agent():
    """Test initializing the global agent."""
    agent = initialize_agent("test_key")
    
    assert isinstance(agent, TodoAgent)
    assert agent.client.api_key == "test_key"


def test_get_agent():
    """Test getting the global agent."""
    # First initialize the agent
    initialize_agent("test_key")
    
    agent = get_agent()
    
    assert isinstance(agent, TodoAgent)
    assert agent.client.api_key == "test_key"


def test_get_agent_not_initialized():
    """Test getting agent when not initialized."""
    # Reset the global agent to None for this test
    import app.agents.todo_agent as todo_agent_module
    original_agent = todo_agent_module.todo_agent
    todo_agent_module.todo_agent = None
    
    try:
        with pytest.raises(RuntimeError, match="Todo agent not initialized"):
            get_agent()
    finally:
        # Restore original agent
        todo_agent_module.todo_agent = original_agent