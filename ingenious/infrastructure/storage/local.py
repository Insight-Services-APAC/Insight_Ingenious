"""
Local file storage repository implementation.
This is a mock implementation for testing.
"""

from ingenious.domain.interfaces.storage import IFileStorage
from ingenious.domain.model.config import Config, FileStorageContainer


class local_FileStorageRepository(IFileStorage):
    """Local file storage repository implementation."""

    def __init__(self, config: Config, fs_config: FileStorageContainer):
        """Initialize the repository."""
        self.config = config
        self.fs_config = fs_config

    def get_base_path(self) -> str:
        """Get the base path for the repository."""
        return self.fs_config.path

    def write_file(self, file_path: str, content: str) -> bool:
        """Write content to a file."""
        return True

    def read_file(self, file_path: str) -> str:
        """Read content from a file."""
        return "Mock file content"

    def delete_file(self, file_path: str) -> bool:
        """Delete a file."""
        return True

    def list_files(self, directory_path: str) -> list:
        """List files in a directory."""
        return ["mock_file1.txt", "mock_file2.txt"]

    def check_if_file_exists(self, file_path: str) -> bool:
        """Check if a file exists."""
        return True
