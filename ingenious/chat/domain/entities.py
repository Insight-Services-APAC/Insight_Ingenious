from datetime import datetime
from typing import Optional
from uuid import uuid4


class Message:
    """Domain entity representing a chat message."""

    def __init__(
        self,
        content: str,
        user_id: str,
        thread_id: Optional[str] = None,
        message_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        event_type: Optional[str] = None,
    ):
        self.message_id = message_id or str(uuid4())
        self.thread_id = thread_id
        self.content = content
        self.user_id = user_id
        self.timestamp = timestamp or datetime.utcnow()
        self.event_type = event_type

    def __eq__(self, other):
        if not isinstance(other, Message):
            return False
        return self.message_id == other.message_id

    def __str__(self):
        return f"Message(id={self.message_id}, user={self.user_id}, content='{self.content[:50]}...')"


class Thread:
    """Domain entity representing a conversation thread."""

    def __init__(
        self,
        thread_id: Optional[str] = None,
        user_id: Optional[str] = None,
        topic: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        self.thread_id = thread_id or str(uuid4())
        self.user_id = user_id
        self.topic = topic
        self.created_at = created_at or datetime.utcnow()
        self.messages: list[Message] = []
        self.memory_summary: Optional[str] = None

    def add_message(self, message: Message) -> None:
        """Add a message to the thread."""
        message.thread_id = self.thread_id
        self.messages.append(message)

    def get_recent_messages(self, limit: int = 10) -> list[Message]:
        """Get the most recent messages from the thread."""
        return sorted(self.messages, key=lambda m: m.timestamp)[-limit:]

    def __eq__(self, other):
        if not isinstance(other, Thread):
            return False
        return self.thread_id == other.thread_id

    def __str__(self):
        return f"Thread(id={self.thread_id}, messages={len(self.messages)})"


class ChatSession:
    """Domain entity representing a chat session."""

    def __init__(
        self,
        user_id: str,
        conversation_flow: str,
        session_id: Optional[str] = None,
    ):
        self.session_id = session_id or str(uuid4())
        self.user_id = user_id
        self.conversation_flow = conversation_flow
        self.created_at = datetime.utcnow()
        self.threads: dict[str, Thread] = {}

    def get_or_create_thread(self, thread_id: Optional[str] = None) -> Thread:
        """Get an existing thread or create a new one."""
        if thread_id and thread_id in self.threads:
            return self.threads[thread_id]

        new_thread = Thread(thread_id=thread_id, user_id=self.user_id)
        self.threads[new_thread.thread_id] = new_thread
        return new_thread
