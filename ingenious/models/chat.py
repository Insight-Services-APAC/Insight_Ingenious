# Legacy file - maintained for backward compatibility
# New implementation is in ingenious.chat.domain.models

from ingenious.chat.domain.models import (
    ChatRequest,
    ChatResponse,
    IChatRequest,
    IChatResponse,
)

# Re-export for backward compatibility
__all__ = [
    "ChatRequest",
    "ChatResponse",
    "IChatRequest",
    "IChatResponse",
]
