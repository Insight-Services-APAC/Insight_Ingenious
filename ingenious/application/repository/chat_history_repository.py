"""Implementation of the chat history repository interface"""

from typing import Any, Dict, List, Optional

from ingenious.common.utils.namespace_utils import import_class_with_fallback
from ingenious.domain.interfaces.repository.chat_history_repository import (
    IChatHistoryRepository,
)
from ingenious.domain.model.chat.chat_history_models import StepDict, ThreadDict, User
from ingenious.domain.model.chat.message import Message
from ingenious.domain.model.database.database_client import DatabaseClientType


class ChatHistoryRepository(IChatHistoryRepository):
    """Implementation of the chat history repository interface"""

    def __init__(self, config: Any):
        """Initialize the chat history repository with configuration."""
        try:
            db_type_val = config.chat_history.database_type.lower()
            db_type = DatabaseClientType(db_type_val)

            module_name = (
                f"ingenious.presentation.infrastructure.database.{db_type.value}"
            )
            class_name = f"{db_type.value}_ChatHistoryRepository"

            repository_class = import_class_with_fallback(module_name, class_name)
            self.chat_history_repo = repository_class(config=config)
        except ValueError as e:
            raise ValueError(f"Unsupported database type: {db_type_val}") from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize chat history repository: {e}"
            ) from e

    async def update_thread(
        self,
        thread_id: str,
        name: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        kwargs = {
            "thread_id": thread_id,
            "name": name,
            "user_id": user_id,
            "metadata": metadata,
        }
        if tags is not None:
            kwargs["tags"] = tags
        return await self.chat_history_repo.update_thread(**kwargs)

    async def add_user(self, identifier: str) -> User:
        return await self.chat_history_repo.add_user(identifier)

    async def add_step(self, step_dict: StepDict) -> str:
        return await self.chat_history_repo.add_step(step_dict)

    async def get_user(self, identifier: str) -> User | None:
        return await self.chat_history_repo.get_user(identifier)

    async def add_message(self, message: Message) -> str:
        return await self.chat_history_repo.add_message(message)

    async def add_memory(self, memory: Message) -> str:
        return await self.chat_history_repo.add_memory(memory)

    async def get_message(self, message_id: str, thread_id: str) -> Message | None:
        return await self.chat_history_repo.get_message(
            message_id=message_id,
            thread_id=thread_id,
        )

    async def get_memory(self, message_id: str, thread_id: str) -> Message | None:
        return await self.chat_history_repo.get_memory(
            message_id=message_id,
            thread_id=thread_id,
        )

    async def update_memory(self) -> Message | None:
        return await self.chat_history_repo.update_memory()

    async def get_thread_messages(self, thread_id: str) -> list[Message]:
        return await self.chat_history_repo.get_thread_messages(
            thread_id=thread_id,
        )

    async def get_thread_memory(self, thread_id: str) -> Optional[list[ThreadDict]]:
        return await self.chat_history_repo.get_thread_memory(
            thread_id=thread_id,
        )

    async def get_threads_for_user(
        self, identifier: str, thread_id: Optional[str]
    ) -> Optional[List[ThreadDict]]:
        return await self.chat_history_repo.get_threads_for_user(
            identifier=identifier,
            thread_id=thread_id,
        )

    async def update_message_feedback(
        self, message_id: str, thread_id: str, positive_feedback: bool | None
    ) -> None:
        return await self.chat_history_repo.update_message_feedback(
            message_id=message_id,
            thread_id=thread_id,
            positive_feedback=positive_feedback,
        )

    async def update_memory_feedback(
        self, message_id: str, thread_id: str, positive_feedback: bool | None
    ) -> None:
        return await self.chat_history_repo.update_memory_feedback(
            message_id=message_id,
            thread_id=thread_id,
            positive_feedback=positive_feedback,
        )

    async def update_message_content_filter_results(
        self, message_id: str, thread_id: str, content_filter_results: dict[str, object]
    ) -> None:
        return await self.chat_history_repo.update_message_content_filter_results(
            message_id=message_id,
            thread_id=thread_id,
            content_filter_results=content_filter_results,
        )

    async def update_memory_content_filter_results(
        self, message_id: str, thread_id: str, content_filter_results: dict[str, object]
    ) -> None:
        return await self.chat_history_repo.update_memory_content_filter_results(
            message_id=message_id,
            thread_id=thread_id,
            content_filter_results=content_filter_results,
        )

    async def delete_thread(self, thread_id: str) -> None:
        return await self.chat_history_repo.delete_thread(
            thread_id=thread_id,
        )

    async def delete_thread_memory(self, thread_id: str) -> None:
        return await self.chat_history_repo.delete_thread_memory(
            thread_id=thread_id,
        )

    async def delete_user_memory(self, user_id: str) -> None:
        return await self.chat_history_repo.delete_user_memory(
            user_id=user_id,
        )

    async def get_messages(self, thread_id: str) -> List[Message]:
        """Implementation for the interface method"""
        return await self.get_thread_messages(thread_id=thread_id)

    async def get_thread_metadata(self, thread_id: str) -> Dict[str, Any]:
        """Implementation for the interface method"""
        # This might need proper implementation based on repository capabilities
        threads = await self.chat_history_repo.get_thread_messages(thread_id=thread_id)
        if threads and isinstance(threads, list) and len(threads) > 0:
            thread = threads[0]
            if hasattr(thread, "metadata"):
                return thread.metadata
        return {}
