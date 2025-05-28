"""
Interface for file storage repositories.
This is a minimal mock implementation for testing.
"""

from abc import ABC, abstractmethod
from typing import List


class IFileStorage(ABC):
    """Interface for file storage repositories."""

    @abstractmethod
    def get_base_path(self) -> str:
        """Get the base path for the repository."""
        pass

    @abstractmethod
    def write_file(self, file_path: str, content: str) -> bool:
        """Write content to a file."""
        pass

    @abstractmethod
    def read_file(self, file_path: str) -> str:
        """Read content from a file."""
        pass

    @abstractmethod
    def delete_file(self, file_path: str) -> bool:
        """Delete a file."""
        pass

    @abstractmethod
    def list_files(self, directory_path: str) -> List[str]:
        """List files in a directory."""
        pass

    @abstractmethod
    def check_if_file_exists(self, file_path: str) -> bool:
        """Check if a file exists."""
        pass
