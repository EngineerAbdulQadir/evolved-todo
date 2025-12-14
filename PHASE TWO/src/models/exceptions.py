"""Custom exceptions for the Evolved Todo application (T009)."""


class TodoAppError(Exception):
    """Base exception for all Todo App errors."""

    pass


class TaskNotFoundError(TodoAppError):
    """Raised when a task ID does not exist in storage."""

    pass


class ValidationError(TodoAppError):
    """Raised when input validation fails."""

    pass


class InvalidTitleError(ValidationError):
    """Raised when task title is invalid (empty, too long)."""

    pass


class InvalidDescriptionError(ValidationError):
    """Raised when description exceeds length limit."""

    pass


class InvalidPriorityError(ValidationError):
    """Raised when priority value is not high/medium/low."""

    pass


class InvalidTagError(ValidationError):
    """Raised when tag is invalid (too long, too many tags)."""

    pass


class InvalidDateError(ValidationError):
    """Raised when date parsing fails."""

    pass


class InvalidTimeError(ValidationError):
    """Raised when time parsing fails."""

    pass


class InvalidRecurrenceError(ValidationError):
    """Raised when recurrence settings are invalid."""

    pass
