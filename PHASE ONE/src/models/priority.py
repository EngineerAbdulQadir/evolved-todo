"""Priority enum for task importance levels (T010, T012)."""

from enum import Enum


class Priority(Enum):
    """Task priority levels for Feature 006."""

    HIGH = "high"  # Most important, needs immediate attention
    MEDIUM = "medium"  # Normal importance (default for display)
    LOW = "low"  # Can be deferred, low urgency


class DueStatus(Enum):
    """Task due date status for Feature 010 (T012)."""

    OVERDUE = "overdue"  # Due date passed, task incomplete
    DUE_TODAY = "due_today"  # Due date is today
    UPCOMING = "upcoming"  # Due date in future
    NO_DUE_DATE = "no_due_date"  # No deadline set
