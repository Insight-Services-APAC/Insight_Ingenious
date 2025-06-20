"""Shared utilities for cross-cutting concerns."""

import importlib
import logging
from typing import Any, Type, Optional


logger = logging.getLogger(__name__)


def import_class_with_fallback(module_name: str, class_name: str) -> Type[Any]:
    """
    Import a class from a module with fallback mechanism.

    Args:
        module_name: The module name to import from
        class_name: The class name to import

    Returns:
        The imported class

    Raises:
        ImportError: If the module cannot be imported
        AttributeError: If the class cannot be found in the module
    """
    try:
        # Try direct import first
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
    except ImportError:
        # Try with ingenious prefix
        prefixed_module = f"ingenious.{module_name}"
        try:
            module = importlib.import_module(prefixed_module)
            return getattr(module, class_name)
        except ImportError as e:
            raise ImportError(
                f"Could not import {class_name} from {module_name} or {prefixed_module}"
            ) from e
    except AttributeError as e:
        raise AttributeError(
            f"Class {class_name} not found in module {module_name}"
        ) from e


def safe_import_module(module_name: str, class_name: str) -> Optional[Type[Any]]:
    """
    Safely import a class from a module, returning None if it fails.

    Args:
        module_name: The module name to import from
        class_name: The class name to import

    Returns:
        The imported class or None if import fails
    """
    try:
        return import_class_with_fallback(module_name, class_name)
    except (ImportError, AttributeError) as e:
        logger.warning(f"Failed to import {class_name} from {module_name}: {e}")
        return None


def validate_not_none(value: Any, name: str) -> Any:
    """
    Validate that a value is not None.

    Args:
        value: The value to validate
        name: The name of the value for error messages

    Returns:
        The value if not None

    Raises:
        ValueError: If the value is None
    """
    if value is None:
        raise ValueError(f"{name} cannot be None")
    return value


def validate_not_empty(value: str, name: str) -> str:
    """
    Validate that a string value is not None or empty.

    Args:
        value: The string value to validate
        name: The name of the value for error messages

    Returns:
        The value if not None or empty

    Raises:
        ValueError: If the value is None or empty
    """
    if not value:
        raise ValueError(f"{name} cannot be None or empty")
    return value
