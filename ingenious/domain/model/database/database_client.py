import enum

# Define the DatabaseClientType enum


class DatabaseClientType(enum.Enum):
    SQLITE = "sqlite"
    COSMOS = "cosmos"


# Define an interface or base class for the database client
class DatabaseClient:
    def connect(self):
        raise NotImplementedError

    def execute_query(self, query, params=None):
        raise NotImplementedError

    def fetch_all(self, query, params=None):
        raise NotImplementedError

    def fetch_one(self, query, params=None):
        raise NotImplementedError
