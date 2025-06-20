"""
Modern chat infrastructure services using DDD patterns.

This module provides chat service implementations that integrate with
the external integrations bounded context for LLM services.
"""

from ..domain.entities import ChatSession
from ..domain.models import ChatRequest, ChatResponse
from ..domain.services import IChatService, IConversationService


class ModernChatService(IChatService):
    """Modern chat service using DDD patterns."""

    def __init__(self, llm_service):
        """Initialize with an LLM service from external_integrations context."""
        self._llm_service = llm_service

    async def process_chat_request(self, request: ChatRequest) -> ChatResponse:
        """Process chat request using modern LLM service."""
        if not request.user_prompt:
            raise ValueError("User prompt is required")

        # Use the LLM service to generate a response
        try:
            # Create a completion request
            completion_request = {
                "prompt": request.user_prompt,
                "max_tokens": getattr(request, "max_tokens", 1000),
                "temperature": getattr(request, "temperature", 0.7),
            }

            # Get completion from LLM service
            completion_response = await self._llm_service.create_completion(
                completion_request
            )

            return ChatResponse(
                response=completion_response.get("text", "No response generated"),
                user_id=request.user_id,
                conversation_flow=request.conversation_flow,
            )

        except Exception as e:
            return ChatResponse(
                response=f"Error processing request: {str(e)}",
                user_id=request.user_id,
                conversation_flow=request.conversation_flow,
            )


class DefaultConversationService(IConversationService):
    """Default implementation of conversation service."""

    def __init__(self, chat_service: IChatService):
        self._chat_service = chat_service
        self._sessions: dict[str, ChatSession] = {}

    async def start_conversation(
        self, user_id: str, conversation_flow: str
    ) -> ChatSession:
        """Start a new conversation session."""
        session = ChatSession(user_id, conversation_flow)
        self._sessions[session.session_id] = session
        return session

    async def continue_conversation(
        self, session_id: str, message: str
    ) -> ChatResponse:
        """Continue an existing conversation."""
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self._sessions[session_id]

        # Create a chat request
        request = ChatRequest(
            user_prompt=message,
            user_id=session.user_id,
            conversation_flow=session.conversation_flow,
        )

        # Process through chat service
        return await self._chat_service.process_chat_request(request)
