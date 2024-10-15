import logging
import os
import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing_extensions import Annotated
from ingenious.db.chat_history_repository import ChatHistoryRepository
from ingenious.db.chat_history_repository import DatabaseClientType

from ingenious.external_services.openai_service import OpenAIService
from ingenious.external_services.search_service import AzureSearchService
from ingenious.services.chat_service import ChatService
from ingenious.services.message_feedback_service import MessageFeedbackService
from ingenious.services.tool_service import ToolService
import ingenious.config.config as Config

logger = logging.getLogger(__name__)
security = HTTPBasic()
config = Config.get_config(os.getenv("INGENIOUS_PROJECT_PATH"))


def get_chat_history_repository():
    db_type_val = config.chat_history.database_type.lower()
    try:
        db_type = DatabaseClientType(db_type_val)

    except ValueError:
        raise ValueError(f"Unknown database type: {db_type_val}")

    chr = ChatHistoryRepository(db_type=db_type, config=config)
    
    return chr


def get_ai_search_manager(index_name: str):
    return AzureSearchService(
        endpoint=os.getenv("AI_SEARCH_ENDPOINT", ""),
        key=os.getenv("AI_SEARCH_KEY", ""),
        index_name=index_name
    )


def get_guideline_search_manager():
    return get_ai_search_manager("vector-sample-guideline")


def get_data_search_manager():
    return get_ai_search_manager("vector-tabulated-data")


def get_openai_service():
    model = config.models[0]
    return OpenAIService(
        azure_endpoint=str(model.base_url),
        api_key=str(model.api_key),
        api_version=str(model.api_version),
        open_ai_model=str(model.api_version)
    )


def get_tool_service(
    guideline_search: Annotated[AzureSearchService, Depends(get_guideline_search_manager)],
    data_search: Annotated[AzureSearchService, Depends(get_data_search_manager)]
):
    if config.tool_service.enable:
        search_services = {
            "guideline": guideline_search,
            "data": data_search
        }
        return ToolService(search_services)
    else: 
        return ToolService({})


def get_security_service(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    if config.web_configuration.authentication.enable:
        current_username_bytes = credentials.username.encode("utf8")
        correct_username_bytes = config.web_configuration.authentication.username.encode('utf-8')
        is_correct_username = secrets.compare_digest(
            current_username_bytes, correct_username_bytes
        )
        current_password_bytes = credentials.password.encode("utf8")
        correct_password_bytes = config.web_configuration.authentication.password.encode('utf-8')
        is_correct_password = secrets.compare_digest(
            current_password_bytes, correct_password_bytes
        )
        if not (is_correct_username and is_correct_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
            )
        return credentials.username
    else:
        return ""
    

def get_chat_service(
    chat_history_repository: Annotated[ChatHistoryRepository, Depends(get_chat_history_repository)],
    #tool_service: Annotated[ToolService, Depends(get_tool_service)],
    conversation_flow: str = ""
):
    cs_type = config.chat_service.type
    return ChatService(
        chat_service_type=cs_type,
        chat_history_repository=chat_history_repository,
        openai_service=cs_type,
        #tool_service=tool_service,
        conversation_flow=conversation_flow
    )


def get_message_feedback_service(
    chat_history_repository: Annotated[ChatHistoryRepository, Depends(get_chat_history_repository)]
):
    return MessageFeedbackService(chat_history_repository)
