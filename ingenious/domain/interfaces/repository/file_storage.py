from abc import ABC, abstractmethod
from typing import List


class IFileStorage(ABC):
    """Interface for file storage implementations"""

    @abstractmethod
    async def write_file(self, contents: str, file_name: str, file_path: str) -> str:
        """Write a file to storage"""
        pass

    @abstractmethod
    async def read_file(self, file_name: str, file_path: str) -> str:
        """Read a file from storage"""
        pass

    @abstractmethod
    async def delete_file(self, file_name: str, file_path: str) -> str:
        """Delete a file from storage"""
        pass

    @abstractmethod
    async def list_files(self, file_path: str) -> List[str]:
        """List files in a directory"""
        pass

    @abstractmethod
    async def check_if_file_exists(self, file_path: str, file_name: str) -> bool:
        """Check if a file exists"""
        pass

    @abstractmethod
    async def get_base_path(self) -> str:
        """Get the base path for storage"""
        pass
