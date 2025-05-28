"""
Enhanced logging features for the Ingenious framework.

This module extends the basic logging functionality with structured logging,
request tracking, and sensitive data masking.
"""

# Import main components to expose them from the structured module
from ingenious.common.logging.structured.context import (
    clear_context,
    get_context,
    set_context,
)
from ingenious.common.logging.structured.formatters import JsonFormatter
from ingenious.common.logging.structured.helpers import (
    get_structured_logger,
    setup_json_logging,
    with_correlation_id,
)
from ingenious.common.logging.structured.logger import StructuredLogger

# Define the public API
__all__ = [
    "StructuredLogger",
    "JsonFormatter",
    "get_structured_logger",
    "with_correlation_id",
    "setup_json_logging",
    "get_context",
    "set_context",
    "clear_context",
]
