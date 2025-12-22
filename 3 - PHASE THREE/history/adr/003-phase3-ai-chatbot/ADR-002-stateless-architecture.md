# ADR-002: Stateless Architecture with Database-Persisted Conversation State

**Status**: Accepted
**Date**: 2025-12-17
**Deciders**: Architecture Team
**Feature**: Phase 3 - AI-Powered Todo Chatbot

## Context

Phase 3 requires implementing a chat endpoint that maintains conversation context across multiple user messages. The system must support:

1. **Multi-Turn Conversations**: Users reference previous messages ("Mark task 3 as done", "Make it high priority")
2. **Context Persistence**: Conversation history must survive server restarts
3. **Horizontal Scalability**: Any server instance should handle any request
4. **Performance**: Response time <3 seconds for 95% of requests
5. **Concurrent Users**: Support 1,000 simultaneous users

**Constraints**:
- Must comply with Constitution Principle XIII (Stateless Architecture)
- Must maintain conversation history for AI agent context
- Must isolate user data (JWT authentication required)
- Must work with existing Neon PostgreSQL database from Phase 2
- Cannot add new infrastructure (no Redis, no WebSockets)

**Problem**: How do we design the chat endpoint to maintain conversation context while remaining stateless, scalable, and resilient to server restarts?

## Decision

We will implement a **stateless POST endpoint** with **database-persisted conversation state**:

**Endpoint**: `POST /api/{user_id}/chat`

**Architecture**:
1. **No In-Memory State**: Server holds zero conversation state between requests
2. **Database as Source of Truth**: All conversation history stored in PostgreSQL (conversations + messages tables)
3. **Stateless Request Cycle**: Each request independently fetches conversation history from database, processes with AI agent, stores response, and forgets everything

**Request Cycle (10 Steps)**:
```
1. Receive POST request (conversation_id optional, message required)
2. Validate JWT token → Extract user_id
3. IF conversation_id provided:
     - Fetch conversation from database
     - Verify conversation.user_id == JWT user_id (403 if not)
     - Fetch last 50 messages ordered by created_at ASC
   ELSE:
     - Create new conversation record
     - Empty message history
4. Store user message in messages table
5. Build message array for agent: [{role: "user", content: "..."}, ...]
6. Pass message array to OpenAI Agents SDK (agent + MCP tools)
7. Agent processes message, calls tools, generates response
8. Store assistant response in messages table
9. Return response to client (conversation_id, response, tool_calls)
10. Server forgets everything → Ready for next request (STATELESS)
```

**Database Schema**:
- **conversations** table: id, user_id, created_at, updated_at
- **messages** table: id, conversation_id, user_id, role (user/assistant), content, created_at

**Conversation History Management**:
- Limit to last 50 messages (prevent GPT-4 token overflow)
- Older messages remain in database but not sent to agent
- User can view full history in UI (separate read-only query)

## Consequences

### Positive

1. **Horizontal Scalability**: Any server instance can handle any request (no sticky sessions required)
2. **Resilience**: Server restarts don't lose conversation history (survives crashes, deployments)
3. **Simplicity**: No session management, no in-memory caches, no cache invalidation logic
4. **Cost-Effective**: No Redis or session store infrastructure needed
5. **Easy Deployment**: No special routing or session affinity configuration
6. **Testable**: Each request independent, easy to write integration tests
7. **Transparent**: All conversation data visible in database for debugging and analysis
8. **Compliance**: Aligns with Constitution Principle XIII (Stateless Architecture)

### Negative

1. **Database Load**: Every request queries database for conversation history (~100ms per request)
2. **Latency**: Additional database round-trip adds ~100ms to response time (acceptable within <3 second target)
3. **No Real-Time Updates**: HTTP polling required for real-time feel (no WebSocket push)
4. **Limited History**: Conversation history capped at 50 messages (older messages not sent to agent)
5. **Database Storage**: Conversation history grows over time (no automatic cleanup in Phase 3)

### Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Database connection pool exhaustion | Low | High | Configure pool size (5-20 connections), monitor usage |
| Slow conversation history queries | Low | Medium | Index on conversation_id + created_at, limit to 50 messages |
| Database unavailable | Low | High | Return 503 Service Unavailable, implement retry logic |
| Token limit overflow | Medium | Medium | Limit conversation history to 50 messages (~10k tokens) |
| Storage growth | Medium | Low | Future: implement conversation archiving/cleanup policy |

## Alternatives Considered

### Alternative 1: Stateful WebSocket Connections with In-Memory State

**Approach**: Use WebSockets for bidirectional communication, maintain conversation state in memory

**Pros**:
- Real-time bidirectional communication
- Lower latency (no HTTP overhead)
- No database query on every message (state in memory)

**Cons**:
- Requires sticky sessions (load balancer must route user to same server)
- Complex deployment (server affinity, connection management)
- Loses state on server restart (unless replicated)
- Doesn't scale horizontally (each server holds subset of conversations)
- Connection management overhead (handle disconnects, reconnects)
- More complex to test (async WebSocket testing)

**Why Rejected**: Violates Constitution Principle XIII (Stateless Architecture), adds deployment complexity, loses resilience

### Alternative 2: Stateful HTTP with In-Memory Cache

**Approach**: Store conversation history in server memory (dict/cache), no database query per request

**Pros**:
- Fast access to conversation history (no database query)
- Simple implementation (Python dict)

**Cons**:
- Loses state on server restart (conversations lost)
- Not scalable (can't add more servers without shared cache)
- Violates Constitution Principle XIII (Stateless Architecture)
- Memory consumption grows unbounded (no automatic cleanup)
- Complex cache invalidation logic needed

**Why Rejected**: Violates constitution, loses resilience, not scalable

### Alternative 3: Stateful HTTP with Redis Session Store

**Approach**: Store conversation history in Redis, query Redis on each request

**Pros**:
- Faster than database queries (~10-20ms vs ~100ms)
- Distributed state storage (multiple servers can access)
- Redis handles cache eviction (TTL-based)

**Cons**:
- Adds infrastructure complexity (Redis deployment, monitoring)
- Another service to manage and maintain
- Redis failures lose conversation history (unless persisted)
- Not needed for Phase 3 scope (1,000 concurrent users, <3 second target)
- Database performance sufficient (100ms acceptable)
- Premature optimization

**Why Rejected**: Adds unnecessary complexity for Phase 3 scope, database performance sufficient

### Alternative 4: Event Sourcing with Message Queue

**Approach**: Store conversation as event stream, use message queue for async processing

**Pros**:
- Full audit trail of all messages
- Could replay conversations for debugging
- Async processing decouples response time from agent processing

**Cons**:
- Massive over-engineering for Phase 3 requirements
- Adds Kafka/RabbitMQ infrastructure (Phase V scope, not Phase 3)
- Complex implementation (event store, projections, subscriptions)
- Synchronous responses still needed for user experience

**Why Rejected**: Out of scope for Phase 3 (Kafka deferred to Phase V), violates YAGNI principle

## Performance Analysis

**Request Cycle Breakdown**:
- Database fetch (conversation + 50 messages): ~100ms
- OpenAI Agents SDK processing: ~1-2 seconds (largest component)
- MCP tool execution: ~50-200ms per tool (1-3 tools per request)
- Database write (2 messages): ~50ms
- **Total: ~1.5-2.5 seconds** (well under <3 second target)

**Scalability**:
- Database connection pooling (5-20 connections) supports 1,000 concurrent users
- Neon Serverless PostgreSQL autoscaling handles increased load
- Stateless design enables adding more FastAPI instances (horizontal scaling)

**Database Optimization**:
- Index on `messages.conversation_id` (conversation history fetch)
- Index on `messages.created_at` (chronological ordering)
- Limit query to 50 messages (reduces query time, token usage)

## References

- [Phase 3 Implementation Plan](../../../specs/003-phase3-ai-chatbot/plan.md) (Section: Stateless Chat Endpoint Architecture)
- [Phase 3 Research Document](../../../specs/003-phase3-ai-chatbot/research.md) (Research Area 4)
- [Chat Endpoint Contract](../../../specs/003-phase3-ai-chatbot/contracts/chat-endpoint.md)
- [Data Model Specification](../../../specs/003-phase3-ai-chatbot/data-model.md)
- [Phase 3 Constitution (v3.0.0)](../../../.specify/memory/constitution.md) (Principle XIII)

## Notes

- Decision aligns with Constitution Principle XIII (Stateless Architecture & Conversation State Management)
- Stateless design mandatory per constitution: "Chat endpoint MUST be stateless. All conversation state MUST be persisted to database."
- Performance target (<3 seconds) achievable with database-persisted state
- Horizontal scalability enabled by stateless design
- Simplicity prioritized over premature optimization (no Redis until proven bottleneck)

---

**Last Updated**: 2025-12-17
**Supersedes**: None (Phase 3 initial architecture)
**Superseded By**: None
