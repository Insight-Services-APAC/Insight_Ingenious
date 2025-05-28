"""
Factory for creating AI service implementations.
"""

from ingenious.domain.interfaces.service.ai_service import AIServiceInterface
from ingenious.presentation.infrastructure.external.openai_service import OpenAIService


class AIServiceFactory:
    """Factory for creating AI service implementations."""

    @staticmethod
    def create_openai_service(
        azure_endpoint: str, api_key: str, api_version: str, model: str
    ) -> AIServiceInterface:
        """
        Create an OpenAI service implementation.

        Args:
            azure_endpoint: The Azure OpenAI endpoint
            api_key: The API key
            api_version: The API version
            model: The model name

        Returns:
            An AI service implementation
        """
        return OpenAIService(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version=api_version,
            open_ai_model=model,
        )
