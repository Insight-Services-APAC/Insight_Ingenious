from enum import Enum
from typing import List

from pydantic import BaseModel, Field, RootModel


class ModelConfig(BaseModel):
    model: str
    api_key: str
    base_url: str


class ChatHistoryConfig(BaseModel):
    database_connection_string: str = ""


class AzureSqlConfig(BaseModel):
    database_connection_string: str = ""


class AzureSearchConfig(BaseModel):
    service: str
    key: str


class ChainlitAuthConfig(BaseModel):
    enable: bool = False
    github_secret: str = ""
    github_client_id: str = ""


class ChainlitConfig(BaseModel):
    authentication: ChainlitAuthConfig = Field(default_factory=ChainlitAuthConfig)


class ToolServiceConfig(BaseModel):
    pass


class ChatServiceConfig(BaseModel):
    pass


class WebAuthConfig(BaseModel):
    type: str = ""
    enable: bool = True
    username: str = ""
    password: str = ""


class WebConfig(BaseModel):
    port: int = 8000
    authentication: WebAuthConfig = Field(default_factory=WebAuthConfig)


class ReceiverConfig(BaseModel):
    enable: bool = True
    api_url: str = ""
    api_key: str = ""


class LoggingConfig(BaseModel):
    pass


class AuthenticationMethod(str, Enum):
    MSI = "msi"
    CLIENT_ID_AND_SECRET = "client_id_and_secret"
    DEFAULT_CREDENTIAL = "default_credential"
    TOKEN = "token"


class FileStorageContainer(BaseModel):
    url: str = Field("", description="File Storage SAS URL")
    client_id: str = Field("", description="File Storage SAS Client ID")
    token: str = Field("", description="File Storage SAS Token")
    authentication_method: AuthenticationMethod = Field(
        AuthenticationMethod.DEFAULT_CREDENTIAL,
        description="File Storage SAS Authentication Method",
    )


class FileStorage(BaseModel):
    revisions: FileStorageContainer = Field(
        default=FileStorageContainer(
            url="",
            client_id="",
            token="",
            authentication_method=AuthenticationMethod.DEFAULT_CREDENTIAL,
        ),
        description="File Storage configuration for revisions",
    )
    data: FileStorageContainer = Field(
        default=FileStorageContainer(
            url="",
            client_id="",
            token="",
            authentication_method=AuthenticationMethod.DEFAULT_CREDENTIAL,
        ),
        description="File Storage configuration for data",
    )


class Profile(BaseModel):
    """
    This is the class for the profiles.yml file. It contains only secret information.
    """

    name: str
    models: List[ModelConfig]
    chat_history: ChatHistoryConfig
    chat_service: ChatServiceConfig = Field(
        default_factory=ChatServiceConfig, description="Chat service configuration"
    )
    azure_search_services: List[AzureSearchConfig]
    azure_sql_services: AzureSqlConfig
    web_configuration: WebConfig
    receiver_configuration: ReceiverConfig
    chainlit_configuration: ChainlitConfig
    tool_service: ToolServiceConfig = Field(
        default_factory=ToolServiceConfig, description="Tool service configuration"
    )
    logging: LoggingConfig = Field(
        default_factory=LoggingConfig, description="Logging configuration"
    )
    file_storage: FileStorage = Field(
        default_factory=FileStorage, description="File Storage configuration"
    )

    # Add a profile property for test compatibility
    @property
    def profile(self):
        # Return the profile name if available, else None
        if hasattr(self, "name"):
            return self.name
        return getattr(self, "profile_name", None)


class Profiles(RootModel[List[Profile]]):
    pass
