class TokenLimitExceededError(Exception):
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
        self.message = message
        self.max_context_length = max_context_length
        self.requested_tokens = requested_tokens
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        super().__init__(self.message)
