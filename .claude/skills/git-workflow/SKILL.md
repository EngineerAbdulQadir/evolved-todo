---
name: git-workflow
description: Manage version control with Git following project conventions and best practices. Use before committing, creating branches, or making pull requests.
---

# Git Workflow

## Instructions

### When to Use

- Before committing any code changes
- When creating feature branches
- Before creating pull requests
- During code review process

## Branching Strategy

### Branch Naming Convention

```bash
# Feature branches
<task-id>-<short-description>

# Examples:
git checkout -b 001-project-setup
git checkout -b 019-task-service-add
git checkout -b 065-due-dates
```

### Branch Workflow

```bash
# 1. Start new feature from main
git checkout main
git pull origin main
git checkout -b 019-task-service-add

# 2. Make changes and commit frequently
git add src/services/task_service.py
git commit -m "feat(task-service): implement add() method"

# 3. Push to remote
git push -u origin 019-task-service-add

# 4. Create PR when ready
gh pr create --title "Feature: Task Service Add Method" --body "Implements T019-T020"
```

## Commit Message Convention

Follow **Conventional Commits** specification:

```
<type>(<scope>): <subject>

<optional body>

<optional footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **refactor**: Code restructuring without behavior change
- **test**: Adding or updating tests
- **docs**: Documentation changes
- **style**: Code style changes (formatting, missing semicolons)
- **perf**: Performance improvements
- **chore**: Build process, dependencies, tooling

## Examples

### Example 1: Good Commit Messages

```bash
# Good commit messages
git commit -m "feat(models): add Task dataclass with validation"
git commit -m "test(task-service): add unit tests for add() method"
git commit -m "fix(cli): handle empty task list display"
git commit -m "refactor(models): extract validation to private methods"
git commit -m "docs(readme): add installation instructions"

# Bad commit messages (avoid these)
git commit -m "updates"
git commit -m "fixed stuff"
git commit -m "WIP"
```

## Commit Workflow (TDD Cycle)

### Red Phase Commit

```bash
git add tests/unit/test_task_service.py
git commit -m "test(task-service): add failing test for add() method

- Test verifies task creation with ID generation
- Test expects ValidationError for empty title
- Related to T019"
```

### Green Phase Commit

```bash
git add src/services/task_service.py
git commit -m "feat(task-service): implement add() method

- Generates sequential task IDs
- Validates title and description
- Saves to in-memory store
- Implements T020"
```

### Refactor Phase Commit

```bash
git add src/services/task_service.py src/models/task.py
git commit -m "refactor(task-service): improve type safety and validation

- Add explicit type hints to all methods
- Extract validation logic to Task model
- Pass mypy --strict checks"
```

## Pull Request Workflow

### Creating PR

```bash
# 1. Ensure all tests pass
uv run pytest --cov=src --cov-fail-under=90

# 2. Ensure quality checks pass
uv run mypy --strict src/
uv run ruff check src/ tests/

# 3. Push final changes
git push origin 019-task-service-add

# 4. Create PR with gh CLI
gh pr create \
  --title "feat: Implement TaskService.add() method (T019-T020)" \
  --body "## Summary
- Implements TaskService.add() with validation
- Adds unit tests for task creation
- Coverage: 95%

## Tasks Completed
- [x] T019: Write unit tests for TaskService.add()
- [x] T020: Implement TaskService.add()

## Testing
\`\`\`bash
uv run pytest tests/unit/test_task_service.py -v
\`\`\`

## Quality Checks
- [x] mypy --strict passes
- [x] ruff check passes
- [x] pytest passes (95% coverage)

Closes #19, #20"
```

### PR Template

See `templates/pr-template.md`

## Pre-Commit Checklist

Before every commit:

- [ ] Code compiles/runs without errors
- [ ] New tests added for new functionality
- [ ] All tests pass: `uv run pytest`
- [ ] Type check passes: `uv run mypy --strict src/`
- [ ] Linter passes: `uv run ruff check src/ tests/`
- [ ] No debugging code (print statements, breakpoints)
- [ ] No commented-out code
- [ ] Commit message follows convention

## Common Git Commands

```bash
# View status
git status
git diff
git log --oneline -10

# Stage changes
git add <file>
git add -p  # Interactive staging

# Commit
git commit -m "message"
git commit --amend  # Amend last commit (use carefully)

# Branching
git branch -a  # List all branches
git checkout -b <branch>  # Create and switch
git branch -d <branch>  # Delete local branch

# Remote operations
git fetch origin
git pull origin main
git push origin <branch>
git push -u origin <branch>  # Set upstream

# Undo changes
git restore <file>  # Discard working changes
git restore --staged <file>  # Unstage
git reset HEAD~1  # Undo last commit (keep changes)
git reset --hard HEAD~1  # Undo last commit (discard changes)

# Stashing
git stash
git stash pop
git stash list
```

## Integration with git-workflow Subagent

After major git operations, invoke the **git-workflow** subagent:

```
Before committing code changes:
- Subagent validates commit message format
- Checks for sensitive data (secrets, tokens)
- Verifies branch naming convention
- Ensures atomic commits

Before creating PR:
- Validates PR description completeness
- Checks commit history quality
- Ensures branch is up-to-date with base
- Verifies CI/CD status
```

## Helper Script

See `scripts/git-helper.py` for automated commit validation and PR creation.
