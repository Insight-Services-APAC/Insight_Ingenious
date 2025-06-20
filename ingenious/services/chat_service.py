from abc import ABC, abstractmethod

from ingenious.config.config import Config
from ingenious.models.chat import ChatRequest, ChatResponse
from ingenious.utils.namespace_utils import import_class_with_fallback


class IChatService(ABC):
    service_class = None

    @abstractmethod
    async def get_chat_response(self, chat_request: ChatRequest) -> ChatResponse:
        pass


class ChatService(IChatService):
    def __init__(
        self,
        chat_service_type: str,
        conversation_flow: str,
        config: Config,
        revision: str = "dfe19b62-07f1-4cb5-ae9a-561a253e4b04",
    ):
        class_name = f"{chat_service_type.lower()}_chat_service"
        self.config = config
        self.revision = revision

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

        self.service_class = service_class(
            config=config,
            conversation_flow=conversation_flow,
        )

    async def get_chat_response(self, chat_request: ChatRequest) -> ChatResponse:
        if not chat_request.conversation_flow:
            raise ValueError(f"conversation_flow not set {chat_request}")
        return await self.service_class.get_chat_response(chat_request)
