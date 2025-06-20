"""
Unit tests for chat domain models.

This module tests the Pydantic models used for chat request/response handling.
"""

import pytest
from pydantic import ValidationError

from ingenious.chat.domain.models import (
    ChatRequest,
    ChatResponse,
    MessageFeedbackRequest,
    MessageFeedbackResponse,
)


class TestChatRequest:
    """Test suite for ChatRequest model."""

    def test_chat_request_valid_data(self):
        """Test creating a ChatRequest with valid data."""
        # Arrange
        data = {
            "user_prompt": "Hello, how are you?",
            "conversation_flow": "general",
            "user_id": "user-123",
            "thread_id": "thread-456",
        }

        # Act
        request = ChatRequest(**data)

        # Assert
        assert request.user_prompt == "Hello, how are you?"
        assert request.conversation_flow == "general"
        assert request.user_id == "user-123"
        assert request.thread_id == "thread-456"
        assert request.memory_record is True  # Default value
        assert request.thread_chat_history == {}  # Default value

    def test_chat_request_minimal_data(self):
        """Test creating a ChatRequest with minimal required data."""
        # Arrange
        data = {"user_prompt": "Hello!", "conversation_flow": "general"}

        # Act
        request = ChatRequest(**data)

        # Assert
        assert request.user_prompt == "Hello!"
        assert request.conversation_flow == "general"
        assert request.thread_id is None
        assert request.user_id is None
        assert request.user_name is None
        assert request.topic is None
        assert request.memory_record is True
        assert request.event_type is None
        assert request.thread_chat_history == {}
        assert request.thread_memory is None

    def test_chat_request_all_fields(self):
        """Test creating a ChatRequest with all fields populated."""
        # Arrange
        data = {
            "thread_id": "thread-123",
            "user_prompt": "What's the weather like?",
            "event_type": "user_question",
            "user_id": "user-456",
            "user_name": "John Doe",
            "topic": "Weather",
            "memory_record": False,
            "conversation_flow": "weather_assistant",
            "thread_chat_history": {"msg-1": "Previous message"},
            "thread_memory": "User asked about weather before",
        }

        # Act
        request = ChatRequest(**data)

        # Assert
        assert request.thread_id == "thread-123"
        assert request.user_prompt == "What's the weather like?"
        assert request.event_type == "user_question"
        assert request.user_id == "user-456"
        assert request.user_name == "John Doe"
        assert request.topic == "Weather"
        assert request.memory_record is False
        assert request.conversation_flow == "weather_assistant"
        assert request.thread_chat_history == {"msg-1": "Previous message"}
        assert request.thread_memory == "User asked about weather before"

    def test_chat_request_invalid_missing_user_prompt(self):
        """Test that ChatRequest validation fails when user_prompt is missing."""
        # Arrange
        data = {
            "conversation_flow": "general"
            # Missing user_prompt
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(**data)

        assert "user_prompt" in str(exc_info.value)

    def test_chat_request_invalid_missing_conversation_flow(self):
        """Test that ChatRequest validation fails when conversation_flow is missing."""
        # Arrange
        data = {
            "user_prompt": "Hello!"
            # Missing conversation_flow
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(**data)

        assert "conversation_flow" in str(exc_info.value)

    def test_chat_request_empty_user_prompt(self):
        """Test ChatRequest with empty user_prompt."""
        # Arrange
        data = {"user_prompt": "", "conversation_flow": "general"}

        # Act
        request = ChatRequest(**data)

        # Assert
        assert request.user_prompt == ""
        assert request.conversation_flow == "general"


class TestChatResponse:
    """Test suite for ChatResponse model."""

    def test_chat_response_minimal_data(self):
        """Test creating a ChatResponse with minimal data."""
        # Arrange
        data = {}

        # Act
        response = ChatResponse(**data)

        # Assert
        assert response.thread_id is None
        assert response.message_id is None
        assert response.agent_response is None
        assert response.followup_questions == {}
        assert response.token_count is None
        assert response.max_token_count is None
        assert response.topic is None
        assert response.memory_summary is None
        assert response.event_type is None

    def test_chat_response_full_data(self):
        """Test creating a ChatResponse with all fields populated."""
        # Arrange
        data = {
            "thread_id": "thread-123",
            "message_id": "msg-456",
            "agent_response": "I'm doing well, thank you for asking!",
            "followup_questions": {
                "q1": "How can I help you today?",
                "q2": "Is there anything specific you'd like to know?",
            },
            "token_count": 25,
            "max_token_count": 4000,
            "topic": "Greeting",
            "memory_summary": "User greeted the assistant",
            "event_type": "agent_response",
        }

        # Act
        response = ChatResponse(**data)

        # Assert
        assert response.thread_id == "thread-123"
        assert response.message_id == "msg-456"
        assert response.agent_response == "I'm doing well, thank you for asking!"
        assert response.followup_questions == {
            "q1": "How can I help you today?",
            "q2": "Is there anything specific you'd like to know?",
        }
        assert response.token_count == 25
        assert response.max_token_count == 4000
        assert response.topic == "Greeting"
        assert response.memory_summary == "User greeted the assistant"
        assert response.event_type == "agent_response"

    def test_chat_response_serialization(self):
        """Test ChatResponse serialization to dict."""
        # Arrange
        response = ChatResponse(
            thread_id="thread-123", agent_response="Hello!", token_count=10
        )

        # Act
        response_dict = response.model_dump()

        # Assert
        assert response_dict["thread_id"] == "thread-123"
        assert response_dict["agent_response"] == "Hello!"
        assert response_dict["token_count"] == 10
        assert "message_id" in response_dict
        assert "followup_questions" in response_dict


class TestMessageFeedbackRequest:
    """Test suite for MessageFeedbackRequest model."""

    def test_message_feedback_request_valid_data(self):
        """Test creating a MessageFeedbackRequest with valid data."""
        # Arrange
        data = {
            "feedback_type": "thumbs_up",
            "feedback_text": "Great response!",
            "user_id": "user-123",
        }

        # Act
        request = MessageFeedbackRequest(**data)

        # Assert
        assert request.feedback_type == "thumbs_up"
        assert request.feedback_text == "Great response!"
        assert request.user_id == "user-123"

    def test_message_feedback_request_minimal_data(self):
        """Test creating a MessageFeedbackRequest with minimal data."""
        # Arrange
        data = {"feedback_type": "thumbs_down"}

        # Act
        request = MessageFeedbackRequest(**data)

        # Assert
        assert request.feedback_type == "thumbs_down"
        assert request.feedback_text is None
        assert request.user_id is None

    def test_message_feedback_request_validation(self):
        """Test MessageFeedbackRequest validation."""
        # Arrange
        data = {}

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            MessageFeedbackRequest(**data)

        assert "feedback_type" in str(exc_info.value)


class TestMessageFeedbackResponse:
    """Test suite for MessageFeedbackResponse model."""

    def test_message_feedback_response_valid_data(self):
        """Test creating a MessageFeedbackResponse with valid data."""
        # Arrange
        data = {
            "feedback_id": "feedback-123",
            "message_id": "msg-456",
            "status": "recorded",
            "timestamp": "2023-01-01T12:00:00Z",
        }

        # Act
        response = MessageFeedbackResponse(**data)

        # Assert
        assert response.feedback_id == "feedback-123"
        assert response.message_id == "msg-456"
        assert response.status == "recorded"
        assert response.timestamp == "2023-01-01T12:00:00Z"

    def test_message_feedback_response_minimal_data(self):
        """Test creating a MessageFeedbackResponse with minimal data."""
        # Arrange
        data = {"status": "recorded"}

        # Act
        response = MessageFeedbackResponse(**data)

        # Assert
        assert response.status == "recorded"
        assert response.feedback_id is None
        assert response.message_id is None
        assert response.timestamp is None


@pytest.mark.unit
class TestChatModelsIntegration:
    """Integration tests for chat models working together."""

    def test_request_response_flow(self):
        """Test a typical request-response flow."""
        # Arrange
        request_data = {
            "user_prompt": "How can I reset my password?",
            "conversation_flow": "support",
            "user_id": "user-123",
            "thread_id": "thread-456",
        }

        # Act
        request = ChatRequest(**request_data)

        # Simulate processing and create response
        response = ChatResponse(
            thread_id=request.thread_id,
            agent_response="To reset your password, please visit the settings page.",
            token_count=15,
            event_type="agent_response",
            followup_questions={
                "q1": "Do you need help finding the settings page?",
                "q2": "Would you like me to guide you through the process?",
            },
        )

        # Assert
        assert response.thread_id == request.thread_id
        assert response.agent_response is not None
        assert response.token_count > 0
        assert len(response.followup_questions) == 2

    def test_feedback_flow(self):
        """Test the message feedback flow."""
        # Arrange
        feedback_request = MessageFeedbackRequest(
            feedback_type="thumbs_up", feedback_text="Very helpful!", user_id="user-123"
        )

        # Act
        feedback_response = MessageFeedbackResponse(
            feedback_id="fb-789",
            message_id="msg-456",
            status="recorded",
            timestamp="2023-01-01T12:00:00Z",
        )

        # Assert
        assert feedback_request.feedback_type == "thumbs_up"
        assert feedback_response.status == "recorded"
        assert feedback_response.feedback_id == "fb-789"

    def test_model_serialization_and_deserialization(self):
        """Test serializing and deserializing models."""
        # Arrange
        original_request = ChatRequest(
            user_prompt="Test message",
            conversation_flow="test",
            user_id="user-123",
            thread_chat_history={"prev": "Previous message"},
        )

        # Act
        # Serialize to dict
        request_dict = original_request.model_dump()

        # Deserialize from dict
        restored_request = ChatRequest(**request_dict)

        # Assert
        assert restored_request.user_prompt == original_request.user_prompt
        assert restored_request.conversation_flow == original_request.conversation_flow
        assert restored_request.user_id == original_request.user_id
        assert (
            restored_request.thread_chat_history == original_request.thread_chat_history
        )
        assert restored_request.memory_record == original_request.memory_record

    def test_model_validation_edge_cases(self):
        """Test model validation with edge cases."""
        # Test ChatRequest with very long user_prompt
        long_prompt = "A" * 10000
        request = ChatRequest(user_prompt=long_prompt, conversation_flow="test")
        assert len(request.user_prompt) == 10000

        # Test ChatResponse with very large token counts
        response = ChatResponse(token_count=999999, max_token_count=1000000)
        assert response.token_count == 999999
        assert response.max_token_count == 1000000

        # Test MessageFeedbackRequest with empty feedback_text
        feedback = MessageFeedbackRequest(feedback_type="neutral", feedback_text="")
        assert feedback.feedback_text == ""
