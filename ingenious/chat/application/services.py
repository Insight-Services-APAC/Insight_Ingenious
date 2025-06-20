from abc import ABC, abstractmethod
from typing import Optional
from ..domain.models import ChatRequest, ChatResponse
from ..domain.services import IChatService


class ChatApplicationService:
    """Application service orchestrating chat operations."""

    def __init__(self, chat_service: IChatService):
        self._chat_service = chat_service

    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        """Process a chat request with validation and error handling."""
        # Validate input
        self._validate_chat_request(request)

        try:
            # Process through domain service
            response = await self._chat_service.process_chat_request(request)

            # Apply any application-level transformations
            return self._enhance_response(response)

        except Exception as e:
            # Handle application-level errors
            return self._handle_error(e, request)

    def _validate_chat_request(self, request: ChatRequest) -> None:
        """Validate chat request at application level."""
        if not request.user_prompt:
            raise ValueError("User prompt is required")

        if not request.conversation_flow:
            raise ValueError("Conversation flow is required")

        # Add more validation as needed

    def _enhance_response(self, response: ChatResponse) -> ChatResponse:
        """Apply application-level enhancements to response."""
        # Add any application-level processing
        return response

    def _handle_error(self, error: Exception, request: ChatRequest) -> ChatResponse:
        """Handle errors at application level."""
        # Log error, apply fallback logic, etc.
        return ChatResponse(
            thread_id=request.thread_id,
            agent_response="I apologize, but I encountered an error processing your request.",
            event_type="error",
        )
