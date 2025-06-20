"""
Unit tests for file management domain services.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from ingenious.file_management.domain.entities import Directory, File, FileSystemObject
from ingenious.file_management.domain.services import (
    IDirectoryService,
    IFileMetadataService,
    IFileRepository,
    IFileStorageService,
)


class TestIFileRepository:
    """Test cases for IFileRepository interface."""

    def test_is_abstract_interface(self):
        """Test that IFileRepository is an abstract interface."""
        with pytest.raises(TypeError):
            IFileRepository()

    @pytest.mark.asyncio
    async def test_save_file_interface(self):
        """Test save_file method interface."""
        mock_repo = Mock(spec=IFileRepository)
        mock_repo.save_file = AsyncMock()

        file = File(name="test.txt", path="/home")
        await mock_repo.save_file(file)

        mock_repo.save_file.assert_called_once_with(file)

    @pytest.mark.asyncio
    async def test_get_file_interface(self):
        """Test get_file method interface."""
        mock_repo = Mock(spec=IFileRepository)
        expected_file = File(name="test.txt", path="/home", file_id="test-id")
        mock_repo.get_file = AsyncMock(return_value=expected_file)

        result = await mock_repo.get_file("test-id")

        assert result == expected_file
        mock_repo.get_file.assert_called_once_with("test-id")

    @pytest.mark.asyncio
    async def test_get_file_by_path_interface(self):
        """Test get_file_by_path method interface."""
        mock_repo = Mock(spec=IFileRepository)
        expected_file = File(name="test.txt", path="/home")
        mock_repo.get_file_by_path = AsyncMock(return_value=expected_file)

        result = await mock_repo.get_file_by_path("/home/test.txt")

        assert result == expected_file
        mock_repo.get_file_by_path.assert_called_once_with("/home/test.txt")

    @pytest.mark.asyncio
    async def test_delete_file_interface(self):
        """Test delete_file method interface."""
        mock_repo = Mock(spec=IFileRepository)
        mock_repo.delete_file = AsyncMock(return_value=True)

        result = await mock_repo.delete_file("test-id")

        assert result is True
        mock_repo.delete_file.assert_called_once_with("test-id")

    @pytest.mark.asyncio
    async def test_list_files_interface(self):
        """Test list_files method interface."""
        mock_repo = Mock(spec=IFileRepository)
        expected_files = [
            File(name="file1.txt", path="/home"),
            File(name="file2.txt", path="/home"),
        ]
        mock_repo.list_files = AsyncMock(return_value=expected_files)

        result = await mock_repo.list_files("/home")

        assert result == expected_files
        mock_repo.list_files.assert_called_once_with("/home")


class TestIFileStorageService:
    """Test cases for IFileStorageService interface."""

    def test_is_abstract_interface(self):
        """Test that IFileStorageService is an abstract interface."""
        with pytest.raises(TypeError):
            IFileStorageService()

    @pytest.mark.asyncio
    async def test_write_file_interface(self):
        """Test write_file method interface."""
        mock_service = Mock(spec=IFileStorageService)
        mock_service.write_file = AsyncMock(return_value="/home/test.txt")

        result = await mock_service.write_file("content", "test.txt", "/home")

        assert result == "/home/test.txt"
        mock_service.write_file.assert_called_once_with("content", "test.txt", "/home")

    @pytest.mark.asyncio
    async def test_read_file_interface(self):
        """Test read_file method interface."""
        mock_service = Mock(spec=IFileStorageService)
        mock_service.read_file = AsyncMock(return_value="file content")

        result = await mock_service.read_file("test.txt", "/home")

        assert result == "file content"
        mock_service.read_file.assert_called_once_with("test.txt", "/home")

    @pytest.mark.asyncio
    async def test_delete_file_interface(self):
        """Test delete_file method interface."""
        mock_service = Mock(spec=IFileStorageService)
        mock_service.delete_file = AsyncMock(return_value=True)

        result = await mock_service.delete_file("test.txt", "/home")

        assert result is True
        mock_service.delete_file.assert_called_once_with("test.txt", "/home")

    @pytest.mark.asyncio
    async def test_list_files_interface(self):
        """Test list_files method interface."""
        mock_service = Mock(spec=IFileStorageService)
        expected_objects = [
            FileSystemObject("file1.txt", "/home", False),
            FileSystemObject("subdir", "/home", True),
        ]
        mock_service.list_files = AsyncMock(return_value=expected_objects)

        result = await mock_service.list_files("/home")

        assert result == expected_objects
        mock_service.list_files.assert_called_once_with("/home")

    @pytest.mark.asyncio
    async def test_file_exists_interface(self):
        """Test file_exists method interface."""
        mock_service = Mock(spec=IFileStorageService)
        mock_service.file_exists = AsyncMock(return_value=True)

        result = await mock_service.file_exists("test.txt", "/home")

        assert result is True
        mock_service.file_exists.assert_called_once_with("test.txt", "/home")


class TestIDirectoryService:
    """Test cases for IDirectoryService interface."""

    def test_is_abstract_interface(self):
        """Test that IDirectoryService is an abstract interface."""
        with pytest.raises(TypeError):
            IDirectoryService()

    @pytest.mark.asyncio
    async def test_create_directory_interface(self):
        """Test create_directory method interface."""
        mock_service = Mock(spec=IDirectoryService)
        expected_dir = Directory(name="testdir", path="/home")
        mock_service.create_directory = AsyncMock(return_value=expected_dir)

        result = await mock_service.create_directory("/home/testdir")

        assert result == expected_dir
        mock_service.create_directory.assert_called_once_with("/home/testdir")

    @pytest.mark.asyncio
    async def test_delete_directory_interface(self):
        """Test delete_directory method interface."""
        mock_service = Mock(spec=IDirectoryService)
        mock_service.delete_directory = AsyncMock(return_value=True)

        result = await mock_service.delete_directory("/home/testdir")

        assert result is True
        mock_service.delete_directory.assert_called_once_with("/home/testdir")

    @pytest.mark.asyncio
    async def test_list_directory_contents_interface(self):
        """Test list_directory_contents method interface."""
        mock_service = Mock(spec=IDirectoryService)
        expected_contents = [
            FileSystemObject("file1.txt", "/home", False),
            FileSystemObject("subdir", "/home", True),
        ]
        mock_service.list_directory_contents = AsyncMock(return_value=expected_contents)

        result = await mock_service.list_directory_contents("/home")

        assert result == expected_contents
        mock_service.list_directory_contents.assert_called_once_with("/home")

    @pytest.mark.asyncio
    async def test_directory_exists_interface(self):
        """Test directory_exists method interface."""
        mock_service = Mock(spec=IDirectoryService)
        mock_service.directory_exists = AsyncMock(return_value=True)

        result = await mock_service.directory_exists("/home/testdir")

        assert result is True
        mock_service.directory_exists.assert_called_once_with("/home/testdir")


class TestIFileMetadataService:
    """Test cases for IFileMetadataService interface."""

    def test_is_abstract_interface(self):
        """Test that IFileMetadataService is an abstract interface."""
        with pytest.raises(TypeError):
            IFileMetadataService()

    @pytest.mark.asyncio
    async def test_get_file_metadata_interface(self):
        """Test get_file_metadata method interface."""
        mock_service = Mock(spec=IFileMetadataService)
        expected_metadata = {"size": 1024, "created": "2023-01-01", "owner": "user"}
        mock_service.get_file_metadata = AsyncMock(return_value=expected_metadata)

        result = await mock_service.get_file_metadata("/home/test.txt")

        assert result == expected_metadata
        mock_service.get_file_metadata.assert_called_once_with("/home/test.txt")

    @pytest.mark.asyncio
    async def test_set_file_metadata_interface(self):
        """Test set_file_metadata method interface."""
        mock_service = Mock(spec=IFileMetadataService)
        mock_service.set_file_metadata = AsyncMock()

        metadata = {"owner": "admin", "permissions": "644"}
        await mock_service.set_file_metadata("/home/test.txt", metadata)

        mock_service.set_file_metadata.assert_called_once_with(
            "/home/test.txt", metadata
        )


class TestDomainServiceInteractions:
    """Test interactions between domain services."""

    @pytest.mark.asyncio
    async def test_file_repository_with_storage_service(self):
        """Test file repository working with storage service."""
        file_repo = Mock(spec=IFileRepository)
        storage_service = Mock(spec=IFileStorageService)

        # Mock file creation workflow
        file = File(name="test.txt", path="/home", content="test content")

        # Save to repository
        file_repo.save_file = AsyncMock()
        await file_repo.save_file(file)

        # Write to storage
        storage_service.write_file = AsyncMock(return_value="/home/test.txt")
        path = await storage_service.write_file(file.content, file.name, file.path)

        assert path == "/home/test.txt"
        file_repo.save_file.assert_called_once_with(file)
        storage_service.write_file.assert_called_once_with(
            file.content, file.name, file.path
        )

    @pytest.mark.asyncio
    async def test_directory_service_with_file_operations(self):
        """Test directory service working with file operations."""
        dir_service = Mock(spec=IDirectoryService)
        file_repo = Mock(spec=IFileRepository)

        # Create directory first
        dir_service.create_directory = AsyncMock(
            return_value=Directory(name="testdir", path="/home")
        )
        await dir_service.create_directory("/home/testdir")

        # List files in the directory
        file_repo.list_files = AsyncMock(
            return_value=[File(name="file1.txt", path="/home/testdir")]
        )
        files = await file_repo.list_files("/home/testdir")

        assert len(files) == 1
        assert files[0].name == "file1.txt"
        dir_service.create_directory.assert_called_once_with("/home/testdir")
        file_repo.list_files.assert_called_once_with("/home/testdir")

    @pytest.mark.asyncio
    async def test_metadata_service_with_file_operations(self):
        """Test metadata service working with file operations."""
        metadata_service = Mock(spec=IFileMetadataService)
        storage_service = Mock(spec=IFileStorageService)

        file_path = "/home/test.txt"

        # Check if file exists
        storage_service.file_exists = AsyncMock(return_value=True)
        exists = await storage_service.file_exists("test.txt", "/home")

        # Get metadata if file exists
        if exists:
            metadata_service.get_file_metadata = AsyncMock(
                return_value={"size": 1024, "owner": "user"}
            )
            metadata = await metadata_service.get_file_metadata(file_path)
            assert metadata["size"] == 1024

        storage_service.file_exists.assert_called_once_with("test.txt", "/home")
        metadata_service.get_file_metadata.assert_called_once_with(file_path)

    @pytest.mark.asyncio
    async def test_complete_file_management_workflow(self):
        """Test a complete file management workflow."""
        file_repo = Mock(spec=IFileRepository)
        storage_service = Mock(spec=IFileStorageService)
        dir_service = Mock(spec=IDirectoryService)
        metadata_service = Mock(spec=IFileMetadataService)

        # 1. Create directory
        dir_service.create_directory = AsyncMock(
            return_value=Directory(name="project", path="/home")
        )
        await dir_service.create_directory("/home/project")

        # 2. Create and save file
        file = File(name="README.md", path="/home/project", content="# Project")
        file_repo.save_file = AsyncMock()
        await file_repo.save_file(file)

        # 3. Write file to storage
        storage_service.write_file = AsyncMock(return_value="/home/project/README.md")
        await storage_service.write_file(file.content, file.name, file.path)

        # 4. Set metadata
        metadata_service.set_file_metadata = AsyncMock()
        await metadata_service.set_file_metadata(
            "/home/project/README.md", {"type": "documentation"}
        )

        # 5. Verify all operations were called
        dir_service.create_directory.assert_called_once()
        file_repo.save_file.assert_called_once()
        storage_service.write_file.assert_called_once()
        metadata_service.set_file_metadata.assert_called_once()
