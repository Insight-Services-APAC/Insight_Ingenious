"""
Factory for creating repository implementations.
"""

from ingenious.domain.interfaces.repository.file_repository import IFileRepository
from ingenious.domain.interfaces.service.blob_storage import BlobStorageInterface
from ingenious.presentation.infrastructure.storage.repo.file_repository import (
    BlobStorageFileRepository,
)


class RepositoryFactory:
    """Factory for creating repository implementations."""

    @staticmethod
    def create_file_repository(blob_storage: BlobStorageInterface) -> IFileRepository:
        """
        Create a file repository implementation.

        Args:
            blob_storage: The blob storage implementation

        Returns:
            A file repository implementation
        """
        return BlobStorageFileRepository(blob_storage)
