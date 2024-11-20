from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ValidationError


class ChatHistoryConfig(BaseModel):
    database_type: str = Field("sqlite", description="Type of the database (e.g., sqlite, cosmosdb). Default is sqlite")
    database_path: str = Field("./tmp/high_level_logs.db", description="File path to the database, if applicable. Only used for sqlite")
    database_connection_string: str = Field("", description="Connection string for the database. Only used for cosmosdb")
    database_name: str = Field("", description="Name of the database. Only used for cosmosdb")
    memory_path: str = Field("./tmp", description="Path to the memory storage.")


class ModelConfig(BaseModel):
    model: str = Field(..., description="Name of the model")
    api_type: str = Field(..., description="Type of the API (e.g., rest, grpc)")
    api_version: str = Field(..., description="Version of the API")


class ChainlitConfig(BaseModel):
    enable: bool = Field(False, description="Enables or Disables the Python based Chainlit chat interface")


class ChatServiceConfig(BaseModel):
    type: str = Field("multi_agent", description="Right now only valid value is 'multi_agent'")


class ToolServiceConfig(BaseModel):
    enable: bool = Field(False, description="Enables or Disables the Tool Service")


class LoggingConfig(BaseModel):
    root_log_level: str = Field("debug", description="Root log level")
    log_level: str = Field("debug", description="Log level")


class AzureSearchConfig(BaseModel):
    service: str = Field(..., description="Name of the service")
    endpoint: str = Field(..., description="Endpoint of the service")


class AzureSqlConfig(BaseModel):
    database_name: str = Field("", description="Name of the database.")
    table_name: str = Field("", description="Name of the table.")
    database_connection_string: str = Field("", description="azure SQL Connection string")


class WebConfig(BaseModel):
    ip_address: str = Field("0.0.0.0", description="IP address of the web server")
    port: int = Field(80, description="Port of the web server")
    type: str = Field("fastapi", description="Type of the web server (e.g. fastapi)")
    asynchronous: bool = Field(False, description="Enables or Disables the Asynchronous Response")


class LocaldbConfig(BaseModel):
    database_path: str = Field("/tmp/sample_sql_db", description="Database path")
    sample_csv_path: str = Field("", description="Sample csv path")
    sample_database_name: str = Field("sample_sql_db", description="Sample database name")


class Config(BaseModel):
    chat_history: ChatHistoryConfig
    profile: str
    models: List[ModelConfig]
    logging: LoggingConfig
    tool_service: ToolServiceConfig
    chat_service: ChatServiceConfig
    chainlit_configuration: ChainlitConfig
    azure_search_services: List[AzureSearchConfig]
    web_configuration: WebConfig
    local_sql_db:LocaldbConfig
    azure_sql_services: AzureSqlConfig
