"""
Custom exceptions for the document parser package.
"""


class DocumentParsingError(Exception):
    """Base exception for document parsing errors."""

    def __init__(self, message: str, filename: str = None) -> None:
        """
        Initialize the DocumentParsingError.

        Args:
            message: Error message
            filename: Name of the file that caused the error
        """
        self.filename = filename
        super().__init__(message)


class UnsupportedFileTypeError(DocumentParsingError):
    """Raised when trying to parse an unsupported file type."""

    pass


class CorruptedFileError(DocumentParsingError):
    """Raised when a file is corrupted or cannot be read."""

    pass


class PasswordProtectedError(DocumentParsingError):
    """Raised when a file is password protected."""

    pass


class FileNotFoundError(DocumentParsingError):
    """Raised when a file cannot be found."""

    pass


class InvalidConfigurationError(Exception):
    """Raised when configuration parameters are invalid."""

    pass
