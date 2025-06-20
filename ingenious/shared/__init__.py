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

from .exceptions import DomainException, ValidationException
from .events import DomainEvent, DomainEventHandler

__all__ = [
    "DomainException",
    "ValidationException",
    "DomainEvent",
    "DomainEventHandler",
]
