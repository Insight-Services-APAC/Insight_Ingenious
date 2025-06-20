"""
Shared Kernel - Common utilities and cross-cutting concerns

This module contains shared functionality that can be used across
all bounded contexts:

- Common value objects
- Base entities and aggregates
- Shared exceptions
- Cross-cutting utilities
- Domain events infrastructure
"""

from .events import DomainEvent, DomainEventHandler
from .exceptions import DomainException, ValidationException
from .interfaces.rest_controllers import EventsController

__all__ = [
    "DomainException",
    "ValidationException",
    "DomainEvent",
    "DomainEventHandler",
    "EventsController",
]
