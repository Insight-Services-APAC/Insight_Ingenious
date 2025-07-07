"""
Utility package initialization.
"""

from .exceptions import (
    DocumentParsingError,
    UnsupportedFileTypeError,
    CorruptedFileError,
    PasswordProtectedError,
    FileNotFoundError,
    InvalidConfigurationError,
)
from .logging import setup_logger, logger
from .templates import TemplateProcessor, TEMPLATE_EXAMPLES

__all__ = [
    "DocumentParsingError",
    "UnsupportedFileTypeError",
    "CorruptedFileError",
    "PasswordProtectedError",
    "FileNotFoundError",
    "InvalidConfigurationError",
    "setup_logger",
    "logger",
    "TemplateProcessor",
    "TEMPLATE_EXAMPLES",
]
