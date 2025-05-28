"""
Chat history repository implementation using a database client.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ingenious.domain.interfaces.repository.chat_history_repository import (
    IChatHistoryRepository,
)
from ingenious.domain.interfaces.repository.database import DatabaseInterface
from ingenious.domain.model.chat.message import Message

logger = logging.getLogger(__name__)


class DatabaseChatHistoryRepository(IChatHistoryRepository):
    """Chat history repository implementation using a database client."""

    def __init__(self, database_client: DatabaseInterface):
        """
        Initialize the chat history repository.

        Args:
            database_client: The database client
        """
        self.db = database_client

    async def _ensure_tables_exist(self) -> None:
        """Ensure the necessary tables exist."""
        # Create threads table
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS threads (
                id TEXT PRIMARY KEY,
                title TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Create messages table
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                thread_id TEXT,
                role TEXT,
                content TEXT,
                created_at TEXT,
                feedback INTEGER,
                FOREIGN KEY (thread_id) REFERENCES threads (id)
            )
        """)

    async def _get_or_create_thread(self, thread_id: str) -> None:
        """
        Get or create a thread.

        Args:
            thread_id: The thread ID
        """
        # Check if thread exists
        threads = await self.db.query(
            "SELECT id FROM threads WHERE id = :thread_id", {"thread_id": thread_id}
        )

        # Create thread if it doesn't exist
        if not threads:
            now = datetime.utcnow().isoformat()
            await self.db.insert(
                "threads",
                {
                    "id": thread_id,
                    "title": f"Thread {thread_id}",
                    "created_at": now,
                    "updated_at": now,
                },
            )

    async def add_message(self, message: Message) -> str:
        """
        Add a message to the chat history.

        Args:
            message: The message to add

        Returns:
            The message ID
        """
        try:
            # Ensure tables exist
            await self._ensure_tables_exist()

            # Get or create thread
            await self._get_or_create_thread(message.thread_id)

            # Prepare message data
            message_id = message.id or str(uuid.uuid4())
            created_at = message.created_at or datetime.utcnow().isoformat()

            # Convert content to JSON if it's not a string
            content = (
                message.content
                if isinstance(message.content, str)
                else json.dumps(message.content)
            )

            # Insert message
            await self.db.insert(
                "messages",
                {
                    "id": message_id,
                    "thread_id": message.thread_id,
                    "role": message.role,
                    "content": content,
                    "created_at": created_at,
                    "feedback": None,
                },
            )

            # Update thread updated_at
            await self.db.update(
                "threads", "id", message.thread_id, {"updated_at": created_at}
            )

            return message_id
        except Exception as e:
            logger.error(f"Failed to add message: {e}")
            raise

    async def get_messages(self, thread_id: str) -> List[Message]:
        """
        Get all messages in a thread.

        Args:
            thread_id: The thread ID

        Returns:
            A list of messages
        """
        try:
            # Ensure tables exist
            await self._ensure_tables_exist()

            # Get messages
            messages_data = await self.db.query(
                "SELECT * FROM messages WHERE thread_id = :thread_id ORDER BY created_at",
                {"thread_id": thread_id},
            )

            # Convert to Message objects
            messages = []
            for msg_data in messages_data:
                # Parse content
                content = msg_data["content"]
                try:
                    content = json.loads(content)
                except (json.JSONDecodeError, TypeError):
                    # Keep as string if not valid JSON
                    pass

                # Create Message object
                message = Message(
                    id=msg_data["id"],
                    thread_id=msg_data["thread_id"],
                    role=msg_data["role"],
                    content=content,
                    created_at=msg_data["created_at"],
                )
                messages.append(message)

            return messages
        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return []

    async def get_thread_metadata(self, thread_id: str) -> Dict[str, Any]:
        """
        Get metadata for a thread.

        Args:
            thread_id: The thread ID

        Returns:
            The thread metadata
        """
        try:
            # Ensure tables exist
            await self._ensure_tables_exist()

            # Get thread
            threads = await self.db.query(
                "SELECT * FROM threads WHERE id = :thread_id", {"thread_id": thread_id}
            )

            if not threads:
                return {}

            return threads[0]
        except Exception as e:
            logger.error(f"Failed to get thread metadata: {e}")
            return {}

    async def update_message_feedback(
        self, message_id: str, thread_id: str, positive_feedback: Optional[bool]
    ) -> None:
        """
        Update feedback for a message.

        Args:
            message_id: The message ID
            thread_id: The thread ID
            positive_feedback: The feedback (True for positive, False for negative, None for neutral)
        """
        try:
            # Ensure tables exist
            await self._ensure_tables_exist()

            # Convert feedback to integer
            feedback_value = None
            if positive_feedback is not None:
                feedback_value = 1 if positive_feedback else -1

            # Update message
            await self.db.update(
                "messages", "id", message_id, {"feedback": feedback_value}
            )
        except Exception as e:
            logger.error(f"Failed to update message feedback: {e}")

    async def delete_thread(self, thread_id: str) -> None:
        """
        Delete a thread and all its messages.

        Args:
            thread_id: The thread ID
        """
        try:
            # Ensure tables exist
            await self._ensure_tables_exist()

            # Delete messages
            await self.db.execute(
                "DELETE FROM messages WHERE thread_id = :thread_id",
                {"thread_id": thread_id},
            )

            # Delete thread
            await self.db.delete("threads", "id", thread_id)
        except Exception as e:
            logger.error(f"Failed to delete thread: {e}")

    async def list_threads(self) -> List[Dict[str, Any]]:
        """
        List all threads.

        Returns:
            A list of thread metadata
        """
        try:
            # Ensure tables exist
            await self._ensure_tables_exist()

            # Get threads
            return await self.db.query("SELECT * FROM threads ORDER BY updated_at DESC")
        except Exception as e:
            logger.error(f"Failed to list threads: {e}")
            return []
