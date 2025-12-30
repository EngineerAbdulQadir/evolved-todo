---
id: 012
title: Generate Universal Tasks for All Specs
stage: tasks
date: 2025-12-06
surface: agent
model: claude-opus-4-5-20251101
feature: 001-phase1-todo-app
branch: 010-due-dates-reminders
user: Engineer Abdul Qadir
command: /sp.tasks
labels: ["tasks", "phase-1", "all-features", "implementation"]
links:
  spec: specs/001-phase1-todo-app/*/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-phase1-todo-app/tasks.md
tests:
  - (none - task generation, no tests required)
---

## Prompt

Now clarify all the specs we have made, then make tasks universal for all specs.

(Followed by /sp.tasks command)

## Response snapshot

Generated comprehensive universal `tasks.md` for all 10 Phase 1 features.

**Summary:**
- **Total Tasks**: 87
- **Phases**: 13 (Setup + Foundation + 10 User Stories + Polish)
- **All specs status updated to "Approved"**

**Phase Breakdown:**

| Phase | Description | Task Count |
|-------|-------------|------------|
| 1 | Setup & Infrastructure | 8 |
| 2 | Foundation (Blocking) | 10 |
| 3 | US1: Add Task | 8 |
| 4 | US2: View Tasks | 7 |
| 5 | US3: Update Task | 6 |
| 6 | US4: Mark Complete | 5 |
| 7 | US5: Delete Task | 5 |
| 8 | US6: Priorities & Tags | 8 |
| 9 | US7: Search & Filter | 7 |
| 10 | US8: Due Dates | 8 |
| 11 | US9: Sort Tasks | 6 |
| 12 | US10: Recurring Tasks | 6 |
| 13 | Polish | 3 |

**Key Features:**
- Tasks organized by user story for independent implementation
- Dependency graph showing execution order
- Parallel execution opportunities identified
- MVP scope defined (Phases 1-4)
- Quality gates per phase
- Strict checklist format with TaskID, [P] markers, [US#] labels, file paths

## Outcome

- Impact: Complete task breakdown enabling TDD implementation of all 10 features
- Tests: N/A (task generation phase)
- Files: specs/001-phase1-todo-app/tasks.md (87 tasks), all 10 spec.md files updated to Approved status
- Next prompts: Run `/sp.implement` to begin implementation, or start with Phase 1 Setup
- Reflection: Universal task file provides clear roadmap; phases enable incremental delivery and parallel development

## Evaluation notes (flywheel)

- Failure modes observed: check-prerequisites.ps1 script looked for wrong path; worked around by reading design docs directly
- Graders run and results (PASS/FAIL): PASS - All tasks follow strict checklist format with IDs, labels, and file paths
- Prompt variant (if applicable): Combined clarify + tasks request
- Next experiment (smallest change to try): Consider auto-generating individual tasks.md files per feature folder as well
