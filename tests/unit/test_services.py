"""
Unit tests for the services module.
"""

import os
from unittest.mock import AsyncMock, Mock, mock_open, patch

import pytest

from ingenious.models.chat import ChatRequest, ChatResponse
from ingenious.models.message_feedback import (
    MessageFeedbackRequest,
)
from ingenious.services.chat_service import ChatService
from ingenious.services.memory_manager import (
    LegacyMemoryManager,
    MemoryManager,
    get_memory_manager,
)
from ingenious.services.message_feedback_service import MessageFeedbackService


class TestChatService:
    """Test cases for ChatService class."""

    def test_init_with_valid_workflow(self):
        """Test ChatService initialization with valid workflow."""
        with patch(
            "ingenious.services.chat_service.import_class_with_fallback"
        ) as mock_import:
            mock_service_class = Mock()
            mock_import.return_value = mock_service_class

            mock_config = Mock()
            mock_repository = Mock()
            service = ChatService(
                "test_workflow", mock_repository, "test_flow", mock_config
            )
            assert service.service_class is not None

    def test_init_with_invalid_workflow(self):
        """Test ChatService initialization with invalid workflow."""
        with patch(
            "ingenious.services.chat_service.import_class_with_fallback"
        ) as mock_import:
            mock_import.side_effect = ValueError("Module not found")

            mock_config = Mock()
            mock_repository = Mock()
            with pytest.raises(Exception, match="An unexpected error occurred"):
                ChatService(
                    "invalid_workflow", mock_repository, "test_flow", mock_config
                )

    @pytest.mark.asyncio
    async def test_get_chat_response_success(self):
        """Test successful chat response generation."""
        with patch(
            "ingenious.services.chat_service.import_class_with_fallback"
        ) as mock_import:
            mock_service_class = Mock()
            mock_service_instance = Mock()
            mock_service_instance.get_chat_response = AsyncMock(
                return_value=ChatResponse(
                    thread_id="test_thread",
                    message_id="test_message_id",
                    agent_response="Test response",
                    token_count=100,
                    max_token_count=1000,
                )
            )
            mock_service_class.return_value = mock_service_instance
            mock_import.return_value = mock_service_class

            mock_config = Mock()
            mock_repository = Mock()
            service = ChatService(
                "test_workflow", mock_repository, "test_flow", mock_config
            )
            request = ChatRequest(
                user_prompt="Test message", conversation_flow="test_flow"
            )

            response = await service.get_chat_response(request)
            assert response.agent_response == "Test response"
            assert response.thread_id == "test_thread"
            mock_service_instance.get_chat_response.assert_called_once_with(request)


class TestMemoryManager:
    """Test cases for MemoryManager class."""

    def test_get_memory_file_path(self):
        """Test memory file path generation."""
        mock_config = Mock()
        mock_config.chat_history.memory_path = "memory"

        with patch("ingenious.services.memory_manager.FileStorage"):
            manager = MemoryManager(mock_config)
            path, name = manager._get_memory_file_path("test_thread")
            expected_path = "memory/test_thread"
            expected_name = "context.md"
            assert path == expected_path
            assert name == expected_name

    @pytest.mark.asyncio
    async def test_read_memory_file_exists(self):
        """Test reading memory when file exists."""
        mock_config = Mock()
        mock_config.chat_history.memory_path = "memory"
        test_content = "Test memory content"

        with patch(
            "ingenious.services.memory_manager.FileStorage"
        ) as mock_storage_class:
            mock_storage = AsyncMock()
            mock_storage.read_file = AsyncMock(return_value=test_content)
            mock_storage_class.return_value = mock_storage

            manager = MemoryManager(mock_config)
            result = await manager.read_memory("test_thread")
            assert result == test_content

    @pytest.mark.asyncio
    async def test_read_memory_file_not_exists(self):
        """Test reading memory when file doesn't exist."""
        mock_config = Mock()
        mock_config.chat_history.memory_path = "memory"

        with patch(
            "ingenious.services.memory_manager.FileStorage"
        ) as mock_storage_class:
            mock_storage = Mock()
            mock_storage.read_file = AsyncMock(return_value="")
            mock_storage_class.return_value = mock_storage

            manager = MemoryManager(mock_config)
            result = await manager.read_memory("test_thread")
            assert result == ""

    @pytest.mark.asyncio
    async def test_write_memory_success(self):
        """Test writing memory successfully."""
        mock_config = Mock()
        mock_config.chat_history.memory_path = "memory"
        test_content = "Test memory content"

        with patch(
            "ingenious.services.memory_manager.FileStorage"
        ) as mock_storage_class:
            mock_storage = Mock()
            mock_storage.write_file = AsyncMock(return_value=True)
            mock_storage_class.return_value = mock_storage

            manager = MemoryManager(mock_config)
            result = await manager.write_memory(test_content, "test_thread")
            assert result

    @pytest.mark.asyncio
    async def test_maintain_memory_within_limit(self):
        """Test memory maintenance when content is within limit."""
        mock_config = Mock()
        mock_config.chat_history.memory_path = "memory"
        test_content = "Short content"

        with patch(
            "ingenious.services.memory_manager.FileStorage"
        ) as mock_storage_class:
            mock_storage = Mock()
            mock_storage_class.return_value = mock_storage

            manager = MemoryManager(mock_config)
            with (
                patch.object(manager, "read_memory", return_value=""),
                patch.object(manager, "write_memory") as mock_write,
            ):
                await manager.maintain_memory(test_content, max_words=10)
                mock_write.assert_called_once()

    @pytest.mark.asyncio
    async def test_maintain_memory_exceeds_limit(self):
        """Test memory maintenance when content exceeds limit."""
        mock_config = Mock()
        mock_config.chat_history.memory_path = "memory"
        test_content = "This is a very long content that exceeds the word limit"

        with patch(
            "ingenious.services.memory_manager.FileStorage"
        ) as mock_storage_class:
            mock_storage = Mock()
            mock_storage_class.return_value = mock_storage

            manager = MemoryManager(mock_config)
            with (
                patch.object(manager, "read_memory", return_value=""),
                patch.object(manager, "write_memory") as mock_write,
            ):
                await manager.maintain_memory(test_content, max_words=5)
                mock_write.assert_called_once()
                # Check that content was truncated
                written_content = mock_write.call_args[0][0]
                assert len(written_content.split()) <= 5

    @pytest.mark.asyncio
    async def test_delete_memory_success(self):
        """Test deleting memory successfully."""
        mock_config = Mock()
        mock_config.chat_history.memory_path = "memory"

        with patch(
            "ingenious.services.memory_manager.FileStorage"
        ) as mock_storage_class:
            mock_storage = Mock()
            mock_storage.delete_file = AsyncMock(return_value=True)
            mock_storage_class.return_value = mock_storage

            manager = MemoryManager(mock_config)
            result = await manager.delete_memory("test_thread")
            assert result

    @pytest.mark.asyncio
    async def test_delete_memory_file_not_exists(self):
        """Test deleting memory when file doesn't exist."""
        mock_config = Mock()
        mock_config.chat_history.memory_path = "memory"

        with patch(
            "ingenious.services.memory_manager.FileStorage"
        ) as mock_storage_class:
            mock_storage = Mock()
            mock_storage.delete_file = AsyncMock(return_value=True)
            mock_storage_class.return_value = mock_storage

            manager = MemoryManager(mock_config)
            result = await manager.delete_memory("test_thread")
            assert result


class TestLegacyMemoryManager:
    """Test cases for LegacyMemoryManager class."""

    def test_init_with_storage_client(self):
        """Test LegacyMemoryManager initialization."""
        memory_path = "/tmp/memory"
        manager = LegacyMemoryManager(memory_path)
        assert manager.memory_path == memory_path

    def test_get_memory_file_path(self):
        """Test memory file path generation."""
        memory_path = "/tmp/memory"
        manager = LegacyMemoryManager(memory_path)

        path = manager._get_memory_file_path("test_thread")
        expected = os.path.join("/tmp/memory", "test_thread", "context.md")
        assert path == expected

    def test_read_memory_success(self):
        """Test reading memory successfully."""
        memory_path = "/tmp/memory"
        manager = LegacyMemoryManager(memory_path)

        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data="Test content")),
        ):
            result = manager.read_memory("test_thread")
            assert result == "Test content"

    def test_write_memory_success(self):
        """Test writing memory successfully."""
        memory_path = "/tmp/memory"
        manager = LegacyMemoryManager(memory_path)

        with (
            patch("os.makedirs") as mock_makedirs,
            patch("builtins.open", mock_open()) as mock_file,
        ):
            result = manager.write_memory("Test content", "test_thread")
            assert result
            mock_makedirs.assert_called_once()
            mock_file.assert_called_once()


class TestMessageFeedbackService:
    """Test cases for MessageFeedbackService class."""

    @pytest.mark.asyncio
    async def test_update_message_feedback_success(self):
        """Test successful message feedback update."""
        mock_repo = Mock()
        mock_repo.get_message = AsyncMock(return_value=Mock(user_id="test_user_id"))
        mock_repo.update_message_feedback = AsyncMock()

        service = MessageFeedbackService(mock_repo)
        feedback = MessageFeedbackRequest(
            thread_id="test_thread_id",
            message_id="test_message_id",
            user_id="test_user_id",
            positive_feedback=True,
        )

        result = await service.update_message_feedback("test_message_id", feedback)
        assert result.message == "Feedback submitted for message test_message_id."

    @pytest.mark.asyncio
    async def test_update_message_feedback_failure(self):
        """Test message feedback update failure."""
        mock_repo = Mock()
        mock_repo.get_message = AsyncMock(return_value=None)

        service = MessageFeedbackService(mock_repo)
        feedback = MessageFeedbackRequest(
            thread_id="test_thread_id",
            message_id="test_message_id",
            user_id="test_user_id",
            positive_feedback=False,
        )

        with pytest.raises(ValueError, match="Message test_message_id not found"):
            await service.update_message_feedback("test_message_id", feedback)


class TestMemoryManagerFactory:
    """Test cases for memory manager factory functions."""

    def test_get_memory_manager_default(self):
        """Test getting default memory manager."""
        mock_config = Mock()
        mock_config.file_storage.storage_type = "azure_blob"

        with patch("ingenious.services.memory_manager.FileStorage"):
            manager = get_memory_manager(mock_config)
            assert isinstance(manager, MemoryManager)

    def test_get_memory_manager_with_storage(self):
        """Test getting memory manager with storage client."""
        mock_config = Mock()
        mock_config.file_storage.storage_type = "local"
        mock_config.chat_history.memory_path = "/tmp/memory"

        with patch("ingenious.services.memory_manager.FileStorage"):
            manager = get_memory_manager(mock_config)
            assert isinstance(manager, MemoryManager)
