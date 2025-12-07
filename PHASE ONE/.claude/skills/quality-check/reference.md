# Quality Check - Extended Reference

## Table of Contents

1. [Quality Gates Overview](#quality-gates-overview)
2. [Type Safety with mypy](#type-safety-with-mypy)
3. [Linting with Ruff](#linting-with-ruff)
4. [Code Formatting](#code-formatting)
5. [Test Coverage](#test-coverage)
6. [Security Scanning](#security-scanning)
7. [Performance Profiling](#performance-profiling)
8. [CI/CD Integration](#cicd-integration)
9. [Pre-Commit Hooks](#pre-commit-hooks)
10. [Best Practices](#best-practices)

---

## Quality Gates Overview

### What are Quality Gates?

Quality gates are automated checks that code must pass before being merged or deployed:
- **Type Safety**: mypy --strict ensures no type errors
- **Linting**: ruff check catches code quality issues
- **Formatting**: ruff format ensures consistent style
- **Testing**: pytest verifies functionality with >90% coverage
- **Security**: pip-audit checks for vulnerabilities

### Quality Gate Philosophy

**Fail Fast**: Catch issues early in development, not in production.

**Automation**: Quality checks run automatically, consistently.

**Non-Negotiable**: All gates must pass - no exceptions.

---

## Type Safety with mypy

### Why Strict Type Checking?

```python
# Without types - runtime error
def add_task(service, title):
    return service.add(title)

add_task(None, "Test")  # Runtime crash!
```

```python
# With types - caught at compile time
def add_task(service: TaskService, title: str) -> Task:
    return service.add(title)

add_task(None, "Test")  # mypy error: Argument 1 has incompatible type "None"
```

### Running mypy

```bash
# Basic check
uv run mypy src/

# Strict mode (recommended)
uv run mypy --strict src/

# Specific file
uv run mypy src/models/task.py

# With HTML report
uv run mypy --html-report mypy-report src/
```

### Common mypy Errors and Fixes

**Error 1: Missing Return Type**

```python
# L Error: Function is missing a return type annotation
def get_task(task_id: int):
    return task_service.get(task_id)
```

```python
#  Fixed
def get_task(task_id: int) -> Task:
    return task_service.get(task_id)
```

**Error 2: Implicit Optional**

```python
# L Error: Incompatible default for argument
def process(data: str = None):
    pass
```

```python
#  Fixed
from typing import Optional

def process(data: Optional[str] = None) -> None:
    pass
```

**Error 3: Untyped Function Definition**

```python
# L Error: Function is missing type annotation
def calculate(items):
    return sum(item.value for item in items)
```

```python
#  Fixed
from typing import List

def calculate(items: List[Task]) -> int:
    return sum(item.value for item in items)
```

**Error 4: Returning Any**

```python
# L Error: Returning Any from function declared to return "Task"
def get_task(task_id: int) -> Task:
    data = store.get(task_id)  # Returns Any
    return data
```

```python
#  Fixed
def get_task(task_id: int) -> Task:
    data = store.get(task_id)
    if not isinstance(data, Task):
        raise TypeError(f"Expected Task, got {type(data)}")
    return data
```

### mypy Configuration

```ini
# pyproject.toml
[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true
```

---

## Linting with Ruff

### What is Ruff?

Ruff is an extremely fast Python linter that replaces:
- flake8
- isort
- pylint
- pycodestyle
- pydocstyle

### Running Ruff

```bash
# Check for issues
uv run ruff check src/ tests/

# Auto-fix issues
uv run ruff check --fix src/ tests/

# Watch mode (auto-fix on save)
uv run ruff check --watch src/

# Specific rules only
uv run ruff check --select E,W src/
```

### Common Ruff Issues

**Issue 1: Unused Imports**

```python
# L F401 [*] `typing.List` imported but unused
from typing import List, Optional

def process(data: Optional[str]) -> None:
    pass
```

```python
#  Fixed
from typing import Optional

def process(data: Optional[str]) -> None:
    pass
```

**Issue 2: Line Too Long**

```python
# L E501 Line too long (112 > 100)
task = Task(id=1, title="Very long title that exceeds the maximum allowed line length of 100 characters")
```

```python
#  Fixed
task = Task(
    id=1,
    title="Very long title that exceeds the maximum allowed "
          "line length of 100 characters"
)
```

**Issue 3: Missing Docstring**

```python
# L D100 Missing docstring in public module
def add_task(title: str) -> Task:
    return service.add(title)
```

```python
#  Fixed
"""Task management operations."""

def add_task(title: str) -> Task:
    """Create a new task with given title."""
    return service.add(title)
```

**Issue 4: Unused Variable**

```python
# L F841 Local variable `result` is assigned to but never used
def process_tasks():
    result = service.all()
    return len(result)
```

```python
#  Fixed
def process_tasks():
    tasks = service.all()
    return len(tasks)
```

### Ruff Configuration

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "N",  # pep8-naming
    "UP", # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by formatter)
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["D"]  # No docstrings in tests
```

---

## Code Formatting

### Why Auto-Formatting?

- **Consistency**: Same style everywhere
- **No Debates**: No arguing about style
- **Fast**: Instant formatting
- **Focus**: Spend time on logic, not formatting

### Running Ruff Format

```bash
# Check formatting
uv run ruff format --check src/ tests/

# Auto-format
uv run ruff format src/ tests/

# Specific file
uv run ruff format src/models/task.py

# Diff mode (show changes without applying)
uv run ruff format --diff src/
```

### Format Configuration

```toml
# pyproject.toml
[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"
```

---

## Test Coverage

### Coverage Requirements

- **Overall**: >90% code coverage
- **Critical Paths**: 100% coverage
- **Error Handling**: All exceptions tested

### Running Coverage

```bash
# Basic coverage
uv run pytest --cov=src

# With missing lines report
uv run pytest --cov=src --cov-report=term-missing

# HTML report (detailed)
uv run pytest --cov=src --cov-report=html
# Open: htmlcov/index.html

# Fail if below threshold
uv run pytest --cov=src --cov-fail-under=90

# Branch coverage (includes if/else branches)
uv run pytest --cov=src --cov-branch
```

### Reading Coverage Reports

```
---------- coverage: platform win32, python 3.13.0 -----------
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
src/__init__.py                    1      0   100%
src/models/task.py                45      2    96%   78-79
src/services/task_service.py      32      0   100%
src/cli/commands.py               28      3    89%   45, 67-68
------------------------------------------------------------
TOTAL                            106      5    95%
```

**Analysis**:
- `task.py` lines 78-79 not covered - add test
- `commands.py` line 45 and 67-68 not covered - add integration tests
- Overall 95% - exceeds 90% threshold 

### Coverage Configuration

```toml
# pyproject.toml
[tool.coverage.run]
source = ["src"]
omit = ["tests/*", "*/migrations/*"]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false

[tool.coverage.html]
directory = "htmlcov"
```

---

## Security Scanning

### Dependency Vulnerabilities

```bash
# Check for known vulnerabilities
uv run pip-audit

# Generate report
uv run pip-audit --format json > security-report.json

# Ignore specific vulnerabilities (with justification)
uv run pip-audit --ignore-vuln GHSA-xxxx-xxxx-xxxx
```

### Common Vulnerabilities

**CVE-2024-XXXX: SQL Injection**
- **Risk**: High
- **Fix**: Update package to version X.Y.Z
- **Action**: `uv pip install package>=X.Y.Z`

### Security Best Practices

1. **Keep Dependencies Updated**
   ```bash
   uv pip list --outdated
   uv pip install --upgrade package-name
   ```

2. **Minimal Dependencies**
   - Only install what you need
   - Review transitive dependencies

3. **Lock Files**
   - Use `uv.lock` to ensure reproducible builds
   - Commit lock file to version control

---

## Performance Profiling

### Why Profile?

- Identify bottlenecks
- Optimize critical paths
- Prevent performance regressions

### Profiling Tools

**1. cProfile (Built-in)**

```bash
# Profile a script
python -m cProfile -o profile.stats src/main.py

# View results
python -m pstats profile.stats
```

**2. pytest-benchmark**

```python
# tests/performance/test_benchmarks.py
def test_add_task_performance(benchmark, task_service):
    """Benchmark task creation."""
    result = benchmark(task_service.add, title="Test")
    assert result.id == 1
```

```bash
# Run benchmarks
uv run pytest tests/performance/ --benchmark-only
```

### Performance Thresholds

```python
# Performance test example
import time

def test_search_performance():
    """Search should complete in <100ms for 1000 tasks."""
    # Setup
    for i in range(1000):
        service.add(title=f"Task {i}")

    # Measure
    start = time.perf_counter()
    results = service.search("Task 500")
    elapsed = time.perf_counter() - start

    # Assert
    assert elapsed < 0.1  # 100ms
    assert len(results) > 0
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/quality-check.yml
name: Quality Checks

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

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

      - name: Test
        run: uv run pytest --cov=src --cov-fail-under=90

      - name: Security scan
        run: uv run pip-audit
```

---

## Pre-Commit Hooks

### Installing Pre-Commit

```bash
# Install pre-commit
uv pip install pre-commit

# Install git hooks
pre-commit install
```

### Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        args: [--strict]
        additional_dependencies: [types-all]

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: uv run pytest --cov=src --cov-fail-under=90
        language: system
        pass_filenames: false
        always_run: true
```

### Manual Hook Script

```bash
# .git/hooks/pre-commit
#!/bin/bash
set -e

echo "= Running quality checks..."

echo "1/4 Type checking..."
uv run mypy --strict src/

echo "2/4 Linting..."
uv run ruff check src/ tests/

echo "3/4 Format checking..."
uv run ruff format --check src/ tests/

echo "4/4 Testing..."
uv run pytest --cov=src --cov-fail-under=90 -q

echo " All checks passed!"
```

---

## Best Practices

### 1. Run Checks Locally First

Always run quality checks before pushing:
```bash
# Quick check
uv run mypy --strict src/ && uv run ruff check src/ && uv run pytest

# Full check (recommended)
./scripts/quality-check.sh
```

### 2. Fix Issues Immediately

Don't accumulate quality debt:
- Fix mypy errors as they appear
- Auto-fix ruff issues: `ruff check --fix`
- Write tests to achieve >90% coverage

### 3. Use IDE Integration

Configure your IDE to run checks on save:
- VSCode: Pylance, Ruff extension
- PyCharm: mypy plugin, ruff plugin

### 4. Incremental Improvements

If coverage is low:
```bash
# Check coverage for new code only
uv run pytest --cov=src --cov-report=term-missing tests/unit/test_new_feature.py
```

### 5. Document Exceptions

If you must ignore a check, document why:
```python
# type: ignore[arg-type]  # Legacy code, will fix in #123
result = legacy_function(data)
```

### 6. Regular Dependency Updates

```bash
# Weekly: Check for updates
uv pip list --outdated

# Monthly: Update dependencies
uv pip install --upgrade-all

# After update: Run full test suite
uv run pytest --cov=src --cov-fail-under=90
```

---

## Resources

- [mypy Documentation](https://mypy.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [pip-audit Documentation](https://pypi.org/project/pip-audit/)
- [Pre-commit Documentation](https://pre-commit.com/)
