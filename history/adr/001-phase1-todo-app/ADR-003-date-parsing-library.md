# ADR-003: Date Parsing Library Selection

**Date**: 2025-12-06
**Status**: Accepted
**Deciders**: Engineer Abdul Qadir
**Feature**: 010-Due-Dates-Reminders, 009-Recurring-Tasks

## Context

The Due Dates & Reminders feature (010) requires parsing user input for dates and times. The specification mandates:
- Support ISO format (YYYY-MM-DD)
- Support natural language ("tomorrow", "next Monday", "Dec 15")
- Support time formats (HH:MM, 2:00 PM)
- Handle edge cases (leap years, month boundaries)

## Decision

**Use `python-dateutil` for date and time parsing.**

```python
from dateutil import parser
from datetime import date, time

def parse_due_date(input_str: str) -> date:
    """Parse natural language or ISO date string."""
    parsed = parser.parse(input_str, fuzzy=True)
    return parsed.date()

def parse_due_time(input_str: str) -> time:
    """Parse time string (HH:MM or 2:00 PM)."""
    parsed = parser.parse(input_str)
    return parsed.time()
```

## Consequences

### Positive
- **Natural language**: Parses "tomorrow", "next Monday", "in 3 days", "Dec 15"
- **Robust**: Handles edge cases (leap years, timezones, DST)
- **Well-maintained**: Active development, wide adoption, battle-tested
- **Lightweight**: Single dependency, no heavy stack
- **Flexible**: Fuzzy parsing handles various input formats

### Negative
- **External dependency**: Adds ~200KB to project
- **Ambiguity**: "next Friday" interpretation depends on current date
- **Locale issues**: Some natural language parsing is English-centric

### Neutral
- Uses local system timezone (acceptable for Phase 1 single-user CLI)
- Fuzzy parsing may accept unexpected inputs (mitigated by validation)

## Alternatives Considered

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| `datetime` only | Standard library, no deps | No natural language parsing | Doesn't meet FR-004 (natural language support) |
| `arrow` | Nice API, timezone handling | Heavier dependency (~500KB) | Overkill for our needs |
| `pendulum` | Excellent TZ handling, immutable | Heavy (~1MB), complex API | Complexity not needed for Phase 1 |
| `parsedatetime` | Good natural language | Less maintained, fewer features | python-dateutil is more robust |

## Usage Examples

```python
# ISO format
parse_due_date("2025-12-15")  # date(2025, 12, 15)

# Natural language
parse_due_date("tomorrow")     # date(2025, 12, 7)
parse_due_date("next Monday")  # date(2025, 12, 9)
parse_due_date("Dec 15")       # date(2025, 12, 15)
parse_due_date("in 3 days")    # date(2025, 12, 9)

# Time parsing
parse_due_time("14:00")        # time(14, 0)
parse_due_time("2:00 PM")      # time(14, 0)
```

## Compliance

- **Constitution IV (Technology Stack)**: Approved dependency for date handling
- **Spec FR-004**: Natural language date support requirement met

## References

- [python-dateutil Documentation](https://dateutil.readthedocs.io/)
- [research.md Section 2](../specs/001-phase1-todo-app/research.md#2-datetime-parsing)
- [010-due-dates-reminders/spec.md FR-004](../specs/001-phase1-todo-app/010-due-dates-reminders/spec.md)
