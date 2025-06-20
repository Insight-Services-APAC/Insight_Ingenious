"""
Shared interfaces module.

This module exports the REST controllers for cross-cutting concerns.
"""

from .rest_controllers import EventsController

__all__ = [
    "EventsController",
]
