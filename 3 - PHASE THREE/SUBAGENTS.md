# Phase 3 Specialized Subagents

**Feature**: Phase 3 - AI-Powered Todo Chatbot
**Date**: 2025-12-19
**Purpose**: Define specialized subagents for implementing the AI chatbot with OpenAI ChatKit, Agents SDK, and MCP SDK

## Overview

Phase 3 introduces 6 specialized subagents to handle the complexity of building a conversational AI interface with stateless architecture, database-persisted state, and natural language understanding. Each subagent has specific skills and responsibilities aligned with Phase 3 architecture.

---

## Subagent 1: Backend API Developer

**Agent File**: `.claude/agents/backend-api-developer.md`

**Purpose**: Implement FastAPI endpoints, MCP tools, and OpenAI Agents SDK integration

**Responsibilities**:
- Create and maintain MCP server with 6 stateless tools
- Implement chat endpoint with stateless architecture
- Integrate OpenAI Agents SDK with MCP tools
- Define system prompts for natural language understanding
- Implement async FastAPI routes with SQLModel
- Ensure database-persisted conversation state

**Skills Used**:
- ✅ **fastapi-sqlmodel** (PRIMARY) - FastAPI + SQLModel async patterns
- ✅ **async-python** - Python async/await best practices
- ✅ **api-contract-testing** - MCP tool contract validation
- error-handling - Robust error handling patterns
- type-safety - Type annotations and mypy compliance

**Key Outputs**:
- `backend/app/mcp/server.py` - MCP server initialization
- `backend/app/mcp/tools/*.py` - 6 MCP tools (add_task, list_tasks, search_tasks, complete_task, delete_task, update_task)
- `backend/app/agents/todo_agent.py` - OpenAI agent configuration
- `backend/app/agents/prompts.py` - System prompts and intent patterns
- `backend/app/routes/chat.py` - Stateless chat endpoint

**Quality Gates**:
- All MCP tools pass unit tests (100% coverage)
- System prompt achieves 90% intent recognition accuracy
- Chat endpoint maintains stateless architecture (no in-memory state)
- Response time <3 seconds for 95% of requests

---

## Subagent 2: Frontend React Developer

**Agent File**: `.claude/agents/frontend-react-dev.md`

**Purpose**: Implement Next.js 16+ frontend with OpenAI ChatKit integration

**Responsibilities**:
- Integrate OpenAI ChatKit conversational UI component
- Create React components for chat interface
- Implement API client for chat endpoint
- Handle JWT token injection in API calls
- Manage conversation history display
- Implement error handling and loading states

**Skills Used**:
- ✅ **nextjs-app-router** (PRIMARY) - Next.js 16+ App Router patterns
- ✅ **react-components** - React 18+ component patterns and hooks
- ✅ **tailwind-design** - Tailwind CSS utility-first design
- testing-patterns - Jest and React Testing Library

**Key Outputs**:
- `frontend/app/(app)/chat/page.tsx` - Chat page with authentication
- `frontend/components/chat/ChatInterface.tsx` - ChatKit wrapper component
- `frontend/lib/api-client.ts` - API client with JWT authentication
- `frontend/types/chat.ts` - TypeScript types for messages and conversations

**Quality Gates**:
- ChatInterface component renders correctly
- Conversation history loads and displays properly
- JWT tokens are correctly injected in API calls
- Error states display user-friendly messages
- Frontend tests pass with >80% coverage

---

## Subagent 3: Database Architect

**Agent File**: `.claude/agents/database-architect.md`

**Purpose**: Design and implement database schema for conversation persistence

**Responsibilities**:
- Define SQLModel models for Conversation and Message tables
- Verify Task model from Phase 2 is preserved
- Design indexes for query performance
- Implement database connection and session management
- Ensure foreign key relationships and data isolation
- Configure Neon Serverless PostgreSQL connection

**Skills Used**:
- ✅ **fastapi-sqlmodel** (PRIMARY) - SQLModel ORM patterns
- ✅ **neon-postgres** - Neon Serverless PostgreSQL integration
- ✅ **alembic-migrations** - Database migration patterns (if needed)
- performance - Query optimization and indexing

**Key Outputs**:
- `backend/app/models.py` - Conversation, Message, Task models
- `backend/app/db.py` - Database connection and session factory
- Database indexes on user_id, conversation_id, created_at

**Quality Gates**:
- All models validate correctly with Pydantic/SQLModel
- Foreign key relationships enforced
- Indexes created for performance (<100ms conversation history fetch)
- User data isolation enforced at database level
- Model tests pass with 100% coverage

---

## Subagent 4: Auth Specialist

**Agent File**: `.claude/agents/auth-specialist.md`

**Purpose**: Implement JWT authentication and multi-user data isolation

**Responsibilities**:
- Extend Better Auth JWT authentication to chat endpoint
- Validate JWT tokens on every request
- Extract user_id from JWT claims
- Enforce user data isolation in all MCP tools
- Implement 401/403 error handling for authentication failures
- Ensure conversation ownership checks

**Skills Used**:
- ✅ **better-auth-jwt** (PRIMARY) - Better Auth JWT integration
- ✅ **jwt-validation** - JWT token validation patterns
- security - Secure coding practices and input validation
- error-handling - Authentication error handling

**Key Outputs**:
- JWT authentication middleware for chat endpoint
- User isolation checks in all MCP tools
- Conversation ownership validation
- Authentication test suite

**Quality Gates**:
- All endpoints require valid JWT tokens (401 if missing)
- Users can only access their own conversations and tasks (403 if violation)
- JWT signature validation passes
- BETTER_AUTH_SECRET correctly configured
- Security tests pass with 100% coverage

---

## Subagent 5: API Contract Validator

**Agent File**: `.claude/agents/api-contract-validator.md`

**Purpose**: Validate MCP tool contracts and ensure schema compliance

**Responsibilities**:
- Define and validate Pydantic schemas for all MCP tool inputs/outputs
- Ensure contract adherence between agent, MCP tools, and database
- Validate chat endpoint request/response schemas
- Create contract tests for all MCP tools
- Document API contracts in contracts/ directory

**Skills Used**:
- ✅ **api-contract-testing** (PRIMARY) - Contract-first API development
- ✅ **openapi-validation** - OpenAPI schema validation
- type-safety - Type annotations and schema validation
- testing-patterns - Contract testing patterns

**Key Outputs**:
- `backend/app/mcp/schemas.py` - Pydantic base schemas
- MCP tool input/output schemas in each tool file
- Contract tests in `backend/tests/unit/test_mcp_tools.py`
- Updated `specs/003-phase3-ai-chatbot/contracts/mcp-tools.md`

**Quality Gates**:
- All MCP tool schemas validate correctly
- Contract tests pass for all 6 tools
- Chat endpoint schema matches specification
- Type safety verified with mypy strict mode
- No schema drift between spec and implementation

---

## Subagent 6: Fullstack Integrator

**Agent File**: `.claude/agents/fullstack-integrator.md`

**Purpose**: Integrate frontend, backend, and agent components end-to-end

**Responsibilities**:
- Wire ChatKit to chat endpoint
- Integrate OpenAI agent with MCP tools
- Connect conversation state to database
- Implement end-to-end conversation flows
- Test full stack integration (ChatKit → Agent → MCP → Database)
- Validate stateless architecture across server restarts

**Skills Used**:
- ✅ **e2e-testing** (PRIMARY) - End-to-end testing strategies
- ✅ **monorepo-structure** - Monorepo coordination patterns
- debugging - Systematic debugging across full stack
- testing-patterns - Integration testing patterns

**Key Outputs**:
- End-to-end integration in `backend/app/routes/chat.py`
- Conversation flow tests in `backend/tests/integration/test_conversation_flows.py`
- Full stack tests in `backend/tests/integration/test_chat_endpoint.py`
- Integration validation scripts

**Quality Gates**:
- Full conversation flow works (user message → agent → MCP tool → database → response)
- All 60 acceptance scenarios from spec.md pass
- Stateless architecture validated (server restarts don't lose state)
- Conversation context preserved across messages
- Integration tests pass with >90% coverage

---

## Skill-to-Subagent Matrix

| Skill | Backend API Dev | Frontend React Dev | Database Architect | Auth Specialist | API Contract Validator | Fullstack Integrator |
|-------|----------------|-------------------|-------------------|----------------|----------------------|---------------------|
| **fastapi-sqlmodel** | ✅ PRIMARY | | ✅ PRIMARY | | | |
| **better-auth-jwt** | | | | ✅ PRIMARY | | |
| **nextjs-app-router** | | ✅ PRIMARY | | | | |
| **api-contract-testing** | ✅ | | | | ✅ PRIMARY | |
| **async-python** | ✅ | | | | | |
| **neon-postgres** | | | ✅ | | | |
| **alembic-migrations** | | | ✅ | | | |
| **jwt-validation** | | | | ✅ | | |
| **react-components** | | ✅ | | | | |
| **tailwind-design** | | ✅ | | | | |
| **openapi-validation** | | | | | ✅ | |
| **e2e-testing** | | | | | | ✅ PRIMARY |
| **monorepo-structure** | | | | | | ✅ |

---

## Subagent Coordination

**Sequential Dependencies**:
1. **Database Architect** creates models first (Conversation, Message)
2. **Backend API Developer** implements MCP tools using models
3. **Auth Specialist** adds JWT validation to endpoints
4. **API Contract Validator** validates all schemas and contracts
5. **Frontend React Dev** builds ChatKit integration
6. **Fullstack Integrator** connects all pieces and validates end-to-end

**Parallel Work Opportunities**:
- Database Architect + Auth Specialist can work in parallel (different concerns)
- Backend API Dev + Frontend React Dev can work in parallel after models ready
- API Contract Validator can validate as Backend API Dev completes tools
- Fullstack Integrator tests incrementally as components complete

**Critical Path**:
1. Database models (BLOCKS all)
2. MCP tools (BLOCKS agent integration)
3. Chat endpoint (BLOCKS frontend integration)
4. ChatKit integration (BLOCKS e2e testing)

---

## Usage Guidelines

**When to Use Each Subagent**:

- **Backend API Developer**: For all MCP tool implementation, agent configuration, chat endpoint
- **Frontend React Dev**: For all ChatKit integration, React components, Next.js pages
- **Database Architect**: For schema changes, model updates, query optimization
- **Auth Specialist**: For JWT issues, user isolation bugs, authentication errors
- **API Contract Validator**: For schema validation, contract testing, type safety
- **Fullstack Integrator**: For end-to-end bugs, integration issues, conversation flow problems

**Invoking Subagents**:

```bash
# Example: Use backend-api-developer for MCP tool implementation
claude --agent backend-api-developer "Implement add_task MCP tool with Pydantic schemas"

# Example: Use frontend-react-dev for ChatKit integration
claude --agent frontend-react-dev "Create ChatInterface component wrapping OpenAI ChatKit"

# Example: Use fullstack-integrator for e2e validation
claude --agent fullstack-integrator "Test full conversation flow from ChatKit to database"
```

---

## Quality Standards

All subagents must adhere to:
- **Constitution v3.0.0**: All 14 principles (stateless architecture, TDD, type safety, etc.)
- **Test Coverage**: >90% for backend, >80% for frontend
- **Type Safety**: mypy strict mode (backend), TypeScript strict (frontend)
- **Documentation**: All public functions documented
- **Error Handling**: Graceful failures with user-friendly messages
- **Performance**: <3 second response time for 95% of requests

---

**Version**: 1.0.0
**Status**: Active for Phase 3 implementation
**Last Updated**: 2025-12-19
