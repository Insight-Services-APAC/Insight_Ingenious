"""Tests for the error decorator utilities."""

import pytest

from ingenious.common.errors.base import IngeniousError
from ingenious.common.errors.common import NotFoundError, ValidationError
from ingenious.common.errors.utilities import assert_ingenious_error


def test_assert_ingenious_error_decorator_success():
    """Test that the decorator works when the function raises the expected error."""

    @assert_ingenious_error(NotFoundError)
    def func_that_raises_not_found():
        raise NotFoundError(
            message="Resource not found", resource_type="test", resource_id="123"
        )

    # This should re-raise the NotFoundError
    with pytest.raises(NotFoundError):
        func_that_raises_not_found()


def test_assert_ingenious_error_decorator_failure():
    """Test that the decorator fails when the function raises the wrong error type."""

    @assert_ingenious_error(NotFoundError)
    def func_that_raises_validation_error():
        raise ValidationError(message="Invalid data")

    # This should raise an AssertionError
    with pytest.raises(AssertionError):
        func_that_raises_validation_error()


def test_assert_ingenious_error_decorator_non_ingenious_error():
    """Test that the decorator fails when the function raises a non-IngeniousError."""

    @assert_ingenious_error()
    def func_that_raises_value_error():
        raise ValueError("Invalid value")

    # This should raise an AssertionError
    with pytest.raises(AssertionError):
        func_that_raises_value_error()


def test_assert_ingenious_error_decorator_any_ingenious_error():
    """Test that the decorator accepts any IngeniousError when no type is specified."""

    @assert_ingenious_error()
    def func_that_raises_ingenious_error():
        raise IngeniousError(message="Generic error")

    # This should re-raise the IngeniousError
    with pytest.raises(IngeniousError):
        func_that_raises_ingenious_error()
