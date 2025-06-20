"""
HTTP error models for the shared domain.

This module contains common HTTP error response models used across
all bounded contexts in the API interfaces.
"""

from pydantic import BaseModel


class HTTPError(BaseModel):
    """Standard HTTP error response model."""

    detail: str
