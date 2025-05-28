from abc import ABC, abstractmethod
from typing import Any, Dict, List, Literal, Optional, TypeVar

T = TypeVar("T")


class IChatHistoryRepository(ABC):
    """Interface for chat history repository interactions"""

    TrueStepType = Literal[
        "assistant_streaming", "code", "tool", "thread", "assistant_step", "user_step"
    ]

    @abstractmethod
    async def update_thread(
        self,
        thread_id: str,
        name: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Update a thread with new information"""
        pass

    @abstractmethod
    async def add_message(self, message: Any) -> str:
        """Add a message to the chat history"""
        pass

    @abstractmethod
    async def add_user(self, identifier: str) -> Any:
        """Add a user to the chat history database"""
        pass

    @abstractmethod
    async def get_user(self, identifier: str) -> Any:
        """Get a user from the chat history database"""
        pass

    @abstractmethod
    async def get_message(self, message_id: str, thread_id: str) -> Any:
        """Get a message from the chat history"""
        pass

    @abstractmethod
    async def get_thread_messages(self, thread_id: str) -> list[Any]:
        """Get all messages in a thread"""
        pass

    @abstractmethod
    async def get_messages(self, thread_id: str) -> List[Any]:
        """Get all messages in a thread (alias for get_thread_messages)"""
        pass

    @abstractmethod
    async def get_threads_for_user(
        self, identifier: str, thread_id: Optional[str]
    ) -> Optional[List[Dict[str, Any]]]:
        """Get all threads for a user"""
        pass

    @abstractmethod
    async def get_thread_metadata(self, thread_id: str) -> Dict[str, Any]:
        """Get metadata for a thread"""
        pass

    @abstractmethod
    async def update_message_feedback(
        self, message_id: str, thread_id: str, positive_feedback: bool | None
    ) -> None:
        """Update feedback for a message"""
        pass

    @abstractmethod
    async def update_memory_feedback(
        self, message_id: str, thread_id: str, positive_feedback: bool | None
    ) -> None:
        """Update feedback for a memory"""
        pass

    @abstractmethod
    async def update_message_content_filter_results(
        self, message_id: str, thread_id: str, content_filter_results: dict[str, object]
    ) -> None:
        """Update content filter results for a message"""
        pass

    @abstractmethod
    async def update_memory_content_filter_results(
        self, message_id: str, thread_id: str, content_filter_results: dict[str, object]
    ) -> None:
        """Update content filter results for a memory"""
        pass

    @abstractmethod
    async def delete_thread(self, thread_id: str) -> None:
        """Delete a thread and all its messages"""
        pass

    @abstractmethod
    async def delete_thread_memory(self, thread_id: str) -> None:
        """Delete all memory records for a thread"""
        pass

    @abstractmethod
    async def delete_user_memory(self, user_id: str) -> None:
        """Delete all memory records for a user"""
        pass
