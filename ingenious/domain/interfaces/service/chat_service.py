from abc import ABC, abstractmethod

from ingenious.domain.model.chat import ChatRequest, ChatResponse


class IChatService(ABC):
    @abstractmethod
    async def get_chat_response(self, chat_request: ChatRequest) -> ChatResponse:
        """Get a response to a chat request"""
        pass
