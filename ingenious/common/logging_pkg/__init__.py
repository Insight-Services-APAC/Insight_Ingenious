"""
Centralized logging configuration for the Ingenious framework.

This module provides a consistent logging setup across the application,
including console and file handlers with proper formatting.
"""

import logging
import logging.handlers
import os
import sys
import time
from pathlib import Path
from typing import Optional

import colorlog


def setup_logging(
    app_module_name: Optional[str] = None,
    log_level: str = None,
    log_file: Optional[str] = None,
    log_dir: Optional[str] = None,
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5,
    log_format: str = "%(asctime)s - %(log_color)s[%(levelname)s]%(reset)s - %(name)s - %(message)s",
) -> None:
    """
    Set up application logging with console and optional file output.

    Args:
        app_module_name: The name of the application module
        log_level: The logging level to use (overrides env var if provided)
        log_file: The name of the log file to write to
        log_dir: The directory to store log files in
        max_bytes: Maximum size of each log file before rotation
        backup_count: Number of backup log files to keep
        log_format: The format string to use for log messages
    """
    # Get log levels from environment or parameters
    root_log_level = os.environ.get("ROOTLOGLEVEL", "WARNING")
    if log_level is None:
        log_level = os.environ.get("LOGLEVEL", "WARNING")

    # Create handlers list
    handlers = []

    # Create a stream handler for console output
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(colorlog.ColoredFormatter(log_format))
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
            log_file_path, maxBytes=max_bytes, backupCount=backup_count
        )
        file_formatter = logging.Formatter(
            "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)

    # Configure root logger
    if root_log_level:
        root_logger = logging.getLogger()
        root_logger.setLevel(root_log_level)

        # Clear existing handlers to avoid duplication
        if root_logger.handlers:
            root_logger.handlers.clear()

        for handler in handlers:
            root_logger.addHandler(handler)

    # Configure app logger if specified
    if app_module_name:
        logger = logging.getLogger(app_module_name)
        logger.setLevel(log_level)

        # Don't propagate to root logger to avoid duplicate logs
        logger.propagate = False

        # Clear existing handlers to avoid duplication
        if logger.handlers:
            logger.handlers.clear()

        for handler in handlers:
            logger.addHandler(handler)

    # Configure uvicorn loggers
    for logger_name in ["uvicorn.access", "uvicorn.error"]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)

        # Clear existing handlers to avoid duplication
        if logger.handlers:
            logger.handlers.clear()

        for handler in handlers:
            logger.addHandler(handler)


class LoggingContext:
    """
    Context manager for temporarily changing logging configuration.

    This can be used to temporarily change the logging level for a
    specific operation and then restore it afterward.
    """

    def __init__(self, logger, level=None, handler=None, close=True):
        """
        Initialize the logging context.

        Args:
            logger: The logger to modify
            level: The logging level to temporarily set
            handler: A handler to temporarily add
            close: Whether to close the handler when exiting
        """
        self.logger = logger
        self.level = level
        self.handler = handler
        self.close = close
        self.old_level = logger.level

    def __enter__(self):
        """Enter the context and apply temporary changes."""
        if self.level is not None:
            self.logger.setLevel(self.level)
        if self.handler:
            self.logger.addHandler(self.handler)
        return self.logger

    def __exit__(self, et, ev, tb):
        """Exit the context and restore original settings."""
        if self.level is not None:
            self.logger.setLevel(self.old_level)
        if self.handler:
            self.logger.removeHandler(self.handler)
            if self.close:
                self.handler.close()


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.

    This is a convenience function to ensure all loggers are obtained
    in a consistent way throughout the application.

    Args:
        name: The name of the logger

    Returns:
        The logger instance
    """
    return logging.getLogger(name)


# Performance timing decorator
def log_execution_time(logger=None, level=logging.DEBUG):
    """
    Decorator to log the execution time of a function.

    Args:
        logger: The logger to use
        level: The log level to use

    Returns:
        Decorator function
    """

    def decorator(func):
        nonlocal logger
        if logger is None:
            logger = logging.getLogger(func.__module__)

        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            logger.log(
                level,
                f"Function '{func.__name__}' executed in {execution_time:.3f} seconds",
            )
            return result

        return wrapper

    return decorator


# Import structured logging components
from ingenious.common.logging.structured import (
    JsonFormatter,
    StructuredLogger,
    get_structured_logger,
    setup_json_logging,
    with_correlation_id,
)

__all__ = [
    "setup_logging",
    "LoggingContext",
    "get_logger",
    "log_execution_time",
    "StructuredLogger",
    "JsonFormatter",
    "get_structured_logger",
    "with_correlation_id",
    "setup_json_logging",
]
