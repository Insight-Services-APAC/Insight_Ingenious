"""
File Management bounded context for the Ingenious application.

This module contains all file-related functionality organized according to
Domain-Driven Design principles:

- domain: Core business logic and entities for files and directories
- application: Use cases and application services for file operations
- infrastructure: External adapters for storage systems
"""

from .application.services import FileManagementApplicationService
from .application.use_cases import DirectoryManagementUseCase, FileManagementUseCase
from .domain.entities import Directory, File, FileSystemObject
from .domain.services import (
    IDirectoryService,
    IFileMetadataService,
    IFileRepository,
    IFileStorageService,
)
from .infrastructure.services import (
    FileSystemDirectoryService,
    FileSystemFileRepository,
    FileSystemMetadataService,
    LegacyFileStorageAdapter,
    LocalFileStorageService,
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
