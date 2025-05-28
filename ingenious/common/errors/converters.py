"""
Error conversion utilities for the Ingenious framework.

This module provides utilities for converting standard Python exceptions
and third-party library exceptions to Ingenious application errors.
"""

import asyncio
import concurrent.futures
import json
import json.decoder
import logging

# Standard library exceptions
import socket
import sqlite3
from typing import Callable, Dict, Type

# Import error classes
from ingenious.common.errors.base import IngeniousError
from ingenious.common.errors.common import (
    ConfigurationError,
    ServiceError,
    ValidationError,
)
from ingenious.common.errors.database_errors import (
    DatabaseError,
    DataIntegrityError,
    QueryError,
)

# Get a logger
logger = logging.getLogger(__name__)


def convert_standard_exception(exc: Exception) -> IngeniousError:
    """
    Convert a standard Python exception to an Ingenious error.

    Args:
        exc: The exception to convert

    Returns:
        An appropriate Ingenious error
    """
    # Type-specific conversions
    if isinstance(exc, ValueError):
        return ValidationError(
            message=str(exc) or "Invalid value",
            details={"exception_type": exc.__class__.__name__},
        )

    if isinstance(exc, KeyError):
        return ValidationError(
            message=f"Missing required key: {str(exc)}",
            details={"exception_type": exc.__class__.__name__},
        )

    if isinstance(exc, TypeError):
        return ValidationError(
            message=str(exc) or "Type error",
            details={"exception_type": exc.__class__.__name__},
        )

    if isinstance(exc, IndexError):
        return ValidationError(
            message=str(exc) or "Index error",
            details={"exception_type": exc.__class__.__name__},
        )

    if isinstance(exc, socket.error):
        return ServiceError(
            service_name="network",
            message=f"Network error: {str(exc)}",
            details={"exception_type": exc.__class__.__name__},
        )

    if isinstance(exc, FileNotFoundError):
        return ConfigurationError(
            message=f"File not found: {str(exc)}",
            details={"exception_type": exc.__class__.__name__},
        )

    if isinstance(exc, json.JSONDecodeError):
        return ValidationError(
            message=f"Invalid JSON: {str(exc)}",
            details={
                "exception_type": exc.__class__.__name__,
                "position": exc.pos,
                "line": exc.lineno,
                "column": exc.colno,
            },
        )

    if isinstance(exc, concurrent.futures.TimeoutError) or isinstance(
        exc, asyncio.TimeoutError
    ):
        return ServiceError(
            service_name="unknown",
            message="Operation timed out",
            details={"exception_type": exc.__class__.__name__},
        )

    # Generic conversion
    return IngeniousError(
        message=str(exc) or "An unexpected error occurred",
        details={"exception_type": exc.__class__.__name__},
    )


# SQLite exception conversion
def convert_sqlite_exception(exc: sqlite3.Error) -> DatabaseError:
    """
    Convert a SQLite exception to a Database error.

    Args:
        exc: The SQLite exception to convert

    Returns:
        An appropriate Database error
    """
    error_code = getattr(exc, "sqlite_errorcode", None)
    error_name = getattr(exc, "sqlite_errorname", None)

    details = {
        "exception_type": exc.__class__.__name__,
    }

    if error_code:
        details["error_code"] = error_code
    if error_name:
        details["error_name"] = error_name

    # Handle specific SQLite errors
    if isinstance(exc, sqlite3.OperationalError):
        if "no such table" in str(exc).lower():
            return QueryError(message=f"Table not found: {str(exc)}", details=details)
        if "syntax error" in str(exc).lower():
            return QueryError(message=f"SQL syntax error: {str(exc)}", details=details)

    if isinstance(exc, sqlite3.IntegrityError):
        return DataIntegrityError(
            message=f"Data integrity error: {str(exc)}", details=details
        )

    # Generic database error
    return DatabaseError(message=f"Database error: {str(exc)}", details=details)


# HTTP client errors (requests)
def convert_requests_exception(exc: Exception) -> ServiceError:
    """
    Convert a requests exception to a Service error.

    Args:
        exc: The requests exception to convert

    Returns:
        An appropriate Service error
    """
    import requests

    details = {
        "exception_type": exc.__class__.__name__,
    }

    # Handle timeout errors
    if isinstance(exc, requests.Timeout):
        return ServiceError(
            service_name="http", message="HTTP request timed out", details=details
        )

    # Handle connection errors
    if isinstance(exc, requests.ConnectionError):
        return ServiceError(
            service_name="http", message="HTTP connection error", details=details
        )

    # Handle HTTP errors
    if isinstance(exc, requests.HTTPError):
        response = getattr(exc, "response", None)
        if response:
            status_code = response.status_code
            details["status_code"] = status_code

            try:
                content = response.json()
                details["response"] = content
            except json.JSONDecodeError:
                details["response"] = response.text[:500]  # Truncate long responses

        return ServiceError(
            service_name="http", message=f"HTTP error: {str(exc)}", details=details
        )

    # Generic service error
    return ServiceError(
        service_name="http", message=f"HTTP request error: {str(exc)}", details=details
    )


# Store converters registry
_CONVERTERS: Dict[Type[Exception], Callable[[Exception], IngeniousError]] = {}


def register_converter(exception_type):
    """
    Register a converter function for a specific exception type as a decorator.
    Usage:
        @register_converter(MyException)
        def my_converter(exc): ...
    """

    def decorator(func):
        _CONVERTERS[exception_type] = func
        return func

    return decorator


def reset_converters() -> None:
    """Reset all registered converters."""
    _CONVERTERS.clear()


def convert_exception(exception: Exception) -> IngeniousError:
    """
    Convert an exception to an IngeniousError using the registered converters.
    If the exception is already an IngeniousError, return it as is.
    """
    if isinstance(exception, IngeniousError):
        return exception
    for exc_type, converter in _CONVERTERS.items():
        if isinstance(exception, exc_type):
            return converter(exception)

    # Default conversion fallback
    return IngeniousError(f"{type(exception).__name__}: {exception}")


# Registry for exception converters
_exception_converters: Dict[Type[Exception], Callable[[Exception], IngeniousError]] = {
    ValueError: convert_standard_exception,
    TypeError: convert_standard_exception,
    KeyError: convert_standard_exception,
    IndexError: convert_standard_exception,
    socket.error: convert_standard_exception,
    FileNotFoundError: convert_standard_exception,
    json.JSONDecodeError: convert_standard_exception,
    concurrent.futures.TimeoutError: convert_standard_exception,
    asyncio.TimeoutError: convert_standard_exception,
    sqlite3.Error: convert_sqlite_exception,
}


# Function to register exception converters
def register_exception_converter(
    exception_class: Type[Exception], converter: Callable[[Exception], IngeniousError]
) -> None:
    """
    Register an exception converter for a specific exception type.

    Args:
        exception_class: The exception class to convert
        converter: The converter function
    """
    _exception_converters[exception_class] = converter


# Function to register a converter as a decorator
# def register_converter(exception_type: Type[Exception]):
#     """
#     Register a converter function for a specific exception type.
#     """
#     def decorator(func: Callable[[Exception], IngeniousError]):
#         _CONVERTER_REGISTRY[exception_type] = func
#         return func
#     return decorator


# Function to convert exceptions
# def convert_exception(exc: Exception) -> IngeniousError:
#     """
#     Convert an exception to an Ingenious error.
#     """
#     exc_type = type(exc)
#     converter = _CONVERTER_REGISTRY.get(exc_type)
#     if converter:
#         return converter(exc)
#     return IngeniousError(str(exc))


# Try to register requests exceptions if the library is available
try:
    import requests

    register_exception_converter(requests.RequestException, convert_requests_exception)
except ImportError:
    logger.debug(
        "Requests library not available, skipping requests exception converters"
    )
