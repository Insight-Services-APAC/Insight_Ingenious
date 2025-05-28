"""
DuckDB database client implementation.
"""

import logging
import os
import uuid
from typing import Any, Dict, List, Optional, Union

import duckdb

from ingenious.presentation.infrastructure.database.base_client import (
    BaseDatabaseClient,
)

logger = logging.getLogger(__name__)


class DuckDBClient(BaseDatabaseClient):
    """DuckDB database client implementation."""

    def __init__(self, database_path: str):
        """
        Initialize the DuckDB client.

        Args:
            database_path: Path to the DuckDB database file
        """
        self.database_path = database_path
        self.connection = None

    async def connect(self) -> None:
        """
        Connect to the database.
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.database_path), exist_ok=True)

            # Connect to the database
            self.connection = duckdb.connect(self.database_path)
            logger.info(f"Connected to DuckDB database at {self.database_path}")
        except Exception as e:
            logger.error(f"Failed to connect to DuckDB database: {e}")
            raise

    async def disconnect(self) -> None:
        """
        Disconnect from the database.
        """
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info(f"Disconnected from DuckDB database at {self.database_path}")

    async def _ensure_connected(self) -> None:
        """
        Ensure the database is connected.
        """
        if not self.connection:
            await self.connect()

    async def query(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a query and return the results.

        Args:
            query: The query to execute
            parameters: Optional query parameters

        Returns:
            The query results
        """
        await self._ensure_connected()

        try:
            if parameters:
                result = self.connection.execute(query, parameters).fetchall()
            else:
                result = self.connection.execute(query).fetchall()

            # Convert to list of dictionaries
            column_names = [desc[0] for desc in self.connection.description]
            return [dict(zip(column_names, row)) for row in result]
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            raise

    async def execute(
        self, statement: str, parameters: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Execute a statement.

        Args:
            statement: The statement to execute
            parameters: Optional statement parameters
        """
        await self._ensure_connected()

        try:
            if parameters:
                self.connection.execute(statement, parameters)
            else:
                self.connection.execute(statement)
        except Exception as e:
            logger.error(f"Failed to execute statement: {e}")
            raise

    async def insert(self, table: str, data: Dict[str, Any]) -> str:
        """
        Insert data into a table.

        Args:
            table: The table name
            data: The data to insert

        Returns:
            The ID of the inserted record
        """
        await self._ensure_connected()

        try:
            # Generate a UUID if id is not provided
            if "id" not in data:
                data["id"] = str(uuid.uuid4())

            # Build the SQL statement
            columns = ", ".join(data.keys())
            placeholders = ", ".join([f"${i + 1}" for i in range(len(data))])
            values = list(data.values())

            statement = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

            # Execute the statement
            self.connection.execute(statement, values)

            return data["id"]
        except Exception as e:
            logger.error(f"Failed to insert data: {e}")
            raise

    async def update(
        self,
        table: str,
        id_column: str,
        id_value: Union[str, int],
        data: Dict[str, Any],
    ) -> bool:
        """
        Update data in a table.

        Args:
            table: The table name
            id_column: The ID column name
            id_value: The ID value
            data: The data to update

        Returns:
            True if successful, False otherwise
        """
        await self._ensure_connected()

        try:
            # Don't update the ID
            if id_column in data:
                del data[id_column]

            # Build the SQL statement
            set_clause = ", ".join(
                [f"{key} = ${i + 1}" for i, key in enumerate(data.keys())]
            )
            values = list(data.values()) + [id_value]

            statement = (
                f"UPDATE {table} SET {set_clause} WHERE {id_column} = ${len(data) + 1}"
            )

            # Execute the statement
            self.connection.execute(statement, values)

            return True
        except Exception as e:
            logger.error(f"Failed to update data: {e}")
            return False

    async def delete(
        self, table: str, id_column: str, id_value: Union[str, int]
    ) -> bool:
        """
        Delete data from a table.

        Args:
            table: The table name
            id_column: The ID column name
            id_value: The ID value

        Returns:
            True if successful, False otherwise
        """
        await self._ensure_connected()

        try:
            # Build the SQL statement
            statement = f"DELETE FROM {table} WHERE {id_column} = $1"

            # Execute the statement
            self.connection.execute(statement, [id_value])

            return True
        except Exception as e:
            logger.error(f"Failed to delete data: {e}")
            return False
