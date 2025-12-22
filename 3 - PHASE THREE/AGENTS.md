# AGENTS.md

## Purpose

This project uses **Spec-Driven Development (SDD)** — a workflow where **no agent is allowed to write code until the specification is complete and approved**.
All AI agents (Claude, Copilot, Gemini, local LLMs, etc.) must follow the **Spec-Kit lifecycle**:

> **Specify → Plan → Tasks → Implement**

This prevents "vibe coding," ensures alignment across agents, and guarantees that every implementation step maps back to an explicit requirement.

---

## How Agents Must Work

Every agent in this project MUST obey these rules:

1. **Never generate code without a referenced Task ID.**
2. **Never modify architecture without updating `speckit.plan`.**
3. **Never propose features without updating `speckit.specify` (WHAT).**
4. **Never change approach without updating `speckit.constitution` (Principles).**
5. **Every code file must contain a comment linking it to the Task and Spec sections.**

If an agent cannot find the required spec, it must **stop and request it**, not improvise.

---

## Spec-Kit Workflow (Source of Truth)

### 1. Constitution (WHY — Principles & Constraints)

File: `.specify/memory/constitution.md`
Defines the project's non-negotiables: architecture values, security rules, tech stack constraints, performance expectations, and patterns allowed.

Agents must check this before proposing solutions.

---

### 2. Specify (WHAT — Requirements, Journeys & Acceptance Criteria)

Files: `specs/<feature-name>/spec.md`

Contains:
- User journeys
- Requirements
- Acceptance criteria
- Domain rules
- Business constraints

Agents must not infer missing requirements — they must request clarification or propose specification updates.

---

### 3. Plan (HOW — Architecture, Components, Interfaces)

Files: `specs/<feature-name>/plan.md`

Includes:
- Component breakdown
- APIs & schema diagrams
- Service boundaries
- System responsibilities
- High-level sequencing

All architectural output MUST be generated from the Specify file.

---

### 4. Tasks (BREAKDOWN — Atomic, Testable Work Units)

Files: `specs/<feature-name>/tasks.md`

Each Task must contain:
- Task ID
- Clear description
- Preconditions
- Expected outputs
- Artifacts to modify
- Links back to Specify + Plan sections

Agents **implement only what these tasks define**.

---

### 5. Implement (CODE — Write Only What the Tasks Authorize)

Agents now write code, but must:
- Reference Task IDs
- Follow the Plan exactly
- Not invent new features or flows
- Stop and request clarification if anything is underspecified

> The golden rule: **No task = No code.**

---

## Agent Behavior in This Project

### When generating code:

Agents must reference:
```
[Task]: T-001
[From]: speckit.specify §2.1, speckit.plan §3.4
```

### When proposing architecture:

Agents must reference:
```
Update required in speckit.plan → add component X
```

### When proposing new behavior or a new feature:

Agents must reference:
```
Requires update in speckit.specify (WHAT)
```

### When changing principles:

Agents must reference:
```
Modify constitution.md → Principle #X
```

---

## Agent Failure Modes (What Agents MUST Avoid)

Agents are NOT allowed to:
- Freestyle code or architecture
- Generate missing requirements
- Create tasks on their own
- Alter stack choices without justification
- Add endpoints, fields, or flows that aren't in the spec
- Ignore acceptance criteria
- Produce "creative" implementations that violate the plan

If a conflict arises between spec files, the **Constitution > Specify > Plan > Tasks** hierarchy applies.

---

## Developer–Agent Alignment

Humans and agents collaborate, but the **spec is the single source of truth**.
Before every session, agents should re-read:

1. `.specify/memory/constitution.md`
2. Current feature's `spec.md`, `plan.md`, `tasks.md`

This ensures predictable, deterministic development.

---

## Phase 3 Specific Context

**Current Phase:** Phase III - AI Chatbot Development
**Technology Stack:**
- Frontend: OpenAI ChatKit
- Backend: FastAPI + OpenAI Agents SDK + Official MCP SDK
- Database: Neon Serverless PostgreSQL (SQLModel)
- Architecture: Stateless chat endpoint with database-persisted conversation state

**Key Constraints for Phase 3:**
- All MCP tools must be stateless (store state in database, not memory)
- Chat endpoint must fetch conversation history from DB on each request
- OpenAI Agents SDK for AI logic and agent orchestration
- MCP server exposes 5 task operation tools (add_task, list_tasks, complete_task, delete_task, update_task)
- Natural language understanding required ("Add task to buy groceries", "Show pending tasks")
- Conversation state persisted to database (Conversation and Message models)

**Agent Must Not:**
- Create in-memory state management (use database only)
- Skip JWT authentication (all endpoints require auth)
- Implement GraphQL or other non-REST APIs (Phase 3 uses REST + MCP)
- Add features beyond Basic Level requirements (no Kafka, no Kubernetes yet)

---

## Spec-Kit Commands Available

Agents can use these commands via MCP server or Claude Code slash commands:

- `/sp.specify` - Create or update feature specification
- `/sp.plan` - Generate architectural plan from spec
- `/sp.tasks` - Break plan into atomic, testable tasks
- `/sp.implement` - Execute tasks and implement code
- `/sp.constitution` - Update project constitution
- `/sp.adr` - Create Architecture Decision Record for significant decisions
- `/sp.clarify` - Ask targeted clarification questions about underspecified areas
- `/sp.analyze` - Perform cross-artifact consistency analysis
- `/sp.checklist` - Generate custom checklist for feature
- `/sp.phr` - Record Prompt History Record for learning
- `/sp.git.commit_pr` - Intelligent git commit and PR creation

---

## Quality Gates (Must Pass Before Implementation)

### Before Writing Code:
- [ ] Constitution reviewed and understood
- [ ] Specification complete with acceptance criteria
- [ ] Plan approved with architecture decisions
- [ ] Tasks broken down with clear inputs/outputs
- [ ] All dependencies identified

### During Implementation:
- [ ] All code references Task IDs in comments
- [ ] Tests written first (TDD - Red → Green → Refactor)
- [ ] Type annotations complete (Python + TypeScript)
- [ ] Error handling explicit for all edge cases
- [ ] Documentation updated alongside code

### After Implementation:
- [ ] All tests pass (backend + frontend)
- [ ] Type checking passes (mypy + tsc)
- [ ] Linting passes (ruff + eslint)
- [ ] Test coverage >90%
- [ ] Constitution compliance verified
- [ ] PHR created for prompt history

---

## Integration with Claude Code

This AGENTS.md file is automatically loaded by Claude Code via CLAUDE.md forwarding.

**Workflow:**
1. User requests feature: "Implement AI chatbot for todo management"
2. Agent reads AGENTS.md + constitution.md
3. Agent uses `/sp.specify` to create spec
4. Agent uses `/sp.plan` to create architecture
5. Agent uses `/sp.tasks` to break down work
6. Agent uses `/sp.implement` to execute tasks
7. Agent validates against constitution and creates PHR

**Human-in-the-Loop:**
- Agent asks clarifying questions when requirements ambiguous
- Agent surfaces architectural decisions for ADR approval
- Agent presents options when multiple valid approaches exist
- Agent confirms completion and next steps at milestones

---

## Version & Maintenance

**Version:** 1.0.0 (Phase 3 - AI Chatbot)
**Created:** 2025-12-17
**Last Updated:** 2025-12-17

This file evolves with the project. Updates must be versioned and documented.

---

**Remember:** The spec is the source of truth. When in doubt, read the spec. When the spec is unclear, clarify it. Never assume or improvise.
