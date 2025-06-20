class ContentFilterError(Exception):
    """Exception raised when the user message violates the OpenAI content filter."""

    DEFAULT_MESSAGE = (
        "The users prompt violates the content filter, please start a new conversation."
    )

    def __init__(
        self, message=DEFAULT_MESSAGE, content_filter_results: dict[str, object] = {}
    ):
        self.message = message
        self.content_filter_results = content_filter_results
        super().__init__(self.message)
