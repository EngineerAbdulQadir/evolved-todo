---
name: tdd-workflow
description: Guide implementation using strict Test-Driven Development with Red-Green-Refactor cycle. Use when implementing any code task (T009-T084) to ensure tests are written first and code quality gates are met.
---

# TDD Workflow

## Instructions

Follow the Red-Green-Refactor TDD cycle for all code implementation tasks:

### TDD Cycle

### Red Phase
1. **Write the failing test first**
   - Read the task requirement from `tasks.md`
   - Identify test file location (unit or integration)
   - Write test that describes expected behavior
   - Run test to confirm it fails: `uv run pytest <test_file> -v`
   - Commit: "test: add failing test for <feature>"

### Green Phase
2. **Make the test pass with minimal code**
   - Implement only what's needed to pass the test
   - No refactoring, no extra features
   - Run test to confirm it passes: `uv run pytest <test_file> -v`
   - Run full suite: `uv run pytest`
   - Commit: "feat: implement <feature>"

### Refactor Phase
3. **Improve code quality**
   - Run type checker: `uv run mypy --strict src/`
   - Run linter: `uv run ruff check src/ tests/`
   - Run formatter: `uv run ruff format src/ tests/`
   - Refactor if needed (DRY, SOLID principles)
   - Run all tests again: `uv run pytest`
   - Commit: "refactor: improve <component>"

## Quality Gates

Before marking task complete:
- [ ] Test passes in isolation
- [ ] Full test suite passes (`pytest`)
- [ ] Type check passes (`mypy --strict src/`)
- [ ] Linter passes (`ruff check`)
- [ ] Code formatted (`ruff format --check`)
- [ ] Coverage maintained >90% (`pytest --cov --cov-fail-under=90`)

## Examples

### Example 1: Complete TDD Cycle

```bash
# Red: Write failing test
uv run pytest tests/unit/test_task_service.py::test_add_task -v
# Expected: FAILED (function not implemented)

# Green: Implement minimal code
uv run pytest tests/unit/test_task_service.py::test_add_task -v
# Expected: PASSED

# Refactor: Check quality
uv run mypy --strict src/
uv run ruff check src/ tests/
uv run pytest --cov=src --cov-fail-under=90

# Commit with conventional commits
git add .
git commit -m "feat(task-service): add task creation with validation"
```

## Integration with Subagents

After TDD cycle completion:
- Invoke **test-guardian** to verify test quality and coverage
- Invoke **type-enforcer** to ensure type safety
- Invoke **style-guardian** for code style consistency
- Invoke **security-sentinel** for security review
