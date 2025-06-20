from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from openai.types.chat import (
    ChatCompletionMessage,
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
)


class ILLMService(ABC):
    """Domain service interface for Language Model operations."""

    @abstractmethod
    async def generate_response(
        self,
        messages: List[ChatCompletionMessageParam],
        tools: Optional[List[ChatCompletionToolParam]] = None,
        tool_choice: Optional[str | Dict] = None,
        json_mode: bool = False,
        **kwargs,
    ) -> ChatCompletionMessage:
        """Generate a response from the language model."""
        pass

    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings for text."""
        pass


class IContentModerationService(ABC):
    """Domain service interface for content moderation."""

    @abstractmethod
    async def moderate_content(self, content: str) -> Dict[str, Any]:
        """Moderate content and return safety analysis."""
        pass


class IExternalServiceRegistry(ABC):
    """Registry for managing external service configurations."""

    @abstractmethod
    def register_service(
        self, service_name: str, service_config: Dict[str, Any]
    ) -> None:
        """Register an external service configuration."""
        pass

    @abstractmethod
    def get_service_config(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a service."""
        pass
