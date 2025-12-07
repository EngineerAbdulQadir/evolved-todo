---
name: feature-implementation
description: Complete end-to-end feature implementation workflow for evolved-todo project. Use when implementing features from specs, following SDD methodology through all 13 phases with quality gates and subagent verification.
---

# Feature Implementation

## Instructions

### When to Use

Use this skill when:
- Implementing any feature from the evolved-todo project specs
- Starting work on a new phase (Phases 3-12)
- Need guidance on complete feature workflow from spec to deployment
- Orchestrating multiple skills for end-to-end implementation
- Ensuring all quality gates and constitutional principles are followed

### Complete Feature Implementation Workflow

This skill orchestrates all other skills and subagents to implement features following the evolved-todo project's SDD methodology.

## Phase-by-Phase Implementation Guide

### Phase 0: Constitution & Setup (Complete ✅)
**Status**: Foundation established
- ✅ Project constitution defined
- ✅ Principles established
- ✅ Forbidden items documented
- ✅ Skills created

### Phase 1: Specification (Complete ✅)
**Status**: Specs written
- ✅ 10 user stories specified
- ✅ Acceptance criteria defined
- ✅ Technical contracts documented

### Phase 2: Planning (Complete ✅)
**Status**: Implementation plan ready
- ✅ Architecture designed
- ✅ Tasks broken down (T001-T092)
- ✅ Dependencies mapped

### Phases 3-12: Feature Implementation (In Progress)

For each feature implementation phase, follow this workflow:

#### Step 1: Pre-Implementation (Constitution Check)

**Invoke**: `constitution-compliance` subagent

```bash
# Before starting any implementation
# Ensure feature aligns with project principles
```

**Verify**:
- Feature doesn't violate forbidden items (databases, file persistence, etc.)
- Follows minimalism principle
- Maintains in-memory architecture
- Uses only approved dependencies

#### Step 2: Spec-to-Code Conversion

**Use Skill**: `spec-to-code`

```bash
# Generate test stubs from acceptance criteria
python .claude/skills/spec-to-code/scripts/helper.py generate-tests \
  --spec specs/[feature-spec].md \
  --output tests/unit/test_[feature].py

# Generate implementation checklist
python .claude/skills/spec-to-code/scripts/helper.py generate-checklist \
  --spec specs/[feature-spec].md
```

**Outputs**:
- Test stubs with AC references
- Implementation checklist
- Traceability matrix template

#### Step 3: Test-First Implementation (TDD)

**Use Skill**: `tdd-workflow`

For each task in the phase:

**RED Phase**:
```bash
# Write failing test
# Run: uv run pytest tests/unit/test_[feature].py -v
# Expected: FAILED
```

**GREEN Phase**:
```bash
# Implement minimal code to pass test
# Run: uv run pytest tests/unit/test_[feature].py -v
# Expected: PASSED
```

**REFACTOR Phase**:
```bash
# Improve code quality
uv run mypy --strict src/
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

**Invoke After Implementation**: `test-guardian` subagent

#### Step 4: Layer-by-Layer Implementation

Follow dependency order using appropriate skills:

**Layer 1: Models**
- **Use Skill**: `model-service`
- Implement dataclasses with validation
- Add type annotations
- Write unit tests first

**Invoke After Models**: `type-enforcer` subagent

**Layer 2: Services**
- **Use Skill**: `model-service`
- Implement business logic
- Dependency injection pattern
- Write unit tests first

**Invoke After Services**: `security-sentinel` subagent

**Layer 3: CLI**
- **Use Skill**: `cli-command`
- Implement Typer commands
- Rich formatting for output
- Write integration tests first

**Invoke After CLI**: `ux-advocate` subagent

#### Step 5: Quality Gates (Before Phase Complete)

**Use Skill**: `quality-check`

Run all quality checks:

```bash
# Type safety
uv run mypy --strict src/

# Linting
uv run ruff check src/ tests/

# Formatting
uv run ruff format --check src/ tests/

# Tests with coverage
uv run pytest --cov=src --cov-fail-under=90 -v
```

**Invoke Subagents**:
- `performance-optimizer` - Validate Big-O complexity
- `style-guardian` - Code style consistency
- `doc-curator` - Documentation completeness

#### Step 6: Verification Against Spec

**Use Skill**: `spec-to-code`

```bash
# Verify all ACs covered
python .claude/skills/spec-to-code/scripts/helper.py verify-coverage \
  --spec specs/[feature-spec].md \
  --tests tests/

# Generate traceability matrix
python .claude/skills/spec-to-code/scripts/helper.py create-matrix \
  --spec specs/[feature-spec].md \
  --tests tests/ \
  --code src/
```

**Checklist**:
- [ ] All acceptance criteria have passing tests
- [ ] All technical contracts match spec exactly
- [ ] Test coverage >90%
- [ ] All quality gates pass
- [ ] Traceability complete (AC → Test → Code)

#### Step 7: Git Workflow (Commit & PR)

**Use Skill**: `git-workflow`

**Invoke Before Commit**: `git-workflow` subagent

```bash
# Stage changes
git add src/ tests/

# Create conventional commit
git commit -m "feat(feature): implement [feature-name]

- Implements AC1: [description]
- Implements AC2: [description]
- Coverage: 95%
- All quality gates pass

🤖 Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Push and create PR
git push -u origin [branch-name]
gh pr create --title "feat: [Feature Name]" --body "[PR body]"
```

**Invoke Before PR**: `git-workflow` subagent (validates PR)

#### Step 8: Final Documentation

**Invoke**: `doc-curator` subagent

Ensure:
- [ ] README updated with new feature
- [ ] CHANGELOG entry added
- [ ] All public APIs documented
- [ ] CLI help text accurate
- [ ] Examples work correctly

### Phase 13: Final Validation

**Complete Project Checklist**:

```bash
# Run all tests
uv run pytest -v

# Full quality check
uv run mypy --strict src/
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run pytest --cov=src --cov-fail-under=90 --cov-report=term-missing

# Security audit
uv run pip-audit
```

**Invoke Final Subagents**:
- `code-architect` - Validate architectural integrity
- `refactoring-scout` - Identify technical debt
- `dependency-auditor` - Security and license check
- `constitution-compliance` - Final constitutional review

---

## Skill Orchestration Map

This skill orchestrates other skills at the right time:

```
feature-implementation (YOU ARE HERE - Master Orchestrator)
    │
    ├─→ constitution-compliance (subagent) - Before starting
    │
    ├─→ spec-to-code - Convert spec to tests/checklist
    │   ├─→ Generate test stubs
    │   ├─→ Generate checklist
    │   └─→ Verify coverage
    │
    ├─→ tdd-workflow - For each task
    │   ├─→ RED: Write failing test
    │   ├─→ GREEN: Minimal implementation
    │   └─→ REFACTOR: Improve quality
    │
    ├─→ model-service - Layer 1 & 2 implementation
    │   ├─→ Dataclass patterns
    │   ├─→ Validation logic
    │   └─→ Service layer with DI
    │
    ├─→ cli-command - Layer 3 implementation
    │   ├─→ Typer commands
    │   ├─→ Rich formatting
    │   └─→ Error handling
    │
    ├─→ testing-patterns - Throughout implementation
    │   ├─→ pytest fixtures
    │   ├─→ Parametrized tests
    │   └─→ Integration tests
    │
    ├─→ quality-check - Before phase complete
    │   ├─→ mypy --strict
    │   ├─→ ruff check/format
    │   └─→ pytest --cov
    │
    ├─→ git-workflow - Commit and PR
    │   ├─→ Conventional commits
    │   ├─→ PR creation
    │   └─→ git-workflow subagent
    │
    └─→ Subagent Verification (at key milestones)
        ├─→ test-guardian (after tests)
        ├─→ type-enforcer (after models)
        ├─→ security-sentinel (after services)
        ├─→ ux-advocate (after CLI)
        ├─→ performance-optimizer (after collections)
        ├─→ style-guardian (after code)
        ├─→ doc-curator (before commit)
        ├─→ code-architect (after major features)
        └─→ constitution-compliance (before & after)
```

---

## Quick Start: Implementing a New Feature

### Example: Implementing US3 - Update Task

**1. Start with Constitution Check**
```
Before implementing US3, verify it aligns with constitution principles.
```
→ Invoke `constitution-compliance` subagent

**2. Generate Implementation Artifacts**
```bash
# Generate test stubs
python .claude/skills/spec-to-code/scripts/helper.py generate-tests \
  --spec specs/001-phase1-todo-app/003-update-task/spec.md \
  --output tests/unit/test_update_task.py

# Generate checklist
python .claude/skills/spec-to-code/scripts/helper.py generate-checklist \
  --spec specs/001-phase1-todo-app/003-update-task/spec.md
```

**3. Follow TDD for Each Task**

From tasks.md:
- T034 [US3] Write unit tests for TaskService.update()
- T035 [US3] Implement TaskService.update()
- T036 [US3] Write integration tests for CLI update command
- T037 [US3] Implement CLI update command

For T034 (RED):
```bash
# Write test first
uv run pytest tests/unit/test_task_service.py::test_update_task -v
# Expected: FAILED
```

For T035 (GREEN):
```python
# Implement TaskService.update()
def update(self, task_id: int, title: Optional[str] = None, ...) -> Task:
    # Implementation
```
```bash
uv run pytest tests/unit/test_task_service.py::test_update_task -v
# Expected: PASSED
```

**4. Run Quality Gates**
```bash
uv run mypy --strict src/
uv run ruff check src/ tests/
uv run pytest --cov=src --cov-fail-under=90
```

**5. Verify Against Spec**
```bash
python .claude/skills/spec-to-code/scripts/helper.py verify-coverage \
  --spec specs/001-phase1-todo-app/003-update-task/spec.md \
  --tests tests/
```

**6. Commit with Git Workflow**
```bash
git add src/services/task_service.py tests/unit/test_task_service.py
git commit -m "feat(task-service): implement update() method

- Implements AC1: Update title
- Implements AC2: Update description
- Implements AC3: Partial updates supported
- Coverage: 95%

🤖 Generated with Claude Code"
```

---

## Constitutional Principles Integration

All implementation must follow `.specify/memory/constitution.md`:

### Code Quality Principles (Applied Throughout)
- **Minimalism**: Simplest solution that works
- **Type Safety**: mypy --strict passes
- **Testing**: >90% coverage, TDD approach
- **Readability**: Clear names, minimal comments

### Architecture Principles
- **In-Memory Only**: No databases, no file persistence
- **Layered Architecture**: CLI → Service → Model → Storage
- **Dependency Flow**: One direction only (no circular deps)

### Forbidden Items (Constitution Check)
- ❌ No databases (SQLite, PostgreSQL, etc.)
- ❌ No file persistence for tasks
- ❌ No external APIs
- ❌ No authentication systems
- ❌ No web frameworks

### Allowed Technologies
- ✅ Python 3.13+
- ✅ UV package manager
- ✅ Typer (CLI framework)
- ✅ Rich (terminal formatting)
- ✅ pytest, mypy, ruff
- ✅ python-dateutil (date parsing)

---

## Progress Tracking

### Current Status
- **Phase 0-2**: ✅ Complete
- **Phase 3-12**: 🔄 In Progress
- **Phase 13**: ⏳ Pending

### Phases Overview

| Phase | Feature | Priority | Status | Tasks |
|-------|---------|----------|--------|-------|
| 3 | US1: Add Task | P1 | 🔄 | T019-T026 |
| 4 | US2: View Tasks | P1 | ⏳ | T027-T033 |
| 5 | US3: Update Task | P1 | ⏳ | T034-T040 |
| 6 | US4: Delete Task | P1 | ⏳ | T041-T047 |
| 7 | US5: Priority Levels | P1 | ⏳ | T048-T054 |
| 8 | US6: Tags | P2 | ⏳ | T055-T061 |
| 9 | US7: Search/Filter | P2 | ⏳ | T062-T068 |
| 10 | US8: Sorting | P2 | ⏳ | T069-T075 |
| 11 | US9: Mark Complete | P1 | ⏳ | T076-T082 |
| 12 | US10: Due Dates | P2 | ⏳ | T083-T090 |
| 13 | Final QA | - | ⏳ | T091-T092 |

---

## Examples

See `examples.md` for complete walkthroughs of:
- Implementing US1 from start to finish
- Multi-phase feature implementation
- Handling complex validation scenarios
- Integration testing strategies

## Integration with Subagents

This skill proactively invokes subagents at key milestones:

**Before Implementation**:
- constitution-compliance

**During Implementation**:
- test-guardian (after writing tests)
- type-enforcer (after models)
- security-sentinel (after services)
- ux-advocate (after CLI)
- performance-optimizer (after collections)
- style-guardian (after code)

**Before Commit**:
- doc-curator
- git-workflow

**Before Phase Complete**:
- code-architect
- refactoring-scout
- dependency-auditor

**Before Project Complete**:
- constitution-compliance (final check)

---

## Success Criteria

A feature is successfully implemented when:

1. ✅ All acceptance criteria have passing tests
2. ✅ Test coverage >90%
3. ✅ All quality gates pass (mypy, ruff, pytest)
4. ✅ Traceability complete (AC → Test → Code)
5. ✅ Constitution principles followed
6. ✅ All subagents invoked and passed
7. ✅ Documentation updated
8. ✅ Git workflow followed (conventional commits, PR)
9. ✅ No forbidden technologies used
10. ✅ Layered architecture maintained

## See Also

- **reference.md**: Detailed phase workflows, quality checklists, troubleshooting
- **examples.md**: Complete feature implementation walkthroughs
- **scripts/helper.py**: Automation for phase tracking, quality gates, progress reports
- **templates/**: Feature implementation checklists, PR templates, phase completion templates
