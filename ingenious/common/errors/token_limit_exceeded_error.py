from ingenious.common.errors.base import IngeniousError

__all__ = ["TokenLimitExceededError"]


class TokenLimitExceededError(IngeniousError):
    """Exception raised when the user has exceeded the OpenAI token limit."""

    DEFAULT_MESSAGE = (
        "This chat has exceeded the token limit, please start a new conversation."
    )

    def __init__(
        self,
        message=DEFAULT_MESSAGE,
        max_context_length: int = 0,
        requested_tokens: int = 0,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ):
        details = {
            "max_context_length": max_context_length,
            "requested_tokens": requested_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        }
        super().__init__(
            message=message,
            status_code=413,  # Payload Too Large
            error_code="TOKEN_LIMIT_EXCEEDED",
            details=details,
        )
        self.max_context_length = max_context_length
        self.requested_tokens = requested_tokens
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
