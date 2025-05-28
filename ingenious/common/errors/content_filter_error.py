from ingenious.common.errors.base import IngeniousError

__all__ = ["ContentFilterError"]


class ContentFilterError(IngeniousError):
    """Exception raised when the user message violates the OpenAI content filter."""

    DEFAULT_MESSAGE = (
        "The users prompt violates the content filter, please start a new conversation."
    )

    def __init__(
        self, message=DEFAULT_MESSAGE, content_filter_results: dict[str, object] = {}
    ):
        details = {"content_filter_results": content_filter_results}
        super().__init__(
            message=message,
            status_code=406,  # Not Acceptable
            error_code="CONTENT_FILTER_ERROR",
            details=details,
        )
        self.content_filter_results = content_filter_results
