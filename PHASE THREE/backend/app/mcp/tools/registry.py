"""MCP tool registry and registration.

This module registers all MCP tools with the server and AI agent.

Task: T026, T029 - Register MCP tools with server and agent
"""

from typing import Dict

from app.agents.todo_agent import TodoAgent
from app.mcp.server import MCPServer
from app.mcp.tools.add_task import AddTaskInput, AddTaskOutput, add_task
from app.mcp.tools.list_tasks import ListTasksInput, ListTasksOutput, list_tasks
from app.mcp.tools.delete_task import DeleteTaskInput, DeleteTaskOutput, delete_task
from app.mcp.tools.update_task import UpdateTaskInput, UpdateTaskOutput, update_task
from app.mcp.tools.complete_task import CompleteTaskInput, CompleteTaskOutput, complete_task
from app.mcp.tools.search_tasks import SearchTasksInput, SearchTasksOutput, search_tasks


def register_tools_with_mcp_server(mcp_server: MCPServer) -> Dict[str, callable]:
    """
    Register all MCP tools with the MCP server.

    Task: T026 - Register tools with MCP server

    Args:
        mcp_server: MCP server instance

    Returns:
        Dictionary mapping tool names to functions
    """
    tools = {}

    # Register add_task tool
    @mcp_server.tool(
        name="add_task",
        description="Create a new task for the user. Extracts task details from natural language.",
        input_schema=AddTaskInput.model_json_schema(),
        output_schema=AddTaskOutput.model_json_schema(),
    )
    async def add_task_handler(input_data: dict) -> dict:
        return await add_task(input_data)

    tools["add_task"] = add_task_handler

    # Register list_tasks tool
    @mcp_server.tool(
        name="list_tasks",
        description="Retrieve tasks with optional filtering and sorting. Use for viewing, listing, or searching tasks.",
        input_schema=ListTasksInput.model_json_schema(),
        output_schema=ListTasksOutput.model_json_schema(),
    )
    async def list_tasks_handler(input_data: dict) -> dict:
        return await list_tasks(input_data)

    tools["list_tasks"] = list_tasks_handler

    # Register complete_task tool
    @mcp_server.tool(
        name="complete_task",
        description="Mark a task as complete. Use for completing, finishing, or checking off tasks.",
        input_schema=CompleteTaskInput.model_json_schema(),
        output_schema=CompleteTaskOutput.model_json_schema(),
    )
    async def complete_task_handler(input_data: dict) -> dict:
        return await complete_task(input_data)

    tools["complete_task"] = complete_task_handler

    # Register update_task tool
    @mcp_server.tool(
        name="update_task",
        description="Update an existing task with new details. Use for changing, modifying, or updating task properties.",
        input_schema=UpdateTaskInput.model_json_schema(),
        output_schema=UpdateTaskOutput.model_json_schema(),
    )
    async def update_task_handler(input_data: dict) -> dict:
        return await update_task(input_data)

    tools["update_task"] = update_task_handler

    # Register delete_task tool
    @mcp_server.tool(
        name="delete_task",
        description="Delete an existing task. Use for removing, deleting, or cancelling tasks.",
        input_schema=DeleteTaskInput.model_json_schema(),
        output_schema=DeleteTaskOutput.model_json_schema(),
    )
    async def delete_task_handler(input_data: dict) -> dict:
        return await delete_task(input_data)

    tools["delete_task"] = delete_task_handler

    # Register search_tasks tool
    @mcp_server.tool(
        name="search_tasks",
        description="Search for tasks containing specific keywords. Use for finding, searching, or looking for tasks.",
        input_schema=SearchTasksInput.model_json_schema(),
        output_schema=SearchTasksOutput.model_json_schema(),
    )
    async def search_tasks_handler(input_data: dict) -> dict:
        return await search_tasks(input_data)

    tools["search_tasks"] = search_tasks_handler

    return tools


def register_tools_with_agent(agent: TodoAgent, mcp_tools: Dict[str, callable]) -> None:
    """
    Register all MCP tools with the OpenAI agent for function calling.

    Task: T029 - Register tools with todo agent

    Args:
        agent: TodoAgent instance
        mcp_tools: Dictionary of MCP tool functions
    """
    # Register add_task with OpenAI function calling format
    agent.register_tool(
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": """Create a new task for the user. Use this when the user wants to add, create, or remember a task.

Examples:
- "Add a task to buy groceries" → title: "Buy groceries"
- "Create a high priority work task for meeting" → title: "Meeting", priority: "high", tags: ["work"]
- "Remind me to call mom tomorrow at 5 PM" → title: "Call mom", due_date: tomorrow, due_time: "17:00"
- "Add a weekly task to exercise every Monday" → title: "Exercise", recurrence: "weekly", recurrence_day: 1

Extract all relevant information from the user's message:
- Title (required): The main task description
- Description (optional): Additional details
- Priority (optional): "high", "medium", or "low" based on urgency keywords
- Tags (optional): Categories like "work", "personal", "health"
- Due date (optional): Parse relative ("tomorrow", "next Monday") or absolute dates
- Due time (optional): Extract time in HH:MM format
- Recurrence (optional): "daily", "weekly", or "monthly" patterns
- Recurrence day (optional): Day of week (1-7) or month (1-31)
""",
                "parameters": AddTaskInput.model_json_schema(),
            },
        }
    )

    # Register list_tasks with OpenAI function calling format
    agent.register_tool(
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": """Retrieve and display tasks with optional filtering and sorting. Use this when the user wants to see, list, or view their tasks.

Examples:
- "Show me my tasks" → list all tasks
- "List pending tasks" → status: "pending"
- "Show completed tasks" → status: "completed"
- "Display high priority tasks" → priority: "high"
- "Show work tasks" → tag: "work"
- "Sort my tasks by due date" → sort_by: "due_date", sort_order: "asc"
- "List all tasks ordered by priority" → sort_by: "priority"

Extract filtering criteria from the user's message:
- Status filter: "pending", "completed", or "all"
- Priority filter: "high", "medium", or "low"
- Tag filter: Extract tag name (e.g., "work", "personal")
- Sort criteria: Extract field and order

Return the list of tasks in a user-friendly format with task IDs, titles, and relevant details.
""",
                "parameters": ListTasksInput.model_json_schema(),
            },
        }
    )

    # Register complete_task with OpenAI function calling format
    agent.register_tool(
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": """Mark a task as complete. Use this when the user wants to complete, finish, or check off a task.

Examples:
- "Mark task 3 as complete" → task_id: 3
- "Complete the grocery shopping task" → task_id: 5 (from context)
- "Finish the meeting task" → task_id: 7 (from context)

Extract the task ID from the user's message or from conversation context.
The tool will mark the task as complete and handle any recurring task logic.
""",
                "parameters": CompleteTaskInput.model_json_schema(),
            },
        }
    )

    # Register update_task with OpenAI function calling format
    agent.register_tool(
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": """Update an existing task with new details. Use this when the user wants to change, modify, update, or edit a task.

Examples:
- "Change task 3 title to 'New title'" → task_id: 3, title: "New title"
- "Update task 5 priority to high" → task_id: 5, priority: "high"
- "Modify task 2 due date to tomorrow" → task_id: 2, due_date: tomorrow
- "Set task 1 description to 'Updated description'" → task_id: 1, description: "Updated description"
- "Update task 4 tags to work, urgent" → task_id: 4, tags: "work,urgent"

Extract the task ID and the specific fields to update from the user's message.
Only update the fields that are explicitly mentioned in the request.
""",
                "parameters": UpdateTaskInput.model_json_schema(),
            },
        }
    )

    # Register delete_task with OpenAI function calling format
    agent.register_tool(
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": """Delete an existing task. Use this when the user wants to remove, delete, or cancel a task.

Examples:
- "Delete task 3" → task_id: 3
- "Remove task 5" → task_id: 5
- "Cancel the meeting task" → task_id: 7 (from context)

Extract the task ID from the user's message or from conversation context.
The tool will permanently delete the task from the database.
""",
                "parameters": DeleteTaskInput.model_json_schema(),
            },
        }
    )

    # Register search_tasks with OpenAI function calling format
    agent.register_tool(
        {
            "type": "function",
            "function": {
                "name": "search_tasks",
                "description": """Search for tasks containing specific keywords. Use this when the user wants to find, search, or look for tasks.

Examples:
- "Search for dentist" → keyword: "dentist"
- "Find tasks about groceries" → keyword: "groceries"
- "Look for meeting tasks" → keyword: "meeting"

Extract the search keyword from the user's message.
The tool will return all tasks containing the keyword in title or description.
""",
                "parameters": SearchTasksInput.model_json_schema(),
            },
        }
    )

    # Store MCP tool reference for execution
    # (Agent will call these after OpenAI returns tool calls)
    agent.mcp_tools = mcp_tools


def initialize_all_tools(mcp_server: MCPServer, agent: TodoAgent) -> Dict[str, callable]:
    """
    Initialize all MCP tools with both server and agent.

    Args:
        mcp_server: MCP server instance
        agent: TodoAgent instance

    Returns:
        Dictionary of registered tool functions
    """
    # Register with MCP server
    mcp_tools = register_tools_with_mcp_server(mcp_server)

    # Register with AI agent
    register_tools_with_agent(agent, mcp_tools)

    return mcp_tools
