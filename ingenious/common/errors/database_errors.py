"""
Database-related error classes for the Ingenious framework.

This module provides specialized error classes for database operations,
ensuring consistent error handling for database-related issues.
"""

from typing import Optional

from ingenious.common.errors.base import IngeniousError

__all__ = [
    "DatabaseError",
    "ConnectionError",
    "QueryError",
    "DataIntegrityError",
    "TransactionError",
]


class DatabaseError(IngeniousError):
    """Base class for database-related errors."""

    def __init__(
        self,
        message: str = "A database error occurred",
        database_name: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the database error.

        Args:
            message: Human-readable error message
            database_name: Name of the database that encountered the error
            operation: Database operation that failed
            **kwargs: Additional arguments to pass to the parent class
        """
        details = {}
        if database_name:
            details["database_name"] = database_name
        if operation:
            details["operation"] = operation

        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR",
            details=details,
            **kwargs,
        )


class ConnectionError(DatabaseError):
    """Error raised when a database connection fails."""

    def __init__(self, message: str = "Database connection failed", **kwargs):
        """
        Initialize the connection error.

        Args:
            message: Human-readable error message
            **kwargs: Additional arguments to pass to the parent class
        """
        super().__init__(
            message=message, error_code="DATABASE_CONNECTION_ERROR", **kwargs
        )


class QueryError(DatabaseError):
    """Error raised when a database query fails."""

    def __init__(
        self,
        message: str = "Database query failed",
        query: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the query error.

        Args:
            message: Human-readable error message
            query: The query that failed
            **kwargs: Additional arguments to pass to the parent class
        """
        details = kwargs.get("details", {})
        if query:
            # Truncate long queries for the log
            truncated_query = query[:500] + "..." if len(query) > 500 else query
            details["query"] = truncated_query

        super().__init__(
            message=message,
            error_code="DATABASE_QUERY_ERROR",
            details=details,
            **kwargs,
        )


class DataIntegrityError(DatabaseError):
    """Error raised when a database operation violates data integrity."""

    def __init__(
        self,
        message: str = "Database data integrity violation",
        constraint: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the data integrity error.

        Args:
            message: Human-readable error message
            constraint: The constraint that was violated
            **kwargs: Additional arguments to pass to the parent class
        """
        details = kwargs.get("details", {})
        if constraint:
            details["constraint"] = constraint

        super().__init__(
            message=message,
            error_code="DATA_INTEGRITY_ERROR",
            details=details,
            **kwargs,
        )


class TransactionError(DatabaseError):
    """Error raised when a database transaction fails."""

    def __init__(self, message: str = "Database transaction failed", **kwargs):
        """
        Initialize the transaction error.

        Args:
            message: Human-readable error message
            **kwargs: Additional arguments to pass to the parent class
        """
        super().__init__(message=message, error_code="TRANSACTION_ERROR", **kwargs)
