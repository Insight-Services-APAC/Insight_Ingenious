from typing import Optional, Dict, Any
from datetime import datetime
from uuid import uuid4
from pathlib import Path


class File:
    """Domain entity representing a file."""

    def __init__(
        self,
        name: str,
        path: str,
        content: Optional[str] = None,
        file_id: Optional[str] = None,
        size: Optional[int] = None,
        mime_type: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.file_id = file_id or str(uuid4())
        self.name = name
        self.path = path
        self.content = content
        self.size = size
        self.mime_type = mime_type
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.metadata = metadata or {}

    @property
    def full_path(self) -> str:
        """Get the full path including filename."""
        return str(Path(self.path) / self.name)

    @property
    def extension(self) -> str:
        """Get file extension."""
        return Path(self.name).suffix

    def update_content(self, new_content: str) -> None:
        """Update file content and timestamp."""
        self.content = new_content
        self.size = len(new_content.encode("utf-8"))
        self.updated_at = datetime.utcnow()

    def __eq__(self, other):
        if not isinstance(other, File):
            return False
        return self.file_id == other.file_id


class Directory:
    """Domain entity representing a directory."""

    def __init__(
        self,
        name: str,
        path: str,
        directory_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.directory_id = directory_id or str(uuid4())
        self.name = name
        self.path = path
        self.created_at = created_at or datetime.utcnow()
        self.metadata = metadata or {}
        self.files: Dict[str, File] = {}
        self.subdirectories: Dict[str, "Directory"] = {}

    @property
    def full_path(self) -> str:
        """Get the full directory path."""
        return str(Path(self.path) / self.name)

    def add_file(self, file: File) -> None:
        """Add a file to this directory."""
        self.files[file.name] = file

    def remove_file(self, filename: str) -> bool:
        """Remove a file from this directory."""
        if filename in self.files:
            del self.files[filename]
            return True
        return False

    def get_file(self, filename: str) -> Optional[File]:
        """Get a file by name."""
        return self.files.get(filename)

    def list_files(self) -> list[str]:
        """List all file names in this directory."""
        return list(self.files.keys())

    def add_subdirectory(self, directory: "Directory") -> None:
        """Add a subdirectory."""
        self.subdirectories[directory.name] = directory

    def get_subdirectory(self, dirname: str) -> Optional["Directory"]:
        """Get a subdirectory by name."""
        return self.subdirectories.get(dirname)


class FileSystemObject:
    """Value object representing a file system object (file or directory)."""

    def __init__(self, name: str, path: str, is_directory: bool):
        self.name = name
        self.path = path
        self.is_directory = is_directory

    @property
    def full_path(self) -> str:
        """Get the full path."""
        return str(Path(self.path) / self.name)

    def __eq__(self, other):
        if not isinstance(other, FileSystemObject):
            return False
        return (
            self.name == other.name
            and self.path == other.path
            and self.is_directory == other.is_directory
        )
