---
id: 003
title: Update Phase 3 Constitution
stage: constitution
date: 2025-12-17
surface: agent
model: claude-sonnet-4-5
feature: none
branch: 003-phase3-ai-chatbot
user: AQI
command: /sp.constitution
labels: ["constitution", "phase3", "ai-chatbot", "mcp", "stateless-architecture"]
links:
  spec: specs/003-phase3-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - AGENTS.md
  - CLAUDE.md
tests:
  - None (constitution update)
---

## Prompt

User: "I want that all our basic to advance level features should be added."

Context: User requested updating the project constitution for Phase 3 to include ALL 10 features (Basic + Intermediate + Advanced levels) via AI chatbot interface, not just Basic Level features.

## Response snapshot

Updated constitution from v2.0.0 to v3.0.0 (MAJOR version bump) with comprehensive Phase 3 changes:

**Key Updates:**
1. **YAGNI Principle (III)**: Expanded to explicitly list all 10 features
   - Basic Level (1-5): Add Task, Delete Task, Update Task, View Task List, Mark as Complete
   - Intermediate Level (6-8): Priorities & Tags, Search & Filter, Sort Tasks
   - Advanced Level (9-10): Recurring Tasks, Due Dates & Reminders
   - All accessible via natural language commands

2. **Technology Stack**: Added Phase 3 technologies
   - Frontend: OpenAI ChatKit (conversational UI)
   - AI Framework: OpenAI Agents SDK (intent recognition, orchestration)
   - Tools: Official MCP SDK (Model Context Protocol)
   - Architecture: Stateless chat endpoint with database-persisted conversation state

3. **Database Models**: Added Phase 3 tables
   - Conversation table (id, user_id, created_at, updated_at)
   - Message table (id, conversation_id, user_id, role, content, created_at)
   - Task table: Preserved all Phase 2 fields (priority, tags, due_date, due_time, recurrence, recurrence_day)

4. **MCP Tools**: Defined 6 stateless tools supporting all 10 features
   - add_task (supports priority, tags, due dates, recurrence)
   - list_tasks (supports filtering by status, priority, tag, sorting)
   - complete_task (handles recurring task logic)
   - delete_task
   - update_task (all fields)
   - search_tasks (keyword search)

5. **New Principles Added:**
   - **Principle XII**: AI Agent Development & MCP Server Architecture
     - MCP server runs within FastAPI backend
     - Official MCP SDK for tool registration
     - All tools stateless (database state only)
     - Intent recognition patterns defined

   - **Principle XIII**: Stateless Architecture & Conversation State Management
     - Chat endpoint stateless (fetch conversation history per request)
     - 10-step request cycle defined
     - Horizontal scalability enabled
     - Database as single source of truth

   - **Principle XIV**: Natural Language Understanding & Intent Recognition
     - Entity extraction (priorities, tags, dates, times, recurrence patterns)
     - Example commands for all 10 features
     - System prompt requirements
     - Ambiguity handling patterns

6. **Natural Language Examples**: Added comprehensive examples for all feature levels
   - "Add a high priority task to call dentist"
   - "Show me high priority tasks"
   - "Add a weekly meeting task every Monday"
   - "Set due date to Friday 5 PM for task 3"

## Outcome

- ✅ Impact: **MAJOR version bump** (2.0.0 → 3.0.0) - Phase transition from Full-Stack Web to AI Chatbot with MCP
- 🧪 Tests: Constitution updated; no code tests required at this stage
- 📁 Files: Updated `.specify/memory/constitution.md`, created `AGENTS.md`, updated `CLAUDE.md`
- 🔁 Next prompts: Create Phase 3 specification (`/sp.specify`), then architecture planning (`/sp.plan`)
- 🧠 Reflection: Critical user correction ensured all 10 features included in Phase 3 scope, not just Basic Level. Constitution now provides complete guidance for AI chatbot development with stateless MCP architecture.

## Evaluation notes (flywheel)

- Failure modes observed: Initial scope misunderstanding (proposed only Basic Level features before user correction)
- Graders run and results (PASS/FAIL): N/A (constitution update)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate constitution alignment during `/sp.plan` phase to ensure all architectural decisions follow the updated principles
