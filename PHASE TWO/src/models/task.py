"""Task dataclass with all Phase 1 attributes (T014, T015)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time

from src.models.priority import DueStatus, Priority
from src.models.recurrence import RecurrencePattern


@dataclass
class Task:
    """
    Represents a todo item with all Phase 1 attributes.

    Attributes:
        id: Unique identifier (auto-generated, immutable)
        title: Task name (required, 1-200 chars)
        description: Additional details (optional, max 1000 chars)
        is_complete: Completion status (default False)
        created_at: Creation timestamp (auto-set, immutable)
        priority: Priority level (high/medium/low)
        tags: Category labels (0-10 tags, each max 50 chars)
        due_date: Deadline date (optional)
        due_time: Deadline time (optional)
        recurrence: Recurrence pattern (daily/weekly/monthly)
        recurrence_day: Day for weekly (1-7) or monthly (1-31) recurrence
    """

    # Core attributes (Basic Level - Features 001-005)
    id: int
    title: str
    description: str | None = None
    is_complete: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    # Organization attributes (Intermediate Level - Feature 006)
    priority: Priority | None = None
    tags: list[str] = field(default_factory=list)

    # Scheduling attributes (Advanced Level - Features 009, 010)
    due_date: date | None = None
    due_time: time | None = None
    recurrence: RecurrencePattern | None = None
    recurrence_day: int | None = None

    def __post_init__(self) -> None:
        """Validate task attributes after initialization."""
        self._validate_title()
        self._validate_description()
        self._validate_tags()
        self._validate_recurrence()

    def _validate_title(self) -> None:
        """
        Ensure title is valid (T015).

        Raises:
            ValueError: If title is empty, whitespace-only, or exceeds 200 chars
        """
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty or whitespace")
        if len(self.title) > 200:
            raise ValueError("Title cannot exceed 200 characters")

    def _validate_description(self) -> None:
        """
        Ensure description is valid if provided (T015).

        Raises:
            ValueError: If description exceeds 1000 chars
        """
        if self.description is not None and len(self.description) > 1000:
            raise ValueError("Description cannot exceed 1000 characters")

    def _validate_tags(self) -> None:
        """
        Ensure tags are valid.

        Raises:
            ValueError: If more than 10 tags or any tag exceeds 50 chars
        """
        if len(self.tags) > 10:
            raise ValueError("Cannot have more than 10 tags")
        for tag in self.tags:
            if len(tag) > 50:
                raise ValueError(f"Tag '{tag}' exceeds 50 character limit")

    def _validate_recurrence(self) -> None:
        """
        Ensure recurrence settings are valid.

        Raises:
            ValueError: If recurrence_day is invalid for pattern
        """
        if self.recurrence == RecurrencePattern.WEEKLY and (
            self.recurrence_day is None or not (1 <= self.recurrence_day <= 7)
        ):
            raise ValueError("Weekly recurrence requires day 1-7 (Mon-Sun)")
        if self.recurrence == RecurrencePattern.MONTHLY and (
            self.recurrence_day is None or not (1 <= self.recurrence_day <= 31)
        ):
            raise ValueError("Monthly recurrence requires day 1-31")

    @property
    def is_overdue(self) -> bool:
        """
        Check if task is overdue (past due date and incomplete).

        Returns:
            True if due date passed and task incomplete, False otherwise
        """
        if self.is_complete or self.due_date is None:
            return False
        today = date.today()
        if self.due_time:
            # Compare date and time
            now = datetime.now()
            due_datetime = datetime.combine(self.due_date, self.due_time)
            return now > due_datetime
        return today > self.due_date

    @property
    def due_status(self) -> DueStatus:
        """
        Get the due date status category.

        Returns:
            DueStatus enum value (OVERDUE/DUE_TODAY/UPCOMING/NO_DUE_DATE)
        """
        if self.due_date is None:
            return DueStatus.NO_DUE_DATE
        if self.is_complete:
            return DueStatus.NO_DUE_DATE  # Completed tasks aren't "overdue"
        today = date.today()
        if self.due_date < today:
            return DueStatus.OVERDUE
        if self.due_date == today:
            return DueStatus.DUE_TODAY
        return DueStatus.UPCOMING

    @property
    def has_recurrence(self) -> bool:
        """
        Check if task has recurrence enabled.

        Returns:
            True if recurrence pattern is set, False otherwise
        """
        return self.recurrence is not None and self.recurrence != RecurrencePattern.NONE

    @property
    def display_due(self) -> str:
        """
        Format due date/time for display.

        Returns:
            Formatted due date string (e.g., "Dec 15, 2025 at 2:00 PM")
        """
        if self.due_date is None:
            return "No due date"
        date_str = self.due_date.strftime("%b %d, %Y")  # e.g., "Dec 15, 2025"
        if self.due_time:
            time_str = self.due_time.strftime("%I:%M %p")  # e.g., "2:00 PM"
            return f"{date_str} at {time_str}"
        return date_str

    def copy_for_recurrence(self, new_id: int, new_due_date: date) -> Task:
        """
        Create a new task instance for recurring task.

        Args:
            new_id: ID for the new occurrence
            new_due_date: Due date for the new occurrence

        Returns:
            New Task instance with reset completion status
        """
        return Task(
            id=new_id,
            title=self.title,
            description=self.description,
            is_complete=False,  # Reset for new occurrence
            created_at=datetime.now(),
            priority=self.priority,
            tags=self.tags.copy(),
            due_date=new_due_date,
            due_time=self.due_time,
            recurrence=self.recurrence,
            recurrence_day=self.recurrence_day,
        )
