"""
Abstract base class for document parsers.
"""

from abc import ABC, abstractmethod
from typing import List
from ..core.models import PageResult


class BaseParser(ABC):
    """Abstract base class for document parsers."""

    @abstractmethod
    def parse(self, file_path: str) -> List[PageResult]:
        """
        Parse a document file and return page results.

        Args:
            file_path: Path to the document file

        Returns:
            List of PageResult objects, one for each page

        Raises:
            DocumentParsingError: If parsing fails
        """
        pass

    @abstractmethod
    def supports_file_type(self, file_path: str) -> bool:
        """
        Check if this parser supports the given file type.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file type is supported, False otherwise
        """
        pass

    def _calculate_metadata(self, text: str) -> dict:
        """
        Calculate metadata for text content.

        Args:
            text: Text content to analyze

        Returns:
            Dictionary with word_count and char_count
        """
        return {"word_count": len(text.split()), "char_count": len(text)}
