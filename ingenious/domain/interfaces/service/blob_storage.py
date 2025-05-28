"""
Interface for blob storage operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class BlobStorageInterface(ABC):
    """Interface for blob storage implementations."""

    @abstractmethod
    async def ensure_container_exists(self) -> None:
        """
        Ensure the storage container exists, creating it if it doesn't.
        """
        pass

    @abstractmethod
    async def upload_blob(self, contents: str, blob_path: str) -> bool:
        """
        Upload content to a blob.

        Args:
            contents: The content to upload
            blob_path: The path to the blob

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def download_blob(self, blob_path: str) -> Optional[str]:
        """
        Download content from a blob.

        Args:
            blob_path: The path to the blob

        Returns:
            The blob content as a string, or None if unsuccessful
        """
        pass

    @abstractmethod
    async def delete_blob(self, blob_path: str) -> bool:
        """
        Delete a blob.

        Args:
            blob_path: The path to the blob

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def list_blobs(self, prefix: str) -> List[str]:
        """
        List blobs with the specified prefix.

        Args:
            prefix: The prefix to filter blobs by

        Returns:
            A list of blob names
        """
        pass

    @abstractmethod
    async def blob_exists(self, blob_path: str) -> bool:
        """
        Check if a blob exists.

        Args:
            blob_path: The path to the blob

        Returns:
            True if the blob exists, False otherwise
        """
        pass
