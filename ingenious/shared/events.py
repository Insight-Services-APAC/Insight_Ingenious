"""Domain events infrastructure."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4


class DomainEvent:
    """Base class for domain events."""

    def __init__(
        self,
        event_type: str,
        aggregate_id: str,
        data: Dict[str, Any] = None,
        event_id: str = None,
        occurred_at: datetime = None,
    ):
        self.event_id = event_id or str(uuid4())
        self.event_type = event_type
        self.aggregate_id = aggregate_id
        self.data = data or {}
        self.occurred_at = occurred_at or datetime.utcnow()

    def __eq__(self, other):
        if not isinstance(other, DomainEvent):
            return False
        return self.event_id == other.event_id


class DomainEventHandler(ABC):
    """Base class for domain event handlers."""

    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """Handle a domain event."""
        pass

    @property
    @abstractmethod
    def event_type(self) -> str:
        """The type of event this handler processes."""
        pass


class DomainEventDispatcher:
    """Dispatcher for domain events."""

    def __init__(self):
        self._handlers: Dict[str, List[DomainEventHandler]] = {}

    def register_handler(self, event_type: str, handler: DomainEventHandler) -> None:
        """Register an event handler for a specific event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def dispatch(self, event: DomainEvent) -> None:
        """Dispatch an event to all registered handlers."""
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            await handler.handle(event)


# Global event dispatcher instance
event_dispatcher = DomainEventDispatcher()
