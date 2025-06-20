from abc import ABC, abstractmethod
from typing import Optional, List
from .entities import File, Directory, FileSystemObject


class IFileRepository(ABC):
    """Repository interface for file persistence."""

    @abstractmethod
    async def save_file(self, file: File) -> None:
        """Save a file to storage."""
        pass

    @abstractmethod
    async def get_file(self, file_id: str) -> Optional[File]:
        """Get a file by ID."""
        pass

    @abstractmethod
    async def get_file_by_path(self, path: str) -> Optional[File]:
        """Get a file by its full path."""
        pass

    @abstractmethod
    async def delete_file(self, file_id: str) -> bool:
        """Delete a file by ID."""
        pass

    @abstractmethod
    async def list_files(self, directory_path: str) -> List[File]:
        """List files in a directory."""
        pass


class IFileStorageService(ABC):
    """Service interface for file storage operations."""

    @abstractmethod
    async def write_file(self, contents: str, file_name: str, file_path: str) -> str:
        """Write a file to storage."""
        pass

    @abstractmethod
    async def read_file(self, file_name: str, file_path: str) -> str:
        """Read a file from storage."""
        pass

    @abstractmethod
    async def delete_file(self, file_name: str, file_path: str) -> bool:
        """Delete a file from storage."""
        pass

    @abstractmethod
    async def list_files(self, file_path: str) -> List[FileSystemObject]:
        """List files in a directory."""
        pass

    @abstractmethod
    async def file_exists(self, file_name: str, file_path: str) -> bool:
        """Check if a file exists."""
        pass


class IDirectoryService(ABC):
    """Service interface for directory operations."""

    @abstractmethod
    async def create_directory(self, directory_path: str) -> Directory:
        """Create a directory."""
        pass

    @abstractmethod
    async def delete_directory(self, directory_path: str) -> bool:
        """Delete a directory."""
        pass

    @abstractmethod
    async def list_directory_contents(
        self, directory_path: str
    ) -> List[FileSystemObject]:
        """List contents of a directory."""
        pass

    @abstractmethod
    async def directory_exists(self, directory_path: str) -> bool:
        """Check if a directory exists."""
        pass


class IFileMetadataService(ABC):
    """Service interface for file metadata operations."""

    @abstractmethod
    async def get_file_metadata(self, file_path: str) -> dict:
        """Get metadata for a file."""
        pass

    @abstractmethod
    async def set_file_metadata(self, file_path: str, metadata: dict) -> None:
        """Set metadata for a file."""
        pass
