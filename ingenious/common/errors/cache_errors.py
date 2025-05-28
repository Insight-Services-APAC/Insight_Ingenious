"""
Cache-related error classes for the Ingenious framework.

This module provides specialized error classes for cache operations,
ensuring consistent error handling for cache-related issues.
"""

from typing import Optional

from ingenious.common.errors.base import IngeniousError

__all__ = ["CacheError", "CacheConnectionError", "CacheKeyError"]


class CacheError(IngeniousError):
    """Base class for cache-related errors."""

    def __init__(
        self,
        message: str = "A cache error occurred",
        cache_name: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the cache error.

        Args:
            message: Human-readable error message
            cache_name: Name of the cache that encountered the error
            operation: Cache operation that failed
            **kwargs: Additional arguments to pass to the parent class
        """
        details = {}
        if cache_name:
            details["cache_name"] = cache_name
        if operation:
            details["operation"] = operation

        super().__init__(
            message=message,
            status_code=500,
            error_code="CACHE_ERROR",
            details=details,
            **kwargs,
        )


class CacheConnectionError(CacheError):
    """Error raised when a cache connection fails."""

    def __init__(self, message: str = "Cache connection failed", **kwargs):
        """
        Initialize the cache connection error.

        Args:
            message: Human-readable error message
            **kwargs: Additional arguments to pass to the parent class
        """
        super().__init__(message=message, error_code="CACHE_CONNECTION_ERROR", **kwargs)


class CacheKeyError(CacheError):
    """Error raised when a cache key operation fails."""

    def __init__(
        self,
        message: str = "Cache key operation failed",
        key: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the cache key error.

        Args:
            message: Human-readable error message
            key: The cache key that failed
            **kwargs: Additional arguments to pass to the parent class
        """
        details = kwargs.get("details", {})
        if key:
            details["key"] = key

        super().__init__(
            message=message, error_code="CACHE_KEY_ERROR", details=details, **kwargs
        )
