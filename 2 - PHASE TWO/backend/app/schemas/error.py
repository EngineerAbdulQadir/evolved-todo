"""
Error response schemas for consistent API error handling.

This module defines Pydantic models for API error responses.
"""

from typing import Any, Optional

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Detailed error information."""

    loc: Optional[list[str]] = None  # Location of error (for validation errors)
    msg: str  # Error message
    type: str  # Error type


class ErrorResponse(BaseModel):
    """Standard API error response."""

    detail: str | list[ErrorDetail]  # Error message or validation errors
    status_code: int  # HTTP status code
    error_type: Optional[str] = None  # Error category (e.g., "ValidationError")


class HTTPError(BaseModel):
    """Simple HTTP error response."""

    detail: str


# Common error responses for OpenAPI documentation
COMMON_ERRORS: dict[int | str, dict[str, Any]] = {
    400: {
        "description": "Bad Request - Invalid input data",
        "model": HTTPError,
    },
    401: {
        "description": "Unauthorized - Missing or invalid authentication token",
        "model": HTTPError,
    },
    403: {
        "description": "Forbidden - Access denied to requested resource",
        "model": HTTPError,
    },
    404: {
        "description": "Not Found - Resource does not exist",
        "model": HTTPError,
    },
    422: {
        "description": "Unprocessable Entity - Validation error",
        "model": ErrorResponse,
    },
    500: {
        "description": "Internal Server Error",
        "model": HTTPError,
    },
}
