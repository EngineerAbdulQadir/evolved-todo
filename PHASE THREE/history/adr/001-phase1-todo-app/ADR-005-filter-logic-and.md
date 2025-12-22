# ADR-005: AND Logic for Combined Filters

**Date**: 2025-12-06
**Status**: Accepted
**Deciders**: Engineer Abdul Qadir
**Feature**: 007-Search-Filter

## Context

The Search & Filter feature allows users to apply multiple filters simultaneously:
- Status filter (complete/incomplete)
- Priority filter (high/medium/low)
- Tag filter (any tag)
- Due status filter (overdue/today/week)

We need to decide how multiple filters combine.

## Decision

**Use AND logic: tasks must match ALL applied filters.**

```python
def filter_tasks(
    tasks: list[Task],
    status: str | None = None,
    priority: str | None = None,
    tag: str | None = None,
    due_status: str | None = None,
) -> list[Task]:
    """Filter tasks by multiple criteria (AND logic)."""
    result = tasks

    if status == "complete":
        result = [t for t in result if t.is_complete]
    elif status == "incomplete":
        result = [t for t in result if not t.is_complete]

    if priority:
        result = [t for t in result if t.priority == Priority(priority)]

    if tag:
        result = [t for t in result if tag.lower() in [t.lower() for t in t.tags]]

    if due_status:
        result = [t for t in result if t.due_status == DueStatus(due_status)]

    return result
```

## Consequences

### Positive
- **Intuitive**: Matches user mental model ("show incomplete AND high priority")
- **Progressive narrowing**: Each filter reduces results (predictable)
- **Composable**: Filters chain cleanly without complex logic
- **Consistent**: Same behavior regardless of filter order
- **Efficient**: Short-circuits if any filter produces empty set

### Negative
- **No OR logic**: Cannot search "high OR medium priority" in single query
- **Empty results**: Conflicting filters return nothing (user must adjust)
- **Power users**: Advanced users might want OR/NOT logic

### Neutral
- Filters applied in consistent order regardless of user input order
- Empty filter = show all (no filtering on that criterion)

## Example Behavior

```bash
# AND logic examples
todo list --status incomplete --priority high
# Shows: incomplete AND high priority tasks only

todo list --status incomplete --priority high --tag work
# Shows: incomplete AND high priority AND tagged "work"

# Progressive narrowing
todo list                           # 20 tasks
todo list --status incomplete       # 15 tasks
todo list --status incomplete --priority high  # 3 tasks
```

## Alternatives Considered

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| OR logic | More flexible queries | Confusing for simple cases, unexpected results | Counter-intuitive for most users |
| Query language | Maximum flexibility | Complex to implement, learning curve | Over-engineering for Phase 1 |
| Saved filters | Reusable filter sets | Persistence needed, complex | Phase 1 is in-memory only |
| Filter expressions | `--filter "priority=high OR status=complete"` | Complex parsing, error-prone | YAGNI - not needed for Phase 1 |

## User Mental Model

When users think "show me incomplete high-priority work tasks", they naturally expect:
- Task is incomplete ✓
- AND task is high priority ✓
- AND task is tagged "work" ✓

All conditions must be true. This is AND logic.

## Compliance

- **Constitution III (YAGNI)**: Simplest logic that meets requirements
- **Spec FR-008**: "Support combining multiple filters (AND logic)"
- **User Story 5**: "Apply multiple filters simultaneously"

## References

- [research.md Section 8](../specs/001-phase1-todo-app/research.md#8-filter-logic)
- [007-search-filter/spec.md](../specs/001-phase1-todo-app/007-search-filter/spec.md)
