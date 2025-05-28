"""
Interface for AI service providers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from openai.types.chat import (
    ChatCompletionMessage,
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
)


class AIServiceInterface(ABC):
    """Interface for AI service provider implementations."""

    @abstractmethod
    async def generate_response(
        self,
        messages: List[ChatCompletionMessageParam],
        tools: Optional[List[ChatCompletionToolParam]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        json_mode: bool = False,
    ) -> ChatCompletionMessage:
        """
        Generate a response from an AI model.

        Args:
            messages: List of message objects to send to the model
            tools: Optional list of tools the model can use
            tool_choice: Optional specification of which tool the model should use
            json_mode: Whether to format the response as JSON

        Returns:
            The model's response message

        Raises:
            ContentFilterError: If the content violates content policies
            TokenLimitExceededError: If the request exceeds token limits
            Exception: For other errors
        """
        pass
