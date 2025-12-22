---
id: 002
title: Create Phase 3 Implementation Plan
stage: plan
date: 2025-12-17
surface: agent
model: claude-sonnet-4-5
feature: 003-phase3-ai-chatbot
branch: 003-phase3-ai-chatbot
user: AQI
command: /sp.plan
labels: ["plan", "phase3", "architecture", "mcp", "stateless", "openai-agents-sdk"]
links:
  spec: specs/003-phase3-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-phase3-ai-chatbot/plan.md
  - specs/003-phase3-ai-chatbot/data-model.md
tests:
  - Plan validated against constitution (all 14 principles passed)
---

## Prompt

User: "create a proper plan for our phase 3 ai chatbot"

Context: User requested comprehensive implementation plan for Phase 3 AI chatbot following the planning workflow (/sp.plan command). Plan should include Phase 0 research (technology decisions), Phase 1 design (data models, contracts, quickstart), constitution check, and project structure.

## Response snapshot

Created comprehensive Phase 3 implementation plan with complete Phase 0 research and Phase 1 design artifacts.

**Planning Phases Completed**:

**Phase 0: Research & Technology Decisions** (10 research areas):
1. **OpenAI ChatKit Integration**: Selected as primary conversational UI component
   - Rationale: Pre-built interface, officially maintained, React/Next.js integration, reduces frontend complexity
   - Alternative rejected: Custom React UI (higher development overhead)

2. **OpenAI Agents SDK for Intent Recognition**: Selected for AI logic and NLU
   - Rationale: Purpose-built for agentic workflows, native MCP tool support, handles conversation context automatically
   - Alternative rejected: Direct OpenAI API calls (requires manual tool calling logic)

3. **Official MCP SDK (Python)**: Selected for stateless tool definitions
   - Rationale: MCP standard for AI tools, schema validation, clean separation of concerns, independently testable
   - Alternative rejected: Custom tool functions (no standardization)

4. **Stateless Chat Endpoint Architecture**: Selected for horizontal scalability
   - Rationale: Any server handles any request, resilient to restarts, no session management, database as single source of truth
   - Alternative rejected: Stateful WebSocket (requires sticky sessions, doesn't scale)

5. **Database Schema**: Add conversations and messages tables to Neon PostgreSQL
   - Rationale: Leverage existing Neon infrastructure, SQLModel automatic table creation, normalized schema
   - Schema: conversations (id, user_id, created_at, updated_at), messages (id, conversation_id, user_id, role, content, created_at)

6. **Natural Language Understanding Strategy**: GPT-4 with system prompt engineering
   - Rationale: Strong NLU out of the box, cheaper than custom models, agent SDK handles tool calling
   - System prompt: Define personality, list tools, entity extraction guidelines, example conversations

7. **JWT Authentication Flow**: Extend Better Auth from Phase 2 to chat endpoint
   - Rationale: No changes needed to existing auth system, simply add JWT middleware to chat endpoint
   - Security: All MCP tools receive user_id from JWT, filter all queries by user_id

8. **Testing Strategy**: Three-tier approach (MCP tool unit tests, conversation flow integration tests, e2e ChatKit tests)
   - Tool tests: 100% coverage for MCP tools with mock database
   - Flow tests: All 60 acceptance scenarios from spec
   - Endpoint tests: >90% coverage for chat endpoint

9. **Performance Optimization**: Database query optimization, connection pooling, conversation history limits
   - Target: <3 seconds for 95% of requests
   - Optimization: Index on conversation_id and created_at, limit to 50 messages, async all the way

10. **Error Handling and Recovery**: Three-layer error handling (MCP tools, agent, chat endpoint)
    - Tool errors: Structured error responses, conversational error messages
    - Agent errors: Ask clarifying questions, continue conversation after errors
    - Endpoint errors: Appropriate HTTP status codes, user-friendly messages

**Phase 1: Design Artifacts**:

1. **Data Models** (data-model.md):
   - Conversation entity (id, user_id, created_at, updated_at)
   - Message entity (id, conversation_id, user_id, role, content, created_at)
   - Task entity (existing from Phase 2, all fields preserved)
   - Entity relationships diagram
   - SQLModel definitions with type safety
   - Query patterns for conversation history, task filtering
   - Performance considerations (indexes, connection pooling)

2. **API Contracts** (contracts/):
   - Chat endpoint specification (POST /api/{user_id}/chat)
   - 6 MCP tool specifications (add_task, list_tasks, search_tasks, complete_task, delete_task, update_task)
   - Agent behavior specification (system prompt, intent recognition patterns)

3. **Quickstart Guide** (quickstart.md):
   - Backend setup (install dependencies, configure env vars, run MCP server)
   - Frontend setup (install dependencies, configure ChatKit, run dev server)
   - Testing commands (pytest for backend, npm test for frontend)
   - Deployment instructions (Vercel for frontend, any platform for backend)

**Project Structure**:
- Monorepo: frontend/ + backend/
- Backend adds: mcp/ directory (MCP server and 6 tools), agents/ directory (OpenAI Agents SDK config)
- Frontend adds: app/(app)/chat/ route (ChatKit integration)
- All Phase 2 infrastructure preserved (database, auth, task models, API routes)

**Constitution Check**: ✅ PASSED - All 14 principles satisfied
- Principle I-XI: Existing principles from Phase 2 (spec-first, TDD, YAGNI, type safety, etc.)
- Principle XII: AI Agent Development & MCP Server Architecture (NEW)
- Principle XIII: Stateless Architecture & Conversation State Management (NEW)
- Principle XIV: Natural Language Understanding & Intent Recognition (NEW)

**Technical Context Finalized**:
- Language: Python 3.13+ (backend), TypeScript 5.x (frontend)
- Dependencies: FastAPI, OpenAI Agents SDK, MCP SDK, SQLModel, Neon PostgreSQL, ChatKit
- Performance Goals: <3 seconds response, 90% intent accuracy, <500ms DB queries
- Constraints: Stateless architecture, 50 message history limit, JWT auth required
- Scope: 6 MCP tools, 10 features, 2 new tables, 1 new endpoint

**Architecture Decisions**:
- Stateless architecture enables horizontal scalability
- Database-persisted conversation state ensures resilience
- MCP tools independently testable with clear separation of concerns
- Three-tier testing validates tool → flow → e2e
- Performance target <3 seconds well-justified (DB 100ms, OpenAI 1-2s, tools 50-200ms)

## Outcome

- ✅ Impact: **Complete Phase 3 implementation plan** ready for task generation (`/sp.tasks`)
- 🧪 Tests: Plan validated against constitution (all 14 principles passed), technical context complete, no NEEDS CLARIFICATION
- 📁 Files: Created `specs/003-phase3-ai-chatbot/plan.md` (759 lines), `specs/003-phase3-ai-chatbot/data-model.md` (complete entity definitions)
- 🔁 Next prompts: Run `/sp.tasks` to generate atomic tasks from plan, then `/sp.implement` to execute with TDD workflow
- 🧠 Reflection: Planning phase comprehensive with 10 research areas, complete technical decisions justified, all architecture patterns documented. Data model design includes full SQLModel definitions, query patterns, and performance considerations. Ready for implementation with clear technology stack (OpenAI ChatKit, Agents SDK, MCP SDK) and stateless architecture.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully with all sections filled
- Graders run and results (PASS/FAIL): Constitution Check PASSED (all 14 principles satisfied)
- Prompt variant (if applicable): Standard /sp.plan command following Spec-Kit Plus workflow
- Next experiment (smallest change to try): During `/sp.tasks`, validate task breakdown includes proper dependencies (MCP tools → agent → chat endpoint → frontend), test-first sequence, and constitution compliance checks
