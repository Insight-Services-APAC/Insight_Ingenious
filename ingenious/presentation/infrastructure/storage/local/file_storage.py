"""
Implementation of local file storage.
"""

import logging
import os
from pathlib import Path
from typing import List, Optional

from ingenious.domain.interfaces.service.blob_storage import BlobStorageInterface
from ingenious.domain.interfaces.service.path_helper import PathHelperInterface
from ingenious.domain.model.config import FileStorageContainer

logger = logging.getLogger(__name__)


class LocalPathHelper(PathHelperInterface):
    """Helper class for constructing and validating local file paths."""

    def __init__(self, fs_config: FileStorageContainer):
        """
        Initialize the path helper.

        Args:
            fs_config: The file storage container configuration
        """
        self.fs_config = fs_config
        self.base_path = Path(fs_config.path)

    def get_absolute_path(self, relative_path: str) -> str:
        """
        Get the absolute path for a given relative path.

        Args:
            relative_path: The relative path

        Returns:
            The absolute path
        """
        return str(self.base_path / Path(relative_path))

    def get_relative_path(self, absolute_path: str) -> Optional[str]:
        """
        Get the relative path from an absolute path.

        Args:
            absolute_path: The absolute path

        Returns:
            The relative path, or None if the path is not within the container
        """
        try:
            full_path = Path(absolute_path)
            if str(full_path).startswith(str(self.base_path)):
                return str(full_path.relative_to(self.base_path))
            return None
        except ValueError:
            # Path is not relative to the base path
            return None


class LocalFileStorage(BlobStorageInterface):
    """Implementation of local file storage."""

    def __init__(
        self,
        fs_config: FileStorageContainer,
        path_helper: Optional[PathHelperInterface] = None,
    ):
        """
        Initialize the local file storage.

        Args:
            fs_config: The file storage container configuration
            path_helper: Optional path helper implementation
        """
        self.fs_config = fs_config
        self.path_helper = path_helper or LocalPathHelper(fs_config)

    async def ensure_container_exists(self) -> None:
        """
        Ensure the storage container (directory) exists, creating it if it doesn't.
        """
        base_path = Path(self.fs_config.path)
        os.makedirs(base_path, exist_ok=True)

    async def upload_blob(self, contents: str, blob_path: str) -> bool:
        """
        Upload content to a file.

        Args:
            contents: The content to upload
            blob_path: The path to the file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure the container exists
            await self.ensure_container_exists()

            # Get the absolute file path
            file_path = self.path_helper.get_absolute_path(blob_path)

            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Write the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(contents)
            return True
        except Exception as e:
            logger.error(f"Failed to write file {blob_path}: {e}")
            return False

    async def download_blob(self, blob_path: str) -> Optional[str]:
        """
        Download content from a file.

        Args:
            blob_path: The path to the file

        Returns:
            The file content as a string, or None if unsuccessful
        """
        try:
            # Get the absolute file path
            file_path = self.path_helper.get_absolute_path(blob_path)

            # Read the file
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read file {blob_path}: {e}")
            return None

    async def delete_blob(self, blob_path: str) -> bool:
        """
        Delete a file.

        Args:
            blob_path: The path to the file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the absolute file path
            file_path = self.path_helper.get_absolute_path(blob_path)

            # Delete the file
            os.remove(file_path)
            return True
        except Exception as e:
            logger.error(f"Failed to delete file {blob_path}: {e}")
            return False

    async def list_blobs(self, prefix: str) -> List[str]:
        """
        List files with the specified prefix.

        Args:
            prefix: The prefix to filter files by

        Returns:
            A list of file paths
        """
        try:
            # Get the absolute directory path
            dir_path = self.path_helper.get_absolute_path(prefix)

            # List files with the prefix
            base_path = Path(self.fs_config.path)
            result = []

            for root, _, files in os.walk(dir_path):
                for file in files:
                    full_path = Path(os.path.join(root, file))
                    relative_path = full_path.relative_to(base_path)
                    result.append(str(relative_path))

            return result
        except Exception as e:
            logger.error(f"Failed to list files with prefix {prefix}: {e}")
            return []

    async def blob_exists(self, blob_path: str) -> bool:
        """
        Check if a file exists.

        Args:
            blob_path: The path to the file

        Returns:
            True if the file exists, False otherwise
        """
        try:
            # Get the absolute file path
            file_path = self.path_helper.get_absolute_path(blob_path)

            # Check if the file exists
            return os.path.isfile(file_path)
        except Exception as e:
            logger.error(f"Failed to check if file {blob_path} exists: {e}")
            return False
