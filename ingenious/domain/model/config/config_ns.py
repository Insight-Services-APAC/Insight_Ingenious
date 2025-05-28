from typing import List

from pydantic import BaseModel, Field

from .profile import WebAuthConfig  # Import WebAuthConfig from profile


class ChatHistoryConfig(BaseModel):
    database_type: str = Field(
        "sqlite",
        description="Type of the database (e.g., sqlite, cosmosdb). Default is sqlite",
    )
    database_path: str = Field(
        "./tmp/high_level_logs.db",
        description="File path to the database, if applicable. Only used for sqlite",
    )
    database_connection_string: str = Field(
        "", description="Connection string for the database. Only used for cosmosdb"
    )
    database_name: str = Field(
        "", description="Name of the database. Only used for cosmosdb"
    )
    memory_path: str = Field("./tmp", description="Path to the memory storage.")


class ModelConfig(BaseModel):
    model: str = Field(..., description="Name of the model")
    api_type: str = Field(..., description="Type of the API (e.g., rest, grpc)")
    api_version: str = Field(..., description="Version of the API")


class ChainlitConfig(BaseModel):
    enable: bool = Field(
        False,
        description="Enables or Disables the Python based Chainlit chat interface",
    )


class ChatServiceConfig(BaseModel):
    type: str = Field(
        "multi_agent", description="Right now only valid value is 'multi_agent'"
    )


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
    database_connection_string: str = Field(
        "", description="azure SQL Connection string"
    )


class WebConfig(BaseModel):
    ip_address: str = Field("0.0.0.0", description="IP address of the web server")
    port: int = Field(80, description="Port of the web server")
    type: str = Field("fastapi", description="Type of the web server (e.g. fastapi)")
    asynchronous: bool = Field(
        False, description="Enables or Disables the Asynchronous Response"
    )
    authentication: WebAuthConfig = Field(
        default_factory=WebAuthConfig,
        description="Authentication config for the web server",
    )


class LocaldbConfig(BaseModel):
    database_path: str = Field("/tmp/sample_sql_db", description="Database path")
    sample_csv_path: str = Field("", description="Sample csv path")
    sample_database_name: str = Field(
        "sample_sql_db", description="Sample database name"
    )


class FileStorageContainer(BaseModel):
    enable: bool = Field(True, description="Enables or Disables File Storage")
    storage_type: str = Field("local", description="Type of the File Storage")
    container_name: str = Field(
        default="",
        description="Name of the container. Used for Azure storage. Not used for local storage.",
    )
    path: str = Field(
        "./",
        description="Path to the file storage. Used for local storage and Azure storage.",
    )
    add_sub_folders: bool = Field(
        default=True,
        description="Add sub_folders to the path. Used for local storage and Azure storage.",
    )


class FileStorage(BaseModel):
    revisions: FileStorageContainer = Field(
        default_factory=lambda: FileStorageContainer(
            enable=True,
            storage_type="local",
            container_name="",
            path="./",
            add_sub_folders=True,
        ),
        description="File Storage configuration for revisions",
    )
    data: FileStorageContainer = Field(
        default_factory=lambda: FileStorageContainer(
            enable=True,
            storage_type="local",
            container_name="",
            path="./",
            add_sub_folders=True,
        ),
        description="File Storage configuration for data",
    )


class Config(BaseModel):
    """
    This is the configuration class for the config.yml file. It contains only non-secret information.
    """

    chat_history: ChatHistoryConfig
    profile: str
    models: List[ModelConfig]
    logging: LoggingConfig
    tool_service: ToolServiceConfig
    chat_service: ChatServiceConfig
    chainlit_configuration: ChainlitConfig
    azure_search_services: List[AzureSearchConfig]
    web_configuration: WebConfig
    local_sql_db: LocaldbConfig
    azure_sql_services: AzureSqlConfig
    file_storage: FileStorage = Field(
        default_factory=lambda: FileStorage(
            revisions=FileStorageContainer(
                enable=True,
                storage_type="local",
                container_name="",
                path="./",
                add_sub_folders=True,
            ),
            data=FileStorageContainer(
                enable=True,
                storage_type="local",
                container_name="",
                path="./",
                add_sub_folders=True,
            ),
        ),
        description="File Storage configuration",
    )
