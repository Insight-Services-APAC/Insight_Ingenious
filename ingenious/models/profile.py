from pydantic import BaseModel, Field, ValidationError, RootModel
from typing import List, Dict, Optional
from enum import Enum


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


class FileStorage(BaseModel):
    url: str = Field("", description="File Storage SAS URL")    
    client_id: str = Field("", description="File Storage SAS Client ID")
    token: str = Field("", description="File Storage SAS Token")
    authentication_method: AuthenticationMethod = Field(AuthenticationMethod.CLIENT_ID_AND_SECRET, description="File Storage SAS Authentication Method")


class Profile(BaseModel):
    """
        This is the class for the profiles.yml file. It contains only secret information.
    """

    name: str
    models: List[ModelConfig]
    chat_history: ChatHistoryConfig
    chat_service: ChatServiceConfig = Field(default_factory=ChatServiceConfig, description="Chat service configuration")
    azure_search_services: List[AzureSearchConfig]
    azure_sql_services: AzureSqlConfig
    web_configuration: WebConfig
    receiver_configuration: ReceiverConfig
    chainlit_configuration: ChainlitConfig
    tool_service: ToolServiceConfig = Field(default_factory=ToolServiceConfig, description="Tool service configuration")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="Logging configuration")
    file_storage: FileStorage = Field(default_factory=FileStorage, description="File Storage configuration")


class Profiles(RootModel[List[Profile]]):
    pass
