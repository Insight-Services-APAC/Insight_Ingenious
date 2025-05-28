"""
Helper functions for structured logging.

This module provides utility functions for working with
structured logging, such as getting loggers and setting up logging.
"""

import functools
import logging
import uuid
from typing import Callable, List, Optional

from ingenious.common.logging.structured.logger import StructuredLogger


def get_structured_logger(
    name: str, mask_fields: Optional[List[str]] = None, level: int = logging.NOTSET
) -> StructuredLogger:
    """
    Get a structured logger with the given name.

    Args:
        name: The name of the logger
        mask_fields: Fields to mask in logs
        level: The initial logging level

    Returns:
        A structured logger instance
    """
    return StructuredLogger(name, mask_fields, level)


def with_correlation_id(correlation_id: Optional[str] = None) -> Callable:
    """
    Decorator to set a correlation ID for the duration of a function call.

    Args:
        correlation_id: The correlation ID to use (generates a new one if None)

    Returns:
        Decorator function
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get the logger name based on the function's module
            logger_name = func.__module__

            # Create a structured logger
            logger = get_structured_logger(logger_name)

            # Set the correlation ID
            if correlation_id is None:
                new_id = str(uuid.uuid4())
            else:
                new_id = correlation_id

            logger.with_correlation_id(new_id)

            try:
                # Call the function
                return func(*args, **kwargs)
            finally:
                # Clear the context when done
                logger.clear_context()

        return wrapper

    return decorator


def setup_json_logging(
    app_module_name: Optional[str] = None,
    log_level: str = None,
    log_file: Optional[str] = None,
    log_dir: Optional[str] = None,
    include_logger_name: bool = True,
    include_level_name: bool = True,
    **kwargs,
) -> None:
    """
    Set up JSON-formatted logging for the application.

    Args:
        app_module_name: The name of the application module
        log_level: The logging level to use
        log_file: The name of the log file to write to
        log_dir: The directory to store log files in
        include_logger_name: Whether to include the logger name in JSON logs
        include_level_name: Whether to include the level name in JSON logs
        **kwargs: Additional arguments to pass to setup_logging
    """
    # Import the base setup function
    import logging.handlers
    import os
    import sys
    from pathlib import Path

    import colorlog

    from ingenious.common.logging.structured.formatters import JsonFormatter

    # Get log levels from environment or parameters
    root_log_level = os.environ.get("ROOTLOGLEVEL", "WARNING")
    if log_level is None:
        log_level = os.environ.get("LOGLEVEL", "WARNING")

    # Create handlers list
    handlers = []

    # Create a stream handler for console output
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(asctime)s - %(log_color)s[%(levelname)s]%(reset)s - %(name)s - %(message)s"
        )
    )
    handlers.append(stream_handler)

    # Create a file handler if requested
    if log_file:
        if log_dir:
            # Create log directory if it doesn't exist
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            log_file_path = os.path.join(log_dir, log_file)
        else:
            log_file_path = log_file

        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path, maxBytes=10485760, backupCount=5
        )
        handlers.append(file_handler)

    # Configure root logger
    if root_log_level:
        root_logger = logging.getLogger()
        root_logger.setLevel(root_log_level)

        # Clear existing handlers to avoid duplication
        if root_logger.handlers:
            root_logger.handlers.clear()

    # Configure app logger if specified
    if app_module_name:
        logger = logging.getLogger(app_module_name)
        logger.setLevel(log_level)

        # Don't propagate to root logger to avoid duplicate logs
        logger.propagate = False

        # Clear existing handlers to avoid duplication
        if logger.handlers:
            logger.handlers.clear()

    # Replace the formatter with our JSON formatter
    formatter = JsonFormatter(
        include_logger_name=include_logger_name, include_level_name=include_level_name
    )

    # Update handlers
    for handler in handlers:
        handler.setFormatter(formatter)

        # Add handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)

        # Add handler to app logger if specified
        if app_module_name:
            app_logger = logging.getLogger(app_module_name)
            app_logger.addHandler(handler)
