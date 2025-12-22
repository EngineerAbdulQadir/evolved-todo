# AI Agent System Prompt Documentation

This directory contains the OpenAI Agents SDK configuration and system prompts for the Evolved Todo AI chatbot.

## Files

- **`todo_agent.py`**: OpenAI agent initialization and MCP tool integration
- **`prompts.py`**: System prompt with natural language understanding patterns
- **`__init__.py`**: Package initialization

## Architecture

The AI agent follows a stateless architecture:

1. User sends message via chat endpoint
2. Chat endpoint fetches conversation history from database
3. Agent processes message with conversation context
4. Agent calls MCP tools (add_task, list_tasks, etc.) as needed
5. Response sent back to user and saved to database

## System Prompt Overview

The system prompt in `prompts.py` teaches the agent to:

- **Understand Natural Language**: Extract task details from conversational text
- **Call MCP Tools**: Use 5 task management tools (add, list, update, complete, delete)
- **Handle Errors Gracefully**: Ask clarifying questions instead of failing
- **Maintain Context**: Reference conversation history for follow-up questions

## System Prompt Examples

### Example 1: Add Task with Priority and Due Date

**User Input:**
```
Add a high priority task to call the dentist tomorrow at 2pm
```

**Agent Understanding:**
- **Tool**: `add_task`
- **title**: "Call the dentist"
- **priority**: "high"
- **due_date**: "2025-12-22" (tomorrow)
- **due_time**: "14:00:00" (2pm)

**Response:**
```
I've added "Call the dentist" to your task list (task #5). It's set as high priority and due tomorrow at 2pm.
```

### Example 2: Create Recurring Task

**User Input:**
```
Add a weekly meeting task every Monday at 10am
```

**Agent Understanding:**
- **Tool**: `add_task`
- **title**: "Weekly meeting"
- **recurrence**: "weekly"
- **recurrence_day**: 1 (Monday)
- **due_time**: "10:00:00"

**Response:**
```
I've added "Weekly meeting" to your task list (task #6). It will recur every Monday at 10am.
```

### Example 3: View Tasks with Filtering

**User Input:**
```
Show me all high priority tasks
```

**Agent Understanding:**
- **Tool**: `list_tasks`
- **priority**: "high"

**Response:**
```
You have 3 high priority tasks:
1. Task #2: Call the dentist (due tomorrow at 2pm)
2. Task #7: Submit report (due Dec 25)
3. Task #9: Pay bills (due this Friday)
```

### Example 4: Complete Task by ID

**User Input:**
```
Mark task 5 as done
```

**Agent Understanding:**
- **Tool**: `complete_task`
- **task_id**: 5

**Response:**
```
Task #5 "Call the dentist" is now complete! Great job!
```

### Example 5: Update Task Priority

**User Input:**
```
Change task 3 to high priority
```

**Agent Understanding:**
- **Tool**: `update_task`
- **task_id**: 3
- **priority**: "high"

**Response:**
```
Updated task #3 "Buy groceries" to high priority.
```

### Example 6: Search Tasks

**User Input:**
```
Find tasks about groceries
```

**Agent Understanding:**
- **Tool**: `search_tasks`
- **keyword**: "groceries"

**Response:**
```
I found 2 tasks matching "groceries":
1. Task #3: Buy groceries (high priority)
2. Task #8: Pick up groceries from store
```

### Example 7: Delete Task

**User Input:**
```
Delete task 10
```

**Agent Understanding:**
- **Tool**: `delete_task`
- **task_id**: 10

**Response:**
```
Task #10 "Old reminder" has been deleted successfully.
```

### Example 8: Sort Tasks

**User Input:**
```
Show my tasks sorted by due date
```

**Agent Understanding:**
- **Tool**: `list_tasks`
- **sort_by**: "due_date"

**Response:**
```
Your tasks sorted by due date (earliest first):
1. Task #2: Call dentist (due tomorrow)
2. Task #7: Submit report (due Dec 25)
3. Task #4: Team meeting (due Jan 5)
...
```

### Example 9: Add Task with Tags

**User Input:**
```
Create a work task to review the proposal, tag it with project-alpha
```

**Agent Understanding:**
- **Tool**: `add_task`
- **title**: "Review the proposal"
- **tags**: ["work", "project-alpha"]

**Response:**
```
I've added "Review the proposal" to your task list (task #11) with tags: work, project-alpha.
```

### Example 10: Error Handling - Task Not Found

**User Input:**
```
Complete task 999
```

**Agent Understanding:**
- **Tool**: `complete_task`
- **task_id**: 999
- **Result**: Error (task not found)

**Response:**
```
I couldn't find task 999 in your list. Would you like me to show you all your tasks?
```

### Example 11: Error Handling - Ambiguous Input

**User Input:**
```
Update the task
```

**Agent Understanding:**
- Missing required information (which task?)

**Response:**
```
Which task would you like to update? Please provide the task ID or title. You can say something like "Update task 5" or "Show me my tasks" to see your list.
```

### Example 12: Error Handling - Invalid Date

**User Input:**
```
Set task 3 due date to yesterday
```

**Agent Understanding:**
- Invalid date (past date)

**Response:**
```
I noticed you want to set a due date in the past. Did you mean tomorrow instead? Or would you like to specify a different date?
```

## Natural Language Understanding Patterns

The agent is trained to recognize various input formats:

### Date Patterns
- **Relative**: "today", "tomorrow", "next Monday", "this Friday"
- **Absolute**: "Dec 25", "December 25th", "2025-12-25"
- **Contextual**: "end of week", "next month", "in 3 days"

### Time Patterns
- **Standard**: "2pm", "14:00", "5:30 PM"
- **Colloquial**: "noon", "midnight", "morning" (9am), "afternoon" (2pm), "evening" (6pm)

### Priority Patterns
- **High**: "urgent", "important", "asap", "critical"
- **Medium**: "normal", "regular"
- **Low**: "someday", "maybe", "low priority"

### Recurrence Patterns
- **Daily**: "every day", "daily", "each day"
- **Weekly**: "every Monday", "weekly on Tuesday"
- **Monthly**: "monthly on the 1st", "every month on the 15th"

### Tag Patterns
- **Explicit**: "tag it with work", "add tags: personal, health"
- **Implicit**: "work task" → tag "work", "personal reminder" → tag "personal"

### Action Patterns
- **Add**: "add", "create", "make", "new"
- **View**: "show", "list", "display", "what are"
- **Update**: "change", "modify", "update", "set"
- **Complete**: "done", "finish", "complete", "mark as done"
- **Delete**: "delete", "remove", "get rid of"

## MCP Tools Available

The agent has access to these MCP tools:

| Tool | Purpose | Parameters |
|------|---------|------------|
| `add_task` | Create new task | title, description, priority, tags, due_date, due_time, recurrence, recurrence_day |
| `list_tasks` | View all tasks | status, priority, tags, sort_by, limit |
| `update_task` | Modify task | task_id, title, description, priority, tags, due_date, due_time |
| `complete_task` | Mark task done | task_id |
| `delete_task` | Remove task | task_id |
| `search_tasks` | Find by keyword | keyword |

## Error Handling Strategy

The agent follows these principles for error handling:

1. **Task Not Found**: Offer to show task list
2. **Ambiguous Input**: Ask clarifying questions
3. **Invalid Data**: Suggest corrections
4. **Multiple Matches**: Present options for user to choose
5. **API/Database Errors**: Apologize and ask user to try again

## Testing the Agent

### Unit Testing

Test individual tool calls:

```python
from app.agents.todo_agent import get_agent

agent = get_agent()

# Test add_task tool
result = await agent.execute_tool_call(
    tool_name="add_task",
    parameters={
        "user_id": "test-user",
        "title": "Test task",
        "priority": "high"
    }
)
```

### Integration Testing

Test full conversation flows:

```python
# Test in test_conversation_flows.py
response = await agent.process_message(
    user_message="Add a high priority task to buy groceries",
    conversation_history=[],
    user_id="test-user"
)

assert "buy groceries" in response["content"].lower()
assert "high priority" in response["content"].lower()
```

### Manual Testing

Use the chat interface:

1. Start backend: `cd backend && uv run uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Navigate to `http://localhost:3000`
4. Chat with the AI assistant

## Configuration

### Agent Parameters

- **Model**: `gpt-4-turbo-preview` (configurable in `todo_agent.py`)
- **Temperature**: `0.7` (balanced creativity/consistency)
- **Max Tokens**: `500` per response
- **Conversation History**: Last 50 messages

### System Prompt Customization

To customize the agent behavior, edit `prompts.py`:

```python
# Add new extraction pattern
"""
### New Feature Extraction

**Pattern**: Recognize "schedule" as synonym for "add task with due date"

**Example**:
- Input: "Schedule dentist appointment for Friday at 3pm"
- Extract: title="Dentist appointment", due_date="2025-12-27", due_time="15:00:00"
"""
```

## Performance Considerations

- **Conversation History Limit**: 50 messages to prevent token overflow
- **Response Time**: Target <2s for AI responses
- **Tool Call Optimization**: Batch multiple operations when possible
- **Database Indexes**: Optimized queries on user_id, conversation_id, created_at

## Security

- **User Isolation**: All MCP tools verify user_id ownership
- **Input Validation**: Pydantic schemas enforce constraints
- **JWT Authentication**: All endpoints require valid Bearer token
- **SQL Injection Protection**: SQLModel ORM with parameterized queries

## Troubleshooting

### Agent Not Calling Tools

**Symptom**: Agent responds conversationally but doesn't call MCP tools

**Solution**: Check system prompt includes tool descriptions and examples

### Agent Calling Wrong Tool

**Symptom**: Agent calls `list_tasks` when should call `add_task`

**Solution**: Add more examples to system prompt for clarity

### Agent Extracting Wrong Parameters

**Symptom**: Agent extracts "tomorrow" as "2025-12-20" instead of "2025-12-22"

**Solution**: Verify date parsing logic in prompts.py matches current date

### Error Responses Not Helpful

**Symptom**: Agent says "Error occurred" instead of explaining

**Solution**: Enhance error handling patterns in prompts.py

## Future Enhancements

Potential improvements for the agent:

1. **Multi-turn Confirmation**: Ask user to confirm before deleting tasks
2. **Bulk Operations**: "Mark all high priority tasks as complete"
3. **Smart Suggestions**: "You have 3 overdue tasks. Would you like to see them?"
4. **Task Dependencies**: "Complete task 5 before starting task 6"
5. **Natural Language Queries**: "Which tasks are due this week?"

## References

- **OpenAI Agents SDK**: https://github.com/openai/openai-agents-sdk
- **MCP SDK**: https://github.com/modelcontextprotocol/python-sdk
- **FastAPI**: https://fastapi.tiangolo.com
- **SQLModel**: https://sqlmodel.tiangolo.com

---

**Last Updated**: 2025-12-21
**Version**: 3.0.0 (Phase 3 - AI Chatbot Complete)
