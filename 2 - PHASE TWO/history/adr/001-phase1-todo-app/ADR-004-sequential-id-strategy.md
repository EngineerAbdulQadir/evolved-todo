# ADR-004: Sequential Integer ID Strategy

**Date**: 2025-12-06
**Status**: Accepted
**Deciders**: Engineer Abdul Qadir
**Feature**: 001-Add-Task (Core)

## Context

Every task needs a unique identifier for:
- User reference in CLI commands (`todo complete 5`, `todo delete 3`)
- Internal storage lookup
- Display in task lists

We need to decide on the ID generation strategy.

## Decision

**Use sequential integers starting from 1, with no ID reuse after deletion.**

```python
class IdGenerator:
    """Generates sequential unique IDs."""

    def __init__(self, start: int = 1) -> None:
        self._next_id = start

    def next_id(self) -> int:
        """Return next available ID and increment counter."""
        current = self._next_id
        self._next_id += 1
        return current
```

## Consequences

### Positive
- **Simple**: Incrementing integer, no complex logic
- **Predictable**: Users can easily reference tasks by number (1, 2, 3...)
- **CLI-friendly**: Short IDs easy to type in commands
- **No external deps**: Pure Python implementation
- **Deterministic**: Same operations produce same IDs (testable)

### Negative
- **Gaps after deletion**: IDs 1, 2, 4 if task 3 deleted (acceptable)
- **No global uniqueness**: IDs reset on app restart (acceptable for in-memory)
- **Overflow potential**: Integer overflow after 2^63 tasks (negligible risk)

### Neutral
- IDs are immutable once assigned
- Cannot reassign or reorder IDs

## ID Behavior

| Action | Result |
|--------|--------|
| Create first task | ID = 1 |
| Create second task | ID = 2 |
| Delete task 1 | ID 1 no longer exists |
| Create third task | ID = 3 (not 1) |
| Restart app | IDs reset to 1 |

## Alternatives Considered

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| UUID | Globally unique, no collisions | Long strings, hard to type in CLI | Poor UX for CLI commands |
| Timestamp-based | Unique, sortable | Long numbers, not user-friendly | Hard to reference in commands |
| ID reuse | No gaps in sequence | Complex tracking, confusing for users | "Task 3" might refer to different tasks |
| Hash-based | Deterministic from content | Collisions possible, not sequential | Overcomplicated for in-memory use |

## Compliance

- **Constitution III (YAGNI)**: Simplest solution that meets requirements
- **Spec Assumption 1**: "Sequential numeric IDs starting from 1"
- **Spec FR-003**: "Assign unique identifier to each newly created task"

## References

- [research.md Section 4](../specs/001-phase1-todo-app/research.md#4-id-generation-strategy)
- [001-add-task/spec.md](../specs/001-phase1-todo-app/001-add-task/spec.md)
