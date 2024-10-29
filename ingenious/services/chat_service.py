from abc import ABC, abstractmethod
from ingenious.models.chat import ChatRequest, ChatResponse
from ingenious.db.chat_history_repository import ChatHistoryRepository
from ingenious.external_services.openai_service import OpenAIService
import importlib


class IChatService(ABC):
    @abstractmethod
    async def get_chat_response(self, chat_request: ChatRequest) -> ChatResponse:
        pass


class ChatService:
    def __init__(
            self,
            chat_service_type: str,
            chat_history_repository: ChatHistoryRepository,
            openai_service: OpenAIService,
            conversation_flow: str
            ):

        module_name = f"ingenious.services.chat_services.{chat_service_type.lower()}.service"
        class_name = f"{chat_service_type.lower()}_chat_service"

        try:
            module = importlib.import_module(f"{module_name}")
            service_class = getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Unsupported chat service type: {module_name}.{class_name}") from e

        self.service_class = service_class(
            chat_history_repository=chat_history_repository,
            openai_service=openai_service,
            conversation_flow=conversation_flow
        )

    async def get_chat_response(self,  chat_request: ChatRequest) -> ChatResponse:
        if not chat_request.conversation_flow:
            raise ValueError(f"conversation_flow not set {chat_request}")
        return await self.service_class.get_chat_response(chat_request)
