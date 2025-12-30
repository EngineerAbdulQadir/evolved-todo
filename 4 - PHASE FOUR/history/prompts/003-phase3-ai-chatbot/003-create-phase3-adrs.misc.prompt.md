---
id: 003
title: Create Phase 3 Architecture Decision Records
stage: misc
date: 2025-12-17
surface: agent
model: claude-sonnet-4-5
feature: 003-phase3-ai-chatbot
branch: 003-phase3-ai-chatbot
user: AQI
command: /sp.adr
labels: ["adr", "architecture", "phase3", "decisions", "documentation"]
links:
  spec: specs/003-phase3-ai-chatbot/spec.md
  ticket: null
  adr: history/adr/003-phase3-ai-chatbot/
  pr: null
files:
  - history/adr/003-phase3-ai-chatbot/ADR-001-ai-technology-stack.md
  - history/adr/003-phase3-ai-chatbot/ADR-002-stateless-architecture.md
  - history/adr/003-phase3-ai-chatbot/ADR-003-database-schema-conversation-persistence.md
  - history/adr/003-phase3-ai-chatbot/ADR-004-natural-language-understanding-strategy.md
tests:
  - None (ADR documentation)
---

## Prompt

User: "now create adr for phase 3"

Context: User requested creation of Architecture Decision Records (ADRs) for Phase 3 after completing planning artifacts (plan.md, research.md, data-model.md, contracts/).

## Response snapshot

Created 4 comprehensive Architecture Decision Records documenting the architecturally significant decisions for Phase 3 AI chatbot implementation.

**ADRs Created**:

**1. ADR-001: AI Technology Stack (ChatKit, Agents SDK, MCP SDK)**
- **Decision Cluster**: Integrated OpenAI technology stack
  - Frontend: OpenAI ChatKit (conversational UI)
  - Backend AI: OpenAI Agents SDK (intent recognition, tool calling)
  - Tool Interface: Official MCP SDK (6 stateless tools)
- **Rationale**: Officially supported, reduced development time, proven UX patterns, native integration, type safety, testability
- **Alternatives Rejected**:
  - Custom React UI + LangChain + Custom Tools (high development overhead, unnecessary complexity)
  - Direct OpenAI API + Third-Party Chat Library (manual tool calling logic, no standardization)
  - Fine-tuned Model + Custom NLU (expensive upfront, longer development time)
- **Consequences**: Vendor lock-in to OpenAI, API costs (~$0.03/1K tokens), external dependency, limited customization
- **Alignment**: Constitution Principles IV (Technology Stack), XII (AI Agent Development)

**2. ADR-002: Stateless Architecture with Database-Persisted Conversation State**
- **Decision**: Stateless POST /api/{user_id}/chat endpoint with all conversation state in database
- **Request Cycle**: 10-step stateless flow (fetch history → process with agent → store response → forget)
- **Rationale**: Horizontal scalability, resilience to restarts, simplicity (no session management), cost-effective (no Redis), easy deployment
- **Alternatives Rejected**:
  - Stateful WebSocket + In-Memory State (sticky sessions, complex deployment, loses state on restart)
  - Stateful HTTP + In-Memory Cache (not scalable, violates constitution)
  - Stateful HTTP + Redis (adds complexity, premature optimization)
  - Event Sourcing + Message Queue (massive over-engineering, out of scope)
- **Consequences**: Database load (~100ms per request), additional latency, no real-time updates, conversation history capped at 50 messages
- **Performance**: 1.5-2.5 seconds total (well under <3 second target)
- **Alignment**: Constitution Principle XIII (Stateless Architecture)

**3. ADR-003: Database Schema for Conversation Persistence**
- **Decision**: Two new normalized tables (conversations + messages) in existing Neon PostgreSQL
- **Schema**:
  - conversations: id, user_id, created_at, updated_at
  - messages: id, conversation_id, user_id, role (user/assistant), content (max 5000 chars), created_at
- **Indexes**: conversation_id, user_id, created_at (optimized for <100ms queries)
- **Rationale**: Normalized schema, fast queries, user isolation via foreign keys, relational integrity, SQLModel automation
- **Alternatives Rejected**:
  - Single Table + JSON Column (can't index messages, poor query performance)
  - NoSQL Document Store (adds complexity, data duplication, violates constraint)
  - TimescaleDB (premature optimization, may not be available on Neon)
  - Separate Database (unnecessary complexity, no benefit for Phase 3 scope)
- **Consequences**: Storage growth over time, index maintenance, no built-in archiving, 5000 char limit per message
- **Query Performance**: Conversation history fetch ~100ms, message insert ~25ms
- **Alignment**: Constitution Principle X (Database Schema Management)

**4. ADR-004: Natural Language Understanding Strategy (GPT-4 + System Prompt)**
- **Decision**: GPT-4 with carefully crafted system prompt for intent recognition and entity extraction
- **Approach**: System prompt engineering (no fine-tuning, no custom NER)
- **Intent Patterns**: 6 intents defined with recognition triggers and entity extraction guidelines
- **Entity Extraction**: Priorities, tags, dates (relative/absolute), times, recurrence patterns
- **Rationale**: Rapid development (days vs weeks), high baseline accuracy (90% target), no training data needed, handles variations, easy iteration
- **Alternatives Rejected**:
  - Fine-Tuned GPT-3.5 (upfront cost, requires training data, maintenance overhead)
  - Custom NLU with spaCy (high development time, requires ML expertise, lower accuracy)
  - Rule-Based with Regex (too brittle, can't handle variations, 50-60% accuracy)
  - Hybrid LLM + Regex (adds complexity, limited benefit)
- **Consequences**: OpenAI dependency, per-token costs ($0.05-0.15 per conversation), ~1-2 second latency, non-deterministic, prompt brittleness
- **Testing**: 60 natural language scenarios from spec, iterative refinement, production accuracy monitoring
- **Alignment**: Constitution Principle XIV (Natural Language Understanding)

**Decision Clustering Applied**:
- Grouped related technologies that change together (ChatKit + Agents SDK + MCP SDK = 1 ADR)
- Separated independent architectural concerns (stateless architecture, database schema, NLU strategy = 3 separate ADRs)
- Each ADR documents clustered decisions with explicit alternatives and tradeoffs

**Quality Validation**:
- ✅ All ADRs document decision clusters (not atomic choices)
- ✅ All ADRs list multiple alternatives with rationale for rejection
- ✅ All ADRs include clear pros and cons
- ✅ All ADRs reference planning artifacts (plan.md, research.md, contracts/)
- ✅ All ADRs align with constitution principles
- ✅ All ADRs concise but sufficiently detailed for future reference

## Outcome

- ✅ Impact: **4 comprehensive ADRs created** documenting all architecturally significant decisions for Phase 3
- 🧪 Tests: N/A (architecture documentation)
- 📁 Files: Created 4 ADR files in `history/adr/003-phase3-ai-chatbot/`
- 🔁 Next prompts: Run `/sp.tasks` to generate implementation tasks, then `/sp.implement` to execute with TDD
- 🧠 Reflection: ADRs capture decision rationale, alternatives, and consequences for future reference. Decision clustering applied to group related technologies. All 4 ADRs align with Phase 3 constitution principles (IV, X, XII, XIII, XIV). No conflicts with existing ADRs (Phase 3 is new architecture).

## Evaluation notes (flywheel)

- Failure modes observed: None - all ADRs pass significance test (impact software structure, notable tradeoffs, will be revisited)
- Graders run and results (PASS/FAIL): **PASS** - All ADRs document clustered decisions with explicit alternatives and tradeoffs
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): During implementation, validate that code follows ADR decisions (e.g., use OpenAI ChatKit not custom UI, stateless endpoint not WebSocket, GPT-4 with system prompt not fine-tuned model)
