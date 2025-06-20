"""
Chat bounded context for the Ingenious application.

This module contains all chat-related functionality organized according to
Domain-Driven Design principles:

- domain: Core business logic and entities
- application: Use cases and application services
- infrastructure: External adapters and implementations
- interfaces: REST API controllers and web interfaces
"""

from .domain.models import ChatRequest, ChatResponse
from .domain.entities import Message, Thread, ChatSession
from .application.services import ChatApplicationService
from .infrastructure.services import (
    LegacyChatServiceAdapter,
    DefaultConversationService,
)
from .interfaces.rest_controllers import ChatController

__all__ = [
    "ChatRequest",
    "ChatResponse",
    "Message",
    "Thread",
    "ChatSession",
    "ChatApplicationService",
    "LegacyChatServiceAdapter",
    "DefaultConversationService",
    "ChatController",
]
