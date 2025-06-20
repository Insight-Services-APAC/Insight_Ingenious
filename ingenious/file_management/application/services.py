from typing import Any, Dict, Optional

from ..application.use_cases import DirectoryManagementUseCase, FileManagementUseCase
from ..domain.entities import Directory, File, FileSystemObject


class FileManagementApplicationService:
    """Application service for file management operations."""

    def __init__(
        self,
        file_use_case: FileManagementUseCase,
        directory_use_case: DirectoryManagementUseCase,
    ):
        self._file_use_case = file_use_case
        self._directory_use_case = directory_use_case

    async def create_file(
        self,
        name: str,
        path: str,
        content: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new file with validation and error handling."""
        try:
            # Validate input
            self._validate_file_input(name, path)

            # Create file
            file = await self._file_use_case.create_file(name, path, content)

            # Add metadata if provided
            if metadata:
                file.metadata.update(metadata)

            return self._file_to_dict(file)

        except Exception as e:
            return {"error": str(e), "success": False}

    async def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get a file by ID."""
        try:
            file = await self._file_use_case.get_file(file_id)
            return self._file_to_dict(file) if file else None
        except Exception as e:
            return {"error": str(e), "success": False}

    async def get_file_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get a file by path."""
        try:
            file = await self._file_use_case.get_file_by_path(file_path)
            return self._file_to_dict(file) if file else None
        except Exception as e:
            return {"error": str(e), "success": False}

    async def update_file(
        self,
        file_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update file content and/or metadata."""
        try:
            result = {"success": True}

            if content is not None:
                file = await self._file_use_case.update_file_content(file_id, content)
                result.update(self._file_to_dict(file))

            if metadata:
                file = await self._file_use_case.get_file(file_id)
                if file:
                    file.metadata.update(metadata)
                    # Would need to save metadata changes

            return result

        except Exception as e:
            return {"error": str(e), "success": False}

    async def delete_file(self, file_id: str) -> Dict[str, Any]:
        """Delete a file."""
        try:
            success = await self._file_use_case.delete_file(file_id)
            return {"success": success}
        except Exception as e:
            return {"error": str(e), "success": False}

    async def list_files(self, directory_path: str) -> Dict[str, Any]:
        """List files in a directory."""
        try:
            files = await self._file_use_case.list_files_in_directory(directory_path)
            return {
                "files": [self._file_to_dict(file) for file in files],
                "count": len(files),
                "success": True,
            }
        except Exception as e:
            return {"error": str(e), "success": False}

    async def copy_file(
        self, source_file_id: str, destination_path: str, new_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Copy a file."""
        try:
            file = await self._file_use_case.copy_file(
                source_file_id, destination_path, new_name
            )
            return self._file_to_dict(file)
        except Exception as e:
            return {"error": str(e), "success": False}

    async def move_file(
        self, file_id: str, new_path: str, new_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Move a file."""
        try:
            file = await self._file_use_case.move_file(file_id, new_path, new_name)
            return self._file_to_dict(file)
        except Exception as e:
            return {"error": str(e), "success": False}

    async def create_directory(self, path: str) -> Dict[str, Any]:
        """Create a directory."""
        try:
            directory = await self._directory_use_case.create_directory(path)
            return self._directory_to_dict(directory)
        except Exception as e:
            return {"error": str(e), "success": False}

    async def delete_directory(self, path: str) -> Dict[str, Any]:
        """Delete a directory."""
        try:
            success = await self._directory_use_case.delete_directory(path)
            return {"success": success}
        except Exception as e:
            return {"error": str(e), "success": False}

    async def list_directory_contents(self, path: str) -> Dict[str, Any]:
        """List directory contents."""
        try:
            contents = await self._directory_use_case.list_directory_contents(path)
            return {
                "contents": [self._file_system_object_to_dict(obj) for obj in contents],
                "count": len(contents),
                "success": True,
            }
        except Exception as e:
            return {"error": str(e), "success": False}

    def _validate_file_input(self, name: str, path: str) -> None:
        """Validate file input parameters."""
        if not name or not name.strip():
            raise ValueError("File name cannot be empty")

        if not path or not path.strip():
            raise ValueError("File path cannot be empty")

        # Additional validation rules can be added here
        invalid_chars = ["<", ">", ":", '"', "|", "?", "*"]
        if any(char in name for char in invalid_chars):
            raise ValueError(f"File name contains invalid characters: {invalid_chars}")

    def _file_to_dict(self, file: File) -> Dict[str, Any]:
        """Convert file entity to dictionary."""
        return {
            "file_id": file.file_id,
            "name": file.name,
            "path": file.path,
            "full_path": file.full_path,
            "extension": file.extension,
            "size": file.size,
            "mime_type": file.mime_type,
            "created_at": file.created_at.isoformat() if file.created_at else None,
            "updated_at": file.updated_at.isoformat() if file.updated_at else None,
            "metadata": file.metadata,
            "success": True,
        }

    def _directory_to_dict(self, directory: Directory) -> Dict[str, Any]:
        """Convert directory entity to dictionary."""
        return {
            "directory_id": directory.directory_id,
            "name": directory.name,
            "path": directory.path,
            "full_path": directory.full_path,
            "created_at": directory.created_at.isoformat()
            if directory.created_at
            else None,
            "metadata": directory.metadata,
            "success": True,
        }

    def _file_system_object_to_dict(self, obj: FileSystemObject) -> Dict[str, Any]:
        """Convert file system object to dictionary."""
        return {
            "name": obj.name,
            "path": obj.path,
            "full_path": obj.full_path,
            "is_directory": obj.is_directory,
        }
