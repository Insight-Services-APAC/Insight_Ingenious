"""
Chat bounded context for the Ingenious application.

This module contains all chat-related functionality organized according to
Domain-Driven Design principles:

- domain: Core business logic and entities
- application: Use cases and application services
- infrastructure: External adapters and implementations
- interfaces: REST API controllers and web interfaces
"""

from .application.services import ChatApplicationService
from .domain.entities import ChatSession, Message, Thread
from .domain.models import ChatRequest, ChatResponse
from .infrastructure.services import (
    DefaultConversationService,
    ModernChatService,
)

__all__ = [
    "ChatRequest",
    "ChatResponse",
    "Message",
    "Thread",
    "ChatSession",
    "ChatApplicationService",
    "ModernChatService",
    "DefaultConversationService",
]
