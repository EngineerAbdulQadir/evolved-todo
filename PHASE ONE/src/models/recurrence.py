"""Recurrence pattern enum for recurring tasks (T011)."""

from enum import Enum


class RecurrencePattern(Enum):
    """Task recurrence patterns for Feature 009."""

    NONE = "none"  # One-time task (no recurrence)
    DAILY = "daily"  # Repeat every day
    WEEKLY = "weekly"  # Repeat on specific day of week
    MONTHLY = "monthly"  # Repeat on specific day of month
