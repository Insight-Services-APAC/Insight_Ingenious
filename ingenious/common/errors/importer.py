"""
Error module importer for the Ingenious framework.

This module handles dynamically importing specialized error modules
and making their classes available at the package level.
"""

import importlib
import logging
from typing import Dict, Type

from ingenious.common.errors.base import IngeniousError

# Create a logger for the module importer
logger = logging.getLogger(__name__)


def import_error_modules() -> Dict[str, Type]:
    """
    Dynamically import all error modules in the package.

    This function attempts to import specialized error modules and make
    their error classes available at the package level.

    Returns:
        A dictionary of error class names to error class types
    """
    error_classes = {}

    # List of specialized error modules to import
    specialized_modules = [
        "content_filter_error",
        "token_limit_exceeded_error",
        "database_errors",
        "cache_errors",
        "rate_limit_errors",
    ]

    # Import each module and collect error classes
    for module_name in specialized_modules:
        try:
            module = importlib.import_module(f"ingenious.common.errors.{module_name}")

            # Get the module's __all__ attribute if it exists, otherwise use dir()
            module_items = getattr(module, "__all__", dir(module))

            # Import all public error classes from the module
            for name in module_items:
                if not name.startswith("_"):
                    attr = getattr(module, name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, IngeniousError)
                        and attr is not IngeniousError
                    ):
                        # Add to the collected error classes
                        error_classes[name] = attr

        except ImportError as e:
            logger.debug(f"Could not import error module {module_name}: {e}")

    return error_classes
