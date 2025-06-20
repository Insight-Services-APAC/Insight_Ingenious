from abc import ABC, abstractmethod
from typing import Optional

from .entities import ChatSession, Message, Thread
from .models import ChatRequest, ChatResponse


class IMessageRepository(ABC):
    """Repository interface for message persistence."""

    @abstractmethod
    async def save_message(self, message: Message) -> None:
        """Save a message to storage."""
        pass

    @abstractmethod
    async def get_message(self, message_id: str) -> Optional[Message]:
        """Retrieve a message by ID."""
        pass

    @abstractmethod
    async def get_messages_by_thread(self, thread_id: str) -> list[Message]:
        """Get all messages for a thread."""
        pass


class IThreadRepository(ABC):
    """Repository interface for thread persistence."""

    @abstractmethod
    async def save_thread(self, thread: Thread) -> None:
        """Save a thread to storage."""
        pass

    @abstractmethod
    async def get_thread(self, thread_id: str) -> Optional[Thread]:
        """Retrieve a thread by ID."""
        pass

    @abstractmethod
    async def get_threads_by_user(self, user_id: str) -> list[Thread]:
        """Get all threads for a user."""
        pass


class IChatRepository(ABC):
    """Repository interface for chat data persistence."""

    @abstractmethod
    async def save_chat_session(self, session: ChatSession) -> None:
        """Save a chat session to storage."""
        pass

    @abstractmethod
    async def get_chat_session(self, session_id: str) -> Optional[ChatSession]:
        """Retrieve a chat session by ID."""
        pass

    @abstractmethod
    async def get_chat_history(self, session_id: str) -> list[Message]:
        """Get chat history for a session."""
        pass


class IChatService(ABC):
    """Domain service interface for chat operations."""

    @abstractmethod
    async def process_chat_request(self, request: ChatRequest) -> ChatResponse:
        """Process a chat request and return a response."""
        pass


class IConversationService(ABC):
    """Domain service interface for conversation management."""

    @abstractmethod
    async def start_conversation(
        self, user_id: str, conversation_flow: str
    ) -> ChatSession:
        """Start a new conversation session."""
        pass

    @abstractmethod
    async def continue_conversation(
        self, session_id: str, message: str
    ) -> ChatResponse:
        """Continue an existing conversation."""
        pass
