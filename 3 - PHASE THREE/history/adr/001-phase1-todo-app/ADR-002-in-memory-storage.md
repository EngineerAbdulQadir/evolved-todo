# ADR-002: In-Memory Storage Only

**Date**: 2025-12-06
**Status**: Accepted
**Deciders**: Engineer Abdul Qadir
**Feature**: Phase 1 Todo App (All Features)

## Context

The Phase 1 Todo App needs to store tasks. The constitution explicitly states:
- "In-memory only (data lost on restart)"
- "NO database or file I/O"
- Phase 1 is CLI-only, single-user

We need to decide on the storage implementation pattern.

## Decision

**Use Python dictionary-based in-memory storage with a TaskStore abstraction.**

```python
class InMemoryTaskStore:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}

    def add(self, task: Task) -> Task:
        self._tasks[task.id] = task
        return task

    def get(self, task_id: int) -> Task:
        if task_id not in self._tasks:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return self._tasks[task_id]

    def all(self) -> list[Task]:
        return list(self._tasks.values())
```

## Consequences

### Positive
- **O(1) lookup**: Dictionary provides constant-time access by ID
- **Simple**: No external dependencies, pure Python
- **Constitution compliant**: No persistence, no database
- **Testable**: Easy to create fresh instances for each test
- **Abstraction ready**: TaskStore interface allows future Phase 2 migration to database

### Negative
- **Data loss**: All tasks lost when application exits
- **No persistence**: Users must recreate tasks each session
- **Memory limit**: Large task counts consume RAM (acceptable for ~10,000 tasks)

### Neutral
- Single-user only (no concurrency concerns)
- No backup/restore capability in Phase 1

## Alternatives Considered

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| SQLite | Persistence, SQL queries | Constitution forbids database | Explicitly forbidden |
| JSON file | Simple persistence | Constitution forbids file I/O | Explicitly forbidden |
| Pickle | Python-native serialization | File I/O, security concerns | Forbidden + insecure |
| Redis | Fast, in-memory with optional persistence | External service, overkill | Over-engineering for Phase 1 |

## Migration Path

The `TaskStore` abstraction enables future Phase 2 migration:

```python
# Phase 1: In-memory
task_store = InMemoryTaskStore()

# Phase 2: Database (future)
task_store = SQLiteTaskStore("todo.db")
# or
task_store = PostgresTaskStore(connection_string)
```

## Compliance

- **Constitution III (YAGNI)**: No over-engineering, simplest solution that works
- **Constitution IV (Technology Stack)**: In-memory per requirements
- **Forbidden Items**: No database, no file persistence

## References

- [Constitution Section IV](../.specify/memory/constitution.md)
- [research.md Section 5](../specs/001-phase1-todo-app/research.md#5-in-memory-storage-pattern)
