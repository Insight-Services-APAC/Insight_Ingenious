"""Simple tests for errors functionality."""

from ingenious.common.errors.base import IngeniousError


def test_basic_error():
    """Test the base error class."""
    error = IngeniousError(
        message="Test error", status_code=500, error_code="TEST_ERROR"
    )
    assert str(error) == "Test error"
    assert error.status_code == 500
    assert error.error_code == "TEST_ERROR"
