"""Todo agent initialization with OpenAI.

This module creates and configures the AI agent that processes natural language
commands and calls appropriate MCP tools using OpenAI GPT-4o-mini.

Task: T014 - Initialize todo agent with AI model and tool registration
Spec: specs/003-phase3-ai-chatbot/plan.md (AI Agents SDK section)
"""

from typing import Any, Dict, List
from openai import AsyncOpenAI

from .prompts import SYSTEM_PROMPT
from app.utils import safe_str


class TodoAgent:
    """
    AI agent for natural language todo management.

    Uses OpenAI GPT-4o-mini for intent recognition and entity extraction.
    Calls MCP tools for task operations.

    Architecture:
        - Stateless: No internal state, receives full conversation history
        - Tool calling: Uses OpenAI function calling to invoke MCP tools
        - Context management: Receives last 50 messages as context
        - Error handling: Graceful degradation on API failures
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        """
        Initialize todo agent with OpenAI.

        Args:
            api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-4o-mini - cheapest and fast)
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.temperature = 0.7
        self.max_tokens = 500
        self.system_prompt = SYSTEM_PROMPT
        self.tools: List[Dict[str, Any]] = []
        self.mcp_tools: Dict[str, Any] = {}  # MCP tool functions for execution

    def register_tool(self, tool_definition: Dict[str, Any]) -> None:
        """
        Register an MCP tool with the agent.

        Args:
            tool_definition: OpenAI function calling tool definition

        Example:
            agent.register_tool({
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Create a new task",
                    "parameters": AddTaskInput.schema()
                }
            })
        """
        self.tools.append(tool_definition)

    async def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Process a user message and generate response.

        Args:
            user_message: New message from user
            conversation_history: Previous messages [{role, content}]
            user_id: User ID for data isolation

        Returns:
            {
                "content": "Assistant response text",
                "tool_calls": [...],  # If tools were called
                "finish_reason": "stop" | "tool_calls"
            }

        Architecture:
            1. Build messages list with system prompt + history + new message
            2. Call OpenAI API with tools enabled
            3. If tool calls requested, execute them via MCP
            4. If no tools, return assistant response directly
            5. Handle errors gracefully
        """
        # Build messages for OpenAI API
        messages = [
            {"role": "system", "content": self.system_prompt},
            *conversation_history,
            {"role": "user", "content": user_message},
        ]

        # Add user_id to message context for MCP tools
        # This ensures all tool calls are scoped to the correct user
        messages[0]["content"] += f"\n\nCurrent user_id: {user_id}"

        # Debug: Show messages being sent to OpenAI
        print(f"[DEBUG] Sending {len(messages)} messages to OpenAI:")
        for i, msg in enumerate(messages):
            role = msg.get('role', 'unknown')
            content_preview = str(msg.get('content', ''))[:150]  # First 150 chars
            print(f"  [{i}] {role}: {content_preview}...")

        try:
            # Call OpenAI API with tools
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore
                tools=self.tools if self.tools else None,
                tool_choice="auto",  # Let model decide when to use tools
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            choice = response.choices[0]
            message = choice.message

            # Extract response content and tool calls
            result = {
                "content": message.content or "",
                "tool_calls": [],
                "finish_reason": choice.finish_reason,
            }

            # If tools were called, include them in response
            if message.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": tc.id,
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    }
                    for tc in message.tool_calls
                ]

            return result

        except Exception as e:
            # Handle OpenAI API errors gracefully (strip emojis from error)
            error_msg = safe_str(e)
            return {
                "content": f"I'm having trouble processing your request right now. Please try again in a moment. (Error: {error_msg})",
                "tool_calls": [],
                "finish_reason": "error",
            }

    async def execute_tool_calls(
        self,
        tool_calls: List[Dict[str, Any]],
        mcp_tools: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Execute tool calls via MCP server.

        Args:
            tool_calls: Tool calls from OpenAI response
            mcp_tools: Mapping of tool names to MCP tool functions

        Returns:
            List of tool execution results
        """
        results = []

        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_func = mcp_tools.get(tool_name)

            if not tool_func:
                results.append(
                    {
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": tool_name,
                        "content": f"Error: Tool '{tool_name}' not found",
                    }
                )
                continue

            try:
                # Parse arguments and call tool
                import json

                arguments = json.loads(tool_call["arguments"])
                result = await tool_func(arguments)

                results.append(
                    {
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": tool_name,
                        "content": str(result),
                    }
                )
            except Exception as e:
                error_msg = safe_str(e)
                results.append(
                    {
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": tool_name,
                        "content": f"Error executing tool: {error_msg}",
                    }
                )

        return results


# Global agent instance (initialized in main.py with OpenAI API key)
todo_agent: TodoAgent | None = None


def initialize_agent(api_key: str) -> TodoAgent:
    """
    Initialize the global todo agent instance.

    Args:
        api_key: OpenAI API key from environment

    Returns:
        Initialized TodoAgent with OpenAI GPT-4o-mini
    """
    global todo_agent
    todo_agent = TodoAgent(api_key=api_key)
    return todo_agent


def get_agent() -> TodoAgent:
    """
    Get the global todo agent instance.

    Returns:
        TodoAgent instance

    Raises:
        RuntimeError: If agent not initialized
    """
    if todo_agent is None:
        raise RuntimeError("Todo agent not initialized. Call initialize_agent() first.")
    return todo_agent
