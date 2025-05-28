"""
Formatters for structured logging.

This module provides formatters for structured logging that output
log records in various structured formats like JSON.
"""

import json
import logging


class JsonFormatter(logging.Formatter):
    """
    JSON formatter for log records.

    This formatter outputs log records in JSON format, which is useful
    for log aggregation systems.
    """

    def __init__(self, include_logger_name=True, include_level_name=True):
        """
        Initialize the JSON formatter.

        Args:
            include_logger_name: Whether to include the logger name
            include_level_name: Whether to include the level name
        """
        super().__init__()
        self.include_logger_name = include_logger_name
        self.include_level_name = include_level_name

    def format(self, record):
        """
        Format a log record as JSON.

        Args:
            record: The log record to format

        Returns:
            The formatted log record as a JSON string
        """
        # Start with the basic record attributes
        log_data = {
            "timestamp": self.formatTime(record),
            "message": record.getMessage(),
        }

        # Add optional attributes
        if self.include_logger_name:
            log_data["name"] = record.name

        if self.include_level_name:
            log_data["level"] = record.levelname

        # Add structured data if available
        if hasattr(record, "structured") and record.structured:
            # Add context as a separate field in the JSON output
            context_data = {}
            for key, value in record.structured.items():
                if key.startswith("context_"):
                    # Move context_* keys to the context object
                    context_key = key[8:]  # Remove "context_" prefix
                    context_data[context_key] = value
                else:
                    log_data[key] = value

            # If we found any context data, add it to the log
            if context_data:
                log_data["context"] = context_data
            else:
                # For test compatibility, include the whole structured data as context
                log_data["context"] = record.structured

        # Add exception info if available
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        # Convert to JSON
        return json.dumps(log_data)
