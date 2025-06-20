from typing import Optional
from ..domain.entities import Message, Thread
from ..domain.services import IMessageRepository, IThreadRepository


class InMemoryMessageRepository(IMessageRepository):
    """In-memory implementation of message repository for testing/development."""

    def __init__(self):
        self._messages: dict[str, Message] = {}
        self._thread_messages: dict[str, list[str]] = {}

    async def save_message(self, message: Message) -> None:
        """Save a message to in-memory storage."""
        self._messages[message.message_id] = message

        if message.thread_id:
            if message.thread_id not in self._thread_messages:
                self._thread_messages[message.thread_id] = []
            self._thread_messages[message.thread_id].append(message.message_id)

    async def get_message(self, message_id: str) -> Optional[Message]:
        """Retrieve a message by ID."""
        return self._messages.get(message_id)

    async def get_messages_by_thread(self, thread_id: str) -> list[Message]:
        """Get all messages for a thread."""
        message_ids = self._thread_messages.get(thread_id, [])
        return [
            self._messages[msg_id] for msg_id in message_ids if msg_id in self._messages
        ]


class InMemoryThreadRepository(IThreadRepository):
    """In-memory implementation of thread repository for testing/development."""

    def __init__(self):
        self._threads: dict[str, Thread] = {}
        self._user_threads: dict[str, list[str]] = {}

    async def save_thread(self, thread: Thread) -> None:
        """Save a thread to in-memory storage."""
        self._threads[thread.thread_id] = thread

        if thread.user_id:
            if thread.user_id not in self._user_threads:
                self._user_threads[thread.user_id] = []
            if thread.thread_id not in self._user_threads[thread.user_id]:
                self._user_threads[thread.user_id].append(thread.thread_id)

    async def get_thread(self, thread_id: str) -> Optional[Thread]:
        """Retrieve a thread by ID."""
        return self._threads.get(thread_id)

    async def get_threads_by_user(self, user_id: str) -> list[Thread]:
        """Get all threads for a user."""
        thread_ids = self._user_threads.get(user_id, [])
        return [
            self._threads[thread_id]
            for thread_id in thread_ids
            if thread_id in self._threads
        ]
