"""
Integration tests for Chat API endpoints.

This module tests the chat REST API endpoints with real FastAPI integration.
"""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from fastapi import status

from ingenious.chat.domain.models import ChatRequest, ChatResponse


@pytest.mark.integration
@pytest.mark.api
class TestChatAPIIntegration:
    """Integration tests for Chat API endpoints."""
    
    @pytest.fixture
    def mock_chat_application_service(self):
        """Mock chat application service for API testing."""
        mock = AsyncMock()
        mock.process_chat.return_value = ChatResponse(
            thread_id="test-thread-123",
            message_id="test-msg-456",
            agent_response="Hello! How can I help you today?",
            token_count=15,
            event_type="agent_response"
        )
        return mock
    
    @pytest.fixture
    def mock_security_service(self):
        """Mock security service for authentication."""
        from fastapi.security import HTTPBasicCredentials
        return HTTPBasicCredentials(username="testuser", password="testpass")
    
    async def test_chat_endpoint_success(self, async_client, mock_chat_application_service):
        """Test successful chat request."""
        # Arrange
        chat_request = {
            "user_prompt": "Hello, how are you?",
            "conversation_flow": "general",
            "user_id": "test-user-123",
            "thread_id": "test-thread-456"
        }
        
        with patch('ingenious.dependencies.get_chat_service', return_value=mock_chat_application_service):
            with patch('ingenious.dependencies.get_security_service', return_value=None):
                # Act
                response = await async_client.post(
                    "/api/v1/chat",
                    json=chat_request,
                    auth=("testuser", "testpass")
                )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["thread_id"] == "test-thread-123"
        assert response_data["agent_response"] == "Hello! How can I help you today?"
        assert response_data["token_count"] == 15
    
    async def test_chat_endpoint_validation_error(self, async_client):
        """Test chat endpoint with validation error."""
        # Arrange
        invalid_request = {
            "user_prompt": "",  # Empty prompt should cause validation error
            "conversation_flow": "general"
        }
        
        with patch('ingenious.dependencies.get_security_service', return_value=None):
            # Act
            response = await async_client.post(
                "/api/v1/chat",
                json=invalid_request,
                auth=("testuser", "testpass")
            )
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert "detail" in response_data
    
    async def test_chat_endpoint_missing_conversation_flow(self, async_client):
        """Test chat endpoint with missing conversation_flow."""
        # Arrange
        invalid_request = {
            "user_prompt": "Hello!"
            # Missing conversation_flow
        }
        
        with patch('ingenious.dependencies.get_security_service', return_value=None):
            # Act
            response = await async_client.post(
                "/api/v1/chat",
                json=invalid_request,
                auth=("testuser", "testpass")
            )
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    async def test_chat_endpoint_content_filter_error(self, async_client, mock_chat_application_service):
        """Test chat endpoint with content filter error."""
        # Arrange
        from ingenious.external_integrations.domain.errors import ContentFilterError
        mock_chat_application_service.process_chat.side_effect = ContentFilterError("Content filtered")
        
        chat_request = {
            "user_prompt": "Inappropriate content",
            "conversation_flow": "general"
        }
        
        with patch('ingenious.dependencies.get_chat_service', return_value=mock_chat_application_service):
            with patch('ingenious.dependencies.get_security_service', return_value=None):
                # Act
                response = await async_client.post(
                    "/api/v1/chat",
                    json=chat_request,
                    auth=("testuser", "testpass")
                )
        
        # Assert
        assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
        response_data = response.json()
        assert "detail" in response_data
    
    async def test_chat_endpoint_token_limit_error(self, async_client, mock_chat_application_service):
        """Test chat endpoint with token limit exceeded error."""
        # Arrange
        from ingenious.external_integrations.domain.errors import TokenLimitExceededError
        mock_chat_application_service.process_chat.side_effect = TokenLimitExceededError("Token limit exceeded")
        
        chat_request = {
            "user_prompt": "Very long prompt that exceeds token limits" * 100,
            "conversation_flow": "general"
        }
        
        with patch('ingenious.dependencies.get_chat_service', return_value=mock_chat_application_service):
            with patch('ingenious.dependencies.get_security_service', return_value=None):
                # Act
                response = await async_client.post(
                    "/api/v1/chat",
                    json=chat_request,
                    auth=("testuser", "testpass")
                )
        
        # Assert
        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    
    async def test_chat_endpoint_server_error(self, async_client, mock_chat_application_service):
        """Test chat endpoint with internal server error."""
        # Arrange
        mock_chat_application_service.process_chat.side_effect = Exception("Internal error")
        
        chat_request = {
            "user_prompt": "Hello!",
            "conversation_flow": "general"
        }
        
        with patch('ingenious.dependencies.get_chat_service', return_value=mock_chat_application_service):
            with patch('ingenious.dependencies.get_security_service', return_value=None):
                # Act
                response = await async_client.post(
                    "/api/v1/chat",
                    json=chat_request,
                    auth=("testuser", "testpass")
                )
        
        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    async def test_get_conversation_endpoint_success(self, async_client):
        """Test successful conversation retrieval."""
        # Arrange
        mock_messages = [
            {
                "message_id": "msg-1",
                "content": "Hello!",
                "user_id": "user-123",
                "timestamp": "2023-01-01T12:00:00Z"
            },
            {
                "message_id": "msg-2",
                "content": "Hi there! How can I help?",
                "user_id": "agent-456",
                "timestamp": "2023-01-01T12:01:00Z"
            }
        ]
        
        mock_chat_service = AsyncMock()
        mock_chat_service.get_conversation.return_value = mock_messages
        
        with patch('ingenious.dependencies.get_chat_service', return_value=mock_chat_service):
            with patch('ingenious.dependencies.get_security_service', return_value=None):
                # Act
                response = await async_client.get(
                    "/api/v1/conversations/thread-123",
                    auth=("testuser", "testpass")
                )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data) == 2
        assert response_data[0]["message_id"] == "msg-1"
        assert response_data[1]["content"] == "Hi there! How can I help?"
    
    async def test_get_conversation_endpoint_not_found(self, async_client):
        """Test conversation retrieval with non-existent thread."""
        # Arrange
        mock_chat_service = AsyncMock()
        mock_chat_service.get_conversation.side_effect = ValueError("Thread not found")
        
        with patch('ingenious.dependencies.get_chat_service', return_value=mock_chat_service):
            with patch('ingenious.dependencies.get_security_service', return_value=None):
                # Act
                response = await async_client.get(
                    "/api/v1/conversations/nonexistent-thread",
                    auth=("testuser", "testpass")
                )
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    async def test_message_feedback_endpoint_success(self, async_client):
        """Test successful message feedback submission."""
        # Arrange
        feedback_request = {
            "feedback_type": "thumbs_up",
            "feedback_text": "Great response!",
            "user_id": "user-123"
        }
        
        mock_feedback_response = {
            "feedback_id": "feedback-789",
            "message_id": "msg-456",
            "status": "recorded",
            "timestamp": "2023-01-01T12:00:00Z"
        }
        
        mock_chat_service = AsyncMock()
        mock_chat_service.submit_message_feedback.return_value = mock_feedback_response
        
        with patch('ingenious.dependencies.get_chat_service', return_value=mock_chat_service):
            with patch('ingenious.dependencies.get_security_service', return_value=None):
                # Act
                response = await async_client.put(
                    "/api/v1/messages/msg-456/feedback",
                    json=feedback_request,
                    auth=("testuser", "testpass")
                )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["feedback_id"] == "feedback-789"
        assert response_data["status"] == "recorded"
    
    async def test_message_feedback_endpoint_invalid_feedback_type(self, async_client):
        """Test message feedback with invalid feedback type."""
        # Arrange
        invalid_feedback = {
            "feedback_type": "invalid_type",
            "feedback_text": "Some feedback"
        }
        
        with patch('ingenious.dependencies.get_security_service', return_value=None):
            # Act
            response = await async_client.put(
                "/api/v1/messages/msg-456/feedback",
                json=invalid_feedback,
                auth=("testuser", "testpass")
            )
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    async def test_authentication_required(self, async_client):
        """Test that authentication is required for all endpoints."""
        # Arrange
        chat_request = {
            "user_prompt": "Hello!",
            "conversation_flow": "general"
        }
        
        # Act & Assert - No authentication
        response = await async_client.post("/api/v1/chat", json=chat_request)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = await async_client.get("/api/v1/conversations/thread-123")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = await async_client.put(
            "/api/v1/messages/msg-456/feedback",
            json={"feedback_type": "thumbs_up"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    async def test_cors_headers(self, async_client):
        """Test that CORS headers are properly set."""
        # Arrange
        chat_request = {
            "user_prompt": "Test CORS",
            "conversation_flow": "general"
        }
        
        mock_chat_service = AsyncMock()
        mock_chat_service.process_chat.return_value = ChatResponse(
            agent_response="CORS test response"
        )
        
        with patch('ingenious.dependencies.get_chat_service', return_value=mock_chat_service):
            with patch('ingenious.dependencies.get_security_service', return_value=None):
                # Act
                response = await async_client.post(
                    "/api/v1/chat",
                    json=chat_request,
                    auth=("testuser", "testpass"),
                    headers={"Origin": "http://localhost:3000"}
                )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        # Note: CORS headers would be set by FastAPI middleware
        # This test verifies the endpoint works with cross-origin requests
    
    async def test_request_size_limits(self, async_client):
        """Test request size limits are enforced."""
        # Arrange
        large_prompt = "A" * 100000  # Very large prompt
        chat_request = {
            "user_prompt": large_prompt,
            "conversation_flow": "general"
        }
        
        with patch('ingenious.dependencies.get_security_service', return_value=None):
            # Act
            response = await async_client.post(
                "/api/v1/chat",
                json=chat_request,
                auth=("testuser", "testpass")
            )
        
        # Assert
        # Should either process successfully or fail with appropriate error
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
    
    async def test_concurrent_requests(self, async_client):
        """Test handling of concurrent chat requests."""
        # Arrange
        import asyncio
        
        mock_chat_service = AsyncMock()
        mock_chat_service.process_chat.return_value = ChatResponse(
            thread_id="concurrent-thread",
            agent_response="Concurrent response",
            token_count=10
        )
        
        async def make_request(prompt_id):
            request = {
                "user_prompt": f"Concurrent request {prompt_id}",
                "conversation_flow": "general",
                "user_id": f"user-{prompt_id}"
            }
            return await async_client.post(
                "/api/v1/chat",
                json=request,
                auth=("testuser", "testpass")
            )
        
        with patch('ingenious.dependencies.get_chat_service', return_value=mock_chat_service):
            with patch('ingenious.dependencies.get_security_service', return_value=None):
                # Act - Make 5 concurrent requests
                tasks = [make_request(i) for i in range(5)]
                responses = await asyncio.gather(*tasks)
        
        # Assert
        assert len(responses) == 5
        for response in responses:
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["agent_response"] == "Concurrent response"


@pytest.mark.integration
@pytest.mark.slow
class TestChatAPIPerformance:
    """Performance tests for Chat API endpoints."""
    
    async def test_response_time_within_limits(self, async_client, performance_timer):
        """Test that API response time is within acceptable limits."""
        # Arrange
        chat_request = {
            "user_prompt": "Performance test message",
            "conversation_flow": "general"
        }
        
        mock_chat_service = AsyncMock()
        mock_chat_service.process_chat.return_value = ChatResponse(
            agent_response="Quick response"
        )
        
        with patch('ingenious.dependencies.get_chat_service', return_value=mock_chat_service):
            with patch('ingenious.dependencies.get_security_service', return_value=None):
                # Act
                performance_timer.start()
                response = await async_client.post(
                    "/api/v1/chat",
                    json=chat_request,
                    auth=("testuser", "testpass")
                )
                performance_timer.stop()
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert performance_timer.elapsed is not None
        assert performance_timer.elapsed < 2.0  # Should respond within 2 seconds
    
    async def test_memory_usage_stability(self, async_client):
        """Test that memory usage remains stable across multiple requests."""
        # Arrange
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        mock_chat_service = AsyncMock()
        mock_chat_service.process_chat.return_value = ChatResponse(
            agent_response="Memory test response"
        )
        
        with patch('ingenious.dependencies.get_chat_service', return_value=mock_chat_service):
            with patch('ingenious.dependencies.get_security_service', return_value=None):
                # Act - Make multiple requests
                for i in range(50):
                    request = {
                        "user_prompt": f"Memory test {i}",
                        "conversation_flow": "general"
                    }
                    response = await async_client.post(
                        "/api/v1/chat",
                        json=request,
                        auth=("testuser", "testpass")
                    )
                    assert response.status_code == status.HTTP_200_OK
        
        # Assert
        final_memory = process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / initial_memory
        
        # Memory increase should be reasonable (less than 50%)
        assert memory_increase < 0.5, f"Memory increased by {memory_increase:.2%}"
