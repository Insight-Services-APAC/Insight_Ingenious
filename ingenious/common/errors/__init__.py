"""
Centralized error handling for the Ingenious framework.

This module provides base exception classes and error utilities to standardize
error handling across the application.
"""

# Import and re-export the base error class
from ingenious.common.errors.base import IngeniousError

# Import and re-export common error types
from ingenious.common.errors.common import (
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
    NotFoundError,
    ServiceError,
    ValidationError,
)

# Import commonly used specialized errors directly
from ingenious.common.errors.content_filter_error import ContentFilterError

# Import and re-export error handler functions
from ingenious.common.errors.handlers import (
    get_error_handler,
    handle_exception,
    register_error_handler,
)

# Import specialized error modules
from ingenious.common.errors.importer import import_error_modules
from ingenious.common.errors.token_limit_exceeded_error import TokenLimitExceededError

# Get all error classes from specialized modules and add them to this module's globals
for name, cls in import_error_modules().items():
    globals()[name] = cls

# Define what symbols should be exported when using "from ingenious.common.errors import *"
__all__ = [
    "IngeniousError",
    "ValidationError",
    "NotFoundError",
    "AuthenticationError",
    "AuthorizationError",
    "ServiceError",
    "ConfigurationError",
    "ContentFilterError",
    "TokenLimitExceededError",
    "handle_exception",
    "register_error_handler",
    "get_error_handler",
]

# Add specialized error classes to __all__
__all__.extend(list(import_error_modules().keys()))
