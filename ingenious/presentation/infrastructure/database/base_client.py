"""
Base database client implementation.
"""

from abc import abstractmethod
from typing import Any, Dict, List, Optional, Union

from ingenious.domain.interfaces.repository.database import DatabaseInterface


class BaseDatabaseClient(DatabaseInterface):
    """Base implementation of a database client."""

    @abstractmethod
    async def connect(self) -> None:
        """
        Connect to the database.
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from the database.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def execute(
        self, statement: str, parameters: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Execute a statement.

        Args:
            statement: The statement to execute
            parameters: Optional statement parameters
        """
        pass

    @abstractmethod
    async def insert(self, table: str, data: Dict[str, Any]) -> str:
        """
        Insert data into a table.

        Args:
            table: The table name
            data: The data to insert

        Returns:
            The ID of the inserted record
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass
