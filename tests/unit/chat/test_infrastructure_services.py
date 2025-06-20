"""
Unit tests for chat infrastructure services.

This module tests the infrastructure layer implementations of chat services.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from ingenious.chat.infrastructure.services import ModernChatService, DefaultConversationService
from ingenious.chat.domain.models import ChatRequest, ChatResponse
from ingenious.chat.domain.entities import ChatSession, Message, Thread


class TestModernChatService:
    """Test suite for ModernChatService."""
    
    @pytest.fixture
    def mock_llm_service(self):
        """Mock LLM service for testing."""
        mock = AsyncMock()
        mock.create_completion.return_value = {
            "text": "Mock LLM response",
            "model": "gpt-4",
            "usage": {"total_tokens": 50}
        }
        mock.is_healthy.return_value = True
        return mock
    
    @pytest.fixture
    def chat_service(self, mock_llm_service):
        """Create ModernChatService with mocked dependencies."""
        return ModernChatService(llm_service=mock_llm_service)
    
    @pytest.fixture
    def valid_chat_request(self):
        """Valid chat request for testing."""
        return ChatRequest(
            user_prompt="Hello, how can you help me?",
            conversation_flow="general",
            user_id="user-123",
            thread_id="thread-456"
        )
    
    async def test_process_chat_request_success(self, chat_service, mock_llm_service, valid_chat_request):
        """Test successful chat request processing."""
        # Arrange
        mock_llm_service.create_completion.return_value = {
            "text": "I can help you with various tasks and questions!",
            "model": "gpt-4",
            "usage": {"total_tokens": 25}
        }
        
        # Act
        response = await chat_service.process_chat_request(valid_chat_request)
        
        # Assert
        assert isinstance(response, ChatResponse)
        assert response.response == "I can help you with various tasks and questions!"
        assert response.user_id == "user-123"
        assert response.conversation_flow == "general"
        
        # Verify LLM service was called correctly
        mock_llm_service.create_completion.assert_called_once()
        call_args = mock_llm_service.create_completion.call_args[0][0]
        assert call_args["prompt"] == "Hello, how can you help me?"
    
    async def test_process_chat_request_empty_prompt(self, chat_service):
        """Test processing with empty user prompt."""
        # Arrange
        request = ChatRequest(
            user_prompt="",
            conversation_flow="general",
            user_id="user-123"
        )
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await chat_service.process_chat_request(request)
        
        assert "User prompt is required" in str(exc_info.value)
    
    async def test_process_chat_request_none_prompt(self, chat_service):
        """Test processing with None user prompt."""
        # Arrange
        request = Mock()
        request.user_prompt = None
        request.conversation_flow = "general"
        request.user_id = "user-123"
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await chat_service.process_chat_request(request)
        
        assert "User prompt is required" in str(exc_info.value)
    
    async def test_process_chat_request_llm_service_exception(self, chat_service, 
                                                             mock_llm_service, valid_chat_request):
        """Test handling LLM service exceptions."""
        # Arrange
        mock_llm_service.create_completion.side_effect = Exception("LLM service error")
        
        # Act
        response = await chat_service.process_chat_request(valid_chat_request)
        
        # Assert
        assert isinstance(response, ChatResponse)
        assert "Error processing request" in response.response
        assert response.user_id == "user-123"
        assert response.conversation_flow == "general"
    
    async def test_process_chat_request_with_options(self, chat_service, mock_llm_service):
        """Test processing with custom options."""
        # Arrange
        request = ChatRequest(
            user_prompt="What's the weather like?",
            conversation_flow="weather",
            user_id="user-789",
            max_tokens=500,
            temperature=0.8
        )
        
        mock_llm_service.create_completion.return_value = {
            "text": "Weather information response",
            "model": "gpt-4"
        }
        
        # Act
        response = await chat_service.process_chat_request(request)
        
        # Assert
        assert response.response == "Weather information response"
        
        # Verify options were passed to LLM service
        call_args = mock_llm_service.create_completion.call_args[0][0]
        assert call_args["max_tokens"] == 500
        assert call_args["temperature"] == 0.8
    
    async def test_process_chat_request_no_llm_response(self, chat_service, 
                                                       mock_llm_service, valid_chat_request):
        """Test handling when LLM service returns no response."""
        # Arrange
        mock_llm_service.create_completion.return_value = {}
        
        # Act
        response = await chat_service.process_chat_request(valid_chat_request)
        
        # Assert
        assert response.response == "No response generated"
        assert response.user_id == "user-123"
    
    async def test_process_chat_request_partial_llm_response(self, chat_service, 
                                                            mock_llm_service, valid_chat_request):
        """Test handling partial LLM service response."""
        # Arrange
        mock_llm_service.create_completion.return_value = {
            "model": "gpt-4",
            "usage": {"total_tokens": 30}
            # Missing 'text' field
        }
        
        # Act
        response = await chat_service.process_chat_request(valid_chat_request)
        
        # Assert
        assert response.response == "No response generated"
    
    async def test_process_chat_request_different_conversation_flows(self, chat_service, mock_llm_service):
        """Test processing with different conversation flows."""
        # Arrange
        flows = ["general", "support", "sales", "technical"]
        mock_llm_service.create_completion.return_value = {
            "text": "Flow-specific response",
            "model": "gpt-4"
        }
        
        for flow in flows:
            # Act
            request = ChatRequest(
                user_prompt=f"Question for {flow}",
                conversation_flow=flow,
                user_id="user-123"
            )
            response = await chat_service.process_chat_request(request)
            
            # Assert
            assert response.conversation_flow == flow
            assert response.response == "Flow-specific response"


class TestDefaultConversationService:
    """Test suite for DefaultConversationService."""
    
    @pytest.fixture
    def conversation_service(self):
        """Create DefaultConversationService."""
        return DefaultConversationService()
    
    async def test_start_conversation_success(self, conversation_service):
        """Test successful conversation start."""
        # Act
        session = await conversation_service.start_conversation("user-123", "general")
        
        # Assert
        assert isinstance(session, ChatSession)
        assert session.user_id == "user-123"
        assert session.conversation_flow == "general"
        assert session.session_id is not None
        assert session.created_at is not None
    
    async def test_start_conversation_different_flows(self, conversation_service):
        """Test starting conversations with different flows."""
        # Arrange
        flows = ["support", "sales", "technical", "general"]
        
        for flow in flows:
            # Act
            session = await conversation_service.start_conversation("user-456", flow)
            
            # Assert
            assert session.conversation_flow == flow
            assert session.user_id == "user-456"
    
    async def test_continue_conversation_success(self, conversation_service):
        """Test continuing an existing conversation."""
        # Arrange
        # First start a conversation
        session = await conversation_service.start_conversation("user-123", "general")
        session_id = session.session_id
        
        # Mock the conversation service's internal storage
        conversation_service._sessions = {session_id: session}
        
        # Act
        response = await conversation_service.continue_conversation(session_id, "Follow-up message")
        
        # Assert
        assert isinstance(response, ChatResponse)
        assert response.thread_id is not None
        assert "Follow-up message" in str(response)  # Basic check
    
    async def test_continue_conversation_nonexistent_session(self, conversation_service):
        """Test continuing a conversation that doesn't exist."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await conversation_service.continue_conversation("nonexistent-session", "Message")
        
        assert "Session not found" in str(exc_info.value)
    
    async def test_conversation_flow_with_multiple_messages(self, conversation_service):
        """Test conversation flow with multiple messages."""
        # Arrange
        session = await conversation_service.start_conversation("user-123", "support")
        session_id = session.session_id
        conversation_service._sessions = {session_id: session}
        
        # Act - Send multiple messages
        response1 = await conversation_service.continue_conversation(session_id, "First message")
        response2 = await conversation_service.continue_conversation(session_id, "Second message")
        response3 = await conversation_service.continue_conversation(session_id, "Third message")
        
        # Assert
        assert all(isinstance(r, ChatResponse) for r in [response1, response2, response3])
        # All responses should be for the same thread in the session
        thread_ids = [r.thread_id for r in [response1, response2, response3]]
        assert len(set(thread_ids)) <= len(session.threads)  # At most one thread per conversation


@pytest.mark.unit
class TestChatInfrastructureIntegration:
    """Integration tests for chat infrastructure services."""
    
    @pytest.fixture
    def integrated_services(self):
        """Set up integrated chat services."""
        mock_llm = AsyncMock()
        mock_llm.create_completion.return_value = {
            "text": "Integrated response",
            "model": "gpt-4",
            "usage": {"total_tokens": 20}
        }
        
        chat_service = ModernChatService(llm_service=mock_llm)
        conversation_service = DefaultConversationService()
        
        return {
            "chat_service": chat_service,
            "conversation_service": conversation_service,
            "mock_llm": mock_llm
        }
    
    async def test_full_conversation_workflow(self, integrated_services):
        """Test a complete conversation workflow."""
        # Arrange
        chat_service = integrated_services["chat_service"]
        conversation_service = integrated_services["conversation_service"]
        
        # Act
        # Start conversation
        session = await conversation_service.start_conversation("user-123", "general")
        
        # Process chat request
        request = ChatRequest(
            user_prompt="Hello, I need assistance",
            conversation_flow="general",
            user_id="user-123",
            thread_id="thread-456"
        )
        chat_response = await chat_service.process_chat_request(request)
        
        # Assert
        assert session.user_id == "user-123"
        assert session.conversation_flow == "general"
        assert chat_response.response == "Integrated response"
        assert chat_response.user_id == "user-123"
        assert chat_response.conversation_flow == "general"
    
    async def test_error_handling_across_services(self, integrated_services):
        """Test error handling across integrated services."""
        # Arrange
        chat_service = integrated_services["chat_service"]
        conversation_service = integrated_services["conversation_service"]
        mock_llm = integrated_services["mock_llm"]
        
        # Make LLM service fail
        mock_llm.create_completion.side_effect = Exception("LLM failure")
        
        # Act
        session = await conversation_service.start_conversation("user-123", "general")
        
        request = ChatRequest(
            user_prompt="This will fail",
            conversation_flow="general",
            user_id="user-123"
        )
        response = await chat_service.process_chat_request(request)
        
        # Assert
        assert session is not None  # Conversation service still works
        assert "Error processing request" in response.response  # Chat service handles error
    
    async def test_service_performance_characteristics(self, integrated_services):
        """Test performance characteristics of services."""
        # Arrange
        chat_service = integrated_services["chat_service"]
        
        import time
        
        # Act
        start_time = time.time()
        
        request = ChatRequest(
            user_prompt="Performance test message",
            conversation_flow="general",
            user_id="user-123"
        )
        response = await chat_service.process_chat_request(request)
        
        end_time = time.time()
        
        # Assert
        execution_time = end_time - start_time
        assert execution_time < 1.0  # Should complete quickly with mocked service
        assert response is not None
