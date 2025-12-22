import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from datetime import datetime
from app.api.chat import (
    chat,
    get_conversation_history,
    get_or_create_conversation,
    fetch_conversation_history,
    persist_messages
)
from app.models import Conversation, Message, MessageRole


@pytest.mark.asyncio
async def test_get_or_create_conversation_new():
    """Test creating a new conversation."""
    mock_session = AsyncMock()
    mock_conversation = MagicMock()
    mock_conversation.id = 1
    mock_conversation.user_id = "test_user"
    mock_conversation.updated_at = datetime.utcnow()

    # Mock the session methods
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    with patch('app.api.chat.Conversation', return_value=mock_conversation):
        result = await get_or_create_conversation(mock_session, "test_user", None)

        # Check that a new conversation was created
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        assert result == mock_conversation


@pytest.mark.asyncio
async def test_get_or_create_conversation_existing():
    """Test getting an existing conversation."""
    mock_session = AsyncMock()
    mock_conversation = MagicMock()
    mock_conversation.id = 1
    mock_conversation.user_id = "test_user"
    mock_conversation.updated_at = datetime.utcnow()

    # Mock the session methods
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    mock_scalars_result = AsyncMock()
    mock_scalars_result.first = AsyncMock(return_value=mock_conversation)
    mock_result = AsyncMock()
    mock_result.scalars = AsyncMock(return_value=mock_scalars_result)

    with patch('app.api.chat.select'):
        with patch.object(mock_session, 'execute', return_value=mock_result):
            result = await get_or_create_conversation(mock_session, "test_user", 1)

            # Check that the existing conversation was returned
            assert result.id == 1
            assert result.user_id == "test_user"


@pytest.mark.asyncio
async def test_get_or_create_conversation_not_found():
    """Test getting a non-existent conversation."""
    mock_session = AsyncMock()

    mock_scalars_result = AsyncMock()
    mock_scalars_result.first = AsyncMock(return_value=None)
    mock_result = AsyncMock()
    mock_result.scalars = AsyncMock(return_value=mock_scalars_result)

    with patch('app.api.chat.select'):
        with patch.object(mock_session, 'execute', return_value=mock_result):
            with pytest.raises(HTTPException) as exc_info:
                await get_or_create_conversation(mock_session, "test_user", 999)

            assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_fetch_conversation_history():
    """Test fetching conversation history."""
    mock_session = AsyncMock()

    mock_message = MagicMock()
    mock_message.role.value = "user"
    mock_message.content = "Hello"

    mock_scalars_result = AsyncMock()
    mock_scalars_result.all = AsyncMock(return_value=[mock_message])
    mock_result = AsyncMock()
    mock_result.scalars = AsyncMock(return_value=mock_scalars_result)

    with patch('app.api.chat.select'):
        with patch.object(mock_session, 'execute', return_value=mock_result):
            result = await fetch_conversation_history(mock_session, 1)

            assert len(result) == 1
            assert result[0]["role"] == "user"
            assert result[0]["content"] == "Hello"


@pytest.mark.asyncio
async def test_persist_messages():
    """Test persisting messages to database."""
    mock_session = AsyncMock()
    
    # Mock the session methods
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    
    await persist_messages(
        mock_session, 1, "test_user", "Hello", "Hi there"
    )
    
    # Check that add and commit were called
    assert mock_session.add.call_count == 2  # Two messages
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_chat_endpoint_success():
    """Test successful chat endpoint call."""
    from app.api.chat import ChatRequest
    
    # Create a mock request
    request = ChatRequest(message="Hello", conversation_id=None)
    
    mock_session = AsyncMock()
    mock_current_user = MagicMock()
    mock_current_user.sub = "test_user"
    
    # Mock the conversation
    mock_conversation = MagicMock()
    mock_conversation.id = 1
    mock_conversation.user_id = "test_user"
    mock_conversation.updated_at = datetime.utcnow()
    
    # Mock the agent
    mock_agent = MagicMock()
    mock_agent.process_message = AsyncMock(return_value={
        "content": "Hi there!",
        "tool_calls": [],
        "finish_reason": "stop"
    })
    
    with patch('app.api.chat.get_or_create_conversation', return_value=mock_conversation):
        with patch('app.api.chat.fetch_conversation_history', return_value=[]):
            with patch('app.api.chat.get_agent', return_value=mock_agent):
                with patch('app.api.chat.persist_messages'):
                    with patch('app.api.chat.strip_emojis', side_effect=lambda x: x):
                        result = await chat(
                            user_id="test_user",
                            request=request,
                            session=mock_session,
                            current_user=mock_current_user
                        )
                        
                        assert result.conversation_id == 1
                        assert result.message == "Hi there!"


@pytest.mark.asyncio
async def test_chat_endpoint_with_tool_calls():
    """Test chat endpoint with tool calls."""
    from app.api.chat import ChatRequest

    # Create a mock request
    request = ChatRequest(message="Add a task", conversation_id=None)

    mock_session = AsyncMock()
    mock_current_user = MagicMock()
    mock_current_user.sub = "test_user"

    # Mock the conversation
    mock_conversation = MagicMock()
    mock_conversation.id = 1
    mock_conversation.user_id = "test_user"
    mock_conversation.updated_at = datetime.utcnow()

    # Mock the agent
    mock_agent = MagicMock()
    mock_agent.process_message = AsyncMock(return_value={
        "content": "",
        "tool_calls": [{
            "id": "call_123",
            "name": "add_task",
            "arguments": '{"title": "Test task", "user_id": "test_user"}'
        }],
        "finish_reason": "tool_calls"
    })
    mock_agent.execute_tool_calls = AsyncMock(return_value=[{
        "tool_call_id": "call_123",
        "role": "tool",
        "name": "add_task",
        "content": '{"status": "success", "message": "Task created"}'
    }])
    mock_agent.model = "gpt-4o-mini"
    mock_agent.temperature = 0.7
    mock_agent.max_tokens = 500
    mock_agent.system_prompt = "System prompt"

    # Mock the OpenAI client response
    mock_openai_response = AsyncMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "Task created successfully"
    mock_choice.message = mock_message
    mock_openai_response.choices = [mock_choice]

    with patch('app.api.chat.get_or_create_conversation', return_value=mock_conversation):
        with patch('app.api.chat.fetch_conversation_history', return_value=[]):
            with patch('app.api.chat.get_agent', return_value=mock_agent):
                with patch('app.api.chat.persist_messages'):
                    with patch('app.api.chat.strip_emojis', side_effect=lambda x: x):
                        with patch.object(mock_agent.client.chat.completions, 'create', return_value=mock_openai_response):
                            result = await chat(
                                user_id="test_user",
                                request=request,
                                session=mock_session,
                                current_user=mock_current_user
                            )

                            assert result.conversation_id == 1
                            assert "Task created" in result.message


@pytest.mark.asyncio
async def test_chat_endpoint_user_id_mismatch():
    """Test chat endpoint with user ID mismatch."""
    from app.api.chat import ChatRequest
    
    request = ChatRequest(message="Hello", conversation_id=None)
    
    mock_session = AsyncMock()
    mock_current_user = MagicMock()
    mock_current_user.sub = "other_user"  # Different from path parameter
    
    with pytest.raises(HTTPException) as exc_info:
        await chat(
            user_id="test_user",
            request=request,
            session=mock_session,
            current_user=mock_current_user
        )
        
        assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_get_conversation_history_success():
    """Test successful retrieval of conversation history."""
    mock_session = AsyncMock()
    mock_current_user = {"id": "test_user"}

    # Mock the conversation
    mock_conversation = MagicMock()
    mock_conversation.id = 1
    mock_conversation.user_id = "test_user"

    # Mock the messages
    mock_message = MagicMock()
    mock_message.id = 1
    mock_message.role.value = "user"
    mock_message.content = "Hello"
    mock_message.created_at = datetime.utcnow()

    mock_scalars_result = AsyncMock()
    mock_scalars_result.all = AsyncMock(return_value=[mock_message])
    mock_result = AsyncMock()
    mock_result.scalars = AsyncMock(return_value=mock_scalars_result)

    with patch('app.api.chat.select'):
        with patch.object(mock_session, 'execute', return_value=mock_result):
            # First get the conversation
            conv_result = await get_conversation_history(
                user_id="test_user",
                conversation_id=1,
                session=mock_session,
                current_user=mock_current_user
            )

            assert conv_result.conversation_id == 1
            assert len(conv_result.messages) == 1
            assert conv_result.messages[0]["content"] == "Hello"


@pytest.mark.asyncio
async def test_get_conversation_history_user_id_mismatch():
    """Test conversation history endpoint with user ID mismatch."""
    mock_session = AsyncMock()
    mock_current_user = {"id": "other_user"}  # Different from path parameter
    
    with pytest.raises(HTTPException) as exc_info:
        await get_conversation_history(
            user_id="test_user",
            conversation_id=1,
            session=mock_session,
            current_user=mock_current_user
        )
        
        assert exc_info.value.status_code == 403