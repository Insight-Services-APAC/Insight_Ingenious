"""
Tests for the logging module in ingenious.common.logging.
"""

import json
import logging
from io import StringIO

from ingenious.common.logging import get_logger, log_execution_time, setup_logging
from ingenious.common.logging.structured import (
    JsonFormatter,
    StructuredLogger,
    clear_context,
    get_context,
    get_structured_logger,
    set_context,
)


class TestLogging:
    """Test suite for basic logging functionality."""

    def test_setup_logging(self):
        """Test basic logging setup."""
        # Setup logging
        setup_logging(app_module_name="test_app", log_level="DEBUG")

        # Get a logger
        logger = logging.getLogger("test_app")

        # Check logger level
        assert logger.level == logging.DEBUG

        # Check handlers
        assert logger.handlers
        assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)

    def test_get_logger(self):
        """Test getting a logger."""
        # Setup logging
        setup_logging(app_module_name="test_app", log_level="INFO")

        # Get a logger
        logger = get_logger("test_module")

        # Check logger
        assert logger.name == "test_module"
        assert logger.level == logging.INFO  # Should inherit from root logger

    def test_log_execution_time_decorator(self):
        """Test log_execution_time decorator."""
        # Create a logger with a StringIO handler
        logger = logging.getLogger("test_timer")
        logger.setLevel(logging.DEBUG)
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logger.addHandler(handler)

        # Define a function with the decorator
        @log_execution_time(logger=logger)
        def slow_function():
            import time

            time.sleep(0.1)
            return "done"

        # Call the function
        result = slow_function()

        # Check the result and log
        assert result == "done"
        log_output = log_stream.getvalue()
        assert "slow_function" in log_output
        assert "execution time:" in log_output
        assert "seconds" in log_output


class TestStructuredLogging:
    """Test suite for structured logging functionality."""

    def setup_method(self):
        """Reset context before each test."""
        clear_context()

    def test_json_formatter(self):
        """Test JSON formatter formats log records as JSON."""
        # Create a formatter
        formatter = JsonFormatter()

        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname=__file__,
            lineno=100,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Format the record
        formatted = formatter.format(record)

        # Parse the JSON
        parsed = json.loads(formatted)

        # Check the parsed JSON
        assert parsed["level"] == "INFO"
        assert parsed["name"] == "test_logger"
        assert parsed["message"] == "Test message"
        assert "timestamp" in parsed

    def test_structured_logger(self):
        """Test StructuredLogger with context."""
        # Create a logger with a StringIO handler
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(JsonFormatter())

        logger = StructuredLogger("test_structured")
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

        # Set context and log
        set_context({"request_id": "123", "user": "test_user"})
        logger.info("Test with context")

        # Parse the log
        log_output = log_stream.getvalue()
        parsed = json.loads(log_output)

        # Check the parsed log
        assert parsed["message"] == "Test with context"
        assert parsed["context"]["request_id"] == "123"
        assert parsed["context"]["user"] == "test_user"

    def test_get_structured_logger(self):
        """Test getting a structured logger."""
        logger = get_structured_logger("test_get_structured")

        assert isinstance(logger, StructuredLogger)
        assert logger.name == "test_get_structured"

    def test_context_management(self):
        """Test setting, getting, and clearing context."""
        # Set context
        set_context({"key": "value"})

        # Get context
        context = get_context()
        assert context == {"key": "value"}

        # Update context
        set_context({"another_key": "another_value"})
        context = get_context()
        assert context == {"key": "value", "another_key": "another_value"}

        # Clear context
        clear_context()
        context = get_context()
        assert context == {}
