"""
ChatKit Server Implementation for Evolved Todo

This module implements a ChatKit server that integrates with our existing
MCP tools and OpenAI Agents SDK for task management.

Task: ChatKit Integration
Spec: specs/003-phase3-ai-chatbot/spec.md
"""

from typing import AsyncIterator
from chatkit.server import ChatKitServer, ThreadStreamEvent
from chatkit.store import Store
from chatkit.types import ThreadMetadata, UserMessageItem
from app.agents.todo_agent import get_agent
from app.core.database import get_session
from app.api.chat import get_or_create_conversation, fetch_conversation_history
from app.models.message import Message, MessageRole
from app.models.conversation import Conversation
from sqlmodel import select
from sqlalchemy import delete as sql_delete
import logging

logger = logging.getLogger(__name__)


class TodoChatKitServer(ChatKitServer[str]):
    """
    ChatKit server implementation for todo management.

    Integrates ChatKit frontend with our custom FastAPI backend,
    OpenAI Agents SDK, and MCP tools.
    """

    def __init__(self, store: Store[str]):
        """Initialize the ChatKit server with a store."""
        super().__init__(store)
        self._agent = None

    @property
    def agent(self):
        """Lazy-load the agent."""
        if self._agent is None:
            self._agent = get_agent()
        return self._agent

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: str,  # user_id
    ) -> AsyncIterator[ThreadStreamEvent]:
        """
        Stream response events for a user message.

        Args:
            thread: Thread metadata
            input_user_message: User's message
            context: User ID for authentication

        Yields:
            Thread stream events (messages, tool calls, etc.)
        """
        if not input_user_message:
            return

        try:
            user_id = context
            user_message_content = ""

            # Extract message content
            for content_part in input_user_message.content:
                if hasattr(content_part, 'text'):
                    user_message_content += content_part.text

            logger.info(f"ChatKit message from user {user_id}: {user_message_content}")
            logger.info(f"ChatKit thread.id received: '{thread.id}' (type: {type(thread.id).__name__})")
            logger.info(f"ChatKit thread metadata: title='{thread.title}', created_at={thread.created_at}")

            # Get database session
            async for session in get_session():
                # Map ChatKit thread.id to our conversation.id
                # If thread.id is valid (numeric and > 0), use it
                # Otherwise, check if this is a NEW chat or auto-continue
                conversation_id = None
                try:
                    if thread.id and thread.id.isdigit() and int(thread.id) > 0:
                        conversation_id = int(thread.id)
                        logger.info(f"Using existing conversation ID from thread.id: {conversation_id}")
                    else:
                        logger.info(f"Invalid thread.id ('{thread.id}'), checking for recent conversation...")

                        # Check if thread.id points to an existing empty conversation (NEW chat)
                        # If conversation exists with ID 0 or thread.id and has NO messages, use it (NEW chat)
                        # Otherwise, auto-continue the most recent conversation
                        from sqlmodel import select
                        from app.models.conversation import Conversation
                        from app.models.message import Message

                        # Try to find conversation matching thread.id
                        if thread.id and thread.id.isdigit():
                            thread_conv_id = int(thread.id)

                            # Check if this conversation exists and is empty (NEW chat)
                            conv_result = await session.execute(
                                select(Conversation)
                                .where(
                                    Conversation.id == thread_conv_id,
                                    Conversation.user_id == user_id
                                )
                            )
                            thread_conversation = conv_result.scalar_one_or_none()

                            if thread_conversation:
                                # Check if conversation has messages
                                msg_result = await session.execute(
                                    select(Message)
                                    .where(Message.conversation_id == thread_conv_id)
                                    .limit(1)
                                )
                                has_messages = msg_result.scalar_one_or_none() is not None

                                if not has_messages:
                                    # Empty conversation - this is a NEW chat, use it
                                    conversation_id = thread_conv_id
                                    logger.info(f"✨ NEW CHAT: Using empty conversation ID: {conversation_id}")
                                else:
                                    # CRITICAL FIX: If conversation 0 has messages, DON'T auto-continue it
                                    # Leave conversation_id as None so the next logic block can find
                                    # newly created empty conversations (from "New Chat" button)
                                    if thread_conv_id != 0:
                                        # Has messages and is NOT conversation 0 - continue this conversation
                                        conversation_id = thread_conv_id
                                        logger.info(f"📝 CONTINUE: Using conversation ID: {conversation_id}")
                                    else:
                                        # Conversation 0 has messages - check for newly created empty conversations
                                        logger.info(f"Conversation 0 has messages, will check for newly created empty conversations...")

                        # If no conversation found yet, check for NEW chat or auto-continue
                        if conversation_id is None:
                            # CRITICAL FIX: First check for newly created conversations (from "New Chat" button)
                            # These are conversations that exist but have NO messages yet
                            recent_conv_result = await session.execute(
                                select(Conversation)
                                .where(Conversation.user_id == user_id)
                                .order_by(Conversation.created_at.desc())
                                .limit(5)  # Check last 5 to find empty one
                            )
                            recent_conversations = recent_conv_result.scalars().all()

                            # Look for a conversation with NO messages (NEW chat)
                            new_chat_conversation = None
                            for conv in recent_conversations:
                                msg_check = await session.execute(
                                    select(Message)
                                    .where(Message.conversation_id == conv.id)
                                    .limit(1)
                                )
                                has_messages = msg_check.scalar_one_or_none() is not None
                                if not has_messages:
                                    new_chat_conversation = conv
                                    break

                            if new_chat_conversation:
                                # This is a NEW CHAT - use the empty conversation
                                conversation_id = new_chat_conversation.id
                                logger.info(f"✨ NEW CHAT: Using newly created conversation ID: {conversation_id}")
                            elif recent_conversations:
                                # No empty conversation found - auto-continue the most recent one with messages
                                conversation_id = recent_conversations[0].id
                                logger.info(f"🔄 AUTO-CONTINUE: Using most recent conversation ID: {conversation_id}")
                            else:
                                logger.info(f"No existing conversations, will create new one")
                except (ValueError, AttributeError) as e:
                    logger.info(f"Error parsing thread.id: {e}, will check for recent conversation")

                logger.info(f"[BEFORE] Calling get_or_create_conversation with conversation_id={conversation_id}")

                conversation = await get_or_create_conversation(
                    session, user_id, conversation_id
                )

                logger.info(f"[AFTER] Got conversation ID: {conversation.id}")

                # CRITICAL FIX: Update thread.id to our conversation.id
                # This ensures ChatKit remembers the conversation on subsequent messages
                thread.id = str(conversation.id)
                logger.info(f"[THREAD UPDATE] Set thread.id = {thread.id}")

                # Fetch conversation history
                history = await fetch_conversation_history(session, conversation.id)

                # Process message with agent
                response = await self.agent.process_message(
                    user_message=user_message_content,
                    conversation_history=history,
                    user_id=user_id,
                )

                # CRITICAL FIX: Store user message FIRST before agent processing
                user_msg = Message(
                    conversation_id=conversation.id,
                    user_id=user_id,
                    role=MessageRole.USER,
                    content=user_message_content
                )
                session.add(user_msg)
                await session.flush()  # Flush to persist immediately

                # Execute tool calls if any
                assistant_message = response.get("content", "")

                if response.get("tool_calls"):
                    # Execute tool calls via MCP
                    # Note: We don't persist intermediate tool call messages to keep conversation clean
                    # Only the final assistant response is stored
                    tool_results = await self.agent.execute_tool_calls(
                        tool_calls=response["tool_calls"],
                        mcp_tools=self.agent.mcp_tools
                    )

                    # Build messages with tool results
                    messages_with_tools = [
                        {"role": "system", "content": self.agent.system_prompt},
                        *history,
                        {"role": "user", "content": user_message_content},
                        {
                            "role": "assistant",
                            "content": response.get("content", ""),
                            "tool_calls": [
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
                        },
                        *tool_results,
                    ]

                    # Get final response
                    final_response = await self.agent.client.chat.completions.create(
                        model=self.agent.model,
                        messages=messages_with_tools,  # type: ignore
                        temperature=self.agent.temperature,
                        max_tokens=self.agent.max_tokens,
                    )

                    assistant_message = final_response.choices[0].message.content or ""

                # CRITICAL FIX: Store FINAL assistant message only
                # User message and tool messages already persisted above
                final_assistant_msg = Message(
                    conversation_id=conversation.id,
                    user_id=user_id,
                    role=MessageRole.ASSISTANT,
                    content=assistant_message
                )
                session.add(final_assistant_msg)
                await session.commit()

                # Stream response back to ChatKit
                # ChatKit expects us to yield ThreadStreamEvents
                # For now, we'll yield a simple text response
                # You can enhance this to yield structured events

                from chatkit.types import (
                    AssistantMessageItem,
                    AssistantMessageContent,
                    ThreadItemAddedEvent,
                    ThreadItemDoneEvent,
                )

                # Create assistant message item
                assistant_item = AssistantMessageItem(
                    id=f"msg_{conversation.id}_{len(history) + 2}",
                    thread_id=str(conversation.id),
                    created_at=final_assistant_msg.created_at,
                    content=[
                        AssistantMessageContent(
                            type="output_text",
                            text=assistant_message,
                            annotations=[],
                        )
                    ]
                )

                # Yield item added event
                yield ThreadItemAddedEvent(
                    type="thread.item.added",
                    item=assistant_item
                )

                # Yield item done event
                yield ThreadItemDoneEvent(
                    type="thread.item.done",
                    item=assistant_item
                )

                break  # Exit the async for loop after first session

        except Exception as e:
            logger.error(f"Error in ChatKit respond: {e}", exc_info=True)
            from chatkit.types import ErrorEvent
            yield ErrorEvent(
                type="error",
                error={
                    "code": "internal_error",
                    "message": f"Failed to process message: {str(e)}"
                }
            )

    async def delete_thread(
        self,
        thread: ThreadMetadata,
        context: str,  # user_id
    ) -> None:
        """
        Delete a thread/conversation and all its messages from the database.

        This is called when a user deletes a conversation from ChatKit UI.

        Args:
            thread: Thread metadata (contains thread.id which maps to conversation_id)
            context: User ID for authentication
        """
        try:
            user_id = context

            # Parse thread.id to get conversation_id
            if not thread.id or not thread.id.isdigit():
                logger.warning(f"Cannot delete thread with invalid ID: {thread.id}")
                return

            conversation_id = int(thread.id)
            logger.info(f"ChatKit delete request: conversation_id={conversation_id}, user_id={user_id}")

            # Get database session and delete the conversation
            async for session in get_session():
                # Verify conversation exists and belongs to user
                result = await session.execute(
                    select(Conversation).where(
                        Conversation.id == conversation_id,
                        Conversation.user_id == user_id
                    )
                )
                conversation = result.scalars().first()

                if not conversation:
                    logger.warning(
                        f"Conversation {conversation_id} not found or doesn't belong to user {user_id}"
                    )
                    break

                # Delete all messages first
                await session.execute(
                    sql_delete(Message).where(Message.conversation_id == conversation_id)
                )

                # Delete the conversation
                await session.delete(conversation)
                await session.commit()

                logger.info(f"Successfully deleted conversation {conversation_id} for user {user_id}")
                break

        except Exception as e:
            logger.error(f"Error deleting thread {thread.id}: {e}", exc_info=True)
