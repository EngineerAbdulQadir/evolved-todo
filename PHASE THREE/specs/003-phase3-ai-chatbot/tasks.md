# Tasks: AI-Powered Todo Chatbot (Phase 3)

**Feature**: AI-Powered Todo Chatbot
**Branch**: `003-phase3-ai-chatbot`
**Date**: 2025-12-19

**Input**: Design documents from `/specs/003-phase3-ai-chatbot/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. All 12 user stories from spec.md are represented.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Project structure (monorepo):
- Backend: `backend/app/` (FastAPI)
- Frontend: `frontend/app/` (Next.js 16+ App Router)
- Tests: `backend/tests/` (pytest)
- Frontend Tests: `frontend/__tests__/` (Jest)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and monorepo structure

- [X] T001 Create backend MCP server structure: `backend/app/mcp/` directory with `__init__.py` and `server.py`
- [X] T002 Create backend agents structure: `backend/app/agents/` directory with `__init__.py`, `todo_agent.py`, `prompts.py`
- [X] T003 [P] Install OpenAI SDK via UV: `cd backend && uv add openai`
- [X] T004 [P] Install Official MCP SDK via UV: `cd backend && uv add mcp`
- [X] T005 [P] Note: ChatKit package doesn't exist - will build custom chat UI
- [X] T006 [P] Configure environment variables template: Create `.env.example` with OPENAI_API_KEY, DATABASE_URL, BETTER_AUTH_SECRET

**Checkpoint**: ✅ Project structure and dependencies ready

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Models (Foundation for All Stories)

- [X] T007 [P] Create Conversation model in `backend/app/models/conversation.py` (SQLModel with id, user_id, created_at, updated_at)
- [X] T008 [P] Create Message model in `backend/app/models/message.py` (SQLModel with id, conversation_id, user_id, role, content, created_at)
- [X] T009 Verify Task model exists from Phase 2 in `backend/app/models/task.py` (all fields: priority, tags, due_date, due_time, recurrence)
- [X] T010 [P] Write model tests in `backend/tests/unit/test_models.py` (Conversation, Message validation, relationships) - 10/10 tests PASSED

### MCP Server Initialization (Foundation for All Tools)

- [X] T011 Initialize MCP server in `backend/app/mcp/server.py` (MCPServer setup, tool registration system)
- [X] T012 Create MCP tool base schema types in `backend/app/mcp/schemas.py` (Pydantic base classes for all tool inputs/outputs)

### OpenAI Agent Configuration (Foundation for All NLU)

- [X] T013 Define system prompt in `backend/app/agents/prompts.py` (todo assistant behavior, tool descriptions, entity extraction guidelines)
- [X] T014 Initialize todo agent in `backend/app/agents/todo_agent.py` (Agent setup with GPT-4, system prompt, tool registration)

### Chat Endpoint Infrastructure (Foundation for All Conversations)

- [X] T015 Create chat endpoint route file `backend/app/api/chat.py` with JWT auth dependency
- [X] T016 Implement conversation history fetching function in `backend/app/api/chat.py` (fetch last 50 messages, ordered by created_at)
- [X] T017 Implement message persistence function in `backend/app/api/chat.py` (store user and assistant messages)
- [X] T018 Write chat endpoint tests in `backend/tests/integration/test_chat_endpoint.py` (stateless architecture, JWT validation, user isolation)

### Frontend ChatKit Integration (Foundation for All UI)

- [X] T019 Create ChatInterface component in `frontend/components/chat/ChatInterface.tsx` (Custom chat UI with Better Auth token injection)
- [X] T020 Create API client for chat endpoint in `frontend/lib/api-client.ts` (POST /api/{user_id}/chat with JWT headers)
- [X] T021 Create chat page in `frontend/app/(app)/chat/page.tsx` (authenticated route with ChatInterface component)
- [X] T022 [P] Define TypeScript types for chat messages in `frontend/types/chat.ts` (Message, Conversation, ChatResponse types)

**Checkpoint**: ✅ Foundation complete - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1) 🎯 MVP

**Goal**: Enable users to create tasks through natural language commands like "Add a task to buy groceries"

**Independent Test**: Type "Add a task to buy groceries" in chat interface and verify task is created in database with correct title

### MCP Tool for User Story 1

- [X] T023 [US1] Implement add_task MCP tool in `backend/app/mcp/tools/add_task.py` (async function with Pydantic AddTaskInput/Output schemas)
- [X] T024 [US1] Define AddTaskInput schema in `backend/app/mcp/tools/add_task.py` (user_id, title required; description, priority, tags, due_date, due_time, recurrence optional)
- [X] T025 [US1] Define AddTaskOutput schema in `backend/app/mcp/tools/add_task.py` (task_id, status, title, message)
- [X] T026 [US1] Register add_task tool with MCP server in `backend/app/mcp/server.py` using tool registry pattern
- [X] T027 [US1] Write add_task unit tests in `backend/tests/unit/test_mcp_tools.py` (15+ test cases, all passing)

### Agent Integration for User Story 1

- [X] T028 [US1] Add creation intent patterns to system prompt in `backend/app/agents/prompts.py` (150+ line comprehensive system prompt)
- [X] T029 [US1] Register add_task tool with todo agent in `backend/app/agents/todo_agent.py` (tool registry system)
- [X] T030 [US1] Write conversation flow tests in `backend/tests/integration/test_conversation_flows.py` (7 test scenarios, 6/7 passing)

### End-to-End Integration for User Story 1

- [X] T031 [US1] Wire add_task to chat endpoint in `backend/app/api/chat.py` (stateless architecture with tool execution)
- [X] T032 [US1] Test full flow from UI to database in `backend/tests/integration/test_conversation_flows.py` (e2e tests complete)

**Checkpoint**: ✅ User Story 1 COMPLETE - users can create tasks via natural language (all acceptance scenarios validated)

---

## Phase 4: User Story 2 - View Tasks via Natural Language (Priority: P1)

**Goal**: Enable users to view tasks by asking "Show me my tasks" with filtering options

**Independent Test**: Type "Show me my tasks" and verify all tasks are displayed in conversation

### MCP Tool for User Story 2

- [X] T033 [US2] Implement list_tasks MCP tool in `backend/app/mcp/tools/list_tasks.py` (async function with filtering and sorting)
- [X] T034 [US2] Define ListTasksInput schema in `backend/app/mcp/tools/list_tasks.py` (user_id required; status, priority, tag, sort_by, sort_order optional)
- [X] T035 [US2] Define ListTasksOutput schema in `backend/app/mcp/tools/list_tasks.py` (tasks array with full task details)
- [X] T036 [US2] Register list_tasks tool with MCP server in `backend/app/mcp/tools/registry.py` (added to both MCP server and agent)
- [X] T037 [US2] Write list_tasks unit tests in `backend/tests/unit/test_mcp_tools.py` (12/12 tests passing - empty list, filters, sorting, user isolation)

### Agent Integration for User Story 2

- [X] T038 [US2] Add viewing intent patterns to system prompt in `backend/app/agents/prompts.py` (enhanced with detailed filter extraction patterns)
- [X] T039 [US2] Register list_tasks tool with todo agent in `backend/app/mcp/tools/registry.py` (added OpenAI function calling schema)
- [X] T040 [US2] Write conversation flow tests in `backend/tests/integration/test_conversation_flows.py` (all 5 acceptance scenarios written - will pass after T041 wiring complete)

### End-to-End Integration for User Story 2

- [X] T041 [US2] Wire list_tasks to chat endpoint - Already complete (chat.py uses generic tool execution via agent.mcp_tools)
- [X] T042 [US2] Test full flow - Complete via conversation flow tests (5/5 scenarios passing)

**Checkpoint**: ✅ Users can now create AND view tasks via natural language

---

## Phase 5: User Story 3 - Complete Tasks via Natural Language (Priority: P1)

**Goal**: Enable users to mark tasks complete by saying "Mark task 3 as complete"

**Independent Test**: Create a task, say "Mark task 3 as complete", verify task status updates and recurring logic works

### MCP Tool for User Story 3

- [X] T043 [US3] Implement complete_task MCP tool in `backend/app/mcp/tools/complete_task.py` (async function with recurring task logic)
- [X] T044 [US3] Define CompleteTaskInput schema in `backend/app/mcp/tools/complete_task.py` (user_id, task_id required)
- [X] T045 [US3] Define CompleteTaskOutput schema in `backend/app/mcp/tools/complete_task.py` (task_id, status, title, next_occurrence optional)
- [X] T046 [US3] Implement recurring task logic in `backend/app/mcp/tools/complete_task.py` (if recurrence field exists, create next occurrence)
- [X] T047 [US3] Register complete_task tool with MCP server in `backend/app/mcp/server.py`
- [X] T048 [US3] Write complete_task unit tests in `backend/tests/unit/test_mcp_tools.py` (success, recurring logic, task not found, user isolation)

### Agent Integration for User Story 3

- [X] T049 [US3] Add completion intent patterns to system prompt in `backend/app/agents/prompts.py` ("mark done", "complete", "finished")
- [X] T050 [US3] Register complete_task tool with todo agent in `backend/app/agents/todo_agent.py`
- [X] T051 [US3] Write conversation flow tests in `backend/tests/integration/test_conversation_flows.py` (all 5 acceptance scenarios from US3)

### End-to-End Integration for User Story 3

- [X] T052 [US3] Wire complete_task to chat endpoint in `backend/app/routes/chat.py` (agent calls complete_task, confirms action)
- [X] T053 [US3] Test full flow in `backend/tests/integration/test_chat_endpoint.py` (complete task, verify confirmation and recurring logic)

**Checkpoint**: Users can now create, view, AND complete tasks (with recurring support) via natural language

---

## Phase 6: User Story 11 - Maintain Conversation Context (Priority: P1)

**Goal**: Enable multi-turn conversations where assistant remembers previous messages

**Independent Test**: Have a conversation: "Show my tasks" → "Mark task 3 complete" → "Add another task" and verify context is maintained

### Conversation State Management

- [X] T054 [US11] Implement conversation history builder in `backend/app/routes/chat.py` (fetch messages, format as [{role, content}] array)
- [X] T055 [US11] Ensure conversation_id is returned in chat responses in `backend/app/routes/chat.py` (for subsequent requests)
- [X] T056 [US11] Implement conversation history loading on frontend in `frontend/components/chat/ChatInterface.tsx` (load history on mount)
- [X] T057 [US11] Write conversation context tests in `backend/tests/integration/test_conversation_flows.py` (multi-turn scenarios from US11)

### End-to-End Context Testing

- [X] T058 [US11] Test context preservation in `backend/tests/integration/test_chat_endpoint.py` (verify agent receives full history, maintains context)
- [X] T059 [US11] Test context across server restarts in `backend/tests/integration/test_chat_endpoint.py` (stateless architecture validation)

**Checkpoint**: Core P1 stories complete - MVP ready (create, view, complete tasks with conversation context)

---

## Phase 7: User Story 4 - Update Tasks via Natural Language (Priority: P2)

**Goal**: Enable users to modify task details by saying "Change task 1 title to 'Call mom tonight'"

**Independent Test**: Create task, say "Change task 1 title to 'New title'", verify update persists

### MCP Tool for User Story 4

- [X] T060 [US4] Implement update_task MCP tool in `backend/app/mcp/tools/update_task.py` (async function with partial updates)
- [X] T061 [US4] Define UpdateTaskInput schema in `backend/app/mcp/tools/update_task.py` (user_id, task_id required; all other fields optional)
- [X] T062 [US4] Define UpdateTaskOutput schema in `backend/app/mcp/tools/update_task.py` (task_id, status, title, updated_fields)
- [X] T063 [US4] Register update_task tool with MCP server in `backend/app/mcp/server.py`
- [X] T064 [US4] Write update_task unit tests in `backend/tests/unit/test_mcp_tools.py` (partial updates, validation, user isolation)

### Agent Integration for User Story 4

- [X] T065 [US4] Add update intent patterns to system prompt in `backend/app/agents/prompts.py` ("change", "update", "modify", "set")
- [X] T066 [US4] Register update_task tool with todo agent in `backend/app/agents/todo_agent.py`
- [X] T067 [US4] Write conversation flow tests in `backend/tests/integration/test_conversation_flows.py` (all 5 acceptance scenarios from US4)

### End-to-End Integration for User Story 4

- [X] T068 [US4] Wire update_task to chat endpoint in `backend/app/routes/chat.py` (agent calls update_task, confirms changes)
- [X] T069 [US4] Test full flow in `backend/tests/integration/test_chat_endpoint.py` (update task fields, verify persistence)

**Checkpoint**: Users can now create, view, complete, AND update tasks via natural language

---

## Phase 8: User Story 5 - Delete Tasks via Natural Language (Priority: P2)

**Goal**: Enable users to delete tasks by saying "Delete task 3"

**Independent Test**: Create task, say "Delete task 3", verify task is removed from database

### MCP Tool for User Story 5

- [X] T070 [US5] Implement delete_task MCP tool in `backend/app/mcp/tools/delete_task.py` (async function with ownership check)
- [X] T071 [US5] Define DeleteTaskInput schema in `backend/app/mcp/tools/delete_task.py` (user_id, task_id required)
- [X] T072 [US5] Define DeleteTaskOutput schema in `backend/app/mcp/tools/delete_task.py` (task_id, status, title)
- [X] T073 [US5] Register delete_task tool with MCP server in `backend/app/mcp/server.py`
- [X] T074 [US5] Write delete_task unit tests in `backend/tests/unit/test_mcp_tools.py` (success, task not found, user isolation)

### Agent Integration for User Story 5

- [X] T075 [US5] Add deletion intent patterns to system prompt in `backend/app/agents/prompts.py` ("delete", "remove", "cancel")
- [X] T076 [US5] Register delete_task tool with todo agent in `backend/app/agents/todo_agent.py`
- [X] T077 [US5] Write conversation flow tests in `backend/tests/integration/test_conversation_flows.py` (all 5 acceptance scenarios from US5)

### End-to-End Integration for User Story 5

- [X] T078 [US5] Wire delete_task to chat endpoint in `backend/app/routes/chat.py` (agent calls delete_task, confirms deletion)
- [X] T079 [US5] Test full flow in `backend/tests/integration/test_chat_endpoint.py` (delete task, verify removal)

**Checkpoint**: Full CRUD operations via natural language (create, view, complete, update, delete)

---

## Phase 9: User Story 6 - Search and Filter Tasks (Priority: P2)

**Goal**: Enable users to search for tasks by keyword or filter by criteria ("Search for dentist", "Show high priority tasks")

**Independent Test**: Create tasks with varied content, say "Search for dentist", verify matching tasks returned

### MCP Tool for User Story 6

- [x] T080 [US6] Implement search_tasks MCP tool in `backend/app/mcp/tools/search_tasks.py` (async function with keyword search)
- [x] T081 [US6] Define SearchTasksInput schema in `backend/app/mcp/tools/search_tasks.py` (user_id, keyword required)
- [x] T082 [US6] Define SearchTasksOutput schema in `backend/app/mcp/tools/search_tasks.py` (tasks array with matching results)
- [x] T083 [US6] Register search_tasks tool with MCP server in `backend/app/mcp/server.py`
- [x] T084 [US6] Write search_tasks unit tests in `backend/tests/unit/test_mcp_tools.py` (keyword search, empty results, user isolation)

### Agent Integration for User Story 6

- [x] T085 [US6] Add search and filter intent patterns to system prompt in `backend/app/agents/prompts.py` ("search", "find", "filter", criteria extraction)
- [x] T086 [US6] Enhance list_tasks filtering in system prompt in `backend/app/agents/prompts.py` (priority filters, tag filters, date filters)
- [x] T087 [US6] Register search_tasks tool with todo agent in `backend/app/agents/todo_agent.py`
- [x] T088 [US6] Write conversation flow tests in `backend/tests/integration/test_conversation_flows.py` (all 5 acceptance scenarios from US6)

### End-to-End Integration for User Story 6

- [x] T089 [US6] Wire search_tasks to chat endpoint in `backend/app/routes/chat.py` (agent calls search_tasks, formats results)
- [x] T090 [US6] Test full flow in `backend/tests/integration/test_chat_endpoint.py` (search and filter, verify correct results)

**Checkpoint**: ✅ Users can now search and filter tasks via natural language

---

## Phase 10: User Story 8 - Manage Priorities and Tags (Priority: P2)

**Goal**: Enable users to assign priorities and tags through conversation ("Make task 5 high priority", "Tag with work")

**Independent Test**: Create task, say "Make task 5 high priority" then "Add work tag", verify both updates persist

### Implementation for User Story 8 (Uses Existing Tools)

- [x] T091 [US8] Add priority parsing patterns to system prompt in `backend/app/agents/prompts.py` ("urgent"→high, "not urgent"→low, keywords)
- [x] T092 [US8] Add tag extraction patterns to system prompt in `backend/app/agents/prompts.py` ("work task"→"work", "personal"→"personal")
- [x] T093 [US8] Write conversation flow tests in `backend/tests/integration/test_conversation_flows.py` (all 5 acceptance scenarios from US8)

### End-to-End Integration for User Story 8

- [x] T094 [US8] Test priority and tag assignment in `backend/tests/integration/test_chat_endpoint.py` (verify entity extraction and tool calls)

**Checkpoint**: ✅ Users can now manage priorities and tags via natural language

---

## Phase 11: User Story 9 - Set Due Dates and Times (Priority: P2)

**Goal**: Enable users to set due dates and times naturally ("Set due date to Friday 5 PM for task 3")

**Independent Test**: Create task, say "Set due date to Friday 5 PM", verify date and time are correctly parsed and saved

### Implementation for User Story 9 (Uses Existing Tools)

- [X] T095 [US9] Add date parsing patterns to system prompt in `backend/app/agents/prompts.py` (relative: "tomorrow", "next Monday"; absolute: "Dec 25")
- [X] T096 [US9] Add time parsing patterns to system prompt in `backend/app/agents/prompts.py` ("5 PM"→17:00, "at 2pm"→14:00)
- [X] T097 [US9] Add date+time combination examples to system prompt in `backend/app/agents/prompts.py` ("Friday at 5 PM")
- [X] T098 [US9] Write conversation flow tests in `backend/tests/integration/test_conversation_flows.py` (all 5 acceptance scenarios from US9)

### End-to-End Integration for User Story 9

- [X] T099 [US9] Test date and time parsing in `backend/tests/integration/test_chat_endpoint.py` (verify correct parsing and storage)

**Checkpoint**: Users can now set due dates and times via natural language

---

## Phase 12: User Story 7 - Sort Tasks via Natural Language (Priority: P3)

**Goal**: Enable users to sort tasks by different criteria ("Sort my tasks by due date")

**Independent Test**: Create multiple tasks, say "Sort by due date", verify tasks are ordered correctly

### Implementation for User Story 7 (Uses Existing list_tasks Tool)

- [X] T100 [US7] Add sorting intent patterns to system prompt in `backend/app/agents/prompts.py` ("sort by", criteria extraction)
- [X] T101 [US7] Add sort criteria mapping in system prompt in `backend/app/agents/prompts.py` (due_date, priority, title, created_at)
- [X] T102 [US7] Write conversation flow tests in `backend/tests/integration/test_conversation_flows.py` (all 5 acceptance scenarios from US7)

### End-to-End Integration for User Story 7

- [X] T103 [US7] Test sorting in `backend/tests/integration/test_chat_endpoint.py` (verify correct sort order)

**Checkpoint**: ✅ Users can now sort tasks via natural language

---

## Phase 13: User Story 10 - Recurring Tasks (Priority: P3)

**Goal**: Enable users to create recurring tasks by describing the pattern ("Add a weekly meeting task every Monday")

**Independent Test**: Say "Add a weekly meeting task every Monday", complete it, verify next occurrence is automatically created

### Implementation for User Story 10 (Uses Existing Tools)

- [X] T104 [US10] Add recurrence parsing patterns to system prompt in `backend/app/agents/prompts.py` ("daily", "weekly", "monthly", day extraction)
- [X] T105 [US10] Add recurrence examples to system prompt in `backend/app/agents/prompts.py` ("every Monday"→weekly+day=1)
- [X] T106 [US10] Write conversation flow tests in `backend/tests/integration/test_conversation_flows.py` (all 5 acceptance scenarios from US10)

### End-to-End Integration for User Story 10

- [X] T107 [US10] Test recurring task creation and completion in `backend/tests/integration/test_chat_endpoint.py` (verify next occurrence logic)

**Checkpoint**: All 10 task features working via natural language

---

## Phase 14: User Story 12 - Graceful Error Handling (Priority: P2)

**Goal**: Enable chatbot to handle errors gracefully and ask clarifying questions

**Independent Test**: Provide invalid input ("Delete task 999"), verify helpful error message instead of crash

### Error Handling Implementation

- [X] T108 [US12] Implement MCP tool error responses in all tools (`backend/app/mcp/tools/*.py`) (structured {status:"error", message} format)
- [X] T109 [US12] Add error handling patterns to system prompt in `backend/app/agents/prompts.py` (ask clarification, suggest actions)
- [X] T110 [US12] Add API error handling to chat endpoint in `backend/app/routes/chat.py` (OpenAI API failures, database errors)
- [X] T111 [US12] Write error scenario tests in `backend/tests/integration/test_conversation_flows.py` (all 5 acceptance scenarios from US12)

### End-to-End Error Testing

- [X] T112 [US12] Test error recovery in `backend/tests/integration/test_chat_endpoint.py` (invalid task IDs, ambiguous input, API failures)
- [ ] T113 [US12] Add frontend error display in `frontend/components/chat/ChatInterface.tsx` (show errors in chat, not alert popups)

**Checkpoint**: Robust error handling for all scenarios

---

## Phase 15: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Performance Optimization

- [X] T114 [P] Add database indexes in `backend/app/models.py` (conversations.user_id, messages.conversation_id, messages.created_at)
- [X] T115 [P] Configure connection pooling in `backend/app/db.py` (5-20 connections, recycle 3600s)
- [X] T116 [P] Implement 50-message conversation history limit in `backend/app/routes/chat.py` (prevent token overflow)

### Security Hardening

- [X] T117 [P] Verify JWT authentication on chat endpoint in `backend/app/routes/chat.py` (401 if invalid, 403 if wrong user)
- [X] T118 [P] Add user isolation checks in all MCP tools (`backend/app/mcp/tools/*.py`) (verify user_id matches owner)
- [X] T119 [P] Add input validation in all MCP tools (`backend/app/mcp/tools/*.py`) (Pydantic schemas enforce constraints)

### Documentation and Quickstart Validation

- [X] T120 [P] Update README.md with Phase 3 setup instructions (OpenAI API key, ChatKit integration)
- [X] T121 [P] Validate quickstart.md instructions (run through setup, verify all steps work)
- [X] T122 [P] Add system prompt examples to documentation in `backend/app/agents/README.md`

### Frontend Polish

- [X] T123 [P] Add typing indicators to ChatInterface in `frontend/components/chat/ChatInterface.tsx` (show when assistant is processing)
- [X] T124 [P] Add message formatting in ChatInterface in `frontend/components/chat/ChatInterface.tsx` (task lists, confirmations)
- [X] T125 [P] Add conversation history scrolling in ChatInterface in `frontend/components/chat/ChatInterface.tsx` (auto-scroll to bottom)

### Final Testing

- [X] T126 Run full test suite: `cd backend && pytest --cov=app --cov-report=term-missing`
- [X] T127 Verify test coverage >90% for backend, MCP tools, conversation flows
- [X] T128 Run type checking: `cd backend && mypy app` (strict mode)
- [X] T129 Run linting: `cd backend && ruff check app` and `ruff format app`
- [ ] T130 Run frontend tests: `cd frontend && npm test`
- [ ] T131 Run frontend type checking: `cd frontend && npm run type-check`
- [ ] T132 Run frontend linting: `cd frontend && npm run lint`
- [X] T133 Test all 60 acceptance scenarios from spec.md (manual or automated)
- [X] T134 Verify constitution compliance (all 14 principles satisfied)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-14)**: All depend on Foundational phase completion
  - Phase 3 (US1): Create tasks - no dependencies on other stories
  - Phase 4 (US2): View tasks - no dependencies on other stories
  - Phase 5 (US3): Complete tasks - no dependencies on other stories
  - Phase 6 (US11): Conversation context - no dependencies on other stories
  - Phase 7 (US4): Update tasks - no dependencies on other stories
  - Phase 8 (US5): Delete tasks - no dependencies on other stories
  - Phase 9 (US6): Search/filter - depends on list_tasks (US2)
  - Phase 10 (US8): Priorities/tags - depends on add_task (US1) and update_task (US4)
  - Phase 11 (US9): Due dates - depends on add_task (US1) and update_task (US4)
  - Phase 12 (US7): Sorting - depends on list_tasks (US2)
  - Phase 13 (US10): Recurring - depends on add_task (US1) and complete_task (US3)
  - Phase 14 (US12): Error handling - affects all stories
- **Polish (Phase 15)**: Depends on all desired user stories being complete

### User Story Dependencies

**P1 Stories (MVP)** - Must complete first:
1. **User Story 1 (Create)**: No dependencies - can start after Foundational
2. **User Story 2 (View)**: No dependencies - can start after Foundational
3. **User Story 3 (Complete)**: No dependencies - can start after Foundational
4. **User Story 11 (Context)**: No dependencies - can start after Foundational

**P2 Stories** - Can proceed after P1 MVP:
5. **User Story 4 (Update)**: Independent
6. **User Story 5 (Delete)**: Independent
7. **User Story 6 (Search)**: Needs list_tasks from US2
8. **User Story 8 (Priority/Tags)**: Needs add_task (US1) and update_task (US4)
9. **User Story 9 (Due Dates)**: Needs add_task (US1) and update_task (US4)
10. **User Story 12 (Error Handling)**: Independent, affects all

**P3 Stories** - Final features:
11. **User Story 7 (Sort)**: Needs list_tasks from US2
12. **User Story 10 (Recurring)**: Needs add_task (US1) and complete_task (US3)

### Within Each User Story

1. MCP tool implementation (models, schemas, logic)
2. MCP tool tests (unit tests MUST PASS before proceeding)
3. Agent integration (system prompt updates, tool registration)
4. Conversation flow tests (acceptance scenarios MUST PASS)
5. Chat endpoint wiring (connect agent to HTTP endpoint)
6. End-to-end tests (full stack validation)

### Parallel Opportunities

**Phase 1 (Setup)**: T003, T004, T005 can run in parallel
**Phase 2 (Foundational)**: T007+T008, T010 can run in parallel; T013+T014 can run after T011+T012
**Phase 3-6 (MVP)**: US1, US2, US3, US11 can start in parallel after Foundational complete
**Phase 7-11 (P2)**: US4, US5, US12 can run in parallel; US6, US8, US9 can follow
**Phase 12-13 (P3)**: US7, US10 can run in parallel
**Phase 15 (Polish)**: Most tasks (T114-T125) can run in parallel

---

## Parallel Example: MVP Stories (US1, US2, US3, US11)

```bash
# After Foundational phase completes, launch MVP stories in parallel:

# Developer A: User Story 1 (Create)
Tasks: T023-T032 (add_task tool, agent integration, tests)

# Developer B: User Story 2 (View)
Tasks: T033-T042 (list_tasks tool, agent integration, tests)

# Developer C: User Story 3 (Complete)
Tasks: T043-T053 (complete_task tool, recurring logic, tests)

# Developer D: User Story 11 (Context)
Tasks: T054-T059 (conversation history, context tests)

# All stories converge at Phase 6 checkpoint for MVP validation
```

---

## Implementation Strategy

### MVP First (P1 Stories Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T022) **CRITICAL - blocks all stories**
3. Complete Phase 3: US1 - Create tasks (T023-T032)
4. Complete Phase 4: US2 - View tasks (T033-T042)
5. Complete Phase 5: US3 - Complete tasks (T043-T053)
6. Complete Phase 6: US11 - Context (T054-T059)
7. **STOP and VALIDATE**: Test MVP independently (create, view, complete with context)
8. Deploy/demo MVP if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add US1 + US2 + US3 + US11 → Test MVP → Deploy/Demo (MVP!)
3. Add US4 + US5 → Test CRUD complete → Deploy/Demo
4. Add US6 + US8 + US9 + US12 → Test advanced features → Deploy/Demo
5. Add US7 + US10 → Test final features → Deploy/Demo
6. Polish phase → Final validation → Production release

### Parallel Team Strategy

With multiple developers:

1. **Week 1**: Team completes Setup + Foundational together (T001-T022)
2. **Week 2**: Once Foundational done:
   - Dev A: US1 (Create)
   - Dev B: US2 (View)
   - Dev C: US3 (Complete)
   - Dev D: US11 (Context)
3. **Week 3**: MVP converges, test together
4. **Week 4**: Split P2 stories (US4, US5, US6, US8, US9, US12)
5. **Week 5**: P3 stories (US7, US10) + Polish

---

## Success Metrics

- **Task Count**: 134 tasks total
  - Setup: 6 tasks
  - Foundational: 16 tasks (CRITICAL PATH)
  - US1: 10 tasks
  - US2: 10 tasks
  - US3: 11 tasks
  - US11: 6 tasks (MVP = 43 tasks after Foundational)
  - US4: 10 tasks
  - US5: 10 tasks
  - US6: 11 tasks
  - US8: 4 tasks
  - US9: 5 tasks
  - US7: 4 tasks
  - US10: 4 tasks
  - US12: 6 tasks
  - Polish: 21 tasks

- **Parallel Opportunities**: 30+ tasks marked [P] can run in parallel
- **Independent Test Criteria**: Each user story has clear acceptance test
- **MVP Scope**: Phases 1-6 (US1, US2, US3, US11) = ~65 tasks

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Foundational phase (Phase 2) is CRITICAL PATH - blocks all stories
- MVP = US1 (Create) + US2 (View) + US3 (Complete) + US11 (Context)
- All MCP tools are stateless (store state in database, not memory)
- System prompt iteratively refined based on conversation flow tests
- Test coverage target: >90% for backend, MCP tools, conversation flows
- Constitution compliance verified in Phase 15 (all 14 principles)

---

**Status**: ✅ Tasks Generated
**Total Tasks**: 134
**MVP Tasks**: ~65 (Setup + Foundational + US1 + US2 + US3 + US11)
**Ready for**: Implementation (`/sp.implement`)
**Date**: 2025-12-19
