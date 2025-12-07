# Quality Check - Complete Examples

## Example 1: Full Quality Check Workflow

### Scenario: Completing Feature Implementation

You've just implemented US1 (Add Task) and need to verify quality before committing.

**Step 1: Run Type Check**

```bash
$ uv run mypy --strict src/

Success: no issues found in 15 source files
```

**Step 2: Run Linter**

```bash
$ uv run ruff check src/ tests/

All checks passed!
```

**Step 3: Check Formatting**

```bash
$ uv run ruff format --check src/ tests/

Would reformat 0 files
```

**Step 4: Run Tests with Coverage**

```bash
$ uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=90

================================ test session starts ================================
collected 24 items

tests/unit/models/test_task.py ........                                       [ 33%]
tests/unit/services/test_task_service.py ..........                           [ 75%]
tests/integration/test_cli_add.py ......                                      [100%]

---------- coverage: platform win32, python 3.13.0 -----------
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
src/__init__.py                    1      0   100%
src/models/__init__.py             2      0   100%
src/models/task.py                45      0   100%
src/models/priority.py             8      0   100%
src/models/exceptions.py          12      0   100%
src/services/task_service.py      32      0   100%
src/lib/id_generator.py           15      0   100%
src/storage/task_store.py         22      0   100%
src/cli/commands.py               28      0   100%
------------------------------------------------------------
TOTAL                            165      0   100%

Required coverage of 90.0% reached. Total coverage: 100.00%
========================= 24 passed in 2.34s ================================
```

**Step 5: Security Check**

```bash
$ uv run pip-audit

No known vulnerabilities found
```

**Result**:  All quality gates passed! Ready to commit.

---

## Example 2: Fixing Type Check Errors

### Scenario: mypy Reports Errors

**Initial Code (with errors):**

```python
# src/services/task_service.py
class TaskService:
    def __init__(self, store, id_gen):  # L Missing type hints
        self._store = store
        self._id_gen = id_gen

    def add(self, title, description=None):  # L Missing type hints
        task = Task(
            id=self._id_gen.next(),
            title=title,
            description=description
        )
        self._store.save(task)
        return task  # L Missing return type

    def get(self, task_id):  # L Untyped function
        task = self._store.get(task_id)
        if not task:
            raise TaskNotFoundError(f"Task #{task_id} not found")
        return task
```

**Running mypy:**

```bash
$ uv run mypy --strict src/

src/services/task_service.py:3: error: Function is missing a type annotation  [no-untyped-def]
src/services/task_service.py:7: error: Function is missing a type annotation  [no-untyped-def]
src/services/task_service.py:18: error: Function is missing a return type annotation  [no-untyped-def]

Found 3 errors in 1 file (checked 15 source files)
```

**Fixed Code:**

```python
# src/services/task_service.py
from typing import Optional
from src.models.task import Task
from src.models.exceptions import TaskNotFoundError
from src.storage.task_store import TaskStore
from src.lib.id_generator import IdGenerator


class TaskService:
    """Business logic for task operations."""

    def __init__(self, store: TaskStore, id_gen: IdGenerator) -> None:
        """Initialize service with dependencies."""
        self._store = store
        self._id_gen = id_gen

    def add(
        self,
        title: str,
        description: Optional[str] = None
    ) -> Task:
        """Create a new task."""
        task = Task(
            id=self._id_gen.next(),
            title=title,
            description=description
        )
        self._store.save(task)
        return task

    def get(self, task_id: int) -> Task:
        """Retrieve task by ID."""
        task = self._store.get(task_id)
        if not task:
            raise TaskNotFoundError(f"Task #{task_id} not found")
        return task
```

**Re-running mypy:**

```bash
$ uv run mypy --strict src/

Success: no issues found in 15 source files
```

---

## Example 3: Fixing Ruff Linting Issues

### Scenario: Multiple Linting Violations

**Initial Code:**

```python
# src/cli/commands.py
from typing import Optional, List  # L F401: List imported but unused
import typer
from rich.console import Console
from src.services.task_service import TaskService


app = typer.Typer()
console = Console()


@app.command("add")
def add_task(title: str = typer.Argument(..., help="Task title (1-200 characters)"), desc: Optional[str] = typer.Option(None, "--desc", "-d", help="Optional description")):  # L E501: Line too long
    """Add a new task."""
    try:
        task = task_service.add(title=title, description=desc)
        console.print(f"[green][/green] Task #{task.id} created: {task.title}")
    except Exception as e:  # L E722: Bare except
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
```

**Running ruff:**

```bash
$ uv run ruff check src/

src/cli/commands.py:1:28: F401 [*] `typing.List` imported but unused
src/cli/commands.py:13:1: E501 Line too long (212 > 100)
src/cli/commands.py:18:5: E722 Do not use bare `except`

Found 3 errors.
[*] 1 fixable with the `--fix` option.
```

**Auto-fix some issues:**

```bash
$ uv run ruff check --fix src/

Fixed 1 error:
- src/cli/commands.py:1:28: Removed unused import `List`

Still to fix manually:
src/cli/commands.py:13:1: E501 Line too long (212 > 100)
src/cli/commands.py:18:5: E722 Do not use bare `except`
```

**Manually fix remaining issues:**

```python
# src/cli/commands.py
from typing import Optional
import typer
from rich.console import Console
from src.services.task_service import TaskService
from src.models.exceptions import ValidationError  # Add specific exception


app = typer.Typer()
console = Console()


@app.command("add")
def add_task(
    title: str = typer.Argument(..., help="Task title (1-200 characters)"),
    desc: Optional[str] = typer.Option(
        None,
        "--desc",
        "-d",
        help="Optional description"
    ),
) -> None:
    """Add a new task."""
    try:
        task = task_service.add(title=title, description=desc)
        console.print(f"[green][/green] Task #{task.id} created: {task.title}")
    except ValidationError as e:  #  Specific exception
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
```

**Re-running ruff:**

```bash
$ uv run ruff check src/

All checks passed!
```

---

## Example 4: Improving Test Coverage

### Scenario: Coverage Below 90%

**Initial Coverage:**

```bash
$ uv run pytest --cov=src --cov-report=term-missing

---------- coverage: platform win32, python 3.13.0 -----------
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
src/models/task.py                45      5    89%   78-82
src/services/task_service.py      32      3    91%   67-69
------------------------------------------------------------
TOTAL                             77      8    90%

FAILED (coverage: 90.00%, required: 90.00%)
```

**Analysis**: task.py lines 78-82 not covered (tag validation)

**Missing Code:**

```python
# src/models/task.py
def _validate_tags(self) -> None:
    """Tags: alphanumeric + hyphens, max 20 chars each."""
    for tag in self.tags:  # Line 78
        if len(tag) > 20:  # Line 79
            raise ValidationError(f"Tag '{tag}' exceeds 20 characters")  # Line 80
        if not tag.replace("-", "").replace("_", "").isalnum():  # Line 81
            raise ValidationError(f"Tag '{tag}' contains invalid characters")  # Line 82
```

**Add Tests:**

```python
# tests/unit/models/test_task.py
import pytest
from src.models.task import Task
from src.models.exceptions import ValidationError


class TestTaskTagValidation:
    """Test tag validation rules."""

    def test_tag_exceeds_max_length_raises_error(self) -> None:
        """Tag exceeding 20 characters should raise ValidationError."""
        long_tag = "x" * 21

        with pytest.raises(ValidationError, match="exceeds 20 characters"):
            Task(id=1, title="Valid", tags={long_tag})

    def test_tag_with_invalid_characters_raises_error(self) -> None:
        """Tag with special characters should raise ValidationError."""
        with pytest.raises(ValidationError, match="invalid characters"):
            Task(id=1, title="Valid", tags={"tag@special"})

    def test_tag_with_spaces_raises_error(self) -> None:
        """Tag with spaces should raise ValidationError."""
        with pytest.raises(ValidationError, match="invalid characters"):
            Task(id=1, title="Valid", tags={"tag with spaces"})

    def test_valid_tag_formats(self) -> None:
        """Valid tag formats should succeed."""
        valid_tags = {"work", "urgent-task", "project_2024"}
        task = Task(id=1, title="Valid", tags=valid_tags)

        assert task.tags == valid_tags
```

**Re-run Coverage:**

```bash
$ uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=90

---------- coverage: platform win32, python 3.13.0 -----------
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
src/models/task.py                45      0   100%
src/services/task_service.py      32      0   100%
------------------------------------------------------------
TOTAL                             77      0   100%

Required coverage of 90.0% reached. Total coverage: 100.00%
========================= 28 passed in 2.45s ================================
```

---

## Example 5: Automated Quality Check Script

### Complete Quality Check Automation

**Create Script:**

```python
#!/usr/bin/env python3
# scripts/quality_check.py
"""
Comprehensive quality check script.

Runs all quality gates and reports results.
"""

import subprocess
import sys
from typing import List, Tuple


def run_command(cmd: List[str], name: str) -> Tuple[bool, str]:
    """Run command and return success status."""
    print(f"\n{'=' * 60}")
    print(f"Running: {name}")
    print(f"{'=' * 60}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    success = result.returncode == 0
    status = " PASSED" if success else "L FAILED"
    print(f"\n{status}: {name}\n")

    return success, status


def main():
    """Run all quality checks."""
    print("= Starting Comprehensive Quality Check\n")

    checks = [
        (["uv", "run", "mypy", "--strict", "src/"], "Type Checking (mypy)"),
        (["uv", "run", "ruff", "check", "src/", "tests/"], "Linting (ruff check)"),
        (["uv", "run", "ruff", "format", "--check", "src/", "tests/"], "Formatting (ruff format)"),
        (["uv", "run", "pytest", "--cov=src", "--cov-fail-under=90", "-v"], "Testing (pytest)"),
    ]

    results = []
    all_passed = True

    for cmd, name in checks:
        success, status = run_command(cmd, name)
        results.append((name, status))

        if not success:
            all_passed = False

    # Summary
    print("\n" + "=" * 60)
    print("QUALITY CHECK SUMMARY")
    print("=" * 60)

    for name, status in results:
        print(f"{status}: {name}")

    print("=" * 60)

    if all_passed:
        print(" ALL QUALITY CHECKS PASSED!")
        sys.exit(0)
    else:
        print("L SOME QUALITY CHECKS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Make Executable:**

```bash
chmod +x scripts/quality_check.py
```

**Run Script:**

```bash
$ python scripts/quality_check.py

= Starting Comprehensive Quality Check

============================================================
Running: Type Checking (mypy)
============================================================
Success: no issues found in 15 source files

 PASSED: Type Checking (mypy)

============================================================
Running: Linting (ruff check)
============================================================
All checks passed!

 PASSED: Linting (ruff check)

============================================================
Running: Formatting (ruff format)
============================================================
Would reformat 0 files

 PASSED: Formatting (ruff format)

============================================================
Running: Testing (pytest)
============================================================
========================= 28 passed in 2.45s ================================

Required coverage of 90.0% reached. Total coverage: 100.00%

 PASSED: Testing (pytest)

============================================================
QUALITY CHECK SUMMARY
============================================================
 PASSED: Type Checking (mypy)
 PASSED: Linting (ruff check)
 PASSED: Formatting (ruff format)
 PASSED: Testing (pytest)
============================================================
 ALL QUALITY CHECKS PASSED!
```

---

## Example 6: Pre-Commit Hook Integration

### Scenario: Prevent Bad Commits

**Install Pre-Commit Hook:**

```bash
# .git/hooks/pre-commit
#!/bin/bash
set -e

echo "= Running pre-commit quality checks..."

# Quick type check
echo "’ Type checking..."
uv run mypy --strict src/ || {
    echo "L Type check failed. Fix errors before committing."
    exit 1
}

# Quick lint
echo "’ Linting..."
uv run ruff check src/ tests/ || {
    echo "L Linting failed. Fix issues before committing."
    exit 1
}

# Quick test (fast tests only)
echo "’ Running tests..."
uv run pytest tests/unit/ -q || {
    echo "L Tests failed. Fix tests before committing."
    exit 1
}

echo " Pre-commit checks passed!"
```

**Make Executable:**

```bash
chmod +x .git/hooks/pre-commit
```

**Test Hook:**

```bash
$ git add .
$ git commit -m "feat: add task priority"

= Running pre-commit quality checks...
’ Type checking...
Success: no issues found
’ Linting...
All checks passed!
’ Running tests...
...................... 24 passed in 1.23s

 Pre-commit checks passed!

[feature/priority abc123d] feat: add task priority
 3 files changed, 45 insertions(+), 2 deletions(-)
```

---

## Example 7: CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/quality.yml
name: Quality Checks

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  quality:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install dependencies
        run: uv sync

      - name: Type check
        run: uv run mypy --strict src/

      - name: Lint
        run: uv run ruff check src/ tests/

      - name: Format check
        run: uv run ruff format --check src/ tests/

      - name: Test with coverage
        run: uv run pytest --cov=src --cov-fail-under=90 --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

      - name: Security audit
        run: uv run pip-audit
```

**Result**: Automated quality checks on every push and PR!

---

## Summary of Examples

1. **Full Quality Workflow** - Complete check sequence
2. **Fixing Type Errors** - mypy error resolution
3. **Fixing Lint Issues** - ruff error resolution
4. **Improving Coverage** - Getting to >90%
5. **Automated Script** - Python automation
6. **Pre-Commit Hooks** - Git integration
7. **CI/CD Pipeline** - GitHub Actions integration

All examples demonstrate real-world scenarios you'll encounter during Phase 1 Todo App development!
