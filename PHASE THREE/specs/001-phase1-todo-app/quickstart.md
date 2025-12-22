# Quickstart Guide: Phase 1 Complete Todo App

**Date**: 2025-12-06 | **Plan**: [plan.md](./plan.md)

This guide helps developers set up the development environment and start working on the Phase 1 Todo CLI application.

---

## Prerequisites

- **Python**: 3.13+ (required by constitution)
- **UV**: Package manager (required by constitution)
- **Git**: Version control

### Install Python 3.13+

```bash
# macOS (Homebrew)
brew install python@3.13

# Windows (winget)
winget install Python.Python.3.13

# Linux (Ubuntu/Debian)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.13 python3.13-venv
```

### Install UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip (if needed)
pip install uv
```

---

## Project Setup

### 1. Clone and Navigate

```bash
cd evolved-todo
```

### 2. Initialize UV Project

```bash
# Create virtual environment and install dependencies
uv sync

# Or initialize new project (if starting fresh)
uv init
```

### 3. Verify Setup

```bash
# Activate virtual environment
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Verify Python version
python --version  # Should show 3.13+

# Verify UV
uv --version
```

---

## Project Structure

Create the following directory structure:

```bash
# Create directories
mkdir -p src/models src/services src/cli src/lib
mkdir -p tests/unit tests/integration tests/contract
mkdir -p docs

# Create __init__.py files
touch src/__init__.py
touch src/models/__init__.py
touch src/services/__init__.py
touch src/cli/__init__.py
touch src/lib/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
touch tests/contract/__init__.py
```

### Expected Structure

```
evolved-todo/
├── pyproject.toml          # UV/pip configuration
├── src/
│   ├── __init__.py
│   ├── main.py             # Entry point
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py         # Task dataclass
│   │   ├── priority.py     # Priority enum
│   │   ├── recurrence.py   # RecurrencePattern
│   │   └── exceptions.py   # Custom exceptions
│   ├── services/
│   │   ├── __init__.py
│   │   ├── task_service.py
│   │   ├── search_service.py
│   │   ├── sort_service.py
│   │   └── recurrence_service.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── commands.py
│   │   ├── formatters.py
│   │   └── validators.py
│   └── lib/
│       ├── __init__.py
│       ├── date_parser.py
│       └── id_generator.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Shared fixtures
│   ├── unit/
│   ├── integration/
│   └── contract/
└── docs/
    ├── architecture.md
    └── commands.md
```

---

## Dependencies

### pyproject.toml

```toml
[project]
name = "evolved-todo"
version = "0.1.0"
description = "Phase 1 CLI Todo Application"
requires-python = ">=3.13"
dependencies = [
    "typer>=0.9.0",
    "python-dateutil>=2.8.2",
    "rich>=13.0.0",
]

[project.scripts]
todo = "src.main:app"

[tool.uv]
dev-dependencies = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "mypy>=1.8.0",
    "ruff>=0.1.0",
]

[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_ignores = true

[tool.ruff]
line-length = 88
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "-v --cov=src --cov-report=term-missing --cov-fail-under=90"
```

### Install Dependencies

```bash
# Install all dependencies (including dev)
uv sync

# Or add individually
uv add typer python-dateutil rich
uv add --dev pytest pytest-cov mypy ruff
```

---

## Running the Application

### Development Mode

```bash
# Run directly
python -m src.main --help

# Or after installing
todo --help
```

### Install as CLI Tool

```bash
# Install in development mode
uv pip install -e .

# Now use 'todo' command directly
todo --help
todo add "Test task"
todo list
```

---

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py

# Run specific test
pytest tests/unit/test_models.py::test_task_creation

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

---

## Code Quality Checks

### Type Checking (mypy)

```bash
# Run mypy
mypy src

# With strict mode (required)
mypy --strict src
```

### Linting (ruff)

```bash
# Check for issues
ruff check src tests

# Auto-fix issues
ruff check --fix src tests
```

### Formatting (ruff)

```bash
# Check formatting
ruff format --check src tests

# Auto-format
ruff format src tests
```

### All Checks (CI Script)

```bash
# Run all quality checks
ruff check src tests
ruff format --check src tests
mypy --strict src
pytest --cov=src --cov-fail-under=90
```

---

## TDD Workflow

Follow the Red-Green-Refactor cycle (constitution mandate):

### 1. RED - Write Failing Test

```python
# tests/unit/test_task_service.py
def test_add_task_with_title():
    """Test creating a task with just a title."""
    service = TaskService()

    task = service.add(title="Buy groceries")

    assert task.id == 1
    assert task.title == "Buy groceries"
    assert task.is_complete is False
```

```bash
# Run test - should FAIL
pytest tests/unit/test_task_service.py::test_add_task_with_title
```

### 2. GREEN - Implement Minimal Code

```python
# src/services/task_service.py
class TaskService:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1

    def add(self, title: str) -> Task:
        task = Task(id=self._next_id, title=title)
        self._tasks[task.id] = task
        self._next_id += 1
        return task
```

```bash
# Run test - should PASS
pytest tests/unit/test_task_service.py::test_add_task_with_title
```

### 3. REFACTOR - Improve Code

```python
# Improved with IdGenerator
class TaskService:
    def __init__(self) -> None:
        self._store = InMemoryTaskStore()
        self._id_gen = IdGenerator()

    def add(self, title: str, **kwargs) -> Task:
        task = Task(id=self._id_gen.next_id(), title=title, **kwargs)
        return self._store.add(task)
```

```bash
# Run test - should still PASS
pytest tests/unit/test_task_service.py::test_add_task_with_title
```

---

## Feature Development Order

Implement features in this order (based on dependency graph):

1. **Foundation** - Task model, ID generator, exceptions
2. **001-Add-Task** - Create tasks
3. **002-View-Tasks** - Display tasks
4. **003-Update-Task** - Modify tasks
5. **004-Mark-Complete** - Toggle completion
6. **005-Delete-Task** - Remove tasks
7. **006-Priorities-Tags** - Extend Task model
8. **007-Search-Filter** - Search/filter services
9. **010-Due-Dates-Reminders** - Due date handling
10. **008-Sort-Tasks** - Sorting logic
11. **009-Recurring-Tasks** - Recurrence logic

---

## Common Commands

```bash
# Development
uv sync                    # Install dependencies
python -m src.main         # Run app
pytest                     # Run tests
mypy --strict src         # Type check
ruff check src            # Lint
ruff format src           # Format

# Git workflow
git checkout -b feature/001-add-task
git add .
git commit -m "feat: implement add task feature"
git push origin feature/001-add-task
```

---

## Troubleshooting

### Python version mismatch

```bash
# Check version
python --version

# Use specific version with UV
uv python pin 3.13
```

### Import errors

```bash
# Ensure package is installed in dev mode
uv pip install -e .

# Check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### mypy errors

```bash
# Install type stubs if needed
uv add --dev types-python-dateutil

# Ignore specific errors (last resort)
# type: ignore[import-untyped]
```

### Test failures

```bash
# Run single test with debug output
pytest tests/unit/test_models.py -v --tb=long

# Drop into debugger on failure
pytest --pdb
```

---

## Next Steps

1. Read the [Plan](./plan.md) for architecture overview
2. Read the [Data Model](./data-model.md) for entity definitions
3. Read the [CLI Contracts](./contracts/cli-commands.md) for command interface
4. Start implementing Feature 001 (Add Task) following TDD
