import logging
import re
from ingenious.errors.content_filter_error import ContentFilterError
from ingenious.errors.token_limit_exceeded_error import TokenLimitExceededError
from openai import AzureOpenAI, NOT_GIVEN, BadRequestError
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
    ChatCompletionMessage
)

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(
        self,
        azure_endpoint: str,
        api_key: str,
        api_version: str,
        open_ai_model: str
    ):
        self.client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version=api_version
        )
        self.model = open_ai_model

    async def generate_response(self,
                                messages: list[ChatCompletionMessageParam],
                                tools: list[ChatCompletionToolParam] | None = None,
                                json_mode=False) -> ChatCompletionMessage:
        logger.debug(f"Generating OpenAI response for messages: {messages}")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools or NOT_GIVEN,
                tool_choice="auto" if tools else NOT_GIVEN,
                response_format={"type": "json_object"} if json_mode else NOT_GIVEN,
            )
            return response.choices[0].message
        except BadRequestError as error:
            # Log the error
            logger.exception(error)

            # Default to the general message from the exception
            message = error.message

            # Check if the body is a dictionary and refine the message if possible
            if isinstance(error.body, dict):
                message = error.body.get("message", message)

                # Check for content filter specific errors
                if error.code == "content_filter" and "innererror" in error.body:
                    content_filter_results = error.body["innererror"].get("content_filter_result", {})
                    raise ContentFilterError(message, content_filter_results)

                # Check for token limit errors
                token_error_pattern = r"This model's maximum context length is (\d+) tokens, however you requested (\d+) tokens \((\d+) in your prompt; (\d+) for the completion\). Please reduce your prompt; or completion length."  # noqa E501
                token_error_match = re.match(token_error_pattern, message)
                if token_error_match:
                    max_context_length, requested_tokens, prompt_tokens, completion_tokens = token_error_match.groups()
                    raise TokenLimitExceededError(
                        message=message, max_context_length=int(max_context_length),
                        requested_tokens=int(requested_tokens),
                        prompt_tokens=int(prompt_tokens),
                        completion_tokens=int(completion_tokens))

            raise Exception(message)
        except Exception as e:
            logger.exception(e)
            raise