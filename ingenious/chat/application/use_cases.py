from typing import Optional
from ..domain.models import ChatRequest, ChatResponse
from ..domain.services import IChatService, IConversationService
from ..domain.entities import Message, Thread, ChatSession


class ChatUseCase:
    """Use case for handling chat interactions."""

    def __init__(
        self, chat_service: IChatService, conversation_service: IConversationService
    ):
        self._chat_service = chat_service
        self._conversation_service = conversation_service

    async def handle_chat_request(self, request: ChatRequest) -> ChatResponse:
        """Handle a chat request through the appropriate service."""
        # Validate request
        if not request.user_prompt:
            raise ValueError("User prompt is required")

        if not request.conversation_flow:
            raise ValueError("Conversation flow is required")

        # Process through chat service
        return await self._chat_service.process_chat_request(request)


class ConversationUseCase:
    """Use case for managing conversations."""

    def __init__(self, conversation_service: IConversationService):
        self._conversation_service = conversation_service

    async def start_new_conversation(
        self, user_id: str, conversation_flow: str
    ) -> ChatSession:
        """Start a new conversation session."""
        if not user_id:
            raise ValueError("User ID is required")

        if not conversation_flow:
            raise ValueError("Conversation flow is required")

        return await self._conversation_service.start_conversation(
            user_id, conversation_flow
        )

    async def continue_conversation(
        self, session_id: str, message: str
    ) -> ChatResponse:
        """Continue an existing conversation."""
        if not session_id:
            raise ValueError("Session ID is required")

        if not message:
            raise ValueError("Message is required")

        return await self._conversation_service.continue_conversation(
            session_id, message
        )
