"""
DOCX parser implementation using python-docx.
"""

from typing import List, Dict, Any
from docx import Document
from .base import BaseParser
from ..core.models import PageResult, PageContent, PageMetadata, HeadingInfo
from ..utils.exceptions import CorruptedFileError
from ..utils.logging import logger


class DOCXParser(BaseParser):
    """Parser for DOCX files using python-docx."""

    def supports_file_type(self, file_path: str) -> bool:
        """Check if file is a DOCX."""
        return file_path.lower().endswith(".docx")

    def parse(self, file_path: str) -> List[PageResult]:
        """
        Parse DOCX file and extract content.

        Note: DOCX files don't have explicit pages, so we simulate pages
        by splitting content into chunks based on page breaks or content length.

        Args:
            file_path: Path to the DOCX file

        Returns:
            List of PageResult objects

        Raises:
            CorruptedFileError: If DOCX is corrupted
        """
        try:
            logger.info(f"Starting DOCX parsing for: {file_path}")

            doc = Document(file_path)

            # Extract all content with structure information
            all_content = self._extract_structured_content(doc)

            # Since DOCX doesn't have explicit pages, we'll create logical pages
            # based on content structure (sections, page breaks, or content length)
            pages = self._create_logical_pages(all_content)

            logger.info(f"Successfully parsed {len(pages)} logical pages from DOCX")
            return pages

        except Exception as e:
            raise CorruptedFileError(f"Failed to parse DOCX file: {str(e)}", file_path)

    def _extract_structured_content(self, doc: Document) -> Dict[str, Any]:
        """
        Extract structured content from DOCX document.

        Args:
            doc: Document object

        Returns:
            Dictionary with structured content
        """
        content = {"paragraphs": [], "headings": [], "text": "", "page_breaks": []}

        full_text = []

        for i, paragraph in enumerate(doc.paragraphs):
            text = paragraph.text.strip()

            if not text:
                continue

            full_text.append(text)
            content["paragraphs"].append(text)

            # Check if this is a heading
            if paragraph.style.name.startswith("Heading"):
                level = (
                    int(paragraph.style.name.split()[-1])
                    if paragraph.style.name.split()[-1].isdigit()
                    else 1
                )
                content["headings"].append(HeadingInfo(level=level, text=text))

            # Check for page breaks (this is a simplified approach)
            if any(run.text == "\f" for run in paragraph.runs):
                content["page_breaks"].append(i)

        content["text"] = "\n".join(full_text)
        return content

    def _create_logical_pages(self, content: Dict[str, Any]) -> List[PageResult]:
        """
        Create logical pages from DOCX content.

        Args:
            content: Structured content dictionary

        Returns:
            List of PageResult objects
        """
        pages = []
        paragraphs = content["paragraphs"]
        headings = content["headings"]
        page_breaks = content["page_breaks"]

        # If we have explicit page breaks, use them
        if page_breaks:
            current_start = 0
            page_num = 1

            for break_pos in page_breaks + [len(paragraphs)]:
                page_paragraphs = paragraphs[current_start:break_pos]
                if page_paragraphs:
                    page = self._create_page_result(page_num, page_paragraphs, headings)
                    pages.append(page)
                    page_num += 1
                current_start = break_pos
        else:
            # No explicit page breaks, create logical pages based on content length
            # Target approximately 500 words per page
            target_words_per_page = 500
            current_paragraphs = []
            current_word_count = 0
            page_num = 1

            for paragraph in paragraphs:
                word_count = len(paragraph.split())

                # If adding this paragraph would exceed target, create a new page
                if (
                    current_word_count + word_count > target_words_per_page
                    and current_paragraphs
                ):
                    page = self._create_page_result(
                        page_num, current_paragraphs, headings
                    )
                    pages.append(page)
                    current_paragraphs = []
                    current_word_count = 0
                    page_num += 1

                current_paragraphs.append(paragraph)
                current_word_count += word_count

            # Add the last page if there's remaining content
            if current_paragraphs:
                page = self._create_page_result(page_num, current_paragraphs, headings)
                pages.append(page)

        # If no pages were created, create at least one empty page
        if not pages:
            empty_page = self._create_page_result(1, [], [])
            pages.append(empty_page)

        return pages

    def _create_page_result(
        self, page_num: int, paragraphs: List[str], all_headings: List[HeadingInfo]
    ) -> PageResult:
        """
        Create a PageResult from paragraphs and headings.

        Args:
            page_num: Page number
            paragraphs: List of paragraph texts
            all_headings: All headings in the document

        Returns:
            PageResult object
        """
        text = "\n\n".join(paragraphs)

        # Filter headings that appear in this page's content
        page_headings = [heading for heading in all_headings if heading.text in text]

        content = PageContent(text=text, paragraphs=paragraphs, headings=page_headings)

        metadata_dict = self._calculate_metadata(text)
        metadata = PageMetadata(
            word_count=metadata_dict["word_count"],
            char_count=metadata_dict["char_count"],
        )

        return PageResult(page_number=page_num, content=content, metadata=metadata)

    def _process_table(self, table) -> Any:
        """
        Process a DOCX table and convert it to structured format.

        Args:
            table: DOCX table object

        Returns:
            Table content object with rows and cells
        """
        from ..core.models import TableContent, TableRow, TableCell

        rows = []
        for row in table.rows:
            cells = []
            for cell in row.cells:
                table_cell = TableCell(text=cell.text.strip())
                cells.append(table_cell)
            table_row = TableRow(cells=cells)
            rows.append(table_row)

        return TableContent(rows=rows)

    def _extract_headings_from_paragraphs(self, paragraphs) -> List[HeadingInfo]:
        """
        Extract headings from DOCX paragraphs based on their styles.

        Args:
            paragraphs: List of DOCX paragraph objects

        Returns:
            List of HeadingInfo objects
        """
        headings = []

        for paragraph in paragraphs:
            style_name = paragraph.style.name

            # Check if paragraph is a heading style
            if style_name.startswith("Heading"):
                try:
                    # Extract heading level from style name (e.g., "Heading 1" -> 1)
                    level = int(style_name.split()[-1])
                    heading = HeadingInfo(level=level, text=paragraph.text.strip())
                    headings.append(heading)
                except (ValueError, IndexError):
                    # If we can't parse the level, treat as level 1
                    heading = HeadingInfo(level=1, text=paragraph.text.strip())
                    headings.append(heading)

        return headings
