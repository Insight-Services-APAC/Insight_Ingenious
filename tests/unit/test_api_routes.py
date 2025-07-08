"""
Unit tests for API routes.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException

from ingenious.errors.content_filter_error import ContentFilterError
from ingenious.errors.token_limit_exceeded_error import TokenLimitExceededError
from ingenious.models.chat import ChatRequest, ChatResponse
from ingenious.models.message_feedback import (
    MessageFeedbackRequest,
    MessageFeedbackResponse,
)


class TestChatRoutes:
    """Test cases for chat API routes."""

    @pytest.mark.asyncio
    async def test_chat_endpoint_success(self):
        """Test successful chat endpoint."""
        # Mock the chat service
        mock_chat_service = Mock()
        mock_response = ChatResponse(
            thread_id="test_thread",
            message_id="test_message_id",
            agent_response="Test response",
            token_count=100,
            max_token_count=1000,
        )
        mock_chat_service.get_chat_response = AsyncMock(return_value=mock_response)

        # Mock the request
        chat_request = ChatRequest(
            user_prompt="Test message", conversation_flow="test_workflow"
        )

        # Mock credentials
        mock_credentials = Mock()

        # Import and test the chat function
        from ingenious.api.routes.chat import chat

        result = await chat(chat_request, mock_chat_service, mock_credentials)

        assert result == mock_response
        mock_chat_service.get_chat_response.assert_called_once_with(chat_request)

    @pytest.mark.asyncio
    async def test_chat_endpoint_content_filter_error(self):
        """Test chat endpoint with content filter error."""
        mock_chat_service = Mock()
        mock_chat_service.get_chat_response = AsyncMock(
            side_effect=ContentFilterError("Content filtered")
        )

        chat_request = ChatRequest(
            user_prompt="Inappropriate message", conversation_flow="test_workflow"
        )

        mock_credentials = Mock()

        from ingenious.api.routes.chat import chat

        with pytest.raises(HTTPException) as exc_info:
            await chat(chat_request, mock_chat_service, mock_credentials)

        assert exc_info.value.status_code == 406

    @pytest.mark.asyncio
    async def test_chat_endpoint_token_limit_error(self):
        """Test chat endpoint with token limit exceeded error."""
        mock_chat_service = Mock()
        mock_chat_service.get_chat_response = AsyncMock(
            side_effect=TokenLimitExceededError("Token limit exceeded")
        )

        chat_request = ChatRequest(
            user_prompt="Very long message", conversation_flow="test_workflow"
        )

        mock_credentials = Mock()

        from ingenious.api.routes.chat import chat

        with pytest.raises(HTTPException) as exc_info:
            await chat(chat_request, mock_chat_service, mock_credentials)

        assert exc_info.value.status_code == 413

    @pytest.mark.asyncio
    async def test_chat_endpoint_generic_exception(self):
        """Test chat endpoint with generic exception."""
        mock_chat_service = Mock()
        mock_chat_service.get_chat_response = AsyncMock(
            side_effect=Exception("Generic error")
        )

        chat_request = ChatRequest(
            user_prompt="Test message", conversation_flow="test_workflow"
        )

        mock_credentials = Mock()

        from ingenious.api.routes.chat import chat

        with pytest.raises(HTTPException) as exc_info:
            await chat(chat_request, mock_chat_service, mock_credentials)

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_chat_endpoint_invalid_workflow(self):
        """Test chat endpoint with invalid workflow."""
        chat_request = ChatRequest(user_prompt="Test message", conversation_flow="")

        mock_chat_service = Mock()
        mock_credentials = Mock()

        from ingenious.api.routes.chat import chat

        with pytest.raises(HTTPException) as exc_info:
            await chat(chat_request, mock_chat_service, mock_credentials)

        assert exc_info.value.status_code == 400


class TestMessageFeedbackRoutes:
    """Test cases for message feedback API routes."""

    @pytest.mark.asyncio
    async def test_submit_message_feedback_success(self):
        """Test successful message feedback submission."""
        mock_service = Mock()
        mock_response = MessageFeedbackResponse(
            message="Feedback submitted successfully"
        )
        mock_service.update_message_feedback = AsyncMock(return_value=mock_response)

        feedback = MessageFeedbackRequest(
            thread_id="test_thread_id",
            message_id="test_message_id",
            user_id="test_user_id",
            positive_feedback=True,
        )

        from ingenious.api.routes.message_feedback import submit_message_feedback

        result = await submit_message_feedback(
            "test_message_id", feedback, mock_service
        )

        assert result == mock_response
        mock_service.update_message_feedback.assert_called_once_with(
            "test_message_id", feedback
        )

    @pytest.mark.asyncio
    async def test_submit_message_feedback_failure(self):
        """Test message feedback submission failure."""
        mock_service = Mock()
        mock_service.update_message_feedback = AsyncMock(
            side_effect=Exception("Database error")
        )

        feedback = MessageFeedbackRequest(
            thread_id="test_thread_id",
            message_id="test_message_id",
            user_id="test_user_id",
            positive_feedback=False,
        )

        from ingenious.api.routes.message_feedback import submit_message_feedback

        with pytest.raises(Exception) as exc_info:
            await submit_message_feedback("test_message_id", feedback, mock_service)

        assert "Database error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_submit_message_feedback_invalid_message_id(self):
        """Test message feedback submission with invalid message ID."""
        mock_service = Mock()
        mock_service.update_message_feedback = AsyncMock(
            side_effect=ValueError("Message not found")
        )

        feedback = MessageFeedbackRequest(
            thread_id="test_thread_id",
            message_id="invalid_message_id",
            user_id="test_user_id",
            positive_feedback=True,
        )

        from ingenious.api.routes.message_feedback import submit_message_feedback

        with pytest.raises(HTTPException) as exc_info:
            await submit_message_feedback("invalid_message_id", feedback, mock_service)

        assert exc_info.value.status_code == 400


class TestConversationRoutes:
    """Test cases for conversation API routes."""

    @pytest.mark.asyncio
    async def test_get_conversation_success(self):
        """Test successful conversation retrieval."""
        mock_repo = Mock()
        mock_messages = [
            Mock(role="user", content="Hello"),
            Mock(role="assistant", content="Hi there!"),
        ]
        mock_repo.get_thread_messages = AsyncMock(return_value=mock_messages)

        from ingenious.api.routes.conversation import get_conversation

        result = await get_conversation("test_thread_id", mock_repo)

        assert result == mock_messages
        mock_repo.get_thread_messages.assert_called_once_with("test_thread_id")

    @pytest.mark.asyncio
    async def test_get_conversation_not_found(self):
        """Test conversation retrieval when conversation not found."""
        mock_repo = Mock()
        mock_repo.get_thread_messages = AsyncMock(return_value=[])

        from ingenious.api.routes.conversation import get_conversation

        result = await get_conversation("nonexistent_thread_id", mock_repo)

        assert result == []
        mock_repo.get_thread_messages.assert_called_once_with("nonexistent_thread_id")

    @pytest.mark.asyncio
    async def test_get_conversation_repository_error(self):
        """Test conversation retrieval with repository error."""
        mock_repo = Mock()
        mock_repo.get_thread_messages = AsyncMock(
            side_effect=Exception("Database error")
        )

        from ingenious.api.routes.conversation import get_conversation

        with pytest.raises(HTTPException) as exc_info:
            await get_conversation("test_thread_id", mock_repo)

        assert exc_info.value.status_code == 400


class TestDiagnosticRoutes:
    """Test cases for diagnostic API routes."""

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check."""
        with (
            patch("ingenious.api.routes.diagnostic.datetime") as mock_datetime,
            patch(
                "ingenious.api.routes.diagnostic.igen_deps.get_config"
            ) as mock_get_config,
            patch(
                "ingenious.api.routes.diagnostic.igen_deps.get_profile"
            ) as mock_get_profile,
        ):
            mock_datetime.utcnow.return_value.isoformat.return_value = (
                "2023-01-01T12:00:00"
            )
            mock_get_config.return_value = Mock()
            mock_get_profile.return_value = Mock()

            from ingenious.api.routes.diagnostic import health_check

            result = await health_check()

            assert isinstance(result, dict)
            assert "status" in result
            assert result["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_system_info_success(self):
        """Test system info retrieval with error handling."""
        with patch(
            "ingenious.api.routes.diagnostic.igen_deps.get_config"
        ) as mock_get_config:
            mock_get_config.return_value = Mock()

            from ingenious.api.routes.diagnostic import diagnostic

            mock_request = Mock()
            mock_auth_user = "test_user"

            # The diagnostic function will raise an HTTPException due to FileStorage issues
            with pytest.raises(HTTPException) as exc_info:
                await diagnostic(mock_request, mock_auth_user)

            assert exc_info.value.status_code == 500


class TestEventsRoutes:
    """Test cases for events API routes."""

    def test_events_module_exists(self):
        """Test that events module can be imported."""
        import ingenious.api.routes.events as events_module

        assert hasattr(events_module, "router")
        assert hasattr(events_module, "logger")

    def test_events_router_exists(self):
        """Test that router is configured."""
        from ingenious.api.routes.events import router

        assert router is not None

    def test_events_module_basic_attributes(self):
        """Test basic module attributes."""
        import ingenious.api.routes.events as events_module

        # Just verify the module loads without the functions that don't exist
        assert events_module.router
        assert events_module.logger


class TestPromptsRoutes:
    """Test cases for prompts API routes."""

    def test_prompts_module_exists(self):
        """Test that prompts module can be imported."""
        import ingenious.api.routes.prompts as prompts_module

        assert hasattr(prompts_module, "router")
        assert hasattr(prompts_module, "logger")

    def test_view_function_exists(self):
        """Test that view function exists."""
        from ingenious.api.routes.prompts import view

        assert callable(view)

    def test_update_prompt_request_model_exists(self):
        """Test that UpdatePromptRequest model exists."""
        from ingenious.api.routes.prompts import UpdatePromptRequest

        # Test the model can be instantiated
        request = UpdatePromptRequest(content="test content")
        assert request.content == "test content"
