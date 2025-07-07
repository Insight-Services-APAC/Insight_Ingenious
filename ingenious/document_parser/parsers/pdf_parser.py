"""
PDF parser implementation using pdfplumber.
"""

from typing import List
import pdfplumber
from .base import BaseParser
from ..core.models import PageResult, PageContent, PageMetadata, HeadingInfo
from ..utils.exceptions import CorruptedFileError, PasswordProtectedError
from ..utils.logging import logger


class PDFParser(BaseParser):
    """Parser for PDF files using pdfplumber."""

    def supports_file_type(self, file_path: str) -> bool:
        """Check if file is a PDF."""
        return file_path.lower().endswith(".pdf")

    def parse(self, file_path: str) -> List[PageResult]:
        """
        Parse PDF file and extract content page by page.

        Args:
            file_path: Path to the PDF file

        Returns:
            List of PageResult objects

        Raises:
            CorruptedFileError: If PDF is corrupted
            PasswordProtectedError: If PDF is password protected
        """
        try:
            logger.info(f"Starting PDF parsing for: {file_path}")

            with pdfplumber.open(file_path) as pdf:
                pages = []

                for page_num, page in enumerate(pdf.pages, 1):
                    logger.debug(f"Processing page {page_num}")

                    # Extract text
                    text = page.extract_text() or ""

                    # Extract paragraphs (split by double newlines)
                    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

                    # Extract headings (basic heuristic - lines that are short and in caps)
                    headings = self._extract_headings(text)

                    # Create page content
                    content = PageContent(
                        text=text, paragraphs=paragraphs, headings=headings
                    )

                    # Calculate metadata
                    metadata_dict = self._calculate_metadata(text)
                    metadata = PageMetadata(
                        word_count=metadata_dict["word_count"],
                        char_count=metadata_dict["char_count"],
                    )

                    # Create page result
                    page_result = PageResult(
                        page_number=page_num, content=content, metadata=metadata
                    )

                    pages.append(page_result)

                logger.info(f"Successfully parsed {len(pages)} pages from PDF")
                return pages

        except Exception as e:
            if "password" in str(e).lower():
                raise PasswordProtectedError(
                    f"PDF file is password protected: {file_path}", file_path
                )
            else:
                raise CorruptedFileError(
                    f"Failed to parse PDF file: {str(e)}", file_path
                )

    def _extract_headings(self, text: str) -> List[HeadingInfo]:
        """
        Extract headings from text using basic heuristics.

        Args:
            text: Text content to analyze

        Returns:
            List of HeadingInfo objects
        """
        headings = []
        lines = text.split("\n")

        for line in lines:
            line = line.strip()

            # Basic heuristic: short lines (< 80 chars) that are mostly uppercase
            # or start with common heading patterns
            if (
                line
                and len(line) < 80
                and (
                    line.isupper()
                    or any(
                        line.startswith(pattern)
                        for pattern in ["Chapter", "Section", "1.", "2.", "3."]
                    )
                )
            ):
                # Determine heading level based on content
                level = 1
                if any(line.startswith(pattern) for pattern in ["1.", "2.", "3."]):
                    level = 2
                elif "section" in line.lower():
                    level = 3

                headings.append(HeadingInfo(level=level, text=line))

        return headings
