"""
Tests for chat history repository in ingenious.application.repository.
"""

import datetime
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ingenious.application.repository.chat_history_repository import (
    ChatHistoryRepository,
)
from ingenious.domain.model.chat import Message, MessageRole
from ingenious.domain.model.config import Config


@pytest.fixture
def mock_config():
    """Create a mock config for testing."""
    mock_config = MagicMock(spec=Config)
    mock_chat_history = MagicMock()
    mock_chat_history.database_type = "sqlite"
    mock_chat_history.database_path = ":memory:"
    type(mock_config).chat_history = mock_chat_history
    return mock_config


@pytest.fixture
def sample_message():
    """Create a sample message for testing."""
    return Message(
        id=str(uuid.uuid4()),
        role=MessageRole.ASSISTANT,
        content="Test message content",
        thread_id=str(uuid.uuid4()),
        created_at=datetime.datetime.now().isoformat(),
        updated_at=datetime.datetime.now().isoformat(),
        user_id="test_user",
        metadata={"test_key": "test_value"},
    )


@pytest.mark.asyncio
class TestChatHistoryRepository:
    """Test suite for ChatHistoryRepository."""

    async def test_initialization(self, mock_config):
        """Test initializing a ChatHistoryRepository."""
        with patch(
            "ingenious.application.repository.chat_history_repository.import_class_with_fallback"
        ) as mock_import:
            mock_db_repo = AsyncMock()
            mock_import.return_value = lambda config: mock_db_repo

            repo = ChatHistoryRepository(mock_config)

            # Check it was initialized with the correct database type
            mock_import.assert_called_once()
            assert "sqlite" in mock_import.call_args[0][0].lower()

            # Check the repository is set up with the mock database repository
            assert repo.chat_history_repo == mock_db_repo

    async def test_add_message(self, mock_config, sample_message):
        """Test adding a message."""
        # Create the repository with a mock database implementation
        mock_db_repo = AsyncMock()
        mock_db_repo.add_message.return_value = "message_id"

        with patch(
            "ingenious.application.repository.chat_history_repository.import_class_with_fallback"
        ) as mock_import:
            mock_import.return_value = lambda config: mock_db_repo
            repo = ChatHistoryRepository(mock_config)

            # Add a message
            result = await repo.add_message(sample_message)

            # Check the result
            assert result == "message_id"
            mock_db_repo.add_message.assert_called_once_with(sample_message)

    async def test_get_message(self, mock_config, sample_message):
        """Test getting a message."""
        # Create the repository with a mock database implementation
        mock_db_repo = AsyncMock()
        mock_db_repo.get_message.return_value = sample_message

        with patch(
            "ingenious.application.repository.chat_history_repository.import_class_with_fallback"
        ) as mock_import:
            mock_import.return_value = lambda config: mock_db_repo
            repo = ChatHistoryRepository(mock_config)

            # Get a message
            result = await repo.get_message(
                message_id=sample_message.id, thread_id=sample_message.thread_id
            )

            # Check the result
            assert result == sample_message
            mock_db_repo.get_message.assert_called_once_with(
                message_id=sample_message.id, thread_id=sample_message.thread_id
            )

    async def test_get_thread_messages(self, mock_config, sample_message):
        """Test getting thread messages."""
        # Create the repository with a mock database implementation
        mock_db_repo = AsyncMock()
        mock_db_repo.get_thread_messages.return_value = [sample_message]

        with patch(
            "ingenious.application.repository.chat_history_repository.import_class_with_fallback"
        ) as mock_import:
            mock_import.return_value = lambda config: mock_db_repo
            repo = ChatHistoryRepository(mock_config)

            # Get thread messages
            result = await repo.get_thread_messages(thread_id=sample_message.thread_id)

            # Check the result
            assert result == [sample_message]
            mock_db_repo.get_thread_messages.assert_called_once_with(
                thread_id=sample_message.thread_id
            )

    async def test_update_message_feedback(self, mock_config):
        """Test updating message feedback."""
        # Create the repository with a mock database implementation
        mock_db_repo = AsyncMock()

        with patch(
            "ingenious.application.repository.chat_history_repository.import_class_with_fallback"
        ) as mock_import:
            mock_import.return_value = lambda config: mock_db_repo
            repo = ChatHistoryRepository(mock_config)

            # Update message feedback
            await repo.update_message_feedback(
                message_id="test_message_id",
                thread_id="test_thread_id",
                positive_feedback=True,
            )

            # Check the method was called
            mock_db_repo.update_message_feedback.assert_called_once_with(
                message_id="test_message_id",
                thread_id="test_thread_id",
                positive_feedback=True,
            )

    async def test_update_message_content_filter_results(self, mock_config):
        """Test updating message content filter results."""
        # Create the repository with a mock database implementation
        mock_db_repo = AsyncMock()

        with patch(
            "ingenious.application.repository.chat_history_repository.import_class_with_fallback"
        ) as mock_import:
            mock_import.return_value = lambda config: mock_db_repo
            repo = ChatHistoryRepository(mock_config)

            # Update message content filter results
            content_filter_results = {
                "filtered": False,
                "categories": {
                    "hate": {"filtered": False, "score": 0.01},
                    "violence": {"filtered": False, "score": 0.02},
                },
            }

            await repo.update_message_content_filter_results(
                message_id="test_message_id",
                thread_id="test_thread_id",
                content_filter_results=content_filter_results,
            )

            # Check the method was called
            mock_db_repo.update_message_content_filter_results.assert_called_once_with(
                message_id="test_message_id",
                thread_id="test_thread_id",
                content_filter_results=content_filter_results,
            )

    async def test_delete_thread(self, mock_config):
        """Test deleting a thread."""
        # Create the repository with a mock database implementation
        mock_db_repo = AsyncMock()

        with patch(
            "ingenious.application.repository.chat_history_repository.import_class_with_fallback"
        ) as mock_import:
            mock_import.return_value = lambda config: mock_db_repo
            repo = ChatHistoryRepository(mock_config)

            # Delete a thread
            await repo.delete_thread(thread_id="test_thread_id")

            # Check the method was called
            mock_db_repo.delete_thread.assert_called_once_with(
                thread_id="test_thread_id"
            )

    async def test_update_thread(self, mock_config):
        """Test updating a thread."""
        # Create the repository with a mock database implementation
        mock_db_repo = AsyncMock()

        with patch(
            "ingenious.application.repository.chat_history_repository.import_class_with_fallback"
        ) as mock_import:
            mock_import.return_value = lambda config: mock_db_repo
            repo = ChatHistoryRepository(mock_config)

            # Update a thread
            await repo.update_thread(
                thread_id="test_thread_id",
                name="Updated Thread Name",
                user_id="user123",
                metadata={"key": "value"},
            )

            # Check the method was called
            mock_db_repo.update_thread.assert_called_once_with(
                thread_id="test_thread_id",
                name="Updated Thread Name",
                user_id="user123",
                metadata={"key": "value"},
            )
