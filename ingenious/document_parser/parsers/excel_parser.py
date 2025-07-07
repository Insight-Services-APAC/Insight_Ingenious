"""
Excel parser implementation using pandas.
"""

from typing import List
import pandas as pd
from .base import BaseParser
from ..core.models import PageResult, PageContent, PageMetadata, HeadingInfo
from ..utils.exceptions import CorruptedFileError
from ..utils.logging import logger


class ExcelParser(BaseParser):
    """Parser for Excel files using pandas."""

    def supports_file_type(self, file_path: str) -> bool:
        """Check if file is an Excel file."""
        return file_path.lower().endswith((".xlsx", ".xls", ".xlsm"))

    def parse(self, file_path: str) -> List[PageResult]:
        """
        Parse Excel file and extract content sheet by sheet.

        Args:
            file_path: Path to the Excel file

        Returns:
            List of PageResult objects (one per sheet)

        Raises:
            CorruptedFileError: If Excel file is corrupted or unreadable
        """
        try:
            logger.info(f"Starting Excel parsing for: {file_path}")

            # Read all sheets from Excel file
            excel_file = pd.ExcelFile(file_path)
            pages = []

            for sheet_num, sheet_name in enumerate(excel_file.sheet_names, 1):
                logger.debug(f"Processing sheet {sheet_num}: {sheet_name}")

                # Read the sheet
                df = pd.read_excel(file_path, sheet_name=sheet_name)

                # Convert to structured content
                content = self._dataframe_to_content(df, sheet_name)

                # Calculate metadata
                text = content.text
                metadata_dict = self._calculate_metadata(text)
                metadata = PageMetadata(
                    word_count=metadata_dict["word_count"],
                    char_count=metadata_dict["char_count"],
                )

                # Create page result (treating each sheet as a page)
                page_result = PageResult(
                    page_number=sheet_num, content=content, metadata=metadata
                )

                pages.append(page_result)

            logger.info(f"Successfully parsed {len(pages)} sheets from Excel file")
            return pages

        except Exception as e:
            raise CorruptedFileError(f"Failed to parse Excel file: {str(e)}", file_path)

    def _dataframe_to_content(self, df: pd.DataFrame, sheet_name: str) -> PageContent:
        """
        Convert pandas DataFrame to PageContent.

        Args:
            df: DataFrame containing sheet data
            sheet_name: Name of the sheet

        Returns:
            PageContent object
        """
        # Generate text representation
        text_parts = []

        # Add sheet name as heading
        text_parts.append(f"Sheet: {sheet_name}")
        text_parts.append("=" * (len(sheet_name) + 7))
        text_parts.append("")

        # Add column headers
        if not df.empty and len(df.columns) > 0:
            headers = " | ".join(str(col) for col in df.columns)
            text_parts.append(headers)
            text_parts.append("-" * len(headers))

            # Add data rows
            for index, row in df.iterrows():
                row_text = " | ".join(str(val) if pd.notna(val) else "" for val in row)
                text_parts.append(row_text)
        else:
            text_parts.append("(Empty sheet)")

        full_text = "\n".join(text_parts)

        # Create paragraphs (each row as a paragraph)
        paragraphs = []
        if not df.empty:
            # Header paragraph
            if len(df.columns) > 0:
                headers = " | ".join(str(col) for col in df.columns)
                paragraphs.append(f"Headers: {headers}")

            # Data paragraphs (limit to avoid too many paragraphs)
            max_rows = min(len(df), 50)  # Limit to first 50 rows for readability
            for index, row in df.head(max_rows).iterrows():
                row_values = [str(val) if pd.notna(val) else "" for val in row]
                if any(val.strip() for val in row_values):  # Only non-empty rows
                    row_text = " | ".join(row_values)
                    paragraphs.append(row_text)

            if len(df) > max_rows:
                paragraphs.append(f"... ({len(df) - max_rows} more rows)")

        # Create headings
        headings = [HeadingInfo(level=1, text=f"Sheet: {sheet_name}")]

        # Add column headers as level 2 headings if they exist
        if not df.empty and len(df.columns) > 0:
            for col in df.columns:
                if str(col).strip() and str(col) != "Unnamed":
                    headings.append(HeadingInfo(level=2, text=str(col)))

        return PageContent(text=full_text, paragraphs=paragraphs, headings=headings)
