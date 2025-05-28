"""
Additional chat models.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Protocol

from pydantic import BaseModel


class LLMType(str, Enum):
    """LLM Type."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    MOCK = "mock"


class ChatFunction(BaseModel):
    """Chat function model."""

    name: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class ChatFunctionCall(BaseModel):
    """Chat function call model."""

    name: str
    arguments: str


class IChatLogger(Protocol):
    """Chat logger interface."""

    def log_request(self, request: Any) -> None:
        """Log request."""
        ...

    def log_response(self, response: Any) -> None:
        """Log response."""
        ...


class IChatProvider(Protocol):
    """Chat provider interface."""

    async def generate_chat_completion(self, messages: List[Any], **kwargs) -> Any:
        """Generate chat completion."""
        ...


class ChatMessage(BaseModel):
    """Chat message model."""

    role: str
    content: Optional[str] = None
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
