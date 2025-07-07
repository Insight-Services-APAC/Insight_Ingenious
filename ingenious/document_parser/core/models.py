"""
Data models for document parsing results.
"""

from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass, asdict, field
import json


@dataclass
class HeadingInfo:
    """Information about a heading in the document."""

    level: int
    text: str


@dataclass
class TableCell:
    """A single cell in a table."""

    text: str


@dataclass
class TableRow:
    """A row in a table."""

    cells: List[TableCell]


@dataclass
class TableContent:
    """A table within document content."""

    rows: List[TableRow]


@dataclass
class PageContent:
    """Content extracted from a single page."""

    text: str
    paragraphs: List[str]
    headings: List[HeadingInfo]
    tables: List[TableContent] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "paragraphs": self.paragraphs,
            "headings": [asdict(heading) for heading in self.headings],
            "tables": [asdict(table) for table in self.tables],
        }


@dataclass
class PageMetadata:
    """Metadata for a single page."""

    word_count: int
    char_count: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class PageResult:
    """Complete result for a single page."""

    page_number: int
    content: PageContent
    metadata: PageMetadata

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "page_number": self.page_number,
            "content": self.content.to_dict(),
            "metadata": self.metadata.to_dict(),
        }


@dataclass
class DocumentInfo:
    """Information about the parsed document."""

    filename: str
    file_type: str
    total_pages: int
    created_at: datetime
    file_size: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "filename": self.filename,
            "file_type": self.file_type,
            "total_pages": self.total_pages,
            "created_at": self.created_at.isoformat(),
            "file_size": self.file_size,
        }


@dataclass
class DocumentResult:
    """Complete result of document parsing."""

    document_info: DocumentInfo
    pages: List[PageResult]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "document_info": self.document_info.to_dict(),
            "pages": [page.to_dict() for page in self.pages],
        }

    def to_json(self, pretty: bool = False) -> str:
        """
        Convert to JSON string.

        Args:
            pretty: Whether to format JSON with indentation

        Returns:
            JSON string representation
        """
        data = self.to_dict()
        if pretty:
            return json.dumps(data, indent=2, ensure_ascii=False)
        return json.dumps(data, ensure_ascii=False)

    def save_to_file(self, filepath: str, pretty: bool = True) -> None:
        """
        Save result to JSON file.

        Args:
            filepath: Path to save the JSON file
            pretty: Whether to format JSON with indentation
        """
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_json(pretty=pretty))
