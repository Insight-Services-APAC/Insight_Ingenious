"""
Legacy compatibility layer for backward compatibility.

This module provides aliases and adapters for the old module structure
to ensure existing code continues to work during the migration period.
"""

# Chat models backward compatibility
from ingenious.chat.domain.models import (
    ChatRequest,
    ChatResponse,
    IChatRequest,
    IChatResponse,
    MessageFeedbackRequest,
    MessageFeedbackResponse,
)

# Configuration backward compatibility
from ingenious.config.config import Config, get_config

# External services backward compatibility
from ingenious.external_integrations.infrastructure.openai_service import (
    AzureOpenAIService,
    OpenAIService,
)

# Shared models backward compatibility
from ingenious.shared.domain.models import HTTPError

# Utils backward compatibility
from ingenious.shared.utils import import_class_with_fallback
from ingenious.utils.namespace_utils import import_module_with_fallback

# Re-export for backward compatibility
__all__ = [
    # Chat
    "ChatRequest",
    "ChatResponse",
    "IChatRequest",
    "IChatResponse",
    "MessageFeedbackRequest",
    "MessageFeedbackResponse",
    # Configuration
    "Config",
    "get_config",
    # External Services
    "OpenAIService",
    "AzureOpenAIService",
    # Shared Models
    "HTTPError",
    # Utils
    "import_class_with_fallback",
    "import_module_with_fallback",
]
