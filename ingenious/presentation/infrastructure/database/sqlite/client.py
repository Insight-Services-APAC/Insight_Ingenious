"""
SQLite database client implementation.
"""

import logging
import sqlite3
import uuid
from typing import Any, Dict, List, Optional, Union

import aiosqlite

from ingenious.presentation.infrastructure.database.base_client import (
    BaseDatabaseClient,
)

logger = logging.getLogger(__name__)


class SQLiteClient(BaseDatabaseClient):
    """SQLite database client implementation."""

    def __init__(self, database_path: str):
        """
        Initialize the SQLite client.

        Args:
            database_path: Path to the SQLite database file
        """
        self.database_path = database_path
        self.connection = None

    async def connect(self) -> None:
        """
        Connect to the database.
        """
        try:
            self.connection = await aiosqlite.connect(self.database_path)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connected to SQLite database at {self.database_path}")
        except Exception as e:
            logger.error(f"Failed to connect to SQLite database: {e}")
            raise

    async def disconnect(self) -> None:
        """
        Disconnect from the database.
        """
        if self.connection:
            await self.connection.close()
            self.connection = None
            logger.info(f"Disconnected from SQLite database at {self.database_path}")

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
            parameters = parameters or {}
            cursor = await self.connection.execute(query, parameters)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
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
            parameters = parameters or {}
            await self.connection.execute(statement, parameters)
            await self.connection.commit()
        except Exception as e:
            logger.error(f"Failed to execute statement: {e}")
            await self.connection.rollback()
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
            placeholders = ", ".join(f":{key}" for key in data.keys())
            statement = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

            # Execute the statement
            await self.connection.execute(statement, data)
            await self.connection.commit()

            return data["id"]
        except Exception as e:
            logger.error(f"Failed to insert data: {e}")
            await self.connection.rollback()
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
            set_clause = ", ".join(f"{key} = :{key}" for key in data.keys())
            statement = f"UPDATE {table} SET {set_clause} WHERE {id_column} = :id_value"

            # Add the ID value to the parameters
            params = {**data, "id_value": id_value}

            # Execute the statement
            await self.connection.execute(statement, params)
            await self.connection.commit()

            return True
        except Exception as e:
            logger.error(f"Failed to update data: {e}")
            await self.connection.rollback()
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
            statement = f"DELETE FROM {table} WHERE {id_column} = :id_value"

            # Execute the statement
            await self.connection.execute(statement, {"id_value": id_value})
            await self.connection.commit()

            return True
        except Exception as e:
            logger.error(f"Failed to delete data: {e}")
            await self.connection.rollback()
            return False
