from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..domain.entities import Directory, File, FileSystemObject
from ..domain.services import (
    IDirectoryService,
    IFileMetadataService,
    IFileRepository,
    IFileStorageService,
)


class LocalFileStorageService(IFileStorageService):
    """Local file system implementation of file storage service."""

    def __init__(self, base_path: str = ""):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def write_file(self, contents: str, file_name: str, file_path: str) -> str:
        """Write a file to local storage."""
        full_path = self.base_path / file_path / file_name
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(contents)

        return str(full_path)

    async def read_file(self, file_name: str, file_path: str) -> str:
        """Read a file from local storage."""
        full_path = self.base_path / file_path / file_name

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")

        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    async def delete_file(self, file_name: str, file_path: str) -> bool:
        """Delete a file from local storage."""
        full_path = self.base_path / file_path / file_name

        if full_path.exists():
            full_path.unlink()
            return True
        return False

    async def list_files(self, file_path: str) -> List[FileSystemObject]:
        """List files in a directory."""
        full_path = self.base_path / file_path

        if not full_path.exists():
            return []

        objects = []
        for item in full_path.iterdir():
            objects.append(
                FileSystemObject(
                    name=item.name, path=file_path, is_directory=item.is_dir()
                )
            )

        return objects

    async def file_exists(self, file_name: str, file_path: str) -> bool:
        """Check if a file exists."""
        full_path = self.base_path / file_path / file_name
        return full_path.exists() and full_path.is_file()


class FileSystemFileRepository(IFileRepository):
    """File system implementation of file repository."""

    def __init__(self, storage_service: IFileStorageService):
        self._storage = storage_service
        self._files: Dict[str, File] = {}

    async def save_file(self, file: File) -> None:
        """Save a file to storage."""
        if file.content is not None:
            await self._storage.write_file(file.content, file.name, file.path)
        self._files[file.file_id] = file

    async def get_file(self, file_id: str) -> Optional[File]:
        """Get a file by ID."""
        return self._files.get(file_id)

    async def get_file_by_path(self, path: str) -> Optional[File]:
        """Get a file by its full path."""
        path_obj = Path(path)
        file_name = path_obj.name
        file_path = str(path_obj.parent)

        try:
            content = await self._storage.read_file(file_name, file_path)
            return File(
                name=file_name,
                path=file_path,
                content=content,
                file_id=path,  # Use path as ID for file system
            )
        except FileNotFoundError:
            return None

    async def delete_file(self, file_id: str) -> bool:
        """Delete a file by ID."""
        file = self._files.get(file_id)
        if file:
            success = await self._storage.delete_file(file.name, file.path)
            if success:
                del self._files[file_id]
            return success
        return False

    async def list_files(self, directory_path: str) -> List[File]:
        """List files in a directory."""
        objects = await self._storage.list_files(directory_path)
        files = []

        for obj in objects:
            if not obj.is_directory:
                try:
                    content = await self._storage.read_file(obj.name, directory_path)
                    file = File(
                        name=obj.name,
                        path=directory_path,
                        content=content,
                        file_id=obj.full_path,
                    )
                    files.append(file)
                except FileNotFoundError:
                    # Skip files that can't be read
                    continue

        return files


class FileSystemDirectoryService(IDirectoryService):
    """File system implementation of directory service."""

    def __init__(self, base_path: str = ""):
        self.base_path = Path(base_path) if base_path else Path.cwd()

    async def create_directory(self, directory_path: str) -> Directory:
        """Create a directory."""
        full_path = self.base_path / directory_path
        full_path.mkdir(parents=True, exist_ok=True)

        path_obj = Path(directory_path)
        return Directory(
            name=path_obj.name, path=str(path_obj.parent), directory_id=directory_path
        )

    async def delete_directory(self, directory_path: str) -> bool:
        """Delete a directory."""
        full_path = self.base_path / directory_path

        if full_path.exists() and full_path.is_dir():
            # Remove directory and all contents
            import shutil

            shutil.rmtree(full_path)
            return True
        return False

    async def list_directory_contents(
        self, directory_path: str
    ) -> List[FileSystemObject]:
        """List contents of a directory."""
        full_path = self.base_path / directory_path

        if not full_path.exists():
            return []

        objects = []
        for item in full_path.iterdir():
            objects.append(
                FileSystemObject(
                    name=item.name, path=directory_path, is_directory=item.is_dir()
                )
            )

        return objects

    async def directory_exists(self, directory_path: str) -> bool:
        """Check if a directory exists."""
        full_path = self.base_path / directory_path
        return full_path.exists() and full_path.is_dir()


class FileSystemMetadataService(IFileMetadataService):
    """File system implementation of file metadata service."""

    def __init__(self, base_path: str = ""):
        self.base_path = Path(base_path) if base_path else Path.cwd()

    async def get_file_metadata(self, file_path: str) -> dict:
        """Get metadata for a file."""
        full_path = self.base_path / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")

        stat = full_path.stat()
        return {
            "size": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime),
            "modified_at": datetime.fromtimestamp(stat.st_mtime),
            "is_directory": full_path.is_dir(),
            "is_file": full_path.is_file(),
            "permissions": oct(stat.st_mode)[-3:],
        }

    async def set_file_metadata(self, file_path: str, metadata: dict) -> None:
        """Set metadata for a file (limited support on file system)."""
        full_path = self.base_path / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")

        # File system has limited metadata support
        # Could implement extended attributes or separate metadata files
        pass
