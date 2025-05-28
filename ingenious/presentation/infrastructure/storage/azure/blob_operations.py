import logging
from typing import List, Optional

from azure.storage.blob import BlobClient, BlobServiceClient, ContainerClient

from ingenious.domain.interfaces.service.blob_storage import BlobStorageInterface
from ingenious.domain.interfaces.service.path_helper import PathHelperInterface
from ingenious.domain.model.config import FileStorageContainer
from ingenious.presentation.infrastructure.storage.azure.path_helper import (
    AzurePathHelper,
)

logger = logging.getLogger(__name__)


class AzureBlobOperations(BlobStorageInterface):
    """Class for performing operations on Azure Blob Storage."""

    def __init__(
        self,
        blob_service_client: BlobServiceClient,
        fs_config: FileStorageContainer,
        path_helper: Optional[PathHelperInterface] = None,
    ):
        """
        Initialize the blob operations.

        Args:
            blob_service_client: The Azure Blob Service client
            fs_config: The file storage container configuration
            path_helper: Optional path helper implementation
        """
        self.blob_service_client = blob_service_client
        self.fs_config = fs_config
        self.container_name = fs_config.container_name
        self.path_helper = path_helper or AzurePathHelper(fs_config)

    def get_container_client(self) -> ContainerClient:
        """
        Get a container client for the configured container.

        Returns:
            The container client
        """
        return self.blob_service_client.get_container_client(self.container_name)

    def get_blob_client(self, blob_path: str) -> BlobClient:
        """
        Get a blob client for the specified blob path.

        Args:
            blob_path: The path to the blob

        Returns:
            The blob client
        """
        return self.blob_service_client.get_blob_client(
            container=self.container_name, blob=blob_path
        )

    async def ensure_container_exists(self):
        """Ensure the container exists, creating it if it doesn't."""
        container_client = self.get_container_client()

        if not container_client.container_name:
            container_client.create_container()

    async def upload_blob(self, contents: str, blob_path: str) -> bool:
        """
        Upload content to a blob.

        Args:
            contents: The content to upload
            blob_path: The path to the blob

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure the container exists
            await self.ensure_container_exists()

            # Get a blob client
            blob_client = self.get_blob_client(blob_path)

            # Upload the content
            blob_client.upload_blob(contents, overwrite=True)
            return True
        except Exception as e:
            logger.error(f"Failed to upload blob {blob_path}: {e}")
            return False

    async def download_blob(self, blob_path: str) -> Optional[str]:
        """
        Download content from a blob.

        Args:
            blob_path: The path to the blob

        Returns:
            The blob content as a string, or None if unsuccessful
        """
        try:
            # Get a blob client
            blob_client = self.get_blob_client(blob_path)

            # Download the blob
            downloader = blob_client.download_blob(max_concurrency=1, encoding="UTF-8")
            return downloader.readall()
        except Exception as e:
            logger.error(f"Failed to download blob {blob_path}: {e}")
            return None

    async def delete_blob(self, blob_path: str) -> bool:
        """
        Delete a blob.

        Args:
            blob_path: The path to the blob

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get a blob client
            blob_client = self.get_blob_client(blob_path)

            # Delete the blob
            blob_client.delete_blob()
            return True
        except Exception as e:
            logger.error(f"Failed to delete blob {blob_path}: {e}")
            return False

    async def list_blobs(self, prefix: str) -> List[str]:
        """
        List blobs with the specified prefix.

        Args:
            prefix: The prefix to filter blobs by

        Returns:
            A list of blob names
        """
        try:
            # Get a container client
            container_client = self.get_container_client()

            # List blobs with the prefix
            return [
                blob.name
                for blob in container_client.list_blobs(name_starts_with=prefix)
            ]
        except Exception as e:
            logger.error(f"Failed to list blobs with prefix {prefix}: {e}")
            return []

    async def blob_exists(self, blob_path: str) -> bool:
        """
        Check if a blob exists.

        Args:
            blob_path: The path to the blob

        Returns:
            True if the blob exists, False otherwise
        """
        try:
            # Get a blob client
            blob_client = self.get_blob_client(blob_path)

            # Check if the blob exists
            return blob_client.exists()
        except Exception as e:
            logger.error(f"Failed to check if blob {blob_path} exists: {e}")
            return False
