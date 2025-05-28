"""
Error handler registry and management for the Ingenious framework.

This module provides utilities for registering and looking up error handlers,
enabling centralized error handling.
"""

import logging
from typing import Any, Callable, Dict, Optional, Type, TypeVar

from ingenious.common.errors.base import IngeniousError

# Type variable for error handlers
T = TypeVar("T")

# Create a logger for the error handlers
logger = logging.getLogger(__name__)

# Registry for error handlers
_error_handlers: Dict[Type[Exception], Callable] = {}


def register_error_handler(exception_class: Type[Exception]) -> Callable:
    """
    Register an error handler for a specific exception type.

    Can be used as a decorator.

    Args:
        exception_class: The exception class to handle

    Returns:
        A decorator function that registers the handler
    """

    def decorator(handler_func: Callable[[Exception], Any]):
        _error_handlers[exception_class] = handler_func
        return handler_func

    return decorator


def reset_error_handlers() -> None:
    """Reset all registered error handlers."""
    _error_handlers.clear()


def get_error_handler(exception_class: Type[Exception]) -> Optional[Callable]:
    """
    Get an error handler for an exception class.

    This will search for handlers registered for the exception class
    and its parent classes.

    Args:
        exception_class: The exception class to find a handler for

    Returns:
        The handler function or None if no handler is found
    """
    # Try to find an exact match
    if exception_class in _error_handlers:
        return _error_handlers[exception_class]

    # Try to find a parent class handler
    for handler_class in _error_handlers:
        if issubclass(exception_class, handler_class):
            return _error_handlers[handler_class]

    return None


def handle_exception(exc: Exception) -> Any:
    """
    Handle an exception using registered error handlers.

    Args:
        exc: The exception to handle

    Returns:
        The result of the error handler
    """
    handler = get_error_handler(type(exc))

    if handler:
        return handler(exc)

    # Default behavior for unhandled exceptions
    if isinstance(exc, IngeniousError):
        exc.log()
        error_dict = exc.to_dict()
        # Add expected status field for compatibility
        return {
            "status": "error",
            "message": error_dict["message"],
            "details": error_dict,
        }

    # Log unhandled exceptions
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    # Convert to a generic error
    generic_error = IngeniousError(
        message=str(exc) or "An unexpected error occurred",
        details={"exception_type": exc.__class__.__name__},
    )

    error_dict = generic_error.to_dict()
    return {"status": "error", "message": error_dict["message"], "details": error_dict}
