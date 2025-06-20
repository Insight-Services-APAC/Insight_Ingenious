from typing import List, Optional

from ..domain.entities import Directory, File, FileSystemObject
from ..domain.services import (
    IDirectoryService,
    IFileMetadataService,
    IFileRepository,
    IFileStorageService,
)


class FileManagementUseCase:
    """Use case for file management operations."""

    def __init__(
        self,
        file_repository: IFileRepository,
        storage_service: IFileStorageService,
        directory_service: IDirectoryService,
        metadata_service: IFileMetadataService,
    ):
        self._file_repository = file_repository
        self._storage_service = storage_service
        self._directory_service = directory_service
        self._metadata_service = metadata_service

    async def create_file(self, name: str, path: str, content: str) -> File:
        """Create a new file."""
        # Validate inputs
        if not name:
            raise ValueError("File name is required")
        if not path:
            raise ValueError("File path is required")

        # Check if file already exists
        if await self._storage_service.file_exists(name, path):
            raise ValueError(f"File {name} already exists in {path}")

        # Create file entity
        file = File(name=name, path=path, content=content)

        # Save to repository
        await self._file_repository.save_file(file)

        return file

    async def get_file(self, file_id: str) -> Optional[File]:
        """Get a file by ID."""
        return await self._file_repository.get_file(file_id)

    async def get_file_by_path(self, file_path: str) -> Optional[File]:
        """Get a file by path."""
        return await self._file_repository.get_file_by_path(file_path)

    async def update_file_content(self, file_id: str, new_content: str) -> File:
        """Update file content."""
        file = await self._file_repository.get_file(file_id)
        if not file:
            raise ValueError(f"File with ID {file_id} not found")

        file.update_content(new_content)
        await self._file_repository.save_file(file)

        return file

    async def delete_file(self, file_id: str) -> bool:
        """Delete a file."""
        return await self._file_repository.delete_file(file_id)

    async def list_files_in_directory(self, directory_path: str) -> List[File]:
        """List all files in a directory."""
        return await self._file_repository.list_files(directory_path)

    async def copy_file(
        self, source_file_id: str, destination_path: str, new_name: Optional[str] = None
    ) -> File:
        """Copy a file to a new location."""
        source_file = await self._file_repository.get_file(source_file_id)
        if not source_file:
            raise ValueError(f"Source file with ID {source_file_id} not found")

        # Create new file with copied content
        copied_file = File(
            name=new_name or source_file.name,
            path=destination_path,
            content=source_file.content,
            metadata=source_file.metadata.copy(),
        )

        await self._file_repository.save_file(copied_file)
        return copied_file

    async def move_file(
        self, file_id: str, new_path: str, new_name: Optional[str] = None
    ) -> File:
        """Move a file to a new location."""
        file = await self._file_repository.get_file(file_id)
        if not file:
            raise ValueError(f"File with ID {file_id} not found")

        # Delete from old location
        await self._storage_service.delete_file(file.name, file.path)

        # Update file properties
        if new_name:
            file.name = new_name
        file.path = new_path

        # Save to new location
        await self._file_repository.save_file(file)

        return file


class DirectoryManagementUseCase:
    """Use case for directory management operations."""

    def __init__(self, directory_service: IDirectoryService):
        self._directory_service = directory_service

    async def create_directory(self, path: str) -> Directory:
        """Create a new directory."""
        if not path:
            raise ValueError("Directory path is required")

        if await self._directory_service.directory_exists(path):
            raise ValueError(f"Directory {path} already exists")

        return await self._directory_service.create_directory(path)

    async def delete_directory(self, path: str) -> bool:
        """Delete a directory."""
        if not await self._directory_service.directory_exists(path):
            raise ValueError(f"Directory {path} does not exist")

        return await self._directory_service.delete_directory(path)

    async def list_directory_contents(self, path: str) -> List[FileSystemObject]:
        """List contents of a directory."""
        return await self._directory_service.list_directory_contents(path)

    async def directory_exists(self, path: str) -> bool:
        """Check if a directory exists."""
        return await self._directory_service.directory_exists(path)
