"""
Factory module for the application layer.

This module provides factories for creating service and repository instances
with proper dependency injection.
"""

from ingenious.application.repository.chat_history_repository import (
    ChatHistoryRepository,
)
from ingenious.application.repository.file_repository import FileRepository
from ingenious.application.service.chat_service import ChatService
from ingenious.application.service.message_feedback_service import (
    MessageFeedbackService,
)
from ingenious.common.di.service_provider_factory import ServiceProviderFactory
from ingenious.domain.interfaces.repository.chat_history_repository import (
    IChatHistoryRepository,
)
from ingenious.domain.interfaces.repository.file_repository import IFileRepository
from ingenious.domain.interfaces.service.chat_service import IChatService
from ingenious.domain.interfaces.service.message_feedback_service import (
    IMessageFeedbackService,
)
from ingenious.domain.model.config import Config
from ingenious.domain.model.database_client import DatabaseClientType


class Factory:
    """Factory for creating service and repository instances with proper dependency injection"""

    def __init__(self, config: Config):
        """
        Initialize the Factory.

        Args:
            config: The application configuration
        """
        self.config = config

        # Initialize service provider factories
        self.chat_history_repository_factory = ServiceProviderFactory(
            interface_type=IChatHistoryRepository,
            implementation_resolver=self._create_chat_history_repository,
            config=config,
        )

        self.file_repository_factory = ServiceProviderFactory(
            interface_type=IFileRepository,
            implementation_resolver=self._create_file_repository,
            config=config,
        )

        self.chat_service_factory = ServiceProviderFactory(
            interface_type=IChatService,
            implementation_resolver=self._create_chat_service,
            config=config,
        )

        self.message_feedback_service_factory = ServiceProviderFactory(
            interface_type=IMessageFeedbackService,
            implementation_resolver=self._create_message_feedback_service,
            config=config,
        )

    def _create_chat_history_repository(self, _=None) -> IChatHistoryRepository:
        """
        Create a chat history repository.

        Returns:
            A chat history repository
        """
        db_type_val = self.config.chat_history.database_type.lower()
        try:
            db_type = DatabaseClientType(db_type_val)
        except ValueError:
            raise ValueError(f"Unknown database type: {db_type_val}")

        return ChatHistoryRepository(db_type=db_type, config=self.config)

    def _create_file_repository(self, category: str = "revisions") -> IFileRepository:
        """
        Create a file repository.

        Args:
            category: The category of files to store

        Returns:
            A file repository
        """
        return FileRepository(config=self.config, category=category)

    def _create_chat_service(self, conversation_flow: str = "") -> IChatService:
        """
        Create a chat service.

        Args:
            conversation_flow: The conversation flow to use

        Returns:
            A chat service
        """
        return ChatService(
            chat_service_type=self.config.chat_service.type,
            chat_history_repository=self.get_chat_history_repository(),
            conversation_flow=conversation_flow,
            config=self.config,
        )

    def _create_message_feedback_service(self, _=None) -> IMessageFeedbackService:
        """
        Create a message feedback service.

        Returns:
            A message feedback service
        """
        return MessageFeedbackService(
            chat_history_repository=self.get_chat_history_repository()
        )

    def get_chat_history_repository(self) -> IChatHistoryRepository:
        """Get a chat history repository instance"""
        return self.chat_history_repository_factory.get()

    def get_file_repository(self, category: str = "revisions") -> IFileRepository:
        """Get a file repository instance"""
        return self.file_repository_factory.get(category)

    def get_chat_service(self, conversation_flow: str = "") -> IChatService:
        """Get a chat service instance"""
        return self.chat_service_factory.get(conversation_flow)

    def get_message_feedback_service(self) -> IMessageFeedbackService:
        """Get a message feedback service instance"""
        return self.message_feedback_service_factory.get()
