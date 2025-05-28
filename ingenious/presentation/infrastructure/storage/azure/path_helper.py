from pathlib import Path
from typing import Optional

from ingenious.domain.interfaces.service.path_helper import PathHelperInterface
from ingenious.domain.model.config import FileStorageContainer


class AzurePathHelper(PathHelperInterface):
    """Helper class for constructing and validating Azure Blob Storage paths."""

    def __init__(self, fs_config: FileStorageContainer):
        """
        Initialize the path helper.

        Args:
            fs_config: The file storage container configuration
        """
        self.fs_config = fs_config

    def construct_blob_path(
        self, file_path: str, file_name: Optional[str] = None
    ) -> str:
        """
        Construct a blob path for Azure Storage.

        Args:
            file_path: The file path
            file_name: Optional file name to append

        Returns:
            The full blob path
        """
        path = Path(self.fs_config.path) / Path(file_path)

        if file_name:
            path = path / Path(file_name)

        # Convert to string with forward slashes for Azure
        return str(path).replace("\\", "/")

    def is_directory(self, path: str) -> bool:
        """
        Check if a path refers to a directory (no file extension).

        Args:
            path: The path to check

        Returns:
            True if the path is a directory, False otherwise
        """
        return not Path(path).suffix

    def get_absolute_path(self, relative_path: str) -> str:
        """
        Get the absolute path for a given relative path.

        Args:
            relative_path: The relative path

        Returns:
            The absolute path
        """
        return self.construct_blob_path(relative_path)

    def get_relative_path(self, absolute_path: str) -> Optional[str]:
        """
        Get the relative path from an absolute path.

        Args:
            absolute_path: The absolute path

        Returns:
            The relative path, or None if the path is not within the container
        """
        base_path = Path(self.fs_config.path)
        try:
            full_path = Path(absolute_path)
            # Check if the absolute path starts with the base path
            if str(full_path).startswith(str(base_path)):
                return str(full_path.relative_to(base_path))
            return None
        except ValueError:
            # Path is not relative to the base path
            return None
