"""
StructuredLogger implementation.

This module provides the StructuredLogger class which adds structured
logging capabilities and context tracking to a standard logger.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional

from ingenious.common.logging.structured.context import get_context_data

# Initialize a logger for this module
logger = logging.getLogger(__name__)


class StructuredLogger:
    """
    Logger wrapper that supports structured logging and context tracking.

    This class wraps a standard Python logger and adds support for:
    - Structured logging with JSON format
    - Thread-local context data
    - Correlation ID tracking
    - Sensitive data masking
    """

    def __init__(
        self,
        name: str,
        mask_fields: Optional[List[str]] = None,
        level: int = logging.NOTSET,
    ):
        """
        Initialize the structured logger.

        Args:
            name: The name of the logger
            mask_fields: Fields to mask in logs
            level: The initial logging level
        """
        self.logger = logging.getLogger(name)
        self.mask_fields = set(mask_fields or [])

        if level != logging.NOTSET:
            self.logger.setLevel(level)

    @property
    def name(self):
        return self.logger.name

    def setLevel(self, level):
        self.logger.setLevel(level)

    def add_mask_field(self, field_name: str) -> None:
        """Add a field to be masked in logs."""
        self.mask_fields.add(field_name)

    def set_context(self, key: str, value: Any) -> None:
        """
        Set a value in the current thread's context.

        Args:
            key: The context key
            value: The context value
        """
        from ingenious.common.logging.structured.context import set_context

        set_context(key, value)

    def get_context(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the current thread's context.

        Args:
            key: The context key
            default: The default value to return if the key is not found

        Returns:
            The context value or default
        """
        from ingenious.common.logging.structured.context import get_context

        return get_context(key, default)

    def clear_context(self) -> None:
        """Clear the current thread's context data."""
        from ingenious.common.logging.structured.context import clear_context

        clear_context()

    def with_correlation_id(
        self, correlation_id: Optional[str] = None
    ) -> "StructuredLogger":
        """
        Set a correlation ID in the current thread's context.

        Args:
            correlation_id: The correlation ID to use (generates a new one if None)

        Returns:
            This logger instance for chaining
        """
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())

        self.set_context("correlation_id", correlation_id)
        return self

    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mask sensitive data in the log data.

        Args:
            data: The data to mask

        Returns:
            The masked data
        """
        # Create a copy to avoid modifying the original
        masked_data = {}

        for key, value in data.items():
            if key in self.mask_fields:
                # Mask the value
                if isinstance(value, str):
                    if len(value) > 4:
                        masked_data[key] = (
                            value[:2] + "*" * (len(value) - 4) + value[-2:]
                        )
                    else:
                        masked_data[key] = "****"
                else:
                    masked_data[key] = "****"
            elif isinstance(value, dict):
                # Recursively mask nested dictionaries
                masked_data[key] = self._mask_sensitive_data(value)
            else:
                masked_data[key] = value

        return masked_data

    def _log(
        self,
        level: int,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info=None,
    ) -> None:
        """
        Log a message with context data.

        Args:
            level: The logging level
            message: The log message
            extra: Additional data to include in the log
            exc_info: Exception info to include
        """
        # Get the current context data
        context = get_context_data()

        # Combine context and extra data
        log_data = {**context}
        if extra:
            log_data.update(extra)

        # Mask sensitive data
        if self.mask_fields:
            log_data = self._mask_sensitive_data(log_data)

        # Log the message with the data
        self.logger.log(
            level, message, extra={"structured": log_data}, exc_info=exc_info
        )

    def debug(
        self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info=None
    ) -> None:
        """Log a debug message."""
        self._log(logging.DEBUG, message, extra, exc_info)

    def info(
        self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info=None
    ) -> None:
        """Log an info message."""
        self._log(logging.INFO, message, extra, exc_info)

    def warning(
        self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info=None
    ) -> None:
        """Log a warning message."""
        self._log(logging.WARNING, message, extra, exc_info)

    def error(
        self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info=None
    ) -> None:
        """Log an error message."""
        self._log(logging.ERROR, message, extra, exc_info)

    def critical(
        self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info=None
    ) -> None:
        """Log a critical message."""
        self._log(logging.CRITICAL, message, extra, exc_info)

    def exception(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log an exception message."""
        self._log(logging.ERROR, message, extra, exc_info=True)

    def addHandler(self, handler):
        """Add a handler to the logger."""
        self.logger.addHandler(handler)
