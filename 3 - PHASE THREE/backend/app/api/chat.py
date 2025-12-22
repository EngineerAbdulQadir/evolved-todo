"""Chat endpoint for AI-powered todo management.

This module implements the stateless chat endpoint that processes user messages
through the OpenAI agent and MCP tools.

Task: T015-T017 - Chat endpoint with conversation persistence
Spec: specs/003-phase3-ai-chatbot/contracts/chat-endpoint.md
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.agents.todo_agent import get_agent
from app.core.database import get_session
from app.middleware.auth import get_current_user, TokenPayload
from app.models import Conversation, Message, MessageRole
from app.utils import strip_emojis, safe_str

# Set up logger for the chat module
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


# Request/Response Schemas
class ChatRequest(BaseModel):
    """Chat request with optional conversation context."""

    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    conversation_id: Optional[int] = Field(None, description="Existing conversation ID")


class ChatResponse(BaseModel):
    """Chat response with conversation context."""

    conversation_id: int = Field(..., description="Conversation ID for subsequent requests")
    message: str = Field(..., description="Assistant response")
    created_at: datetime = Field(..., description="Response timestamp")


class ConversationHistoryResponse(BaseModel):
    """Conversation history for frontend display."""

    conversation_id: int
    messages: List[dict]


# Helper Functions
async def get_or_create_conversation(
    session: AsyncSession, user_id: str, conversation_id: Optional[int] = None
) -> Conversation:
    """
    Get existing conversation or create new one.

    Task: T016 - Conversation history fetching

    Args:
        session: Database session
        user_id: User ID from JWT token
        conversation_id: Optional existing conversation ID

    Returns:
        Conversation instance

    Raises:
        HTTPException 404: Conversation not found or access denied
    """
    if conversation_id:
        # Fetch existing conversation
        result = await session.execute(
            select(Conversation).where(
                Conversation.id == conversation_id, Conversation.user_id == user_id
            )
        )
        conversation = result.scalars().first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found or access denied",
            )

        # Update timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        return conversation
    else:
        # Create new conversation
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        return conversation


async def fetch_conversation_history(
    session: AsyncSession, conversation_id: int, limit: int = 50
) -> List[dict]:
    """
    Fetch conversation history (last N messages).

    Task: T016 - Conversation history fetching

    Args:
        session: Database session
        conversation_id: Conversation ID
        limit: Maximum messages to fetch (default 50)

    Returns:
        List of message dicts [{role, content}]
    """
    # Fetch last N messages ordered by created_at
    result = await session.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()

    # Reverse to get chronological order
    messages.reverse()

    # Convert to OpenAI format
    return [{"role": msg.role.value, "content": msg.content} for msg in messages]


async def persist_messages(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,
    user_message: str,
    assistant_message: str,
) -> None:
    """
    Persist user and assistant messages to database.

    Task: T017 - Message persistence

    Args:
        session: Database session
        conversation_id: Conversation ID
        user_id: User ID
        user_message: User's message content
        assistant_message: Assistant's response content
    """
    # Store user message
    user_msg = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=MessageRole.USER,
        content=user_message,
    )
    session.add(user_msg)

    # Store assistant message
    assistant_msg = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=MessageRole.ASSISTANT,
        content=assistant_message,
    )
    session.add(assistant_msg)

    await session.commit()


# Endpoints
@router.post("/{user_id}", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    session: AsyncSession = Depends(get_session),
    current_user: TokenPayload = Depends(get_current_user),
) -> ChatResponse:
    """
    Process chat message with AI agent.

    Stateless architecture:
    1. Fetch conversation history from database
    2. Process message with OpenAI agent + MCP tools
    3. Store user and assistant messages
    4. Return response (server forgets everything)

    Task: T015-T017 - Chat endpoint with JWT auth and conversation persistence

    Args:
        user_id: User ID from URL path
        request: Chat request with message and optional conversation_id
        session: Database session (dependency injection)
        current_user: Current user from JWT token (dependency injection)

    Returns:
        ChatResponse with assistant message and conversation_id

    Raises:
        HTTPException 403: User ID mismatch (accessing other user's data)
        HTTPException 404: Conversation not found
        HTTPException 500: Server error
    """
    # Verify user can only access their own data
    if current_user.sub != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' conversations",
        )

    try:
        # Get or create conversation
        conversation = await get_or_create_conversation(
            session, user_id, request.conversation_id
        )

        # Fetch conversation history (last 50 messages)
        history = await fetch_conversation_history(session, conversation.id)

        # Get AI agent
        agent = get_agent()

        # Debug: Show available tools
        print(f"[DEBUG] User message: '{request.message.encode('ascii', errors='ignore').decode('ascii')}'")
        print(f"[DEBUG] Available MCP tools: {list(agent.mcp_tools.keys())}")
        print(f"[DEBUG] Number of registered tools: {len(agent.tools)}")

        # Process message with agent
        response = await agent.process_message(
            user_message=request.message,
            conversation_history=history,
            user_id=user_id,
        )

        # Debug: Show agent response (ASCII-safe)
        response_str = str(response).encode('ascii', errors='ignore').decode('ascii')
        print(f"[DEBUG] Agent response: {response_str}")

        # Check if agent wants to call tools
        if response.get("tool_calls"):
            # Execute tool calls via MCP
            tool_results = await agent.execute_tool_calls(
                tool_calls=response["tool_calls"], mcp_tools=agent.mcp_tools
            )

            # Format tool_calls for OpenAI API (needs type and function fields)
            formatted_tool_calls = [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": tc["arguments"],
                    },
                }
                for tc in response["tool_calls"]
            ]

            # Send tool results back to agent for final response
            # Build messages with tool results
            messages_with_tools = [
                {"role": "system", "content": agent.system_prompt},
                *history,
                {"role": "user", "content": request.message},
                {"role": "assistant", "content": response.get("content", ""), "tool_calls": formatted_tool_calls},
                *tool_results,
            ]

            # Get final response from agent
            final_response = await agent.client.chat.completions.create(
                model=agent.model,
                messages=messages_with_tools,  # type: ignore
                temperature=agent.temperature,
                max_tokens=agent.max_tokens,
            )

            # Get the response content and IMMEDIATELY strip emojis
            assistant_message = final_response.choices[0].message.content
            if assistant_message:
                assistant_message = strip_emojis(assistant_message)

            # Debug logging (ASCII-safe)
            safe_message = str(assistant_message) if assistant_message else "None"
            print(f"[DEBUG] Final response content: {safe_message}")
            print(f"[DEBUG] Tool results: [hidden]")

            # If Gemini returns empty response, create a helpful message from tool results
            if not assistant_message or assistant_message.strip() == "":
                print("[DEBUG] Empty response from Gemini, generating fallback message")
                # Try to create a meaningful response from tool results
                if tool_results and len(tool_results) > 0:
                    first_tool_result = tool_results[0]
                    tool_content = first_tool_result.get("content", "")

                    # Parse tool content if it's a JSON string
                    try:
                        import json
                        tool_data = json.loads(tool_content) if isinstance(tool_content, str) else tool_content

                        # Handle list_tasks response
                        if "tasks" in tool_data:
                            tasks = tool_data.get("tasks", [])
                            if len(tasks) == 0:
                                assistant_message = "You don't have any tasks yet. Create your first task to get started!"
                            else:
                                # Format tasks nicely
                                pending_tasks = [t for t in tasks if not t.get("is_complete")]
                                completed_tasks = [t for t in tasks if t.get("is_complete")]

                                msg = "Here are your tasks:\n\n"

                                if pending_tasks:
                                    msg += "PENDING TASKS:\n"
                                    for task in pending_tasks:
                                        task_line = f"* Task #{task['id']}: {task['title']}"
                                        if task.get('priority'):
                                            task_line += f" (Priority: {task['priority']})"
                                        if task.get('tags'):
                                            task_line += f" (Tags: {', '.join(task['tags'])})"
                                        msg += task_line + "\n"
                                    msg += "\n"

                                if completed_tasks:
                                    msg += "COMPLETED TASKS:\n"
                                    for task in completed_tasks:
                                        msg += f"* Task #{task['id']}: {task['title']} [DONE]\n"
                                    msg += "\n"

                                msg += f"Total: {len(pending_tasks)} pending, {len(completed_tasks)} completed"
                                assistant_message = msg
                        else:
                            # Other tool responses - use generic message
                            assistant_message = tool_data.get("message", "Task completed successfully.")
                    except Exception as e:
                        print(f"[DEBUG] Error parsing tool response: {e}")
                        assistant_message = "Task completed."
                else:
                    assistant_message = "Task completed."
        else:
            # No tools called, use direct response and strip emojis IMMEDIATELY
            content = response.get("content", "")
            if content:
                content = strip_emojis(content)
            assistant_message = content if content and content.strip() else "I'm not sure how to help with that."

            # Debug: log when no tools are called
            print(f"[DEBUG] No tools called. Response content: '{assistant_message}'")

        # Strip all emojis from assistant message (Windows compatibility)
        assistant_message = strip_emojis(assistant_message)

        # Persist messages to database
        await persist_messages(
            session=session,
            conversation_id=conversation.id,
            user_id=user_id,
            user_message=request.message,
            assistant_message=assistant_message,
        )

        return ChatResponse(
            conversation_id=conversation.id,
            message=assistant_message,
            created_at=datetime.utcnow(),
        )

    except HTTPException:
        raise
    except Exception as e:
        # Log error internally but return generic message to avoid encoding issues
        try:
            error_msg = safe_str(e)
            print(f"[ERROR] Chat processing failed: {error_msg}")
        except:
            print("[ERROR] Chat processing failed with non-serializable error")

        # Return generic error without details to avoid encoding issues
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your message. Please try again.",
        )


@router.get("/{user_id}/conversations/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    user_id: str,
    conversation_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> ConversationHistoryResponse:
    """
    Get full conversation history for display.

    Args:
        user_id: User ID from URL path
        conversation_id: Conversation ID
        session: Database session
        current_user: Current user from JWT token

    Returns:
        Conversation history with all messages

    Raises:
        HTTPException 403: User ID mismatch
        HTTPException 404: Conversation not found
    """
    # Verify user can only access their own data
    if current_user["id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' conversations",
        )

    # Verify conversation ownership
    result = await session.execute(
        select(Conversation).where(
            Conversation.id == conversation_id, Conversation.user_id == user_id
        )
    )
    conversation = result.scalars().first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found or access denied",
        )

    # Fetch all messages (no limit for history view)
    result = await session.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()

    return ConversationHistoryResponse(
        conversation_id=conversation_id,
        messages=[
            {
                "id": msg.id,
                "role": msg.role.value,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ],
    )
