from typing import Optional
from ..domain.models import ChatRequest, ChatResponse
from ..domain.services import IChatService, IConversationService
from ..domain.entities import Message, Thread, ChatSession
from ingenious.config.config import Config
from ingenious.utils.namespace_utils import import_class_with_fallback


class LegacyChatServiceAdapter(IChatService):
    """Adapter for legacy chat service implementation."""

    def __init__(
        self,
        chat_service_type: str,
        conversation_flow: str,
        config: Config,
        revision: str = "dfe19b62-07f1-4cb5-ae9a-561a253e4b04",
    ):
        self.config = config
        self.revision = revision
        self.conversation_flow = conversation_flow

        # Import the legacy service class
        class_name = f"{chat_service_type.lower()}_chat_service"

        try:
            module_name = f"services.chat_services.{chat_service_type.lower()}.service"
            service_class = import_class_with_fallback(module_name, class_name)

        except ImportError as e:
            raise ImportError(
                f"Failed to import module for chat service type '{chat_service_type}'. "
                f"Attempted modules: '{module_name}', "
                f"'ingenious.services.chat_services.{chat_service_type.lower()}.service'. "
                f"Error: {str(e)}"
            ) from e
        except AttributeError as e:
            raise AttributeError(
                f"Module '{module_name}' does not have the expected class '{class_name}'. "
                f"Ensure the class name matches the service type. Error: {str(e)}"
            ) from e
        except Exception as e:
            raise Exception(
                f"An unexpected error occurred while initializing the chat service. "
                f"Service type: '{chat_service_type}', Module: '{module_name}', "
                f"Class: '{class_name}'. Error: {str(e)}"
            ) from e

        self._service = service_class(
            config=config,
            conversation_flow=conversation_flow,
        )

    async def process_chat_request(self, request: ChatRequest) -> ChatResponse:
        """Process chat request through legacy service."""
        if not request.conversation_flow:
            raise ValueError(f"conversation_flow not set {request}")

        # Use the legacy method name
        return await self._service.get_chat_response(request)


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
