from typing import List, Optional

from pydantic import BaseModel, Field

# Import directly to avoid circular imports
from ingenious.domain.model.config import config_ns
from ingenious.domain.model.config import profile as profile_models


class ChatHistoryConfig(config_ns.ChatHistoryConfig):
    database_connection_string: str = Field(
        "", description="Connection string for the database. Only used for cosmosdb"
    )

    def __init__(
        self,
        config: config_ns.ChatHistoryConfig,
        profile: profile_models.ChatHistoryConfig,
    ):
        super().__init__(
            database_type=config.database_type,
            database_path=config.database_path,
            database_connection_string=profile.database_connection_string,
            database_name=config.database_name,
            memory_path=config.memory_path,
        )


class ModelConfig(config_ns.ModelConfig):
    api_key: str = ""
    base_url: str = ""

    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self, config: config_ns.ModelConfig, profile: profile_models.ModelConfig
    ):
        super().__init__(
            model=config.model,
            api_type=config.api_type,
            api_version=config.api_version,
        )
        self.base_url = profile.base_url
        self.api_key = profile.api_key


class ChainlitConfig(config_ns.ChainlitConfig):
    authentication: profile_models.ChainlitAuthConfig = Field(
        default_factory=profile_models.ChainlitAuthConfig
    )

    def __init__(
        self,
        config: config_ns.ChainlitConfig,
        profile: profile_models.ChainlitConfig,
    ):
        super().__init__(enable=config.enable)
        self.authentication = profile.authentication


class ChatServiceConfig(config_ns.ChatServiceConfig):
    def __init__(
        self,
        config: config_ns.ChatServiceConfig,
        profile: profile_models.ChatServiceConfig,
    ):
        super().__init__(type=config.type)


class ToolServiceConfig(config_ns.ToolServiceConfig):
    def __init__(
        self,
        config: config_ns.ToolServiceConfig,
        profile: profile_models.ToolServiceConfig,
    ):
        super().__init__(enable=config.enable)


class LoggingConfig(config_ns.LoggingConfig):
    def __init__(
        self,
        config: config_ns.LoggingConfig,
        profile: profile_models.LoggingConfig,
    ):
        super().__init__(
            root_log_level=config.root_log_level, log_level=config.log_level
        )


class AzureSearchConfig(config_ns.AzureSearchConfig):
    key: str = ""

    def __init__(
        self,
        config: config_ns.AzureSearchConfig,
        profile: profile_models.AzureSearchConfig,
    ):
        # Initialize the parent class with appropriate fields
        super().__init__(service=config.service, endpoint=config.endpoint)
        # Set key from profile
        self.key = profile.key


class AzureSqlConfig(config_ns.AzureSqlConfig):
    database_connection_string: str = Field(
        "", description="azure SQL Connection string"
    )

    def __init__(
        self,
        config: config_ns.AzureSqlConfig,
        profile: profile_models.AzureSqlConfig,
    ):
        super().__init__(
            table_name=config.table_name,
            database_name=config.database_name,
            database_connection_string=profile.database_connection_string,
        )


class ReceiverConfig(profile_models.ReceiverConfig):
    def __init__(self, profile: profile_models.ReceiverConfig):
        super().__init__(
            enable=profile.enable,
            api_url=profile.api_url,
            api_key=profile.api_key,
        )


class WebConfig(config_ns.WebConfig):
    authentication: profile_models.WebAuthConfig = Field(
        default_factory=profile_models.WebAuthConfig
    )

    def __init__(self, config: config_ns.WebConfig, profile: profile_models.WebConfig):
        super().__init__(
            ip_address=getattr(config, "ip_address", "0.0.0.0"),
            port=getattr(config, "port", 8000),
            type=getattr(config, "type", "fastapi"),
            asynchronous=getattr(config, "asynchronous", False),
        )
        # Explicitly set authentication from profile
        self.authentication = getattr(
            profile, "authentication", profile_models.WebAuthConfig()
        )
        # Ensure port is always set for compatibility with tests
        self.port = getattr(config, "port", 8000)


class LocaldbConfig(config_ns.LocaldbConfig):
    def __init__(self, config: config_ns.LocaldbConfig):
        super().__init__(
            database_path=config.database_path,
            sample_csv_path=config.sample_csv_path,
            sample_database_name=config.sample_database_name,
        )


# Use the same enum type from profile_models to ensure compatibility
AuthenticationMethod = profile_models.AuthenticationMethod


class FileStorageContainer(config_ns.FileStorageContainer):
    url: str = Field("", description="File Storage SAS URL")
    client_id: str = Field("", description="File Storage SAS Client ID")
    token: str = Field("", description="File Storage SAS Token")
    authentication_method: AuthenticationMethod = Field(
        AuthenticationMethod.DEFAULT_CREDENTIAL,
        description="File Storage SAS Authentication Method",
    )

    def __init__(
        self,
        config: config_ns.FileStorageContainer,
        profile: profile_models.FileStorageContainer,
    ):
        super().__init__(
            enable=config.enable,
            storage_type=config.storage_type,
            container_name=config.container_name,
            path=config.path,
            add_sub_folders=config.add_sub_folders,
        )
        self.url = profile.url
        self.token = profile.token
        self.client_id = profile.client_id
        self.authentication_method = profile.authentication_method


class FileStorage(config_ns.FileStorage):
    revisions: FileStorageContainer = Field(
        default_factory=lambda: FileStorageContainer(
            config=config_ns.FileStorageContainer(
                enable=True,
                storage_type="local",
                container_name="",
                path="./",
                add_sub_folders=True,
            ),
            profile=profile_models.FileStorageContainer(
                url="",
                client_id="",
                token="",
                authentication_method=AuthenticationMethod.DEFAULT_CREDENTIAL,
            ),
        ),
        description="File Storage configuration for revisions",
    )
    data: FileStorageContainer = Field(
        default_factory=lambda: FileStorageContainer(
            config=config_ns.FileStorageContainer(
                enable=True,
                storage_type="local",
                container_name="",
                path="./",
                add_sub_folders=True,
            ),
            profile=profile_models.FileStorageContainer(
                url="",
                client_id="",
                token="",
                authentication_method=AuthenticationMethod.DEFAULT_CREDENTIAL,
            ),
        ),
        description="File Storage configuration for data",
    )

    def __init__(
        self, config: config_ns.FileStorage, profile: profile_models.FileStorage
    ):
        super().__init__()  # Initialize the parent without arguments
        # Then set the properties explicitly
        self.revisions = FileStorageContainer(config.revisions, profile.revisions)
        self.data = FileStorageContainer(config.data, profile.data)


class Config(BaseModel):
    """
    This is the constructor class that brings together the configuration and profile classes.
    """

    chat_history: ChatHistoryConfig
    models: List[ModelConfig] = []
    logging: LoggingConfig
    tool_service: ToolServiceConfig
    chat_service: ChatServiceConfig
    chainlit_configuration: ChainlitConfig
    azure_search_services: List[AzureSearchConfig] = []
    web_configuration: WebConfig
    receiver_configuration: ReceiverConfig
    local_sql_db: LocaldbConfig
    azure_sql_services: AzureSqlConfig
    file_storage: FileStorage
    profile_name: Optional[str] = None  # Store the profile name

    def __init__(self, config: config_ns.Config, profile: profile_models.Profile):
        # Store the profile name for compatibility
        profile_name = getattr(profile, "name", None)

        # Initialize with empty lists for collections
        super().__init__(
            chat_history=ChatHistoryConfig(config.chat_history, profile.chat_history),
            models=[],  # Initialize as empty, will be filled below
            logging=LoggingConfig(config.logging, profile.logging),
            tool_service=ToolServiceConfig(config.tool_service, profile.tool_service),
            chat_service=ChatServiceConfig(config.chat_service, profile.chat_service),
            chainlit_configuration=ChainlitConfig(
                config.chainlit_configuration, profile.chainlit_configuration
            ),
            azure_search_services=[],  # Initialize as empty, will be filled below
            web_configuration=WebConfig(
                config.web_configuration, profile.web_configuration
            ),
            receiver_configuration=ReceiverConfig(profile.receiver_configuration),
            local_sql_db=LocaldbConfig(config.local_sql_db),
            azure_sql_services=AzureSqlConfig(
                config.azure_sql_services, profile.azure_sql_services
            ),
            file_storage=FileStorage(config.file_storage, profile.file_storage),
            profile_name=profile_name,
        )

        # Fill the models list with type-compatible objects
        for config_model in config.models:
            for profile_model in profile.models:
                if config_model.model == profile_model.model:
                    self.models.append(ModelConfig(config_model, profile_model))

        # Fill the azure search services list with type-compatible objects
        for as_config in config.azure_search_services:
            for profile_as_config in profile.azure_search_services:
                if as_config.service == profile_as_config.service:
                    self.azure_search_services.append(
                        AzureSearchConfig(as_config, profile_as_config)
                    )

    # Add a profile property for test compatibility
    @property
    def profile(self) -> Optional[str]:
        # Return the profile name if available, else None
        if hasattr(self, "profile_name") and self.profile_name is not None:
            return self.profile_name
        return None
