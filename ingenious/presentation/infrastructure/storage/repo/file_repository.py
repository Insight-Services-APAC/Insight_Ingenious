"""
File repository implementation using blob storage.
"""

import logging
import os
from typing import List, Optional

from ingenious.domain.interfaces.repository.file_repository import IFileRepository
from ingenious.domain.interfaces.service.blob_storage import BlobStorageInterface

logger = logging.getLogger(__name__)


class BlobStorageFileRepository(IFileRepository):
    """File repository implementation using blob storage."""

    def __init__(self, blob_storage: BlobStorageInterface):
        """
        Initialize the file repository.

        Args:
            blob_storage: The blob storage implementation
        """
        self.blob_storage = blob_storage

    def _get_full_path(self, file_path: str, file_name: Optional[str] = None) -> str:
        """
        Get the full path for a file.

        Args:
            file_path: The file path
            file_name: Optional file name

        Returns:
            The full path
        """
        if file_name:
            return os.path.join(file_path, file_name)
        return file_path

    async def write_file(self, contents: str, file_name: str, file_path: str) -> str:
        """
        Write a file to storage.

        Args:
            contents: The file contents
            file_name: The file name
            file_path: The file path

        Returns:
            The file path if successful, empty string otherwise
        """
        try:
            full_path = self._get_full_path(file_path, file_name)
            success = await self.blob_storage.upload_blob(contents, full_path)

            if success:
                return full_path
            return ""
        except Exception as e:
            logger.error(f"Failed to write file {file_name} to {file_path}: {e}")
            return ""

    async def read_file(self, file_name: str, file_path: str) -> str:
        """
        Read a file from storage.

        Args:
            file_name: The file name
            file_path: The file path

        Returns:
            The file contents
        """
        try:
            full_path = self._get_full_path(file_path, file_name)
            contents = await self.blob_storage.download_blob(full_path)

            return contents or ""
        except Exception as e:
            logger.error(f"Failed to read file {file_name} from {file_path}: {e}")
            return ""

    async def delete_file(self, file_name: str, file_path: str) -> str:
        """
        Delete a file from storage.

        Args:
            file_name: The file name
            file_path: The file path

        Returns:
            "success" if successful, "error" otherwise
        """
        try:
            full_path = self._get_full_path(file_path, file_name)
            success = await self.blob_storage.delete_blob(full_path)

            if success:
                return "success"
            return "error"
        except Exception as e:
            logger.error(f"Failed to delete file {file_name} from {file_path}: {e}")
            return "error"

    async def list_files(self, file_path: str) -> List[str]:
        """
        List files in a directory.

        Args:
            file_path: The directory path

        Returns:
            A list of file names
        """
        try:
            return await self.blob_storage.list_blobs(file_path)
        except Exception as e:
            logger.error(f"Failed to list files in {file_path}: {e}")
            return []

    async def check_if_file_exists(self, file_path: str, file_name: str) -> bool:
        """
        Check if a file exists.

        Args:
            file_path: The file path
            file_name: The file name

        Returns:
            True if the file exists, False otherwise
        """
        try:
            full_path = self._get_full_path(file_path, file_name)
            return await self.blob_storage.blob_exists(full_path)
        except Exception as e:
            logger.error(
                f"Failed to check if file {file_name} exists in {file_path}: {e}"
            )
            return False
