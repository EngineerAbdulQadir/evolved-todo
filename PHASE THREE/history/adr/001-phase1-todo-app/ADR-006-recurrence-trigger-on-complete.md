# ADR-006: Recurrence Trigger on Completion

**Date**: 2025-12-06
**Status**: Accepted
**Deciders**: Engineer Abdul Qadir
**Feature**: 009-Recurring-Tasks

## Context

Recurring tasks need to automatically create the next occurrence. We need to decide:
- When is the next occurrence created?
- How is the next due date calculated?
- What happens to the completed occurrence?

## Decision

**Create next occurrence immediately when user marks a recurring task as complete.**

```python
def toggle_complete(self, task_id: int) -> Task:
    """Toggle task completion. Creates next occurrence for recurring tasks."""
    task = self.get(task_id)
    task.is_complete = not task.is_complete

    # If completing a recurring task, create next occurrence
    if task.is_complete and task.has_recurrence:
        next_due = self._recurrence_service.calculate_next_occurrence(task)
        new_task = task.copy_for_recurrence(
            new_id=self._id_gen.next_id(),
            new_due_date=next_due
        )
        self.add(new_task)

    return task
```

## Consequences

### Positive
- **Immediate feedback**: User sees new occurrence created instantly
- **Simple logic**: No background jobs, timers, or schedulers needed
- **User control**: Recurrence only advances when user completes task
- **No drift**: User must complete task before next occurrence appears
- **Testable**: Deterministic behavior, easy to test

### Negative
- **Manual trigger**: If user forgets to complete, next occurrence doesn't appear
- **No auto-creation**: Tasks don't auto-appear at scheduled time
- **Backlog risk**: Missed daily tasks don't pile up (feature or bug?)

### Neutral
- Completed occurrence remains in task list (marked complete)
- Each occurrence is a separate task with unique ID
- New occurrence inherits all attributes except completion status

## Recurrence Calculation

```python
def calculate_next_occurrence(task: Task) -> date:
    """Calculate next due date for recurring task."""
    today = date.today()

    match task.recurrence:
        case RecurrencePattern.DAILY:
            return today + timedelta(days=1)

        case RecurrencePattern.WEEKLY:
            # Same day next week
            days_ahead = (task.recurrence_day - today.weekday() + 7) % 7
            return today + timedelta(days=days_ahead or 7)

        case RecurrencePattern.MONTHLY:
            # Same day next month, adjusted for month length
            next_month = today.month % 12 + 1
            next_year = today.year + (1 if next_month == 1 else 0)
            max_day = monthrange(next_year, next_month)[1]
            target_day = min(task.recurrence_day, max_day)
            return date(next_year, next_month, target_day)
```

## Edge Cases Handled

| Scenario | Behavior |
|----------|----------|
| Monthly on 31st in February | Adjusts to Feb 28/29 |
| Complete task multiple times rapidly | Only one new occurrence created |
| Complete then uncomplete | New occurrence already created, remains |
| Recurring task with no due date | Calculate from today |

## Alternatives Considered

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| Time-based auto-creation | Tasks appear at scheduled time | Requires scheduler, background process | Phase 1 is CLI-only, no daemon |
| Batch creation | Pre-create N occurrences | Complex to manage, delete, update | Over-engineering, hard to modify recurrence |
| On-view creation | Create when user views list | Unpredictable, side effects on read | Violates principle of least surprise |
| Cron-style scheduling | Flexible patterns | Complex implementation, parsing | YAGNI for Phase 1 requirements |

## Compliance

- **Constitution III (YAGNI)**: Simplest recurrence that meets requirements
- **Constitution IV (Technology)**: No external scheduler or daemon needed
- **Spec FR-004**: "Automatically create next occurrence when marked complete"

## References

- [research.md Section 6](../specs/001-phase1-todo-app/research.md#6-recurrence-edge-cases)
- [009-recurring-tasks/spec.md](../specs/001-phase1-todo-app/009-recurring-tasks/spec.md)
