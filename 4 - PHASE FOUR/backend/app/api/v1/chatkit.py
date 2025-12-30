"""
ChatKit Integration for Evolved Todo

This module provides integration with OpenAI's ChatKit service.
It acts as a bridge between ChatKit and our existing MCP tools and database.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import openai
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.core.settings import settings
from app.core.database import get_session
from app.middleware.auth import get_current_user
from app.middleware.auth import TokenPayload
from app.models.user import User
from app.models.conversation import Conversation
from app.agents.todo_agent import TodoAgent
from openai import OpenAI
import asyncio
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatKitMessageRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatKitMessageResponse(BaseModel):
    message: str
    conversation_id: str
    metadata: Optional[Dict[str, Any]] = None


@router.post("/chatkit/{user_id}", response_model=ChatKitMessageResponse)
async def chatkit_message(
    user_id: str,
    request: ChatKitMessageRequest,
    session: AsyncSession = Depends(get_session),
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    ChatKit-compatible endpoint that integrates with our existing MCP tools.

    This endpoint receives messages from ChatKit and processes them using
    our existing AI agent and MCP tools infrastructure.
    """
    # Verify that the requesting user matches the user_id in the path
    if current_user.sub != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' conversations",
        )

    try:
        # Import required dependencies
        from app.agents.todo_agent import get_agent
        from app.models.conversation import get_or_create_conversation, fetch_conversation_history
        from app.models.message import create_message
        from app.utils import strip_emojis
        from sqlmodel.ext.asyncio.session import AsyncSession

        # Get AI agent
        agent = get_agent()

        # Get or create conversation
        conversation = await get_or_create_conversation(
            session, user_id, request.conversation_id
        )

        # Fetch conversation history (last 50 messages)
        history = await fetch_conversation_history(session, conversation.id)

        # Process message with agent
        response = await agent.process_message(
            user_message=request.message,
            conversation_history=history,
            user_id=user_id,
        )

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

            # If Gemini returns empty response, create a helpful message from tool results
            if not assistant_message or assistant_message.strip() == "":
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
                                else:
                                    msg += "No pending tasks.\n"

                                if completed_tasks:
                                    msg += "\nCOMPLETED TASKS:\n"
                                    for task in completed_tasks:
                                        task_line = f"* Task #{task['id']}: {task['title']}"
                                        msg += task_line + "\n"

                                assistant_message = msg
                        else:
                            # For other tool results, try to format them nicely
                            assistant_message = f"Operation completed: {str(tool_content)[:200]}..."
                    except json.JSONDecodeError:
                        # If not JSON, use as-is (with length limit)
                        assistant_message = f"Operation completed: {str(tool_content)[:200]}..."
        else:
            # No tools called, use direct response
            assistant_message = response.get("content", "I processed your request.")

        # Store user message in database
        await create_message(
            session=session,
            conversation_id=conversation.id,
            role="user",
            content=request.message,
            user_id=user_id
        )

        # Store assistant message in database
        await create_message(
            session=session,
            conversation_id=conversation.id,
            role="assistant",
            content=assistant_message,
            user_id=user_id
        )

        return ChatKitMessageResponse(
            message=assistant_message,
            conversation_id=str(conversation.id)
        )
    except Exception as e:
        logger.error(f"Error processing ChatKit message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing ChatKit message: {str(e)}")


# Additional endpoints for ChatKit compatibility
@router.get("/chatkit/health")
async def chatkit_health():
    """Health check for ChatKit integration"""
    return {"status": "ok", "chatkit": "enabled", "status": "ready"}


@router.get("/chatkit/{user_id}/conversations")
async def list_user_conversations(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """List all conversations for a user"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Return mock data for now - would connect to your conversation DB in real implementation
    return {
        "conversations": [
            {"id": f"chatkit_conv_{user_id}_1", "title": "Task Management", "last_message": "2025-12-24T10:00:00Z"},
            {"id": f"chatkit_conv_{user_id}_2", "title": "Project Planning", "last_message": "2025-12-24T09:30:00Z"}
        ]
    }


@router.get("/chatkit/{user_id}/conversations/{conversation_id}")
async def get_conversation_history(
    user_id: str,
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get conversation history for a specific conversation"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Return mock data for now - would connect to your conversation DB in real implementation
    return {
        "conversation_id": conversation_id,
        "messages": [
            {"role": "user", "content": "Add a task to buy groceries", "timestamp": "2025-12-24T10:00:00Z"},
            {"role": "assistant", "content": "I've added 'Buy groceries' to your task list.", "timestamp": "2025-12-24T10:00:05Z"}
        ]
    }