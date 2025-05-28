"""
Rate limiting error classes for the Ingenious framework.

This module provides specialized error classes for rate limiting,
ensuring consistent error handling for rate limit violations.
"""

from typing import Optional

from ingenious.common.errors.base import IngeniousError

__all__ = ["RateLimitError", "QuotaExceededError"]


class RateLimitError(IngeniousError):
    """Error raised when a rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: Optional[int] = None,
        reset_after: Optional[int] = None,
        scope: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the rate limit error.

        Args:
            message: Human-readable error message
            limit: The rate limit that was exceeded
            reset_after: Seconds until the rate limit resets
            scope: The scope of the rate limit (e.g., "user", "ip", "global")
            **kwargs: Additional arguments to pass to the parent class
        """
        details = {}
        if limit is not None:
            details["limit"] = limit
        if reset_after is not None:
            details["reset_after"] = reset_after
        if scope:
            details["scope"] = scope

        super().__init__(
            message=message,
            status_code=429,  # Too Many Requests
            error_code="RATE_LIMIT_EXCEEDED",
            details=details,
            **kwargs,
        )

        # Add Retry-After header information
        if reset_after is not None:
            self.headers = {"Retry-After": str(reset_after)}


class QuotaExceededError(IngeniousError):
    """Error raised when a usage quota is exceeded."""

    def __init__(
        self,
        message: str = "Usage quota exceeded",
        quota: Optional[int] = None,
        usage: Optional[int] = None,
        resource: Optional[str] = None,
        reset_time: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the quota exceeded error.

        Args:
            message: Human-readable error message
            quota: The quota limit
            usage: Current usage
            resource: The resource being limited
            reset_time: When the quota will reset (ISO format string)
            **kwargs: Additional arguments to pass to the parent class
        """
        details = {}
        if quota is not None:
            details["quota"] = quota
        if usage is not None:
            details["usage"] = usage
        if resource:
            details["resource"] = resource
        if reset_time:
            details["reset_time"] = reset_time

        super().__init__(
            message=message,
            status_code=429,  # Too Many Requests
            error_code="QUOTA_EXCEEDED",
            details=details,
            **kwargs,
        )
