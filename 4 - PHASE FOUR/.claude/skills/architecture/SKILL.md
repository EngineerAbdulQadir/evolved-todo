---
name: architecture
description: Maintain clean layered architecture and prevent coupling. Use before starting major features, during design phase, or before merging large PRs.
---

# Architecture

## Instructions

### When to Use

- Before starting major features
- During design phase
- When adding new modules
- Before merging large PRs

## Layered Architecture

```
┌─────────────────────────────────────┐
│   CLI Layer (src/cli/)              │  ← User interface
│   - commands.py                      │
│   - formatters.py                    │
└──────────────┬──────────────────────┘
               │ depends on
               ▼
┌─────────────────────────────────────┐
│   Service Layer (src/services/)     │  ← Business logic
│   - task_service.py                 │
│   - search_service.py               │
└──────────────┬──────────────────────┘
               │ depends on
               ▼
┌─────────────────────────────────────┐
│   Model Layer (src/models/)         │  ← Data structures
│   - task.py                         │
│   - priority.py                     │
│   - exceptions.py                   │
└──────────────┬──────────────────────┘
               │ depends on
               ▼
┌─────────────────────────────────────┐
│   Storage Layer (src/services/)     │  ← Persistence
│   - task_store.py                   │
└─────────────────────────────────────┘
```

## Dependency Rules

1. **CLI** may depend on **Services** and **Models**
2. **Services** may depend on **Models** and **Storage**
3. **Models** depend on nothing (pure data + validation)
4. **Storage** may depend on **Models**

### ❌ Forbidden Dependencies

```python
# Models MUST NOT depend on Services
# Bad:
from src.services.task_service import TaskService  # in models/task.py

# Services MUST NOT depend on CLI
# Bad:
from src.cli.formatters import format_task  # in services/task_service.py
```

## Examples

### Separation of Concerns

```python
# ✅ CLI: User interface only
@app.command("add")
def add_task(title: str, desc: Optional[str] = None) -> None:
    """CLI handles parsing and formatting only."""
    try:
        task = task_service.add(title, desc)  # Delegate to service
        console.print(format_success(task))   # Format output
    except ValidationError as e:
        console.print(format_error(e))

# ✅ Service: Business logic only
class TaskService:
    def add(self, title: str, description: Optional[str]) -> Task:
        """Service handles validation and orchestration."""
        task = Task(id=self._id_gen.next(), title=title, description=description)
        # Task validates itself
        self._store.save(task)
        return task

# ✅ Model: Data + validation only
@dataclass
class Task:
    """Model handles data structure and validation."""
    id: int
    title: str

    def __post_init__(self) -> None:
        self._validate_title()
```

## Integration with code-architect Subagent

Invoke before merging features:

```
Reviews:
- Layer dependency violations
- Circular import detection
- Separation of concerns
- Design pattern appropriateness
```
