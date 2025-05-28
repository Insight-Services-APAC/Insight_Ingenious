"""
Factory for creating database clients.
"""

from ingenious.domain.interfaces.repository.database import DatabaseInterface
from ingenious.presentation.infrastructure.database.duckdb.client import DuckDBClient
from ingenious.presentation.infrastructure.database.sqlite.client import SQLiteClient


class DatabaseFactory:
    """Factory for creating database clients."""

    @staticmethod
    def create_sqlite_client(database_path: str) -> DatabaseInterface:
        """
        Create a SQLite database client.

        Args:
            database_path: Path to the SQLite database file

        Returns:
            A database client
        """
        return SQLiteClient(database_path)

    @staticmethod
    def create_duckdb_client(database_path: str) -> DatabaseInterface:
        """
        Create a DuckDB database client.

        Args:
            database_path: Path to the DuckDB database file

        Returns:
            A database client
        """
        return DuckDBClient(database_path)
