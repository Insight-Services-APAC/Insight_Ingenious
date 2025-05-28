"""
Integration tests for the chat service.
"""

import json
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from ingenious.application.service.chat_service import ChatService
from ingenious.domain.model.chat import (
    ChatRequest,
    ChatResponse,
    Message,
    MessageRole,
)
from ingenious.domain.model.config import Config


@pytest.fixture
def mock_openai_service():
    """Create a mock OpenAI service."""
    mock_service = AsyncMock()
    # Provide all required fields for ChatResponse
    mock_service.generate_chat_completion.return_value = ChatResponse(
        content="This is a test response",
        model="gpt-4o",
        prompt_tokens=10,
        completion_tokens=5,
        total_tokens=15,
        job_id=str(uuid.uuid4()),
        thread_id=str(uuid.uuid4()),
        message_id=str(uuid.uuid4()),
        agent_response="This is a test response",
        token_count=15,
        max_token_count=32,
    )
    return mock_service


@pytest.fixture
def mock_chat_history_repo(mock_openai_service):
    """Create a mock chat history repository and attach openai_service for injection."""
    mock_repo = AsyncMock()
    mock_repo.add_message.return_value = "message_id"
    mock_repo.get_thread_messages.return_value = []
    mock_repo.openai_service = mock_openai_service
    return mock_repo


@pytest.fixture
def mock_config():
    """Create a mock config."""
    mock_config = MagicMock(spec=Config)
    mock_config.chat_service = MagicMock()
    mock_config.chat_service.type = "basic"
    # Add web_configuration with port attribute for config tests
    mock_web_config = MagicMock()
    mock_web_config.port = 8000
    mock_web_config.authentication = MagicMock()
    mock_web_config.authentication.username = "test_user"
    mock_web_config.authentication.password = "test_password"
    mock_config.web_configuration = mock_web_config
    return mock_config


@pytest.mark.asyncio
class TestChatService:
    """Integration tests for ChatService."""

    async def test_process_chat_request(
        self, mock_openai_service, mock_chat_history_repo, mock_config
    ):
        """Test processing a chat request."""
        # Create the chat service
        chat_service = ChatService(
            chat_service_type="basic",
            chat_history_repository=mock_chat_history_repo,
            conversation_flow="default",
            config=mock_config,
        )

        # Create a test request
        request = ChatRequest(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, how are you?"},
            ],
            model="gpt-4o",
            user_id="test_user",
            thread_id=str(uuid.uuid4()),
            user_prompt="Hello, how are you?",
            conversation_flow="default",
        )

        # Patch the mock_openai_service to return a valid ChatResponse
        mock_openai_service.generate_chat_completion.return_value = ChatResponse(
            content="This is a test response",
            model="gpt-4o",
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
            job_id=str(uuid.uuid4()),
            thread_id=request.thread_id,
            message_id=str(uuid.uuid4()),
            agent_response="This is a test response",
            token_count=15,
            max_token_count=32,
        )

        # Process the request
        response = await chat_service.process_chat_request(request)

        # Verify the response
        assert response.content == "This is a test response"
        assert response.model == "gpt-4o"
        assert response.total_tokens == 15

        # Verify the OpenAI service was called
        mock_openai_service.generate_chat_completion.assert_called_once()

        # Verify messages were saved to chat history
        assert (
            mock_chat_history_repo.add_message.call_count == 2
        )  # User message and assistant response

    async def test_process_chat_request_with_history(
        self, mock_openai_service, mock_chat_history_repo, mock_config
    ):
        """Test processing a chat request with existing history."""
        # Set up previous messages in the chat history
        previous_messages = [
            Message(
                id="msg1",
                role=MessageRole.SYSTEM.value,
                content="You are a helpful assistant.",
                thread_id="thread_123",
                created_at="2023-01-01T00:00:00Z",
                updated_at="2023-01-01T00:00:00Z",
            ),
            Message(
                id="msg2",
                role=MessageRole.USER.value,
                content="What is the capital of France?",
                thread_id="thread_123",
                created_at="2023-01-01T00:01:00Z",
                updated_at="2023-01-01T00:01:00Z",
            ),
            Message(
                id="msg3",
                role=MessageRole.ASSISTANT.value,
                content="The capital of France is Paris.",
                thread_id="thread_123",
                created_at="2023-01-01T00:02:00Z",
                updated_at="2023-01-01T00:02:00Z",
            ),
        ]
        mock_chat_history_repo.get_thread_messages.return_value = previous_messages

        # Create the chat service
        chat_service = ChatService(
            chat_service_type="basic",
            chat_history_repository=mock_chat_history_repo,
            conversation_flow="default",
            config=mock_config,
        )

        # Create a test request with the same thread ID
        request = ChatRequest(
            messages=[
                {"role": "user", "content": "And what is the capital of Germany?"}
            ],
            model="gpt-4o",
            user_id="test_user",
            thread_id="thread_123",
            user_prompt="And what is the capital of Germany?",
            conversation_flow="default",
        )

        # Patch the mock_openai_service to return a valid ChatResponse
        thread_id = str(uuid.uuid4())
        mock_openai_service.generate_chat_completion.return_value = ChatResponse(
            content="This is a test response",
            model="gpt-4o",
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
            job_id=str(uuid.uuid4()),
            thread_id=thread_id,
            message_id=str(uuid.uuid4()),
            agent_response="This is a test response",
            token_count=15,
            max_token_count=32,
        )

        # Process the request
        await chat_service.process_chat_request(request)

        # Verify the OpenAI service was called with all messages (history + new)
        call_args = mock_openai_service.generate_chat_completion.call_args
        sent_messages = call_args[0][0].messages

        assert len(sent_messages) == 4  # 3 history messages + 1 new message
        assert sent_messages[0]["role"] == "system"
        assert sent_messages[1]["role"] == "user"
        assert sent_messages[1]["content"] == "What is the capital of France?"
        assert sent_messages[2]["role"] == "assistant"
        assert sent_messages[2]["content"] == "The capital of France is Paris."
        assert sent_messages[3]["role"] == "user"
        assert sent_messages[3]["content"] == "And what is the capital of Germany?"

    async def test_process_chat_request_with_function_call(
        self, mock_openai_service, mock_chat_history_repo, mock_config
    ):
        """Test processing a chat request that uses a function call."""
        # Set up the OpenAI service to return a function call
        function_call_response = ChatResponse(
            content=None,
            function_call={
                "name": "get_weather",
                "arguments": json.dumps({"location": "Seattle"}),
            },
            model="gpt-4o",
            prompt_tokens=20,
            completion_tokens=15,
            total_tokens=35,
            job_id=str(uuid.uuid4()),
            thread_id=str(uuid.uuid4()),
            message_id=str(uuid.uuid4()),
            agent_response=None,
            token_count=35,
            max_token_count=64,
        )
        mock_openai_service.generate_chat_completion.return_value = (
            function_call_response
        )

        # Create the chat service
        chat_service = ChatService(
            chat_service_type="basic",
            chat_history_repository=mock_chat_history_repo,
            conversation_flow="default",
            config=mock_config,
        )

        # Create a test request with a function
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
            messages=[{"role": "user", "content": "What's the weather in Seattle?"}],
            model="gpt-4o",
            user_id="test_user",
            thread_id=str(uuid.uuid4()),
            functions=functions,
            function_call="auto",
            user_prompt="What's the weather in Seattle?",
            conversation_flow="default",
        )

        # Process the request
        response = await chat_service.process_chat_request(request)

        # Verify the response contains the function call
        assert response.content is None
        assert response.function_call is not None
        assert response.function_call["name"] == "get_weather"
        assert json.loads(response.function_call["arguments"]) == {
            "location": "Seattle"
        }

        # Verify the function call was saved to chat history
        assert (
            mock_chat_history_repo.add_message.call_count == 2
        )  # User message and function call
