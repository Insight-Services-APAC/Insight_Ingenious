from datetime import datetime, timezone
import importlib
import uuid
from ingenious.models.database_client import DatabaseClientType
from ingenious.models.message import Message
import ingenious.config.config as Config
from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    Protocol,
    TypedDict,
    TypeVar,
    Union,
)
from uuid import UUID
from dataclasses import dataclass


class IChatHistoryRepository(ABC):
    
    TrueStepType = Literal["run", "tool", "llm", "embedding", "retrieval", "rerank", "undefined"]

    MessageStepType = Literal["user_message", "assistant_message", "system_message"]

    StepType = Union[TrueStepType, MessageStepType]

    mime_types = {
        "text": "text/plain",
        "tasklist": "application/json",
        "plotly": "application/json",
    }

    ElementType = Literal[
        "image", "text", "pdf", "tasklist", "audio", "video", "file", "plotly", "component"
    ]
    ElementDisplay = Literal["inline", "side", "page"]
    ElementSize = Literal["small", "medium", "large"]

    @dataclass
    class ElementDict(TypedDict):
        id: str
        threadId: Optional[str]
        type: 'IChatHistoryRepository.ElementType'
        chainlitKey: Optional[str]
        url: Optional[str]
        objectKey: Optional[str]
        name: str
        display: 'IChatHistoryRepository.ElementDisplay'
        size: Optional['IChatHistoryRepository.ElementSize']
        language: Optional[str]
        page: Optional[int]
        autoPlay: Optional[bool]
        playerConfig: Optional[dict]
        forId: Optional[str]
        mime: Optional[str]

    @dataclass
    class ChatHistory:
        user_id: str
        thread_id: str
        message_id: str
        positive_feedback: Optional[bool]
        timestamp: str
        role: str
        content: str
        content_filter_results: Optional[str]
        tool_calls: Optional[str]
        tool_call_id: Optional[str]
        tool_call_function: Optional[str]

    @dataclass
    class User:
        id: UUID
        identifier: str
        metadata: dict
        createdAt: Optional[str]

    @dataclass
    class Thread:
        id: UUID
        createdAt: Optional[str]
        name: Optional[str]
        userId: UUID
        userIdentifier: Optional[str]
        tags: Optional[List[str]]
        metadata: Optional[dict]

    @dataclass
    class Step:
        id: UUID
        name: str
        type: str
        threadId: UUID
        parentId: Optional[UUID]
        disableFeedback: bool
        streaming: bool
        waitForAnswer: Optional[bool]
        isError: Optional[bool]
        metadata: Optional[dict]
        tags: Optional[List[str]]
        input: Optional[str]
        output: Optional[str]
        createdAt: Optional[str]
        start: Optional[str]
        end: Optional[str]
        generation: Optional[dict]
        showInput: Optional[str]
        language: Optional[str]
        indent: Optional[int]

    @dataclass
    class Element:
        id: UUID
        threadId: Optional[UUID]
        type: Optional[str]
        url: Optional[str]
        chainlitKey: Optional[str]
        name: str
        display: Optional[str]
        objectKey: Optional[str]
        size: Optional[str]
        page: Optional[int]
        language: Optional[str]
        forId: Optional[UUID]
        mime: Optional[str]

    @dataclass
    class Feedback:
        id: UUID
        forId: UUID
        threadId: UUID
        value: int
        comment: Optional[str]
    
    @dataclass
    class FeedbackDict(TypedDict):
        forId: str
        id: Optional[str]
        value: Literal[0, 1]
        comment: Optional[str]

    @dataclass
    class StepDict(TypedDict, total=False):
        name: str
        type: 'IChatHistoryRepository.StepType'
        id: str
        threadId: str
        parentId: Optional[str]
        disableFeedback: bool
        streaming: bool
        waitForAnswer: Optional[bool]
        isError: Optional[bool]
        metadata: Dict
        tags: Optional[List[str]]
        input: str
        output: str
        createdAt: Optional[str]
        start: Optional[str]
        end: Optional[str]
        generation: Optional[Dict]
        showInput: Optional[Union[bool, str]]
        language: Optional[str]
        indent: Optional[int]
        feedback: Optional['IChatHistoryRepository.FeedbackDict']

    @dataclass
    class ThreadDict(TypedDict):
        id: str
        createdAt: str
        name: Optional[str]
        userId: Optional[str]
        userIdentifier: Optional[str]
        tags: Optional[List[str]]
        metadata: Optional[Dict]
        steps: List['IChatHistoryRepository.StepDict']
        elements: Optional[List['IChatHistoryRepository.ElementDict']]
    
    def get_now(self):
        return datetime.now(timezone.utc)

    def get_now_as_string(self):
        return self.get_now().strftime("%Y-%m-%d %H:%M:%S.%f%z")
    
    @abstractmethod
    async def update_thread(
        self,
        thread_id: str,
        name: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        pass
    
    @abstractmethod
    async def add_message(self, message: Message) -> str:
        """ adds a message to the chat history """
        pass

    @abstractmethod
    async def add_user(self, identifier: str) -> User:
        """ adds a user to the chat history database """
        pass

    @abstractmethod
    async def get_user(self, identifier: str) -> User | None:
        """ gets a user from the chat history database """
        pass

    @abstractmethod
    async def get_message(self, message_id: str, thread_id: str) -> Message | None:
        """ gets a message from the chat history """
        pass

    @abstractmethod
    async def get_thread_messages(self, thread_id: str) -> list[Message]:
        pass
    
    @abstractmethod
    async def get_threads_for_user(self, identifier: str, thread_id: Optional[str]) -> Optional[List['IChatHistoryRepository.ThreadDict']]:
        pass

    @abstractmethod
    async def update_message_feedback(self, message_id: str, thread_id: str, positive_feedback: bool | None) -> None:
        pass

    @abstractmethod
    async def update_message_content_filter_results(
            self, message_id: str, thread_id: str, content_filter_results: dict[str, object]) -> None:
        pass

    @abstractmethod
    async def delete_thread(self, thread_id: str) -> None:
        pass


class ChatHistoryRepository:
    
    def __init__(self, db_type: DatabaseClientType, config: Config.Config):
        module_name = f"ingenious.db.{db_type.value.lower()}"
        class_name = f"{db_type.value.lower()}_ChatHistoryRepository"

        try:
            module = importlib.import_module(module_name)
            repository_class = getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Unsupported database client type: {module_name}.{class_name}") from e

        self.repository = repository_class(config=config)

    async def update_thread(
            self,
            thread_id: str,
            name: Optional[str] = None,
            user_id: Optional[str] = None,
            metadata: Optional[Dict] = None,
            tags: Optional[List[str]] = None
    ) -> str:
        return await self.repository.update_thread(
            thread_id=thread_id,
            name=name,
            user_id=user_id,
            metadata=metadata,
        )


    async def add_user(self, identifier: str) -> IChatHistoryRepository.User:
        return await self.repository.add_user(identifier)

    async def add_step(self, step_dict: IChatHistoryRepository.StepDict) -> str:
        return await self.repository.add_step(step_dict)

    async def get_user(self, identifier: str) -> IChatHistoryRepository.User | None:
        return await self.repository.get_user(identifier)
    
    async def add_message(self, message: Message) -> str:
        return await self.repository.add_message(message)

    async def add_memory(self, memory: Message) -> str:
        return await self.repository.add_memory(memory)

    async def get_message(self, message_id: str, thread_id: str) -> Message | None:
        return await self.repository.get_message(message_id, thread_id)

    async def get_memory(self, message_id: str, thread_id: str) -> Message | None:
        return await self.repository.get_memory(message_id, thread_id)

    async def update_memory(self) -> Message | None:
        return await self.repository.update_memory()

    async def get_thread_messages(self, thread_id: str) -> Optional[list[IChatHistoryRepository.ThreadDict]]:
        return await self.repository.get_thread_messages(thread_id)

    async def get_thread_memory(self, thread_id: str) -> Optional[list[IChatHistoryRepository.ThreadDict]]:
        return await self.repository.get_thread_memory(thread_id)
    
    async def get_threads_for_user(self, identifier: str, thread_id: Optional[str]) -> Optional[List[IChatHistoryRepository.ThreadDict]]:
        return await self.repository.get_threads_for_user(identifier, thread_id)

    async def update_message_feedback(self, message_id: str, thread_id: str, positive_feedback: bool | None) -> None:
        return await self.repository.update_message_feedback(message_id, thread_id, positive_feedback)

    async def update_memory_feedback(self, message_id: str, thread_id: str, positive_feedback: bool | None) -> None:
        return await self.repository.update_memory_feedback(message_id, thread_id, positive_feedback)

    async def update_message_content_filter_results(
            self, message_id: str, thread_id: str, content_filter_results: dict[str, object]) -> None:
        return await self.repository.update_message_content_filter_results(message_id, thread_id, content_filter_results)

    async def update_memory_content_filter_results(
            self, message_id: str, thread_id: str, content_filter_results: dict[str, object]) -> None:
        return await self.repository.update_memory_content_filter_results(message_id, thread_id, content_filter_results)

    async def delete_thread(self, thread_id: str) -> None:
        return await self.repository.delete_thread(thread_id)

    async def delete_thread_memory(self, thread_id: str) -> None:
        return await self.repository.delete_thread_memory(thread_id)