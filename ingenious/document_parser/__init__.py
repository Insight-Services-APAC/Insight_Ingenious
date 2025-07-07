"""
Document Parser Package

A professional Python package for parsing PDF and DOCX files into structured JSON format.
"""

from .core.models import DocumentResult, PageContent, DocumentInfo

__version__ = "1.0.0"
__author__ = "Document Parser Team"
__email__ = "support@documentparser.com"


# Delayed import to avoid circular dependency issues
def get_document_parser():
    """Get DocumentParser class with delayed import."""
    from .core.parser import DocumentParser

    return DocumentParser


# Create a class proxy for better import experience
class DocumentParser:
    """Proxy class for DocumentParser with delayed import."""

    def __new__(cls, *args, **kwargs):
        from .core.parser import DocumentParser as ActualDocumentParser

        return ActualDocumentParser(*args, **kwargs)


__all__ = [
    "DocumentParser",
    "DocumentResult",
    "PageContent",
    "DocumentInfo",
    "get_document_parser",
]
