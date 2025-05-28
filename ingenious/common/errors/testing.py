"""
Testing utilities for error handling.

This module provides utilities for testing error handling code.
"""

import contextlib
from typing import Any, Callable, Dict, Optional, Type, TypeVar

import pytest

from ingenious.common.errors.base import IngeniousError

T = TypeVar("T", bound=Exception)


@contextlib.contextmanager
def assert_raises(
    exception_type: Type[T], message: Optional[str] = None, **attributes
) -> T:
    """
    Context manager to assert that an exception is raised.

    This is similar to pytest.raises but also allows asserting
    attributes of the exception.

    Args:
        exception_type: The expected exception type
        message: The expected exception message
        **attributes: Additional attributes to check on the exception

    Yields:
        The caught exception

    Raises:
        AssertionError: If the exception isn't raised or doesn't match
    """
    try:
        yield
        pytest.fail(
            f"Expected {exception_type.__name__} to be raised, but no exception was raised"
        )
    except exception_type as exc:
        if message is not None:
            assert str(exc) == message, (
                f"Expected message '{message}', got '{str(exc)}'"
            )

        for attr_name, attr_value in attributes.items():
            assert hasattr(exc, attr_name), (
                f"Exception doesn't have attribute '{attr_name}'"
            )
            actual_value = getattr(exc, attr_name)
            assert actual_value == attr_value, (
                f"Expected {attr_name}='{attr_value}', got '{actual_value}'"
            )

        # Re-raise the exception if it's not the expected type
        # This is handled above, but mypy doesn't know that
        if not isinstance(exc, exception_type):
            raise


def assert_ingenious_error(exception_type: Type[IngeniousError], **kwargs) -> Callable:
    """
    Decorator for testing functions that should raise Ingenious errors.

    Args:
        exception_type: The expected exception type
        **kwargs: Additional attributes to check on the exception

    Returns:
        Decorator function
    """

    def decorator(func):
        # This works with both pytest and unittest
        if hasattr(func, "__call__"):

            def wrapper(*args, **inner_kwargs):
                with assert_raises(exception_type, **kwargs):
                    return func(*args, **inner_kwargs)

            return wrapper
        # This is a direct pytest parametrize call
        else:
            original_func = func.func

            def wrapper(*args, **inner_kwargs):
                with assert_raises(exception_type, **kwargs):
                    return original_func(*args, **inner_kwargs)

            wrapper.__name__ = original_func.__name__

            # Create a new parametrize with the wrapped function
            new_params = getattr(func, "params", [])
            new_ids = getattr(func, "ids", None)

            return pytest.mark.parametrize(
                *func.args, **{"argvalues": new_params, "ids": new_ids}
            )(wrapper)

    return decorator


class MockException:
    """
    Utility to create mock exceptions for testing error handlers.

    This class allows creating mock exceptions with custom attributes
    that can be used to test error handling code.
    """

    def __init__(self, exception_type: Type[Exception], **attributes):
        """
        Initialize the mock exception.

        Args:
            exception_type: The exception type to mock
            **attributes: Attributes to set on the mock exception
        """
        self.exception_type = exception_type
        self.attributes = attributes

    def __enter__(self):
        """Enter the context and prepare to raise the mock exception."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context and raise the mock exception."""
        # Create a mock exception with the specified attributes
        exception = self.exception_type(self.attributes.get("message", ""))

        # Set the attributes on the exception
        for attr_name, attr_value in self.attributes.items():
            setattr(exception, attr_name, attr_value)

        # Raise the exception
        raise exception


def assert_error_conversion(
    original_exception: Exception,
    expected_error_type: Type[IngeniousError],
    expected_attributes: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Assert that an exception is correctly converted to an Ingenious error.

    Args:
        original_exception: The original exception
        expected_error_type: The expected Ingenious error type
        expected_attributes: Expected attributes on the converted error

    Raises:
        AssertionError: If the conversion doesn't match expectations
    """
    from ingenious.common.errors.converters import convert_exception

    # Convert the exception
    ingenious_error = convert_exception(original_exception)

    # Check the type
    assert isinstance(ingenious_error, expected_error_type), (
        f"Expected {expected_error_type.__name__}, got {type(ingenious_error).__name__}"
    )

    # Check the attributes
    if expected_attributes:
        for attr_name, attr_value in expected_attributes.items():
            assert hasattr(ingenious_error, attr_name), (
                f"Converted error doesn't have attribute '{attr_name}'"
            )
            actual_value = getattr(ingenious_error, attr_name)
            assert actual_value == attr_value, (
                f"Expected {attr_name}='{attr_value}', got '{actual_value}'"
            )
