from datetime import datetime

import pytest
from pydantic import ValidationError

from ingenious.models.message import Message
from ingenious.models.message_feedback import (
    MessageFeedbackRequest,
    MessageFeedbackResponse,
)


@pytest.mark.unit
class TestMessage:
    """Test Message model"""

    def test_message_required_fields(self):
        """Test Message model with required fields only"""
        message = Message(user_id="user123", thread_id="thread456", role="user")

        assert message.user_id == "user123"
        assert message.thread_id == "thread456"
        assert message.role == "user"
        assert message.message_id is None
        assert message.positive_feedback is None
        assert message.timestamp is None
        assert message.content is None
        assert message.content_filter_results is None
        assert message.tool_calls is None
        assert message.tool_call_id is None
        assert message.tool_call_function is None

    def test_message_all_fields(self):
        """Test Message model with all fields"""
        timestamp = datetime.now()
        content_filter_results = {"hate": {"filtered": False}}
        tool_calls = [{"id": "call1", "function": {"name": "test"}}]
        tool_call_function = {"name": "test_function", "arguments": "{}"}

        message = Message(
            user_id="user123",
            thread_id="thread456",
            message_id="msg789",
            positive_feedback=True,
            timestamp=timestamp,
            role="assistant",
            content="Hello, how can I help you?",
            content_filter_results=content_filter_results,
            tool_calls=tool_calls,
            tool_call_id="call1",
            tool_call_function=tool_call_function,
        )

        assert message.user_id == "user123"
        assert message.thread_id == "thread456"
        assert message.message_id == "msg789"
        assert message.positive_feedback is True
        assert message.timestamp == timestamp
        assert message.role == "assistant"
        assert message.content == "Hello, how can I help you?"
        assert message.content_filter_results == content_filter_results
        assert message.tool_calls == tool_calls
        assert message.tool_call_id == "call1"
        assert message.tool_call_function == tool_call_function

    def test_message_missing_required_field(self):
        """Test Message model validation with missing required field"""
        with pytest.raises(ValidationError) as exc_info:
            Message(user_id="user123", role="user")  # Missing thread_id

        assert "thread_id" in str(exc_info.value)

    def test_message_serialization(self):
        """Test Message model serialization"""
        message = Message(
            user_id="user123",
            thread_id="thread456",
            role="user",
            content="Test message",
        )

        data = message.model_dump()

        assert data["user_id"] == "user123"
        assert data["thread_id"] == "thread456"
        assert data["role"] == "user"
        assert data["content"] == "Test message"

    def test_message_deserialization(self):
        """Test Message model deserialization"""
        data = {
            "user_id": "user123",
            "thread_id": "thread456",
            "role": "user",
            "content": "Test message",
        }

        message = Message(**data)

        assert message.user_id == "user123"
        assert message.thread_id == "thread456"
        assert message.role == "user"
        assert message.content == "Test message"

    def test_message_optional_user_id(self):
        """Test Message model with optional user_id as None"""
        message = Message(user_id=None, thread_id="thread456", role="user")

        assert message.user_id is None
        assert message.thread_id == "thread456"
        assert message.role == "user"

    def test_message_different_roles(self):
        """Test Message model with different roles"""
        roles = ["user", "assistant", "system", "tool"]

        for role in roles:
            message = Message(user_id="user123", thread_id="thread456", role=role)
            assert message.role == role

    def test_message_complex_tool_calls(self):
        """Test Message model with complex tool calls"""
        complex_tool_calls = [
            {
                "id": "call_1",
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"location": "New York"}',
                },
            },
            {
                "id": "call_2",
                "type": "function",
                "function": {
                    "name": "calculate",
                    "arguments": '{"expression": "2 + 2"}',
                },
            },
        ]

        message = Message(
            user_id="user123",
            thread_id="thread456",
            role="assistant",
            tool_calls=complex_tool_calls,
        )

        assert message.tool_calls == complex_tool_calls
        assert len(message.tool_calls) == 2


@pytest.mark.unit
class TestMessageFeedbackRequest:
    """Test MessageFeedbackRequest model"""

    def test_message_feedback_request_required_fields(self):
        """Test MessageFeedbackRequest with required fields only"""
        request = MessageFeedbackRequest(thread_id="thread456", message_id="msg789")

        assert request.thread_id == "thread456"
        assert request.message_id == "msg789"
        assert request.user_id is None
        assert request.positive_feedback is None

    def test_message_feedback_request_all_fields(self):
        """Test MessageFeedbackRequest with all fields"""
        request = MessageFeedbackRequest(
            thread_id="thread456",
            message_id="msg789",
            user_id="user123",
            positive_feedback=True,
        )

        assert request.thread_id == "thread456"
        assert request.message_id == "msg789"
        assert request.user_id == "user123"
        assert request.positive_feedback is True

    def test_message_feedback_request_negative_feedback(self):
        """Test MessageFeedbackRequest with negative feedback"""
        request = MessageFeedbackRequest(
            thread_id="thread456", message_id="msg789", positive_feedback=False
        )

        assert request.positive_feedback is False

    def test_message_feedback_request_missing_required_field(self):
        """Test MessageFeedbackRequest validation with missing required field"""
        with pytest.raises(ValidationError) as exc_info:
            MessageFeedbackRequest(thread_id="thread456")  # Missing message_id

        assert "message_id" in str(exc_info.value)

    def test_message_feedback_request_serialization(self):
        """Test MessageFeedbackRequest serialization"""
        request = MessageFeedbackRequest(
            thread_id="thread456",
            message_id="msg789",
            user_id="user123",
            positive_feedback=True,
        )

        data = request.model_dump()

        assert data["thread_id"] == "thread456"
        assert data["message_id"] == "msg789"
        assert data["user_id"] == "user123"
        assert data["positive_feedback"] is True

    def test_message_feedback_request_deserialization(self):
        """Test MessageFeedbackRequest deserialization"""
        data = {
            "thread_id": "thread456",
            "message_id": "msg789",
            "user_id": "user123",
            "positive_feedback": True,
        }

        request = MessageFeedbackRequest(**data)

        assert request.thread_id == "thread456"
        assert request.message_id == "msg789"
        assert request.user_id == "user123"
        assert request.positive_feedback is True


@pytest.mark.unit
class TestMessageFeedbackResponse:
    """Test MessageFeedbackResponse model"""

    def test_message_feedback_response_creation(self):
        """Test MessageFeedbackResponse creation"""
        response = MessageFeedbackResponse(message="Feedback received successfully")

        assert response.message == "Feedback received successfully"

    def test_message_feedback_response_missing_message(self):
        """Test MessageFeedbackResponse validation with missing message"""
        with pytest.raises(ValidationError) as exc_info:
            MessageFeedbackResponse()  # Missing message

        assert "message" in str(exc_info.value)

    def test_message_feedback_response_empty_message(self):
        """Test MessageFeedbackResponse with empty message"""
        response = MessageFeedbackResponse(message="")

        assert response.message == ""

    def test_message_feedback_response_serialization(self):
        """Test MessageFeedbackResponse serialization"""
        response = MessageFeedbackResponse(message="Success")

        data = response.model_dump()

        assert data["message"] == "Success"

    def test_message_feedback_response_deserialization(self):
        """Test MessageFeedbackResponse deserialization"""
        data = {"message": "Success"}

        response = MessageFeedbackResponse(**data)

        assert response.message == "Success"

    def test_message_feedback_response_long_message(self):
        """Test MessageFeedbackResponse with long message"""
        long_message = "This is a very long message that contains a lot of text and should still be handled properly by the MessageFeedbackResponse model without any issues."
        response = MessageFeedbackResponse(message=long_message)

        assert response.message == long_message

    def test_message_feedback_response_special_characters(self):
        """Test MessageFeedbackResponse with special characters"""
        special_message = (
            "Message with special characters: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        )
        response = MessageFeedbackResponse(message=special_message)

        assert response.message == special_message
