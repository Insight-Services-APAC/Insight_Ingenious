"""
Tests for chat model in ingenious.domain.model.chat.
"""

import datetime
import json
import uuid

import pytest
from pydantic import ValidationError

from ingenious.domain.model.chat import (
    ChatRequest,
    ChatResponse,
    Message,
    MessageFeedback,
    MessageRole,
)


class TestChatModels:
    """Test suite for chat models."""

    def test_message_creation(self):
        """Test creating a Message object."""
        # Create a message with all fields
        message_id = str(uuid.uuid4())
        thread_id = str(uuid.uuid4())
        created_at = datetime.datetime.now().isoformat()
        updated_at = datetime.datetime.now().isoformat()

        message = Message(
            id=message_id,
            role=MessageRole.USER,
            content="Hello, world!",
            thread_id=thread_id,
            created_at=created_at,
            updated_at=updated_at,
            user_id="test_user",
            metadata={"source": "test"},
            feedback={"positive": True},
            content_filter_results={"filtered": False},
        )

        # Verify the message
        assert message.id == message_id
        assert message.role == MessageRole.USER
        assert message.content == "Hello, world!"
        assert message.thread_id == thread_id
        assert message.created_at == created_at
        assert message.updated_at == updated_at
        assert message.user_id == "test_user"
        assert message.metadata == {"source": "test"}
        assert message.feedback == {"positive": True}
        assert message.content_filter_results == {"filtered": False}

        # Create a message with minimal fields (should auto-generate some fields)
        message = Message(
            id=str(uuid.uuid4()),
            role=MessageRole.ASSISTANT,
            content="I'm an AI assistant.",
            thread_id=thread_id,
            created_at=datetime.datetime.now().isoformat(),
            updated_at=datetime.datetime.now().isoformat(),
            user_id="test_user",
        )

        # Verify the message
        assert message.id is not None  # Should be auto-generated UUID
        assert message.role == MessageRole.ASSISTANT
        assert message.content == "I'm an AI assistant."
        assert message.thread_id == thread_id
        assert message.created_at is not None  # Should be auto-generated timestamp
        assert message.updated_at is not None  # Should be auto-generated timestamp

    def test_message_role_enum(self):
        """Test MessageRole enum values."""
        assert MessageRole.USER == "user"
        assert MessageRole.ASSISTANT == "assistant"
        assert MessageRole.SYSTEM == "system"
        assert MessageRole.FUNCTION == "function"
        assert MessageRole.TOOL == "tool"

    def test_message_validation(self):
        """Test Message validation."""
        thread_id = str(uuid.uuid4())

        # Test with invalid role
        with pytest.raises(ValidationError):
            Message(
                role="invalid_role",  # Invalid role
                content="Test content",
                thread_id=thread_id,
            )

        # Test with empty content
        with pytest.raises(ValidationError):
            Message(
                role=MessageRole.USER,
                content="",  # Empty content
                thread_id=thread_id,
            )

        # Test with invalid thread_id
        with pytest.raises(ValidationError):
            Message(
                role=MessageRole.USER,
                content="Test content",
                thread_id="not-a-uuid",  # Invalid UUID
            )

    def test_message_feedback(self):
        """Test MessageFeedback model."""
        # Create a feedback object
        feedback = MessageFeedback(
            message_id="msg_123",
            thread_id="thread_456",
            user_id="user_789",
            positive_feedback=True,
        )

        # Verify the feedback
        assert feedback.message_id == "msg_123"
        assert feedback.thread_id == "thread_456"
        assert feedback.positive_feedback is True

        # Test with None feedback value (should be valid)
        feedback = MessageFeedback(
            message_id="msg_123",
            thread_id="thread_456",
            positive_feedback=None,
        )

        assert feedback.positive_feedback is None

    def test_chat_request(self):
        """Test ChatRequest model."""
        # Create a simple chat request
        request = ChatRequest(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ],
            model="gpt-4o",
            user_id="test_user",
            thread_id="thread_123",
            user_prompt="Hello!",
            conversation_flow="default",
        )

        # Verify the request
        assert len(request.messages) == 2
        assert request.messages[0]["role"] == "system"
        assert request.messages[0]["content"] == "You are a helpful assistant."
        assert request.messages[1]["role"] == "user"
        assert request.messages[1]["content"] == "Hello!"
        assert request.model == "gpt-4o"
        assert request.user_id == "test_user"
        assert request.functions is None  # Default value
        assert request.function_call is None  # Default value

        # Create a more complex request with functions
        functions = [
            {
                "name": "get_weather",
                "description": "Get the weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to get weather for",
                        }
                    },
                    "required": ["location"],
                },
            }
        ]

        request = ChatRequest(
            messages=[
                {"role": "user", "content": "What's the weather in Seattle?"},
            ],
            model="gpt-4o",
            functions=functions,
            function_call="auto",
            user_id="test_user",
            user_prompt="What's the weather in Seattle?",
            conversation_flow="default",
            thread_id="thread_456",
        )

        # Verify the request
        assert len(request.messages) == 1
        assert request.functions == functions
        assert request.function_call == "auto"

    def test_chat_response(self):
        """Test ChatResponse model."""
        # Create a chat response
        response = ChatResponse(
            content="Hello! How can I help you today?",
            model="gpt-4o",
            prompt_tokens=10,
            completion_tokens=8,
            total_tokens=18,
            job_id="job_123",
            tools=[],
            thread_id="thread_123",
            message_id="msg_456",
            agent_response="Hello! How can I help you today?",
            token_count=18,
            max_token_count=32,
        )

        # Verify the response
        assert response.content == "Hello! How can I help you today?"
        assert response.model == "gpt-4o"
        assert response.prompt_tokens == 10
        assert response.completion_tokens == 8
        assert response.total_tokens == 18
        assert response.job_id == "job_123"
        assert response.tools == []

        # Test with function call
        function_call = {
            "name": "get_weather",
            "arguments": json.dumps({"location": "Seattle"}),
        }

        response = ChatResponse(
            content=None,  # Content can be None if there's a function call
            function_call=function_call,
            model="gpt-4o",
            prompt_tokens=15,
            completion_tokens=12,
            total_tokens=27,
            job_id="job_456",
            thread_id="thread_789",
            message_id="msg_789",
            agent_response=None,
            token_count=27,
            max_token_count=64,
            tools=[],
        )

        # Verify the response
        assert response.content is None
        assert response.function_call == function_call
        assert response.model == "gpt-4o"
