"""
Tests for file repository module in ingenious.application.repository.
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from ingenious.application.repository.file_repository import FileRepository
from ingenious.domain.model.config import Config, FileStorage, FileStorageContainer


@pytest.fixture
def mock_config():
    """Create a mock config for testing."""
    mock_config = MagicMock(spec=Config)
    file_storage = MagicMock(spec=FileStorage)
    mock_revisions = MagicMock(spec=FileStorageContainer)
    mock_revisions.url = "https://example.com/revisions"
    mock_revisions.path = ".files"
    mock_revisions.client_id = "test_client_id"
    mock_revisions.token = "test_token"
    mock_revisions.add_sub_folders = True
    mock_revisions.storage_type = "local"  # Add storage_type for compatibility

    mock_data = MagicMock(spec=FileStorageContainer)
    mock_data.url = "https://example.com/data"
    mock_data.path = ".files"
    mock_data.client_id = "test_client_id"
    mock_data.token = "test_token"
    mock_data.add_sub_folders = True
    mock_data.storage_type = "local"  # Add storage_type for compatibility

    file_storage.revisions = mock_revisions
    file_storage.data = mock_data
    file_storage.storage_type = (
        "local"  # Add storage_type to file_storage itself for DI
    )
    mock_config.file_storage = file_storage
    return mock_config


@pytest.mark.asyncio
class TestFileRepository:
    """Test suite for FileRepository."""

    async def test_initialization(self, mock_config):
        """Test initializing a FileRepository."""
        # Use the "revisions" category
        repo = FileRepository(mock_config, Category="revisions")
        assert repo.fs_config == mock_config.file_storage.revisions
        assert repo.category == "revisions"
        assert repo.add_sub_folders is True

        # Use the "data" category
        repo = FileRepository(mock_config, Category="data")
        assert repo.fs_config == mock_config.file_storage.data
        assert repo.category == "data"
        assert repo.add_sub_folders is True

    async def test_get_base_path(self, mock_config):
        """Test getting the base path."""
        repo = FileRepository(mock_config, Category="revisions")

        # Mock the implementation of the storage Repository
        mock_impl = AsyncMock()
        mock_impl.get_base_path.return_value = "/base/path"
        repo.file_storage_repo = mock_impl

        # Test getting the base path
        base_path = await repo.get_base_path()
        assert base_path == "/base/path"
        mock_impl.get_base_path.assert_called_once()

    async def test_write_file(self, mock_config):
        """Test writing a file."""
        repo = FileRepository(mock_config, Category="revisions")

        # Mock the implementation of the storage Repository
        mock_impl = AsyncMock()
        repo.file_storage_repo = mock_impl

        # Test writing a file
        await repo.write_file("Test content", "test.txt", "test/path")
        mock_impl.write_file.assert_called_once_with(
            contents="Test content", file_name="test.txt", file_path="test/path"
        )

    async def test_read_file(self, mock_config):
        """Test reading a file."""
        repo = FileRepository(mock_config, Category="revisions")

        # Mock the implementation of the storage Repository
        mock_impl = AsyncMock()
        mock_impl.read_file.return_value = "File content"
        repo.file_storage_repo = mock_impl

        # Test reading a file
        content = await repo.read_file("test.txt", "test/path")
        assert content == "File content"
        mock_impl.read_file.assert_called_once_with(
            file_name="test.txt", file_path="test/path"
        )

    async def test_delete_file(self, mock_config):
        """Test deleting a file."""
        repo = FileRepository(mock_config, Category="revisions")

        # Mock the implementation of the storage Repository
        mock_impl = AsyncMock()
        repo.file_storage_repo = mock_impl

        # Test deleting a file
        await repo.delete_file("test.txt", "test/path")
        mock_impl.delete_file.assert_called_once_with(
            file_name="test.txt", file_path="test/path"
        )

    async def test_list_files(self, mock_config):
        """Test listing files."""
        repo = FileRepository(mock_config, Category="revisions")

        # Mock the implementation of the storage Repository
        mock_impl = AsyncMock()
        mock_impl.list_files.return_value = ["file1.txt", "file2.txt"]
        repo.file_storage_repo = mock_impl

        # Test listing files
        files = await repo.list_files("test/path")
        assert files == ["file1.txt", "file2.txt"]
        mock_impl.list_files.assert_called_once_with(file_path="test/path")

    async def test_check_if_file_exists(self, mock_config):
        """Test checking if a file exists."""
        repo = FileRepository(mock_config, Category="revisions")

        # Mock the implementation of the storage Repository
        mock_impl = AsyncMock()
        mock_impl.check_if_file_exists.return_value = True
        repo.file_storage_repo = mock_impl

        # Test checking if a file exists
        exists = await repo.check_if_file_exists("test/path", "test.txt")
        assert exists is True
        mock_impl.check_if_file_exists.assert_called_once_with(
            file_path="test/path", file_name="test.txt"
        )

    async def test_get_prompt_template_path(self, mock_config):
        """Test getting the prompt template path."""
        repo = FileRepository(mock_config, Category="revisions")

        # Test without revision_id
        path = await repo.get_prompt_template_path()
        assert path == str(Path("templates") / Path("prompts"))

        # Test with revision_id
        path = await repo.get_prompt_template_path("test_revision")
        assert path == str(Path("templates") / Path("prompts") / Path("test_revision"))

    async def test_get_data_path(self, mock_config):
        """Test getting the data path."""
        repo = FileRepository(mock_config, Category="revisions")
        repo.add_sub_folders = True

        # Test without revision_id
        path = await repo.get_data_path()
        assert path == str(Path("functional_test_outputs"))

        # Test with revision_id
        path = await repo.get_data_path("test_revision")
        assert path == str(Path("functional_test_outputs") / Path("test_revision"))

        # Test without sub folders
        repo.add_sub_folders = False
        path = await repo.get_data_path()
        assert path == ""

    async def test_get_output_path(self, mock_config):
        """Test getting the output path."""
        repo = FileRepository(mock_config, Category="revisions")

        # Test without revision_id
        path = await repo.get_output_path()
        assert path == str(Path("functional_test_outputs"))

        # Test with revision_id
        path = await repo.get_output_path("test_revision")
        assert path == str(Path("functional_test_outputs") / Path("test_revision"))

    async def test_get_events_path(self, mock_config):
        """Test getting the events path."""
        repo = FileRepository(mock_config, Category="revisions")

        # Test without revision_id
        path = await repo.get_events_path()
        assert path == str(Path("functional_test_outputs"))

        # Test with revision_id
        path = await repo.get_events_path("test_revision")
        assert path == str(Path("functional_test_outputs") / Path("test_revision"))
