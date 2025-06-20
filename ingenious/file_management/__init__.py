"""
File Management bounded context for the Ingenious application.

This module contains all file-related functionality organized according to
Domain-Driven Design principles:

- domain: Core business logic and entities for files and directories
- application: Use cases and application services for file operations
- infrastructure: External adapters for storage systems
"""

from .domain.entities import File, Directory, FileSystemObject
from .domain.services import (
    IFileRepository,
    IFileStorageService,
    IDirectoryService,
    IFileMetadataService,
)
from .application.use_cases import FileManagementUseCase, DirectoryManagementUseCase
from .application.services import FileManagementApplicationService
from .infrastructure.services import (
    LocalFileStorageService,
    FileSystemFileRepository,
    FileSystemDirectoryService,
    FileSystemMetadataService,
    LegacyFileStorageAdapter,
)

__all__ = [
    # Domain
    "File",
    "Directory",
    "FileSystemObject",
    "IFileRepository",
    "IFileStorageService",
    "IDirectoryService",
    "IFileMetadataService",
    # Application
    "FileManagementUseCase",
    "DirectoryManagementUseCase",
    "FileManagementApplicationService",
    # Infrastructure
    "LocalFileStorageService",
    "FileSystemFileRepository",
    "FileSystemDirectoryService",
    "FileSystemMetadataService",
    "LegacyFileStorageAdapter",
]
