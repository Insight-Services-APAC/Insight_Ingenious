import logging
import os
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing_extensions import Annotated

import ingenious.config.config as Config
import ingenious.models.config as config_models
from ingenious.external_services.openai_service import OpenAIService
from ingenious.files.files_repository import FileStorage
from ingenious.services.chat_service import ChatService

logger = logging.getLogger(__name__)
security = HTTPBasic()
config: config_models.Config = Config.get_config(
    os.getenv("INGENIOUS_PROJECT_PATH", "")
)


def get_openai_service():
    model = config.models[0]
    return OpenAIService(
        azure_endpoint=str(model.base_url),
        api_key=str(model.api_key),
        api_version=str(model.api_version),
        open_ai_model=str(model.model),
    )


def get_file_storage():
    return FileStorage(config)


def get_security_service(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    if config.web_configuration.authentication.enable:
        current_username_bytes = credentials.username.encode("utf8")
        correct_username_bytes = (
            config.web_configuration.authentication.username.encode("utf-8")
        )
        is_correct_username = secrets.compare_digest(
            current_username_bytes, correct_username_bytes
        )
        current_password_bytes = credentials.password.encode("utf8")
        correct_password_bytes = (
            config.web_configuration.authentication.password.encode("utf-8")
        )
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
        # Raise warning if authentication is disabled
        logger.warning(
            "Authentication is disabled. This is not recommended for production use."
        )


def get_chat_service(conversation_flow: str = ""):
    cs_type = config.chat_service.type
    return ChatService(
        chat_service_type=cs_type,
        conversation_flow=conversation_flow,
        config=config,
    )


def sync_templates():
    if config.file_storage.storage_type == "local":
        return
    else:
        fs = FileStorage(config)
        working_dir = os.getcwd()
        template_path = os.path.join(working_dir, "ingenious", "templates")
        template_files = fs.list_files(file_path=template_path)
        for file in template_files:
            file_name = os.path.basename(file)
            file_contents = fs.read_file(file_name=file_name, file_path=template_path)
            file_path = os.path.join(working_dir, "ingenious", "templates", file_name)
            with open(file_path, "w") as f:
                f.write(file_contents)


def get_file_storage_data() -> FileStorage:
    return FileStorage(config, Category="data")


def get_file_storage_revisions() -> FileStorage:
    return FileStorage(config, Category="revisions")


def get_config():
    return config
