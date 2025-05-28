"""Tests for error utilities."""

from ingenious.common.errors.common import NotFoundError


def test_not_found_error():
    """Test creating a NotFoundError."""
    error = NotFoundError(
        message="Resource not found", resource_type="test", resource_id="123"
    )
    assert "Resource not found" in str(error)
    assert error.details["resource_type"] == "test"
    assert error.details["resource_id"] == "123"
