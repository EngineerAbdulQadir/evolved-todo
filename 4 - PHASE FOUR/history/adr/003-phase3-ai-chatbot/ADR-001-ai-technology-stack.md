# ADR-001: AI Technology Stack (ChatKit, Agents SDK, MCP SDK)

**Status**: Accepted
**Date**: 2025-12-17
**Deciders**: Architecture Team
**Feature**: Phase 3 - AI-Powered Todo Chatbot

## Context

Phase 3 requires transforming the Phase 2 web application into an AI-powered conversational interface where users manage all 10 task features through natural language. We need to select an integrated technology stack that provides:

1. **Conversational UI**: Pre-built chat interface for user interaction
2. **AI Agent Framework**: Intent recognition and natural language understanding
3. **Tool Execution**: Standardized interface for task operations (add, list, complete, etc.)

**Constraints**:
- Must support all 10 features (Basic + Intermediate + Advanced) via natural language
- Must integrate with existing FastAPI backend and Neon PostgreSQL database
- Must maintain Better Auth JWT authentication from Phase 2
- Must achieve 90% intent recognition accuracy
- Must support multi-turn conversations with context
- Response time target: <3 seconds for 95% of requests

**Problem**: Need to select technologies that work together seamlessly and provide production-ready AI capabilities without building custom NLU infrastructure.

## Decision

We will use an integrated AI technology stack consisting of three OpenAI technologies that work together:

1. **OpenAI ChatKit** (Frontend)
   - Purpose: Conversational UI component for user interaction
   - Integration: React/Next.js component via npm package `@openai/chatkit`
   - Responsibilities: Message display, input handling, typing indicators, conversation history

2. **OpenAI Agents SDK** (Backend - AI Logic)
   - Purpose: Intent recognition and natural language understanding
   - Integration: Python SDK via UV package manager
   - Responsibilities: Parse user intent, decide which tools to call, generate conversational responses, manage conversation context

3. **Official MCP SDK** (Backend - Tool Interface)
   - Purpose: Standardized tool definitions and execution
   - Integration: Python implementation via UV package manager
   - Responsibilities: 6 stateless tools (add_task, list_tasks, search_tasks, complete_task, delete_task, update_task), input/output schema validation, error handling

**Integration Architecture**:
```
User → ChatKit (Frontend)
      ↓ HTTP POST /api/{user_id}/chat
      ↓
Chat Endpoint (FastAPI)
      ↓ Fetch conversation history from DB
      ↓
OpenAI Agents SDK (AI Agent)
      ↓ Calls tools based on intent
      ↓
MCP Server (6 Tools)
      ↓ Database operations
      ↓
Neon PostgreSQL
```

## Consequences

### Positive

1. **Officially Supported**: All three technologies maintained by OpenAI, ensuring compatibility and long-term support
2. **Reduced Development Time**: Pre-built components eliminate need for custom UI and NLU implementation
3. **Proven UX Patterns**: ChatKit provides battle-tested conversational interface patterns
4. **Native Integration**: Agents SDK has native support for MCP tools, simplifying tool calling logic
5. **Type Safety**: MCP SDK provides Pydantic schema validation for all tool inputs/outputs
6. **Testability**: MCP tools are independently testable with mock database
7. **Scalability**: Stateless tools and agent design enable horizontal scaling
8. **Future-Proof**: MCP is emerging standard for AI tool interfaces

### Negative

1. **Vendor Lock-in**: Tightly coupled to OpenAI ecosystem (ChatKit, Agents SDK, GPT-4 API)
2. **API Costs**: OpenAI API usage incurs per-token costs (estimated $0.03 per 1K tokens for GPT-4)
3. **External Dependency**: Requires OpenAI API availability (mitigated with retry logic and graceful degradation)
4. **Limited Customization**: ChatKit customization limited compared to custom UI
5. **Learning Curve**: Team needs to learn three new technologies (ChatKit, Agents SDK, MCP SDK)
6. **Token Limits**: Conversation history limited to 50 messages due to GPT-4 token limits

### Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| OpenAI API downtime | Low | High | Implement retry logic, return 503 with user-friendly message |
| Rate limiting (429 errors) | Medium | Medium | Implement exponential backoff, queue requests during high load |
| Cost overruns | Low | Medium | Monitor API usage, implement conversation history limits (50 messages) |
| MCP SDK changes | Low | Medium | Pin SDK version, test before upgrades |
| ChatKit breaking changes | Low | Medium | Pin npm package version, monitor release notes |

## Alternatives Considered

### Alternative 1: Custom React UI + LangChain + Custom Tools

**Approach**: Build custom chat UI, use LangChain for AI orchestration, custom tool functions

**Pros**:
- Full control over UI and behavior
- No vendor lock-in to OpenAI ecosystem
- Could support multiple LLM providers (OpenAI, Anthropic, etc.)

**Cons**:
- High development overhead (2-3 weeks for custom UI)
- Need to implement message formatting, scrolling, typing indicators, accessibility
- LangChain adds unnecessary complexity for simple tool calling
- More code to maintain and test
- No benefit from OpenAI's proven UX patterns

**Why Rejected**: Development time too high, ChatKit provides proven patterns, LangChain overkill for Phase 3 requirements

### Alternative 2: Direct OpenAI API + Third-Party Chat Library

**Approach**: Use OpenAI function calling API directly, integrate third-party chat library (e.g., stream-chat-react)

**Pros**:
- Lower-level control over API calls
- Could use any chat library

**Cons**:
- Manual conversation tracking and tool calling logic
- Third-party chat libraries not optimized for AI agents
- Need to implement retry logic, error handling, context management
- More boilerplate code
- Lack of native tool interface standardization

**Why Rejected**: Agents SDK abstracts complexity, MCP provides standardization, ChatKit optimized for AI

### Alternative 3: Fine-tuned Model + Custom NLU

**Approach**: Fine-tune GPT-3.5 or similar model on task intents, build custom NER for entity extraction

**Pros**:
- Potentially higher accuracy for specific intents
- Lower per-request costs (after fine-tuning)

**Cons**:
- Requires training data collection and labeling
- Fine-tuning expensive upfront ($100-500)
- Longer development time (1-2 weeks for training pipeline)
- Maintenance overhead (retrain when adding features)
- GPT-4 baseline accuracy already sufficient (90% target)

**Why Rejected**: GPT-4 baseline meets requirements, fine-tuning premature optimization, system prompt engineering faster

## References

- [Phase 3 Implementation Plan](../../../specs/003-phase3-ai-chatbot/plan.md)
- [Phase 3 Research Document](../../../specs/003-phase3-ai-chatbot/research.md)
- [MCP Tools Contract](../../../specs/003-phase3-ai-chatbot/contracts/mcp-tools.md)
- [Agent Behavior Contract](../../../specs/003-phase3-ai-chatbot/contracts/agent-behavior.md)
- [Phase 3 Constitution (v3.0.0)](../../../.specify/memory/constitution.md)
- [OpenAI ChatKit Documentation](https://platform.openai.com/docs/guides/chatkit)
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-sdk)
- [MCP SDK](https://github.com/modelcontextprotocol/python-sdk)

## Notes

- All three technologies work together as an integrated solution
- Decision aligns with Constitution Principle IV (Technology Stack Requirements)
- Decision aligns with Constitution Principle XII (AI Agent Development & MCP Server Architecture)
- MCP tools are stateless, supporting Constitution Principle XIII (Stateless Architecture)
- System prompt engineering achieves 90% intent recognition (Constitution Principle XIV)

---

**Last Updated**: 2025-12-17
**Supersedes**: None (Phase 3 initial architecture)
**Superseded By**: None
