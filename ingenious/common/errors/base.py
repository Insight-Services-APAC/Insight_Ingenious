"""
Base error class for the Ingenious framework.

This module defines the base IngeniousError exception class that all
other Ingenious error types extend.
"""

import logging
from typing import Any, Dict, Optional

# Create a logger for the errors module
logger = logging.getLogger(__name__)


class IngeniousError(Exception):
    """Base exception class for all Ingenious application errors."""

    def __init__(
        self,
        message: str = "An error occurred in the Ingenious application",
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the base Ingenious error.

        Args:
            message: Human-readable error message
            status_code: HTTP status code to return if this is an API error
            error_code: Machine-readable error code
            details: Additional error details and context
        """
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary representation."""
        error_dict = {
            "error": self.error_code,
            "message": self.message,
            "status_code": self.status_code,
        }

        if self.details:
            error_dict["details"] = self.details

        return error_dict

    def log(
        self, log_level: int = logging.ERROR, include_traceback: bool = True
    ) -> None:
        """
        Log the error with appropriate severity.

        Args:
            log_level: The logging level to use
            include_traceback: Whether to include the traceback in the log
        """
        error_dict = self.to_dict()
        log_message = f"Error {self.error_code}: {self.message}"

        if include_traceback:
            log_message += f"\nDetails: {error_dict}"
            logger.log(log_level, log_message, exc_info=True)
        else:
            logger.log(log_level, log_message)
