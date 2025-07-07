"""
CSV parser implementation using pandas.
"""

import os
from typing import List
import pandas as pd
from .base import BaseParser
from ..core.models import PageResult, PageContent, PageMetadata, HeadingInfo
from ..utils.exceptions import CorruptedFileError
from ..utils.logging import logger


class CSVParser(BaseParser):
    """Parser for CSV files using pandas."""

    def supports_file_type(self, file_path: str) -> bool:
        """Check if file is a CSV file."""
        return file_path.lower().endswith(".csv")

    def parse(self, file_path: str) -> List[PageResult]:
        """
        Parse CSV file and extract content.

        Args:
            file_path: Path to the CSV file

        Returns:
            List of PageResult objects (single page for CSV)

        Raises:
            CorruptedFileError: If CSV file is corrupted or unreadable
        """
        try:
            logger.info(f"Starting CSV parsing for: {file_path}")

            # Try different encodings and separators
            df = self._read_csv_with_fallback(file_path)

            # Convert to structured content
            content = self._dataframe_to_content(df, file_path)

            # Calculate metadata
            text = content.text
            metadata_dict = self._calculate_metadata(text)
            metadata = PageMetadata(
                word_count=metadata_dict["word_count"],
                char_count=metadata_dict["char_count"],
            )

            # Create page result (CSV is treated as single page)
            page_result = PageResult(page_number=1, content=content, metadata=metadata)

            logger.info(f"Successfully parsed CSV file with {len(df)} rows")
            return [page_result]

        except Exception as e:
            raise CorruptedFileError(f"Failed to parse CSV file: {str(e)}", file_path)

    def _read_csv_with_fallback(self, file_path: str) -> pd.DataFrame:
        """
        Read CSV with multiple encoding and separator attempts.

        Args:
            file_path: Path to the CSV file

        Returns:
            DataFrame containing CSV data
        """
        # Common encodings to try
        encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
        # Common separators to try
        separators = [",", ";", "\t", "|"]

        for encoding in encodings:
            for sep in separators:
                try:
                    df = pd.read_csv(file_path, encoding=encoding, sep=sep)

                    # Check if the parsing was successful (more than 1 column suggests correct separator)
                    if len(df.columns) > 1 or len(df) > 0:
                        logger.debug(
                            f"Successfully read CSV with encoding={encoding}, separator='{sep}'"
                        )
                        return df

                except Exception:
                    continue

        # If all attempts fail, try with default settings
        logger.warning(f"Using default CSV settings for {file_path}")
        return pd.read_csv(file_path)

    def _dataframe_to_content(self, df: pd.DataFrame, file_path: str) -> PageContent:
        """
        Convert pandas DataFrame to PageContent.

        Args:
            df: DataFrame containing CSV data
            file_path: Path to the CSV file

        Returns:
            PageContent object
        """
        # Generate text representation
        text_parts = []

        # Add file name as heading
        file_name = os.path.basename(file_path)
        text_parts.append(f"CSV File: {file_name}")
        text_parts.append("=" * (len(file_name) + 11))
        text_parts.append("")

        # Add summary statistics
        text_parts.append(f"Rows: {len(df)}")
        text_parts.append(f"Columns: {len(df.columns)}")
        text_parts.append("")

        # Add column headers
        if not df.empty and len(df.columns) > 0:
            headers = " | ".join(str(col) for col in df.columns)
            text_parts.append("Headers:")
            text_parts.append(headers)
            text_parts.append("-" * len(headers))
            text_parts.append("")

            # Add sample data rows (first 20 rows)
            max_display_rows = min(len(df), 20)
            text_parts.append("Data:")
            for index, row in df.head(max_display_rows).iterrows():
                row_text = " | ".join(str(val) if pd.notna(val) else "" for val in row)
                text_parts.append(row_text)

            if len(df) > max_display_rows:
                text_parts.append(f"... ({len(df) - max_display_rows} more rows)")

            # Add column statistics for numeric columns
            numeric_cols = df.select_dtypes(include=["number"]).columns
            if len(numeric_cols) > 0:
                text_parts.append("")
                text_parts.append("Numeric Column Statistics:")
                for col in numeric_cols:
                    stats = df[col].describe()
                    text_parts.append(
                        f"{col}: mean={stats['mean']:.2f}, std={stats['std']:.2f}, min={stats['min']:.2f}, max={stats['max']:.2f}"
                    )
        else:
            text_parts.append("(Empty CSV file)")

        full_text = "\n".join(text_parts)

        # Create paragraphs
        paragraphs = []
        if not df.empty:
            # Summary paragraph
            paragraphs.append(
                f"CSV file with {len(df)} rows and {len(df.columns)} columns"
            )

            # Header paragraph
            if len(df.columns) > 0:
                headers = ", ".join(str(col) for col in df.columns)
                paragraphs.append(f"Columns: {headers}")

            # Sample data paragraphs (limit to avoid too many)
            max_rows = min(len(df), 10)
            for index, row in df.head(max_rows).iterrows():
                row_values = [str(val) if pd.notna(val) else "" for val in row]
                if any(val.strip() for val in row_values):  # Only non-empty rows
                    row_dict = dict(zip(df.columns, row_values))
                    # Create a readable sentence from the row
                    row_description = ", ".join(
                        [f"{k}: {v}" for k, v in row_dict.items() if v.strip()]
                    )
                    paragraphs.append(row_description)

            if len(df) > max_rows:
                paragraphs.append(f"Additional {len(df) - max_rows} rows available")

        # Create headings
        headings = [
            HeadingInfo(level=1, text=f"CSV File: {os.path.basename(file_path)}")
        ]

        # Add column headers as level 2 headings
        if not df.empty and len(df.columns) > 0:
            headings.append(HeadingInfo(level=2, text="Data Columns"))
            for col in df.columns:
                if str(col).strip():
                    headings.append(HeadingInfo(level=3, text=str(col)))

        return PageContent(text=full_text, paragraphs=paragraphs, headings=headings)
