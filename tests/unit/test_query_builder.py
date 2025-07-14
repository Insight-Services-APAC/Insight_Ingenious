import pytest

from ingenious.db.query_builder import (
    AzureSQLDialect,
    QueryBuilder,
    SQLiteDialect,
)


class TestSQLiteDialect:
    """Test SQLite dialect implementation."""
    
    def setup_method(self):
        self.dialect = SQLiteDialect()
    
    def test_create_table_if_not_exists_prefix(self):
        result = self.dialect.get_create_table_if_not_exists_prefix()
        assert result == "CREATE TABLE IF NOT EXISTS"
    
    def test_limit_clause(self):
        result = self.dialect.get_limit_clause(5)
        assert result == "LIMIT 5"
    
    def test_upsert_query(self):
        result = self.dialect.get_upsert_query("test_table", ["id", "name", "value"], "id")
        assert "INSERT INTO test_table" in result
        assert "ON CONFLICT" in result
        assert "DO UPDATE" in result
        assert "SET" in result
        assert '"id"' in result
        assert '"name"' in result
        assert '"value"' in result
    
    def test_temp_table_syntax(self):
        select_query = "SELECT * FROM source_table"
        result = self.dialect.get_temp_table_syntax("temp_table", select_query)
        assert "CREATE TEMP TABLE temp_table AS" in result
        assert select_query in result
    
    def test_drop_temp_table_syntax(self):
        result = self.dialect.get_drop_temp_table_syntax("temp_table")
        assert result == "DROP TABLE temp_table"
    
    def test_data_types(self):
        data_types = self.dialect.get_data_types()
        assert data_types["uuid"] == "UUID"
        assert data_types["varchar"] == "TEXT"
        assert data_types["boolean"] == "BOOLEAN"
        assert data_types["datetime"] == "TEXT"
        assert data_types["json"] == "JSONB"


class TestAzureSQLDialect:
    """Test Azure SQL dialect implementation."""
    
    def setup_method(self):
        self.dialect = AzureSQLDialect()
    
    def test_create_table_if_not_exists_prefix(self):
        result = self.dialect.get_create_table_if_not_exists_prefix()
        assert "IF NOT EXISTS" in result
        assert "sysobjects" in result
        assert "CREATE TABLE" in result
    
    def test_limit_clause(self):
        result = self.dialect.get_limit_clause(5)
        assert result == "TOP 5"
    
    def test_upsert_query(self):
        result = self.dialect.get_upsert_query("test_table", ["id", "name", "value"], "id")
        assert "MERGE test_table AS target" in result
        assert "WHEN MATCHED THEN" in result
        assert "WHEN NOT MATCHED THEN" in result
        assert "[id]" in result
        assert "[name]" in result
        assert "[value]" in result
    
    def test_temp_table_syntax(self):
        select_query = "SELECT * FROM source_table"
        result = self.dialect.get_temp_table_syntax("temp_table", select_query)
        assert select_query in result
        assert "INTO #temp_table" in result
    
    def test_drop_temp_table_syntax(self):
        result = self.dialect.get_drop_temp_table_syntax("temp_table")
        assert result == "DROP TABLE #temp_table"
    
    def test_data_types(self):
        data_types = self.dialect.get_data_types()
        assert data_types["uuid"] == "UNIQUEIDENTIFIER"
        assert data_types["varchar"] == "NVARCHAR(255)"
        assert data_types["boolean"] == "BIT"
        assert data_types["datetime"] == "DATETIME2"
        assert data_types["json"] == "NVARCHAR(MAX)"


class TestQueryBuilder:
    """Test QueryBuilder with different dialects."""
    
    def test_sqlite_query_builder_initialization(self):
        dialect = SQLiteDialect()
        builder = QueryBuilder(dialect)
        assert builder.dialect == dialect
        assert builder._data_types == dialect.get_data_types()
    
    def test_azuresql_query_builder_initialization(self):
        dialect = AzureSQLDialect()
        builder = QueryBuilder(dialect)
        assert builder.dialect == dialect
        assert builder._data_types == dialect.get_data_types()


class TestSQLiteQueryBuilder:
    """Test QueryBuilder with SQLite dialect."""
    
    def setup_method(self):
        self.builder = QueryBuilder(SQLiteDialect())
    
    def test_create_chat_history_table(self):
        query = self.builder.create_chat_history_table()
        assert "CREATE TABLE IF NOT EXISTS chat_history" in query
        assert "user_id TEXT" in query
        assert "thread_id TEXT" in query
        assert "message_id TEXT" in query
        assert "positive_feedback BOOLEAN" in query
        assert "timestamp TEXT" in query
        assert "role TEXT" in query
        assert "content TEXT" in query
    
    def test_create_users_table(self):
        query = self.builder.create_users_table()
        assert "CREATE TABLE IF NOT EXISTS users" in query
        assert "id UUID PRIMARY KEY" in query
        assert "identifier TEXT NOT NULL UNIQUE" in query
        assert "metadata JSONB NOT NULL" in query
        assert "createdAt TEXT" in query
    
    def test_create_threads_table(self):
        query = self.builder.create_threads_table()
        assert "CREATE TABLE IF NOT EXISTS threads" in query
        assert "id UUID PRIMARY KEY" in query
        assert "userId UUID" in query
        assert "tags TEXT[]" in query
        assert "metadata JSONB" in query
        assert "FOREIGN KEY" in query
    
    def test_create_steps_table(self):
        query = self.builder.create_steps_table()
        assert "CREATE TABLE IF NOT EXISTS steps" in query
        assert "id UUID PRIMARY KEY" in query
        assert "disableFeedback BOOLEAN NOT NULL" in query
        assert "streaming BOOLEAN NOT NULL" in query
        assert "generation JSONB" in query
        # Check that 'end' column is not bracketed in SQLite
        assert "end DATETIME2" in query or "end TEXT" in query
    
    def test_insert_message(self):
        query = self.builder.insert_message()
        assert "INSERT INTO chat_history" in query
        assert "user_id, thread_id, message_id" in query
        assert "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)" in query
    
    def test_select_message(self):
        query = self.builder.select_message()
        assert "SELECT user_id, thread_id, message_id" in query
        assert "FROM chat_history" in query
        assert "WHERE message_id = ? AND thread_id = ?" in query
    
    def test_select_latest_memory(self):
        query = self.builder.select_latest_memory()
        assert "FROM chat_history_summary" in query
        assert "WHERE thread_id = ?" in query
        assert "ORDER BY timestamp DESC" in query
        assert "LIMIT 1" in query
    
    def test_select_thread_messages(self):
        query = self.builder.select_thread_messages()
        assert "FROM chat_history" in query
        assert "WHERE thread_id = ?" in query
        assert "ORDER BY timestamp" in query
        assert "LIMIT 5" in query
    
    def test_update_message_feedback(self):
        query = self.builder.update_message_feedback()
        assert "UPDATE chat_history" in query
        assert "SET positive_feedback = ?" in query
        assert "WHERE message_id = ? AND thread_id = ?" in query
    
    def test_delete_thread(self):
        query = self.builder.delete_thread()
        assert "DELETE FROM chat_history" in query
        assert "WHERE thread_id = ?" in query
    
    def test_get_query_method(self):
        # Test the generic get_query method
        query = self.builder.get_query("insert_message")
        assert "INSERT INTO chat_history" in query
        
        # Test with parameters
        query = self.builder.get_query("select_thread_messages", limit=10)
        assert "LIMIT 10" in query
        
        # Test with non-existent query
        query = self.builder.get_query("non_existent_query")
        assert query == ""


class TestAzureSQLQueryBuilder:
    """Test QueryBuilder with Azure SQL dialect."""
    
    def setup_method(self):
        self.builder = QueryBuilder(AzureSQLDialect())
    
    def test_create_chat_history_table(self):
        query = self.builder.create_chat_history_table()
        assert "IF NOT EXISTS" in query
        assert "sysobjects" in query
        assert "chat_history" in query
        assert "user_id NVARCHAR(255)" in query
        assert "positive_feedback BIT" in query
        assert "timestamp DATETIME2" in query
        assert "content NVARCHAR(MAX)" in query
    
    def test_create_users_table(self):
        query = self.builder.create_users_table()
        assert "IF NOT EXISTS" in query
        assert "users" in query
        assert "id UNIQUEIDENTIFIER PRIMARY KEY" in query
        assert "identifier NVARCHAR(255) NOT NULL UNIQUE" in query
        assert "metadata NVARCHAR(MAX) NOT NULL" in query
    
    def test_create_threads_table(self):
        query = self.builder.create_threads_table()
        assert "IF NOT EXISTS" in query
        assert "threads" in query
        assert "userId UNIQUEIDENTIFIER" in query
        assert "tags NVARCHAR(MAX)" in query
        assert "FOREIGN KEY (userId) REFERENCES users(id)" in query
    
    def test_create_steps_table(self):
        query = self.builder.create_steps_table()
        assert "IF NOT EXISTS" in query
        assert "steps" in query
        assert "disableFeedback BIT NOT NULL" in query
        assert "streaming BIT NOT NULL" in query
        # Check that 'end' column is bracketed in SQL Server
        assert "[end] DATETIME2" in query
    
    def test_select_latest_memory(self):
        query = self.builder.select_latest_memory()
        assert "SELECT TOP 1" in query
        assert "FROM chat_history_summary" in query
        assert "WHERE thread_id = ?" in query
        assert "ORDER BY timestamp DESC" in query
    
    def test_select_thread_messages(self):
        query = self.builder.select_thread_messages()
        assert "SELECT TOP 5" in query
        assert "FROM (" in query
        assert "ROW_NUMBER() OVER" in query
        assert "ORDER BY timestamp ASC" in query


class TestQueryBuilderCompatibility:
    """Test that both dialects produce working queries for the same operations."""
    
    def setup_method(self):
        self.sqlite_builder = QueryBuilder(SQLiteDialect())
        self.azuresql_builder = QueryBuilder(AzureSQLDialect())
    
    def test_insert_queries_have_same_parameter_count(self):
        """Ensure both dialects use the same number of parameters for inserts."""
        sqlite_query = self.sqlite_builder.insert_message()
        azuresql_query = self.azuresql_builder.insert_message()
        
        # Count parameter placeholders
        sqlite_params = sqlite_query.count("?")
        azuresql_params = azuresql_query.count("?")
        
        assert sqlite_params == azuresql_params == 11
    
    def test_update_queries_have_same_parameter_count(self):
        """Ensure both dialects use the same number of parameters for updates."""
        sqlite_query = self.sqlite_builder.update_message_feedback()
        azuresql_query = self.azuresql_builder.update_message_feedback()
        
        sqlite_params = sqlite_query.count("?")
        azuresql_params = azuresql_query.count("?")
        
        assert sqlite_params == azuresql_params == 3
    
    def test_select_queries_have_same_parameter_count(self):
        """Ensure both dialects use the same number of parameters for selects."""
        sqlite_query = self.sqlite_builder.select_message()
        azuresql_query = self.azuresql_builder.select_message()
        
        sqlite_params = sqlite_query.count("?")
        azuresql_params = azuresql_query.count("?")
        
        assert sqlite_params == azuresql_params == 2
    
    def test_delete_queries_have_same_parameter_count(self):
        """Ensure both dialects use the same number of parameters for deletes."""
        sqlite_query = self.sqlite_builder.delete_thread()
        azuresql_query = self.azuresql_builder.delete_thread()
        
        sqlite_params = sqlite_query.count("?")
        azuresql_params = azuresql_query.count("?")
        
        assert sqlite_params == azuresql_params == 1
    
    def test_both_dialects_support_all_query_types(self):
        """Ensure both dialects support all query types."""
        query_methods = [
            "create_chat_history_table",
            "create_chat_history_summary_table", 
            "create_users_table",
            "create_threads_table",
            "create_steps_table",
            "create_elements_table",
            "create_feedbacks_table",
            "insert_message",
            "insert_memory",
            "select_message",
            "select_latest_memory",
            "update_message_feedback",
            "update_memory_feedback",
            "update_message_content_filter",
            "update_memory_content_filter",
            "insert_user",
            "select_user", 
            "select_thread_messages",
            "select_thread_memory",
            "delete_thread",
            "delete_thread_memory",
            "delete_user_memory",
        ]
        
        for method_name in query_methods:
            sqlite_query = getattr(self.sqlite_builder, method_name)()
            azuresql_query = getattr(self.azuresql_builder, method_name)()
            
            assert len(sqlite_query.strip()) > 0, f"SQLite {method_name} returned empty query"
            assert len(azuresql_query.strip()) > 0, f"Azure SQL {method_name} returned empty query"


class TestDataTypeMapping:
    """Test data type mapping between dialects."""
    
    def test_sqlite_data_types(self):
        dialect = SQLiteDialect()
        data_types = dialect.get_data_types()
        
        # Test key mappings
        assert data_types["uuid"] == "UUID"
        assert data_types["varchar"] == "TEXT"
        assert data_types["text"] == "TEXT"
        assert data_types["boolean"] == "BOOLEAN"
        assert data_types["datetime"] == "TEXT"
        assert data_types["int"] == "INT"
        assert data_types["json"] == "JSONB"
        assert data_types["array"] == "TEXT[]"
    
    def test_azuresql_data_types(self):
        dialect = AzureSQLDialect()
        data_types = dialect.get_data_types()
        
        # Test key mappings
        assert data_types["uuid"] == "UNIQUEIDENTIFIER"
        assert data_types["varchar"] == "NVARCHAR(255)"
        assert data_types["text"] == "NVARCHAR(MAX)"
        assert data_types["boolean"] == "BIT"
        assert data_types["datetime"] == "DATETIME2"
        assert data_types["int"] == "INT"
        assert data_types["json"] == "NVARCHAR(MAX)"
        assert data_types["array"] == "NVARCHAR(MAX)"
    
    def test_query_builder_uses_correct_data_types(self):
        """Test that QueryBuilder uses the correct data types from dialect."""
        sqlite_builder = QueryBuilder(SQLiteDialect())
        azuresql_builder = QueryBuilder(AzureSQLDialect())
        
        sqlite_query = sqlite_builder.create_users_table()
        azuresql_query = azuresql_builder.create_users_table()
        
        # SQLite should use UUID, Azure SQL should use UNIQUEIDENTIFIER
        assert "id UUID" in sqlite_query
        assert "id UNIQUEIDENTIFIER" in azuresql_query
        
        # SQLite should use TEXT, Azure SQL should use NVARCHAR
        assert "identifier TEXT" in sqlite_query
        assert "identifier NVARCHAR(255)" in azuresql_query