from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from ingenious.common.utils.namespace_utils import import_class_with_fallback

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from ingenious.domain.interfaces.repository.chat_history_repository import (
        IChatHistoryRepository,
    )
from ingenious.domain.model.chat import ChatRequest, ChatResponse
from ingenious.domain.model.config import Config


@runtime_checkable
class ChatServiceProtocol(Protocol):
    """Protocol defining the interface for chat service implementations."""

    async def process_chat_request(self, chat_request: ChatRequest) -> ChatResponse: ...

    async def get_chat_response(self, chat_request: ChatRequest) -> ChatResponse: ...


class ChatService:  # Define as IChatService at runtime
    def __init__(
        self,
        chat_service_type: str,
        chat_history_repository: "IChatHistoryRepository",
        conversation_flow: str,
        config: Config,
        revision: str = "dfe19b62-07f1-4cb5-ae9a-561a253e4b04",
    ):
        class_name = f"{chat_service_type.lower()}_chat_service"
        self.config = config
        self.revision = revision

        try:
            module_name = (
                f"application.service.chat.{chat_service_type.lower()}.service"
            )
            service_class_type = import_class_with_fallback(module_name, class_name)

        except ImportError as e:
            raise ImportError(
                f"Failed to import module for chat service type '{chat_service_type}'. "
                f"Attempted modules: '{module_name}', "
                f"'ingenious.application.service.chat.{chat_service_type.lower()}.service'. "
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

        # Pass openai_service if present on chat_history_repository (for test injection)
        openai_service = getattr(chat_history_repository, "openai_service", None)
        init_kwargs = {
            "config": config,
            "chat_history_repository": chat_history_repository,
            "conversation_flow": conversation_flow,
        }

        # Only add openai_service if it's accepted by the service class
        import inspect

        if openai_service is not None and hasattr(service_class_type, "__init__"):
            sig = inspect.signature(service_class_type.__init__)
            if "openai_service" in sig.parameters:
                init_kwargs["openai_service"] = openai_service

        self.service_class: Any = service_class_type(**init_kwargs)

    async def get_chat_response(self, chat_request: ChatRequest) -> ChatResponse:
        if not chat_request.conversation_flow:
            raise ValueError(f"conversation_flow not set {chat_request}")
        if hasattr(self.service_class, "get_chat_response"):
            return await self.service_class.get_chat_response(chat_request)
        else:
            raise AttributeError(
                f"Service class {type(self.service_class).__name__} does not implement get_chat_response method"
            )

    async def process_chat_request(self, chat_request: ChatRequest) -> ChatResponse:
        # Forward to the underlying service_class if it exists, else fallback to get_chat_response
        if hasattr(self.service_class, "process_chat_request"):
            return await self.service_class.process_chat_request(chat_request)
        elif hasattr(self.service_class, "get_chat_response"):
            return await self.get_chat_response(chat_request)
        else:
            raise AttributeError(
                f"Service class {type(self.service_class).__name__} does not implement process_chat_request or get_chat_response methods"
            )
