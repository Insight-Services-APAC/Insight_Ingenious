"""Utility functions for error handling."""

import functools
from typing import Any, Callable, Type

from ingenious.common.errors.base import IngeniousError


def format_error_message(message: str, **kwargs: Any) -> str:
    """
    Format an error message with the given parameters.

    Args:
        message: The message template
        **kwargs: The parameters to format the message with

    Returns:
        The formatted message
    """
    if not kwargs:
        return message

    return message.format(**kwargs)


def assert_ingenious_error(expected_error_type: Type[IngeniousError] = None):
    """
    Decorator that asserts a function raises a specific IngeniousError.

    This decorator is primarily used for testing error handling code. It ensures
    that the function raises the expected error type.

    Args:
        expected_error_type: The expected error type (subclass of IngeniousError)
                            If None, any IngeniousError is accepted.

    Returns:
        A decorator function

    Example:
        @assert_ingenious_error(NotFoundError)
        def test_function():
            # This function should raise a NotFoundError
            raise NotFoundError("Resource not found")
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Check if it's an IngeniousError
                if not isinstance(e, IngeniousError):
                    raise AssertionError(
                        f"Function {func.__name__} raised {type(e).__name__}, "
                        f"which is not an IngeniousError"
                    ) from e

                # If expected_error_type is specified, check the type
                if expected_error_type and not isinstance(e, expected_error_type):
                    raise AssertionError(
                        f"Function {func.__name__} raised {type(e).__name__}, "
                        f"expected {expected_error_type.__name__}"
                    ) from e

                # Re-raise the original error
                raise e

        return wrapper

    return decorator
