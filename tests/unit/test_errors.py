import pytest

from ingenious.errors.content_filter_error import ContentFilterError
from ingenious.errors.token_limit_exceeded_error import TokenLimitExceededError


@pytest.mark.unit
class TestContentFilterError:
    """Test ContentFilterError exception class"""

    def test_content_filter_error_default_message(self):
        """Test ContentFilterError with default message"""
        error = ContentFilterError()

        assert str(error) == ContentFilterError.DEFAULT_MESSAGE
        assert error.message == ContentFilterError.DEFAULT_MESSAGE
        assert error.content_filter_results == {}

    def test_content_filter_error_custom_message(self):
        """Test ContentFilterError with custom message"""
        custom_message = "Custom content filter violation"
        error = ContentFilterError(message=custom_message)

        assert str(error) == custom_message
        assert error.message == custom_message
        assert error.content_filter_results == {}

    def test_content_filter_error_with_results(self):
        """Test ContentFilterError with content filter results"""
        custom_message = "Custom violation"
        filter_results = {
            "hate": {"filtered": True, "severity": "high"},
            "violence": {"filtered": False, "severity": "safe"},
        }
        error = ContentFilterError(
            message=custom_message, content_filter_results=filter_results
        )

        assert str(error) == custom_message
        assert error.message == custom_message
        assert error.content_filter_results == filter_results

    def test_content_filter_error_inheritance(self):
        """Test that ContentFilterError inherits from Exception"""
        error = ContentFilterError()
        assert isinstance(error, Exception)

    def test_content_filter_error_can_be_raised(self):
        """Test that ContentFilterError can be raised and caught"""
        with pytest.raises(ContentFilterError) as exc_info:
            raise ContentFilterError("Test message")

        assert str(exc_info.value) == "Test message"

    def test_content_filter_error_empty_results_dict(self):
        """Test ContentFilterError with explicitly empty results dict"""
        error = ContentFilterError(content_filter_results={})

        assert error.content_filter_results == {}


@pytest.mark.unit
class TestTokenLimitExceededError:
    """Test TokenLimitExceededError exception class"""

    def test_token_limit_exceeded_error_default_values(self):
        """Test TokenLimitExceededError with default values"""
        error = TokenLimitExceededError()

        assert str(error) == TokenLimitExceededError.DEFAULT_MESSAGE
        assert error.message == TokenLimitExceededError.DEFAULT_MESSAGE
        assert error.max_context_length == 0
        assert error.requested_tokens == 0
        assert error.prompt_tokens == 0
        assert error.completion_tokens == 0

    def test_token_limit_exceeded_error_custom_message(self):
        """Test TokenLimitExceededError with custom message"""
        custom_message = "Custom token limit exceeded"
        error = TokenLimitExceededError(message=custom_message)

        assert str(error) == custom_message
        assert error.message == custom_message

    def test_token_limit_exceeded_error_with_token_details(self):
        """Test TokenLimitExceededError with token details"""
        error = TokenLimitExceededError(
            message="Token limit exceeded",
            max_context_length=4096,
            requested_tokens=5000,
            prompt_tokens=4500,
            completion_tokens=500,
        )

        assert str(error) == "Token limit exceeded"
        assert error.message == "Token limit exceeded"
        assert error.max_context_length == 4096
        assert error.requested_tokens == 5000
        assert error.prompt_tokens == 4500
        assert error.completion_tokens == 500

    def test_token_limit_exceeded_error_inheritance(self):
        """Test that TokenLimitExceededError inherits from Exception"""
        error = TokenLimitExceededError()
        assert isinstance(error, Exception)

    def test_token_limit_exceeded_error_can_be_raised(self):
        """Test that TokenLimitExceededError can be raised and caught"""
        with pytest.raises(TokenLimitExceededError) as exc_info:
            raise TokenLimitExceededError("Test message")

        assert str(exc_info.value) == "Test message"

    def test_token_limit_exceeded_error_partial_token_info(self):
        """Test TokenLimitExceededError with partial token information"""
        error = TokenLimitExceededError(max_context_length=4096, requested_tokens=5000)

        assert error.max_context_length == 4096
        assert error.requested_tokens == 5000
        assert error.prompt_tokens == 0  # Default value
        assert error.completion_tokens == 0  # Default value

    def test_token_limit_exceeded_error_realistic_scenario(self):
        """Test TokenLimitExceededError with realistic token counts"""
        error = TokenLimitExceededError(
            message="This model's maximum context length is 4096 tokens, however you requested 4500 tokens (4000 in your prompt; 500 for the completion). Please reduce your prompt; or completion length.",
            max_context_length=4096,
            requested_tokens=4500,
            prompt_tokens=4000,
            completion_tokens=500,
        )

        assert error.max_context_length == 4096
        assert error.requested_tokens == 4500
        assert error.prompt_tokens == 4000
        assert error.completion_tokens == 500
        assert "4096 tokens" in error.message
