---
name: quality-check
description: Run comprehensive quality gates (mypy, ruff, pytest) before committing code. Use after completing implementation tasks and before marking phases complete.
---

# Quality Check

## Instructions

Run these quality gates before committing:

### Quality Gates Checklist

### 1. Type Safety (mypy)

```bash
# Run mypy strict mode
uv run mypy --strict src/

# Expected output: Success: no issues found
```

**Common Issues & Fixes**:
```python
# Issue: Missing return type
def add_task(title: str):  # ❌ No return type
    ...

def add_task(title: str) -> Task:  # ✅ Return type specified
    ...

# Issue: Implicit Optional
def process(data: str = None):  # ❌ Implicit Optional
    ...

def process(data: Optional[str] = None) -> None:  # ✅ Explicit Optional
    ...

# Issue: Missing type hint
def calculate(items):  # ❌ No parameter type
    ...

def calculate(items: List[Task]) -> int:  # ✅ Fully typed
    ...
```

### 2. Linting (ruff check)

```bash
# Check for issues
uv run ruff check src/ tests/

# Auto-fix issues
uv run ruff check --fix src/ tests/

# Expected output: All checks passed!
```

**Common Issues**:
- Unused imports
- Line too long (>100 chars)
- Missing docstrings
- Unused variables

### 3. Formatting (ruff format)

```bash
# Check formatting
uv run ruff format --check src/ tests/

# Auto-format
uv run ruff format src/ tests/

# Expected output: Would reformat 0 files
```

### 4. Testing (pytest)

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run with coverage threshold (fail if <90%)
uv run pytest --cov=src --cov-fail-under=90

# Expected output: All tests passed, coverage >90%
```

**Coverage Report Example**:
```
---------- coverage: platform win32, python 3.13.0 -----------
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
src/__init__.py                    1      0   100%
src/models/task.py                45      2    96%   78-79
src/services/task_service.py      32      0   100%
------------------------------------------------------------
TOTAL                             78      2    97%
```

### 5. Security Check

```bash
# Check dependencies for vulnerabilities
uv run pip-audit

# Expected output: No known vulnerabilities found
```

## Pre-Commit Quality Script

Create a helper script for convenience:

```powershell
# scripts/quality-check.ps1
Write-Host "Running quality checks..." -ForegroundColor Cyan

Write-Host "`n1. Type checking (mypy)..." -ForegroundColor Yellow
uv run mypy --strict src/
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "`n2. Linting (ruff)..." -ForegroundColor Yellow
uv run ruff check src/ tests/
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "`n3. Formatting (ruff)..." -ForegroundColor Yellow
uv run ruff format --check src/ tests/
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "`n4. Testing (pytest)..." -ForegroundColor Yellow
uv run pytest --cov=src --cov-fail-under=90
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "`n✅ All quality checks passed!" -ForegroundColor Green
```

```bash
# scripts/quality-check.sh
#!/bin/bash
set -e

echo "Running quality checks..."

echo -e "\n1. Type checking (mypy)..."
uv run mypy --strict src/

echo -e "\n2. Linting (ruff)..."
uv run ruff check src/ tests/

echo -e "\n3. Formatting (ruff)..."
uv run ruff format --check src/ tests/

echo -e "\n4. Testing (pytest)..."
uv run pytest --cov=src --cov-fail-under=90

echo -e "\n✅ All quality checks passed!"
```

Usage:
```bash
# Windows
.\scripts\quality-check.ps1

# Linux/Mac
./scripts/quality-check.sh
```

## Quality Gates Per Phase

### Phase Completion Checklist

Before marking any phase (3-12) complete:

- [ ] **All tasks in phase completed**
- [ ] **Type check passes**: `mypy --strict src/`
- [ ] **Linter passes**: `ruff check src/ tests/`
- [ ] **Formatter passes**: `ruff format --check src/ tests/`
- [ ] **Tests pass**: `pytest`
- [ ] **Coverage >90%**: `pytest --cov=src --cov-fail-under=90`
- [ ] **Integration tests pass**: Verify CLI commands work end-to-end
- [ ] **Spec requirements met**: All acceptance criteria satisfied
- [ ] **No regressions**: Previous phases still work

### Task 87 (Phase 13): Final Quality Check

```bash
# T087: Run quality checks
uv run mypy --strict src/
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run pytest --cov=src --cov-fail-under=90 -v
```

Expected results:
- **mypy**: Success: no issues found
- **ruff check**: All checks passed!
- **ruff format**: Would reformat 0 files
- **pytest**: All tests passed (>90% coverage)

## Quality Metrics Dashboard

Track metrics over time:

```python
# scripts/quality-metrics.py
"""Generate quality metrics report."""
import subprocess
import json

def run_mypy() -> dict:
    result = subprocess.run(
        ["uv", "run", "mypy", "--strict", "src/"],
        capture_output=True,
        text=True,
    )
    return {"mypy": "✅ PASS" if result.returncode == 0 else "❌ FAIL"}

def run_tests() -> dict:
    result = subprocess.run(
        ["uv", "run", "pytest", "--cov=src", "--cov-report=json"],
        capture_output=True,
    )

    with open("coverage.json") as f:
        data = json.load(f)

    coverage = data["totals"]["percent_covered"]
    return {
        "tests": "✅ PASS" if result.returncode == 0 else "❌ FAIL",
        "coverage": f"{coverage:.1f}%",
    }

def main():
    print("📊 Quality Metrics Report\n")
    print(f"Type Safety: {run_mypy()['mypy']}")

    test_results = run_tests()
    print(f"Tests: {test_results['tests']}")
    print(f"Coverage: {test_results['coverage']}")

if __name__ == "__main__":
    main()
```

## Integration with Subagents

After quality checks, invoke these subagents:
- **test-guardian**: Comprehensive test quality audit
- **type-enforcer**: Deep type safety review
- **style-guardian**: Code style consistency
- **security-sentinel**: Security vulnerability scan
- **performance-optimizer**: Performance profiling
- **doc-curator**: Documentation completeness

## Git Pre-Commit Hook

Automate quality checks before commits:

```bash
# .git/hooks/pre-commit
#!/bin/bash
set -e

echo "Running pre-commit quality checks..."

uv run mypy --strict src/
uv run ruff check src/ tests/
uv run pytest --cov=src --cov-fail-under=90

echo "✅ Pre-commit checks passed"
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```
