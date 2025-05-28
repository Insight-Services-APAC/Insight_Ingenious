"""
Factory for creating blob storage implementations.
"""

from typing import Optional

from azure.storage.blob import BlobServiceClient

from ingenious.domain.interfaces.service.blob_storage import BlobStorageInterface
from ingenious.domain.interfaces.service.path_helper import PathHelperInterface
from ingenious.domain.model.config import FileStorageContainer
from ingenious.presentation.infrastructure.storage.azure.blob_operations import (
    AzureBlobOperations,
)
from ingenious.presentation.infrastructure.storage.azure.path_helper import (
    AzurePathHelper,
)
from ingenious.presentation.infrastructure.storage.local.file_storage import (
    LocalFileStorage,
    LocalPathHelper,
)


class BlobStorageFactory:
    """Factory for creating blob storage implementations."""

    @staticmethod
    def create_azure_storage(
        connection_string: str,
        fs_config: FileStorageContainer,
        path_helper: Optional[PathHelperInterface] = None,
    ) -> BlobStorageInterface:
        """
        Create an Azure blob storage implementation.

        Args:
            connection_string: The Azure Storage connection string
            fs_config: The file storage container configuration
            path_helper: Optional path helper implementation

        Returns:
            A blob storage implementation
        """
        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        path_helper = path_helper or AzurePathHelper(fs_config)
        return AzureBlobOperations(blob_service_client, fs_config, path_helper)

    @staticmethod
    def create_local_storage(
        fs_config: FileStorageContainer,
        path_helper: Optional[PathHelperInterface] = None,
    ) -> BlobStorageInterface:
        """
        Create a local file storage implementation.

        Args:
            fs_config: The file storage container configuration
            path_helper: Optional path helper implementation

        Returns:
            A blob storage implementation
        """
        path_helper = path_helper or LocalPathHelper(fs_config)
        return LocalFileStorage(fs_config, path_helper)
