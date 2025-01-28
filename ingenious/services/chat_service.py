from abc import ABC, abstractmethod
from ingenious.models.chat import ChatRequest, ChatResponse
from ingenious.db.chat_history_repository import ChatHistoryRepository
from ingenious.utils.conversation_builder import Sync_Prompt_Templates
from ingenious.config.config import Config
import importlib


class IChatService(ABC):
    service_class = None

    @abstractmethod
    async def get_chat_response(self, chat_request: ChatRequest) -> ChatResponse:
        pass

class ChatService:
    def __init__(
            self,
            chat_service_type: str,
            chat_history_repository: ChatHistoryRepository,
            conversation_flow: str,
            config: Config,
            revision: str = "dfe19b62-07f1-4cb5-ae9a-561a253e4b04"
            ):

        class_name = f"{chat_service_type.lower()}_chat_service"
        self.config = config
        self.revision = revision

        try:
            # First look for the module in the extensions namespace
            # module_name = f"ingenious.services.chat_services.{chat_service_type.lower()}.service"
            module_name = f"ingenious_extensions.services.chat_services.{chat_service_type.lower()}.service"
            if importlib.util.find_spec(module_name) is None:
                module_name = f"ingenious.services.chat_services.{chat_service_type.lower()}.service"
            else:
                module = importlib.import_module(module_name)
            service_class = getattr(module, class_name)

        except (ImportError, AttributeError) as e:
            raise ValueError(f"Unsupported chat service type: {module_name}.{class_name}") from e

        self.service_class = service_class(
            chat_history_repository=chat_history_repository,
            conversation_flow=conversation_flow
        )

    async def get_chat_response(self,  chat_request: ChatRequest) -> ChatResponse:
        # Sync the prompt templates
        await Sync_Prompt_Templates(self.config, revision=self.revision)

        if not chat_request.conversation_flow:
            raise ValueError(f"conversation_flow not set {chat_request}")
        return await self.service_class.get_chat_response(chat_request)


