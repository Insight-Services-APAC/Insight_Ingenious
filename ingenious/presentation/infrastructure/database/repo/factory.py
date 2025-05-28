"""
Factory for creating database repository implementations.
"""

from ingenious.domain.interfaces.repository.chat_history_repository import (
    IChatHistoryRepository,
)
from ingenious.domain.interfaces.repository.database import DatabaseInterface
from ingenious.presentation.infrastructure.database.repo.chat_history_repository import (
    DatabaseChatHistoryRepository,
)


class DatabaseRepositoryFactory:
    """Factory for creating database repository implementations."""

    @staticmethod
    def create_chat_history_repository(
        database_client: DatabaseInterface,
    ) -> IChatHistoryRepository:
        """
        Create a chat history repository implementation.

        Args:
            database_client: The database client

        Returns:
            A chat history repository implementation
        """
        return DatabaseChatHistoryRepository(database_client)
