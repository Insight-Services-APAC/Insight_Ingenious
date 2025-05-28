"""
Interface for path helpers used in storage implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional


class PathHelperInterface(ABC):
    """Interface for path helper implementations."""

    @abstractmethod
    def get_absolute_path(self, relative_path: str) -> str:
        """
        Get the absolute path for a given relative path.

        Args:
            relative_path: The relative path

        Returns:
            The absolute path
        """
        pass

    @abstractmethod
    def get_relative_path(self, absolute_path: str) -> Optional[str]:
        """
        Get the relative path from an absolute path.

        Args:
            absolute_path: The absolute path

        Returns:
            The relative path, or None if the path is not within the container
        """
        pass
