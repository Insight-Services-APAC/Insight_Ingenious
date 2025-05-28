"""
Thread-local context management for structured logging.

This module provides functionality for storing and retrieving
context data in thread-local storage.
"""

import threading
from typing import Any, Dict

# Thread-local storage for context data
_context_data = threading.local()


def get_context_data() -> Dict[str, Any]:
    """Get the current thread's context data dictionary."""
    if not hasattr(_context_data, "data"):
        _context_data.data = {}
    return _context_data.data


def set_context(context_data: dict = None, **kwargs):
    """
    Set the entire context dictionary or a single key-value pair.

    Args:
        context_data: The context dictionary to replace or update the current context
        **kwargs: Key-value pairs to add to the context
    """
    current_context = get_context_data()

    if context_data is not None:
        if isinstance(context_data, dict):
            # Update existing context with the new values
            current_context.update(context_data)
        else:
            # If a key-value pair is provided (old behavior)
            key = context_data
            if len(kwargs) == 0 or "value" not in kwargs:
                raise ValueError("Value must be provided when setting a single key")
            current_context[key] = kwargs.get("value")

    # Add any additional kwargs to the context
    for key, value in kwargs.items():
        if key != "value":  # Skip the 'value' if it was used for a single key
            current_context[key] = value


def get_context(key: str = None, default: Any = None) -> Any:
    """
    Get a value from the current thread's context, or the whole context if no key is provided.

    Args:
        key: The context key
        default: The default value to return if the key is not found

    Returns:
        The context value or default
    """
    context = get_context_data()
    if key is None:
        return context
    return context.get(key, default)


def clear_context() -> None:
    """Clear the current thread's context data."""
    if hasattr(_context_data, "data"):
        _context_data.data.clear()
