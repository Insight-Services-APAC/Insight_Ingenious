from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ValidationError
from ingenious.models import profile as profile_models
from ingenious.models import config as config_models
from ingenious.models import config_ns as config_ns_models


class ChatHistoryConfig(config_ns_models.ChatHistoryConfig):
    database_connection_string: str = Field("",
                                            description="Connection string for the database. Only used for cosmosdb")

    def __init__(self, config: config_ns_models.ChatHistoryConfig, profile: profile_models.ChatHistoryConfig):
        super().__init__(
            database_type=config.database_type,
            database_path=config.database_path,
            database_connection_string=profile.database_connection_string,
            database_name=config.database_name,
            memory_path=config.memory_path)


class ModelConfig(config_ns_models.ModelConfig):
    api_key: str
    base_url: str

    def __init__(self, config: config_ns_models.ModelConfig, profile: profile_models.ModelConfig):
        super().__init__(model=config.model, api_type=config.api_type, api_version=config.api_version,
                         base_url=profile.base_url, api_key=profile.api_key)


class ChainlitConfig(config_ns_models.ChainlitConfig):
    authentication: profile_models.ChainlitAuthConfig = Field(default_factory=profile_models.ChainlitAuthConfig)

    def __init__(self, config: config_ns_models.ChainlitConfig, profile: profile_models.ChainlitConfig):
        super().__init__(enable=config.enable, authentication=profile.authentication)


class ChatServiceConfig(config_ns_models.ChatServiceConfig):
    def __init__(self, config: config_ns_models.ChatServiceConfig, profile: profile_models.ChatServiceConfig):
        super().__init__(type=config.type)


class ToolServiceConfig(config_ns_models.ToolServiceConfig):
    def __init__(self, config: config_ns_models.ToolServiceConfig, profile: profile_models.ToolServiceConfig):
        super().__init__(enable=config.enable)


class LoggingConfig(config_ns_models.LoggingConfig):
    def __init__(self, config: config_ns_models.LoggingConfig, profile: profile_models.LoggingConfig):
        super().__init__(root_log_level=config.root_log_level, log_level=config.log_level)


class AzureSearchConfig(config_ns_models.AzureSearchConfig):
    key: str = ""

    def __init__(self, config: config_ns_models.AzureSearchConfig, profile: profile_models.AzureSearchConfig):
        super().__init__(service=config.service, endpoint=config.endpoint, key=profile.key)


class AzureSqlConfig(config_ns_models.AzureSqlConfig):
    database_connection_string: str = Field("", description="azure SQL Connection string")

    def __init__(self, config: config_ns_models.AzureSqlConfig, profile: profile_models.AzureSqlConfig):
        super().__init__(
            table_name=config.table_name,
            database_name=config.database_name,
            database_connection_string=profile.database_connection_string,
        )


class WebConfig(config_ns_models.WebConfig):
    authentication: profile_models.WebAuthConfig = {}

    def __init__(self, config: config_ns_models.WebConfig, profile: profile_models.WebConfig):
        super().__init__(ip_address=config.ip_address,
                         port=config.port,
                         type=config.type,
                         asynchronous=config.asynchronous,
                         authentication=profile.authentication)


class LocaldbConfig(config_ns_models.LocaldbConfig):
    def __init__(self, config: config_ns_models.LocaldbConfig):
        super().__init__(database_path=config.database_path, sample_csv_path=config.sample_csv_path,
                         sample_database_name=config.sample_database_name)


class Config(BaseModel):
    chat_history: ChatHistoryConfig
    models: List[ModelConfig]
    logging: LoggingConfig
    tool_service: ToolServiceConfig
    chat_service: ChatServiceConfig
    chainlit_configuration: ChainlitConfig
    azure_search_services: List[AzureSearchConfig]
    web_configuration: WebConfig
    local_sql_db: LocaldbConfig
    azure_sql_services: AzureSqlConfig

    def __init__(self, config: config_ns_models.Config, profile: profile_models.Profile):
        super().__init__(
            chat_history=ChatHistoryConfig(config.chat_history, profile.chat_history),
            models=[],
            logging=LoggingConfig(config.logging, profile.logging),
            tool_service=ToolServiceConfig(config.tool_service, profile.tool_service),
            chat_service=ChatServiceConfig(config.chat_service, profile.chat_service),
            chainlit_configuration=ChainlitConfig(config.chainlit_configuration, profile.chainlit_configuration),
            azure_search_services=[],
            web_configuration=WebConfig(config.web_configuration, profile.web_configuration),
            local_sql_db=LocaldbConfig(config.local_sql_db),
            azure_sql_services=AzureSqlConfig(config.azure_sql_services, profile.azure_sql_services)
        )

        models: List[config_models.ModelConfig] = []
        for config_model in config.models:
            for profile_model in profile.models:
                if config_model.model == profile_model.model:
                    models.append(config_models.ModelConfig(config_model, profile_model))
        self.models = models

        self.azure_search_services = []
        for as_config in config.azure_search_services:
            for profile_as_config in profile.azure_search_services:
                if as_config.service == profile_as_config.service:
                    self.azure_search_services.append(config_models.AzureSearchConfig(as_config, profile_as_config))


