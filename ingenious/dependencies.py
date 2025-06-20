"""
Modern dependency injection using DDD-compliant services.

This module provides dependency injection for the new Domain-Driven Design
architecture. All legacy imports have been removed for clean separation.
"""

import logging
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing_extensions import Annotated

from ingenious.chat.application.services import ChatApplicationService
from ingenious.configuration.application.services import ConfigurationRetrievalUseCase
from ingenious.core.dependency_injection import get_container
from ingenious.external_integrations.application.services import LLMCompletionUseCase
from ingenious.file_management.application.services import (
    FileManagementApplicationService,
)

logger = logging.getLogger(__name__)
security = HTTPBasic()


def get_service_container():
    """Get the global service container."""
    return get_container()


def get_configuration_service():
    """Get configuration service using DDD pattern."""
    container = get_container()
    try:
        return container.get_service("configuration_service")
    except ValueError:
        # Create a minimal configuration service for now
        # TODO: Fix configuration infrastructure after legacy model cleanup
        config_use_case = ConfigurationRetrievalUseCase(None)
        container.register_service("configuration_service", config_use_case)
        return config_use_case


def get_llm_service():
    """Get LLM service using DDD pattern."""
    container = get_container()
    try:
        return container.get_service("llm_service")
    except ValueError:
        # Create and register if not exists
        from ingenious.external_integrations.infrastructure.openai_service import (
            AzureOpenAIService,
        )

        # Get configuration for LLM setup - using minimal config for now
        # TODO: Replace with proper configuration service integration
        llm_impl = AzureOpenAIService(
            azure_endpoint="https://example.openai.azure.com/",
            api_key="dummy-key",
            api_version="2023-05-15",
            model="gpt-3.5-turbo",
        )
        llm_use_case = LLMCompletionUseCase(llm_impl)

        container.register_service("llm_service", llm_use_case)
        return llm_use_case


def get_file_management_service():
    """Get file management service using DDD pattern."""
    container = get_container()
    try:
        return container.get_service("file_management_service")
    except ValueError:
        # Create and register if not exists
        from ingenious.file_management.application.use_cases import (
            DirectoryManagementUseCase,
            FileManagementUseCase,
        )
        from ingenious.file_management.infrastructure.services import (
            FileSystemFileRepository,
        )

        file_repo = FileSystemFileRepository()
        file_use_case = FileManagementUseCase(file_repo)
        dir_use_case = DirectoryManagementUseCase(file_repo)
        file_service = FileManagementApplicationService(file_use_case, dir_use_case)

        container.register_service("file_management_service", file_service)
        return file_service


def get_chat_service():
    """Get chat service using DDD pattern."""
    container = get_container()
    try:
        return container.get_service("chat_service")
    except ValueError:
        # Create and register if not exists
        from ingenious.chat.infrastructure.services import ModernChatService

        # Get LLM service for chat processing
        llm_service = get_llm_service()
        chat_impl = ModernChatService(llm_service)
        chat_service = ChatApplicationService(chat_impl)

        container.register_service("chat_service", chat_service)
        return chat_service


def get_security_service(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    """Modern security dependency using configuration service."""
    try:
        config_service = get_configuration_service()

        # Try to get authentication config
        auth_config = config_service.get_configuration("authentication")

        if auth_config and auth_config.get("authentication", {}).get("enable", False):
            auth_data = auth_config["authentication"]
            current_username_bytes = credentials.username.encode("utf8")
            correct_username_bytes = auth_data.get("username", "").encode("utf-8")

            is_correct_username = secrets.compare_digest(
                current_username_bytes, correct_username_bytes
            )

            current_password_bytes = credentials.password.encode("utf8")
            correct_password_bytes = auth_data.get("password", "").encode("utf-8")

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
            # Authentication is disabled
            logger.warning(
                "Authentication is disabled. This is not recommended for production use."
            )
            return "anonymous"
    except Exception as e:
        logger.warning(f"Authentication configuration error: {e}")
        logger.warning("Falling back to disabled authentication mode.")
        return "anonymous"


def get_config():
    """Get configuration using new DDD pattern."""
    config_service = get_configuration_service()
    return config_service
