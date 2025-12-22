"""
Tests for error schema models.
"""

import pytest
from app.schemas.error import ErrorDetail, ErrorResponse, HTTPError, COMMON_ERRORS


def test_error_detail_creation():
    """Test ErrorDetail model instantiation."""
    error = ErrorDetail(
        loc=["body", "title"],
        msg="Field required",
        type="value_error.missing"
    )

    assert error.loc == ["body", "title"]
    assert error.msg == "Field required"
    assert error.type == "value_error.missing"


def test_error_detail_without_location():
    """Test ErrorDetail without location."""
    error = ErrorDetail(
        msg="General error",
        type="error"
    )

    assert error.loc is None
    assert error.msg == "General error"


def test_error_response_with_string_detail():
    """Test ErrorResponse with string detail."""
    response = ErrorResponse(
        detail="Task not found",
        status_code=404,
        error_type="NotFoundError"
    )

    assert response.detail == "Task not found"
    assert response.status_code == 404
    assert response.error_type == "NotFoundError"


def test_error_response_with_list_detail():
    """Test ErrorResponse with list of ErrorDetail."""
    errors = [
        ErrorDetail(loc=["body", "title"], msg="Field required", type="value_error.missing"),
        ErrorDetail(loc=["body", "due_date"], msg="Invalid date", type="value_error.date")
    ]

    response = ErrorResponse(
        detail=errors,
        status_code=422
    )

    assert len(response.detail) == 2
    assert response.status_code == 422
    assert response.error_type is None


def test_http_error_creation():
    """Test HTTPError model instantiation."""
    error = HTTPError(detail="Unauthorized access")

    assert error.detail == "Unauthorized access"


def test_common_errors_structure():
    """Test COMMON_ERRORS dictionary structure."""
    assert 400 in COMMON_ERRORS
    assert 401 in COMMON_ERRORS
    assert 403 in COMMON_ERRORS
    assert 404 in COMMON_ERRORS
    assert 422 in COMMON_ERRORS
    assert 500 in COMMON_ERRORS

    # Check structure of error definitions
    assert "description" in COMMON_ERRORS[400]
    assert "model" in COMMON_ERRORS[400]
    assert COMMON_ERRORS[400]["model"] == HTTPError
    assert COMMON_ERRORS[422]["model"] == ErrorResponse


def test_common_errors_descriptions():
    """Test that all common errors have proper descriptions."""
    for code, error_def in COMMON_ERRORS.items():
        assert isinstance(error_def["description"], str)
        assert len(error_def["description"]) > 0
        assert "model" in error_def
