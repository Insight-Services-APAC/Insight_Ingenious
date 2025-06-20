"""
Unit tests for chat application services.

This module tests the application layer services that orchestrate chat operations.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from ingenious.chat.application.services import ChatApplicationService
from ingenious.chat.domain.models import ChatRequest, ChatResponse
from ingenious.chat.domain.services import IChatService


class TestChatApplicationService:
    """Test suite for ChatApplicationService."""

    @pytest.fixture
    def mock_chat_service(self):
        """Mock chat service for testing."""
        mock = AsyncMock(spec=IChatService)
        return mock

    @pytest.fixture
    def chat_app_service(self, mock_chat_service):
        """Create ChatApplicationService with mocked dependencies."""
        return ChatApplicationService(chat_service=mock_chat_service)

    @pytest.fixture
    def valid_chat_request(self):
        """Valid chat request for testing."""
        return ChatRequest(
            user_prompt="Hello, how are you?",
            conversation_flow="general",
            user_id="user-123",
            thread_id="thread-456",
        )

    @pytest.fixture
    def mock_chat_response(self):
        """Mock chat response for testing."""
        return ChatResponse(
            thread_id="thread-456",
            message_id="msg-789",
            agent_response="I'm doing well, thank you!",
            token_count=20,
            event_type="agent_response",
        )

    async def test_process_chat_success(
        self,
        chat_app_service,
        mock_chat_service,
        valid_chat_request,
        mock_chat_response,
    ):
        """Test successful chat processing."""
        # Arrange
        mock_chat_service.process_chat_request.return_value = mock_chat_response

        # Act
        result = await chat_app_service.process_chat(valid_chat_request)

        # Assert
        assert result == mock_chat_response
        mock_chat_service.process_chat_request.assert_called_once_with(
            valid_chat_request
        )

    async def test_process_chat_validation_missing_user_prompt(self, chat_app_service):
        """Test chat processing with missing user prompt."""
        # Arrange
        invalid_request = ChatRequest(
            user_prompt="",  # Empty prompt
            conversation_flow="general",
        )

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await chat_app_service.process_chat(invalid_request)

        assert "User prompt is required" in str(exc_info.value)

    async def test_process_chat_validation_missing_conversation_flow(
        self, chat_app_service
    ):
        """Test chat processing with missing conversation flow."""
        # Arrange
        invalid_request = ChatRequest(
            user_prompt="Hello!",
            conversation_flow="",  # Empty conversation flow
        )

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await chat_app_service.process_chat(invalid_request)

        assert "Conversation flow is required" in str(exc_info.value)

    async def test_process_chat_domain_service_exception(
        self, chat_app_service, mock_chat_service, valid_chat_request
    ):
        """Test chat processing when domain service raises an exception."""
        # Arrange
        mock_chat_service.process_chat_request.side_effect = Exception("Service error")

        # Act
        result = await chat_app_service.process_chat(valid_chat_request)

        # Assert
        assert result is not None
        assert result.thread_id == valid_chat_request.thread_id
        assert "error" in result.agent_response.lower()
        assert result.event_type == "error"

    async def test_process_chat_specific_llm_exception(
        self, chat_app_service, mock_chat_service, valid_chat_request
    ):
        """Test chat processing with specific LLM service exceptions."""
        # Arrange
        from ingenious.external_integrations.domain.errors import (
            TokenLimitExceededError,
        )

        mock_chat_service.process_chat_request.side_effect = TokenLimitExceededError(
            "Token limit exceeded"
        )

        # Act
        result = await chat_app_service.process_chat(valid_chat_request)

        # Assert
        assert result is not None
        assert result.event_type == "error"
        assert "error" in result.agent_response.lower()

    def test_validate_chat_request_valid(self, chat_app_service, valid_chat_request):
        """Test validation of a valid chat request."""
        # Act & Assert - Should not raise any exception
        chat_app_service._validate_chat_request(valid_chat_request)

    def test_validate_chat_request_empty_prompt(self, chat_app_service):
        """Test validation with empty user prompt."""
        # Arrange
        request = ChatRequest(user_prompt="", conversation_flow="general")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            chat_app_service._validate_chat_request(request)

        assert "User prompt is required" in str(exc_info.value)

    def test_validate_chat_request_none_prompt(self, chat_app_service):
        """Test validation with None user prompt."""
        # Arrange
        request = Mock()
        request.user_prompt = None
        request.conversation_flow = "general"

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            chat_app_service._validate_chat_request(request)

        assert "User prompt is required" in str(exc_info.value)

    def test_validate_chat_request_empty_conversation_flow(self, chat_app_service):
        """Test validation with empty conversation flow."""
        # Arrange
        request = ChatRequest(user_prompt="Hello!", conversation_flow="")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            chat_app_service._validate_chat_request(request)

        assert "Conversation flow is required" in str(exc_info.value)

    def test_enhance_response_basic(self, chat_app_service, mock_chat_response):
        """Test basic response enhancement."""
        # Act
        enhanced_response = chat_app_service._enhance_response(mock_chat_response)

        # Assert
        assert (
            enhanced_response == mock_chat_response
        )  # Currently just returns the same response

    def test_enhance_response_with_modifications(self, chat_app_service):
        """Test response enhancement with potential modifications."""
        # Arrange
        response = ChatResponse(agent_response="Simple response", token_count=5)

        # Act
        enhanced_response = chat_app_service._enhance_response(response)

        # Assert
        assert enhanced_response.agent_response == "Simple response"
        assert enhanced_response.token_count == 5

    def test_handle_error_with_exception(self, chat_app_service, valid_chat_request):
        """Test error handling with a generic exception."""
        # Arrange
        error = Exception("Test error")

        # Act
        error_response = chat_app_service._handle_error(error, valid_chat_request)

        # Assert
        assert error_response.thread_id == valid_chat_request.thread_id
        assert "error" in error_response.agent_response.lower()
        assert error_response.event_type == "error"

    def test_handle_error_with_specific_error_type(
        self, chat_app_service, valid_chat_request
    ):
        """Test error handling with specific error types."""
        # Arrange
        error = ValueError("Invalid input")

        # Act
        error_response = chat_app_service._handle_error(error, valid_chat_request)

        # Assert
        assert error_response.thread_id == valid_chat_request.thread_id
        assert error_response.event_type == "error"
        assert "error" in error_response.agent_response.lower()

    async def test_process_chat_end_to_end_success(
        self, chat_app_service, mock_chat_service, valid_chat_request
    ):
        """Test end-to-end successful chat processing."""
        # Arrange
        expected_response = ChatResponse(
            thread_id=valid_chat_request.thread_id,
            agent_response="Complete response",
            token_count=30,
            event_type="agent_response",
        )
        mock_chat_service.process_chat_request.return_value = expected_response

        # Act
        result = await chat_app_service.process_chat(valid_chat_request)

        # Assert
        assert result.thread_id == valid_chat_request.thread_id
        assert result.agent_response == "Complete response"
        assert result.token_count == 30
        assert result.event_type == "agent_response"

        # Verify the domain service was called correctly
        mock_chat_service.process_chat_request.assert_called_once_with(
            valid_chat_request
        )

    async def test_process_chat_with_long_prompt(
        self, chat_app_service, mock_chat_service, mock_chat_response
    ):
        """Test chat processing with a very long prompt."""
        # Arrange
        long_prompt = "A" * 5000
        request = ChatRequest(user_prompt=long_prompt, conversation_flow="general")
        mock_chat_service.process_chat_request.return_value = mock_chat_response

        # Act
        result = await chat_app_service.process_chat(request)

        # Assert
        assert result == mock_chat_response
        mock_chat_service.process_chat_request.assert_called_once_with(request)

    async def test_process_chat_with_special_characters(
        self, chat_app_service, mock_chat_service, mock_chat_response
    ):
        """Test chat processing with special characters in prompt."""
        # Arrange
        request = ChatRequest(
            user_prompt="Hello! @#$%^&*()_+ 🚀 ñáéíóú", conversation_flow="general"
        )
        mock_chat_service.process_chat_request.return_value = mock_chat_response

        # Act
        result = await chat_app_service.process_chat(request)

        # Assert
        assert result == mock_chat_response
        mock_chat_service.process_chat_request.assert_called_once_with(request)


@pytest.mark.unit
class TestChatApplicationServiceIntegration:
    """Integration tests for ChatApplicationService with realistic scenarios."""

    @pytest.fixture
    def realistic_chat_service(self):
        """A more realistic mock chat service."""
        mock = AsyncMock(spec=IChatService)

        async def process_request(request):
            # Simulate realistic processing
            if "error" in request.user_prompt.lower():
                raise Exception("Simulated processing error")

            return ChatResponse(
                thread_id=request.thread_id or "auto-generated-thread",
                message_id="msg-" + str(hash(request.user_prompt))[-6:],
                agent_response=f"Response to: {request.user_prompt[:50]}...",
                token_count=len(request.user_prompt.split()) + 10,
                event_type="agent_response",
            )

        mock.process_chat_request.side_effect = process_request
        return mock

    async def test_realistic_conversation_flow(self, realistic_chat_service):
        """Test a realistic conversation flow."""
        # Arrange
        app_service = ChatApplicationService(chat_service=realistic_chat_service)

        # Act - Multiple messages in conversation
        request1 = ChatRequest(
            user_prompt="Hello, I need help with my account",
            conversation_flow="support",
            user_id="user-123",
        )
        response1 = await app_service.process_chat(request1)

        request2 = ChatRequest(
            user_prompt="I can't log in to my account",
            conversation_flow="support",
            user_id="user-123",
            thread_id=response1.thread_id,
        )
        response2 = await app_service.process_chat(request2)

        # Assert
        assert response1.thread_id is not None
        assert response2.thread_id == response1.thread_id
        assert "Response to: Hello, I need help" in response1.agent_response
        assert "Response to: I can't log in" in response2.agent_response
        assert response1.token_count > 0
        assert response2.token_count > 0

    async def test_error_recovery_flow(self, realistic_chat_service):
        """Test error recovery in conversation flow."""
        # Arrange
        app_service = ChatApplicationService(chat_service=realistic_chat_service)

        # Act - First request causes error, second succeeds
        error_request = ChatRequest(
            user_prompt="This will cause an error in processing",
            conversation_flow="general",
            user_id="user-123",
        )
        error_response = await app_service.process_chat(error_request)

        success_request = ChatRequest(
            user_prompt="This should work fine",
            conversation_flow="general",
            user_id="user-123",
        )
        success_response = await app_service.process_chat(success_request)

        # Assert
        assert error_response.event_type == "error"
        assert "error" in error_response.agent_response.lower()

        assert success_response.event_type == "agent_response"
        assert "Response to: This should work fine" in success_response.agent_response
