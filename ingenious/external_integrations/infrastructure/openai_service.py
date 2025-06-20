import logging
import re
from typing import Any, Dict, List, Optional

from openai import NOT_GIVEN, AzureOpenAI, BadRequestError
from openai.types.chat import (
    ChatCompletionMessage,
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
)

from ingenious.errors.content_filter_error import ContentFilterError
from ingenious.errors.token_limit_exceeded_error import TokenLimitExceededError

from ..domain.services import IContentModerationService, ILLMService

logger = logging.getLogger(__name__)


class AzureOpenAIService(ILLMService):
    """Azure OpenAI implementation of the LLM service."""

    def __init__(self, azure_endpoint: str, api_key: str, api_version: str, model: str):
        self.client = AzureOpenAI(
            azure_endpoint=azure_endpoint, api_key=api_key, api_version=api_version
        )
        self.model = model

    async def generate_response(
        self,
        messages: List[ChatCompletionMessageParam],
        tools: Optional[List[ChatCompletionToolParam]] = None,
        tool_choice: Optional[str | Dict] = None,
        json_mode: bool = False,
        **kwargs,
    ) -> ChatCompletionMessage:
        """Generate a response using Azure OpenAI."""
        logger.debug(f"Generating OpenAI response for messages: {messages}")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools or NOT_GIVEN,
                tool_choice=tool_choice or ("auto" if tools else NOT_GIVEN),
                response_format={"type": "json_object"} if json_mode else NOT_GIVEN,
                temperature=kwargs.get("temperature", 0.2),
            )
            return response.choices[0].message

        except BadRequestError as error:
            logger.exception(error)
            message = error.message

            # Check if the body is a dictionary and refine the message if possible
            if isinstance(error.body, dict):
                message = error.body.get("message", message)

                # Check for content filter specific errors
                if error.code == "content_filter" and "innererror" in error.body:
                    content_filter_results = error.body["innererror"].get(
                        "content_filter_result", {}
                    )
                    raise ContentFilterError(message, content_filter_results)

                # Check for token limit errors
                token_error_pattern = (
                    r"This model's maximum context length is (\d+) tokens, "
                    r"however you requested (\d+) tokens \((\d+) in your prompt; "
                    r"(\d+) for the completion\). Please reduce your prompt; or "
                    r"completion length."
                )
                token_error_match = re.match(token_error_pattern, message)
                if token_error_match:
                    (
                        max_context_length,
                        requested_tokens,
                        prompt_tokens,
                        completion_tokens,
                    ) = token_error_match.groups()
                    raise TokenLimitExceededError(
                        message=message,
                        max_context_length=int(max_context_length),
                        requested_tokens=int(requested_tokens),
                        prompt_tokens=int(prompt_tokens),
                        completion_tokens=int(completion_tokens),
                    )

            raise Exception(message)
        except Exception as e:
            logger.exception(e)
            raise

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings for text using Azure OpenAI."""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",  # Default embedding model
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.exception(e)
            raise


class OpenAIContentModerationService(IContentModerationService):
    """OpenAI-based content moderation service."""

    def __init__(self, client: AzureOpenAI):
        self.client = client

    async def moderate_content(self, content: str) -> Dict[str, Any]:
        """Moderate content using OpenAI's moderation API."""
        try:
            response = self.client.moderations.create(input=content)
            return {
                "flagged": response.results[0].flagged,
                "categories": response.results[0].categories.model_dump(),
                "category_scores": response.results[0].category_scores.model_dump(),
            }
        except Exception as e:
            logger.exception(e)
            return {"flagged": False, "error": str(e)}


# Legacy alias for backward compatibility
OpenAIService = AzureOpenAIService
