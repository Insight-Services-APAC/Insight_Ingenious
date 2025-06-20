"""
Shared domain layer initialization.

This module exports shared domain models and entities used across
multiple bounded contexts.
"""

from .models import HTTPError

__all__ = [
    "HTTPError",
]
