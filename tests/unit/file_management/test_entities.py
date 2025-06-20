"""
Unit tests for file management domain entities.
"""

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from ingenious.file_management.domain.entities import (
    Directory,
    File,
    FileSystemObject,
)


class TestFile:
    """Test cases for File entity."""

    def test_file_creation_with_defaults(self):
        """Test creating a file with default values."""
        file = File(name="test.txt", path="/home/user")

        assert file.name == "test.txt"
        assert file.path == "/home/user"
        assert file.file_id is not None
        assert isinstance(file.created_at, datetime)
        assert isinstance(file.updated_at, datetime)
        assert file.metadata == {}

    def test_file_creation_with_all_parameters(self):
        """Test creating a file with all parameters."""
        created_at = datetime(2023, 1, 1, 12, 0, 0)
        updated_at = datetime(2023, 1, 2, 12, 0, 0)
        metadata = {"author": "test", "version": "1.0"}

        file = File(
            name="document.pdf",
            path="/documents",
            content="file content",
            file_id="custom-id",
            size=1024,
            mime_type="application/pdf",
            created_at=created_at,
            updated_at=updated_at,
            metadata=metadata,
        )

        assert file.name == "document.pdf"
        assert file.path == "/documents"
        assert file.content == "file content"
        assert file.file_id == "custom-id"
        assert file.size == 1024
        assert file.mime_type == "application/pdf"
        assert file.created_at == created_at
        assert file.updated_at == updated_at
        assert file.metadata == metadata

    def test_full_path_property(self):
        """Test full_path property."""
        file = File(name="test.txt", path="/home/user")
        expected_path = str(Path("/home/user") / "test.txt")
        assert file.full_path == expected_path

    def test_extension_property(self):
        """Test extension property."""
        file = File(name="document.pdf", path="/docs")
        assert file.extension == ".pdf"

        file_no_ext = File(name="README", path="/docs")
        assert file_no_ext.extension == ""

    @patch("ingenious.file_management.domain.entities.datetime")
    def test_update_content(self, mock_datetime):
        """Test updating file content."""
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = mock_now

        file = File(name="test.txt", path="/home")
        original_updated_at = file.updated_at

        new_content = "Updated content"
        file.update_content(new_content)

        assert file.content == new_content
        assert file.size == len(new_content.encode("utf-8"))
        assert file.updated_at == mock_now
        assert file.updated_at != original_updated_at

    def test_file_equality(self):
        """Test file equality based on file_id."""
        file1 = File(name="test.txt", path="/home", file_id="same-id")
        file2 = File(name="other.txt", path="/other", file_id="same-id")
        file3 = File(name="test.txt", path="/home", file_id="different-id")

        assert file1 == file2  # Same ID
        assert file1 != file3  # Different ID
        assert file1 != "not a file"  # Different type


class TestDirectory:
    """Test cases for Directory entity."""

    def test_directory_creation_with_defaults(self):
        """Test creating a directory with default values."""
        directory = Directory(name="testdir", path="/home/user")

        assert directory.name == "testdir"
        assert directory.path == "/home/user"
        assert directory.directory_id is not None
        assert isinstance(directory.created_at, datetime)
        assert directory.metadata == {}
        assert directory.files == {}
        assert directory.subdirectories == {}

    def test_directory_creation_with_all_parameters(self):
        """Test creating a directory with all parameters."""
        created_at = datetime(2023, 1, 1, 12, 0, 0)
        metadata = {"owner": "admin", "permissions": "755"}

        directory = Directory(
            name="projects",
            path="/home/user",
            directory_id="custom-dir-id",
            created_at=created_at,
            metadata=metadata,
        )

        assert directory.name == "projects"
        assert directory.path == "/home/user"
        assert directory.directory_id == "custom-dir-id"
        assert directory.created_at == created_at
        assert directory.metadata == metadata

    def test_full_path_property(self):
        """Test full_path property."""
        directory = Directory(name="testdir", path="/home/user")
        expected_path = str(Path("/home/user") / "testdir")
        assert directory.full_path == expected_path

    def test_add_and_get_file(self):
        """Test adding and getting files."""
        directory = Directory(name="testdir", path="/home")
        file = File(name="test.txt", path="/home/testdir")

        directory.add_file(file)

        assert len(directory.files) == 1
        assert directory.get_file("test.txt") == file
        assert directory.get_file("nonexistent.txt") is None

    def test_remove_file(self):
        """Test removing files."""
        directory = Directory(name="testdir", path="/home")
        file = File(name="test.txt", path="/home/testdir")

        directory.add_file(file)
        assert len(directory.files) == 1

        # Remove existing file
        result = directory.remove_file("test.txt")
        assert result is True
        assert len(directory.files) == 0

        # Try to remove non-existent file
        result = directory.remove_file("nonexistent.txt")
        assert result is False

    def test_list_files(self):
        """Test listing files in directory."""
        directory = Directory(name="testdir", path="/home")

        file1 = File(name="file1.txt", path="/home/testdir")
        file2 = File(name="file2.txt", path="/home/testdir")

        directory.add_file(file1)
        directory.add_file(file2)

        file_list = directory.list_files()
        assert len(file_list) == 2
        assert "file1.txt" in file_list
        assert "file2.txt" in file_list

    def test_add_and_get_subdirectory(self):
        """Test adding and getting subdirectories."""
        parent_dir = Directory(name="parent", path="/home")
        child_dir = Directory(name="child", path="/home/parent")

        parent_dir.add_subdirectory(child_dir)

        assert len(parent_dir.subdirectories) == 1
        assert parent_dir.get_subdirectory("child") == child_dir
        assert parent_dir.get_subdirectory("nonexistent") is None


class TestFileSystemObject:
    """Test cases for FileSystemObject value object."""

    def test_file_system_object_creation(self):
        """Test creating a FileSystemObject."""
        # Test file object
        file_obj = FileSystemObject(name="test.txt", path="/home", is_directory=False)
        assert file_obj.name == "test.txt"
        assert file_obj.path == "/home"
        assert file_obj.is_directory is False

        # Test directory object
        dir_obj = FileSystemObject(name="testdir", path="/home", is_directory=True)
        assert dir_obj.name == "testdir"
        assert dir_obj.path == "/home"
        assert dir_obj.is_directory is True

    def test_full_path_property(self):
        """Test full_path property."""
        fs_obj = FileSystemObject(
            name="test.txt", path="/home/user", is_directory=False
        )
        expected_path = str(Path("/home/user") / "test.txt")
        assert fs_obj.full_path == expected_path

    def test_file_system_object_equality(self):
        """Test FileSystemObject equality."""
        obj1 = FileSystemObject(name="test.txt", path="/home", is_directory=False)
        obj2 = FileSystemObject(name="test.txt", path="/home", is_directory=False)
        obj3 = FileSystemObject(name="test.txt", path="/home", is_directory=True)
        obj4 = FileSystemObject(name="other.txt", path="/home", is_directory=False)

        assert obj1 == obj2  # Same name, path, and type
        assert obj1 != obj3  # Different type (file vs directory)
        assert obj1 != obj4  # Different name
        assert obj1 != "not a filesystem object"  # Different type


class TestDomainEntityInteractions:
    """Test interactions between domain entities."""

    def test_directory_with_files_and_subdirectories(self):
        """Test a directory containing both files and subdirectories."""
        root = Directory(name="root", path="/")

        # Add files to root
        file1 = File(name="readme.txt", path="/root")
        file2 = File(name="config.json", path="/root")
        root.add_file(file1)
        root.add_file(file2)

        # Add subdirectories
        subdir1 = Directory(name="src", path="/root")
        subdir2 = Directory(name="tests", path="/root")
        root.add_subdirectory(subdir1)
        root.add_subdirectory(subdir2)

        # Add files to subdirectories
        src_file = File(name="main.py", path="/root/src")
        subdir1.add_file(src_file)

        # Verify structure
        assert len(root.files) == 2
        assert len(root.subdirectories) == 2
        assert root.get_file("readme.txt") == file1
        assert root.get_subdirectory("src") == subdir1
        assert subdir1.get_file("main.py") == src_file

    def test_file_content_updates_preserve_identity(self):
        """Test that updating file content preserves file identity."""
        file = File(name="test.txt", path="/home", file_id="test-id")
        original_id = file.file_id

        file.update_content("New content")

        assert file.file_id == original_id
        assert file.content == "New content"
