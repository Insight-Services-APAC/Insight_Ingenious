"""
Configuration REST controllers for the configuration bounded context.

This module contains FastAPI route handlers for configuration management
including configuration retrieval, updates, and secret management.
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasicCredentials
from pydantic import BaseModel
from typing_extensions import Annotated

import ingenious.dependencies as igen_deps
from ingenious.shared.domain.models import HTTPError

from ..application.services import (
    ConfigurationApplicationService,
    ConfigurationRetrievalUseCase,
    ConfigurationUpdateUseCase,
)
from ..infrastructure.repositories import (
    FileSystemConfigurationRepository,
)

logger = logging.getLogger(__name__)


# Request/Response models
class ConfigurationResponse(BaseModel):
    config: Dict[str, Any]
    profile: str
    source: str  # "file" | "environment" | "key_vault"


class UpdateConfigurationRequest(BaseModel):
    config: Dict[str, Any]
    config_path: Optional[str] = None


class SecretRequest(BaseModel):
    secret_name: str
    secret_value: Optional[str] = None


class ConfigurationController:
    """REST controller for configuration operations."""

    def __init__(self, config_app_service: ConfigurationApplicationService):
        self._config_app_service = config_app_service
        self._router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """Setup the configuration routes."""
        self._router.get(
            "/configuration",
            responses={
                200: {
                    "model": ConfigurationResponse,
                    "description": "Current configuration",
                },
                500: {"model": HTTPError, "description": "Configuration load failed"},
            },
        )(self.get_configuration)

        self._router.post(
            "/configuration",
            responses={
                200: {"model": dict, "description": "Configuration updated"},
                400: {"model": HTTPError, "description": "Bad request"},
            },
        )(self.update_configuration)

        self._router.get(
            "/secrets/{secret_name}",
            responses={
                200: {"model": dict, "description": "Secret value"},
                404: {"model": HTTPError, "description": "Secret not found"},
            },
        )(self.get_secret)

        self._router.post(
            "/secrets",
            responses={
                200: {"model": dict, "description": "Secret stored"},
                400: {"model": HTTPError, "description": "Bad request"},
            },
        )(self.set_secret)

    @property
    def router(self) -> APIRouter:
        """Get the FastAPI router."""
        return self._router

    async def get_configuration(
        self,
        config_path: Optional[str] = None,
        credentials: Annotated[
            HTTPBasicCredentials, Depends(igen_deps.get_security_service)
        ] = None,
    ) -> ConfigurationResponse:
        """Get current configuration."""
        try:
            config = await self._config_app_service.get_configuration()

            return ConfigurationResponse(
                config=config,
                profile="default",  # TODO: Get actual profile from app service
                source="file",  # TODO: Track actual source
            )
        except FileNotFoundError as e:
            logger.warning(f"Configuration file not found: {e}")
            raise HTTPException(status_code=404, detail="Configuration file not found")
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=500, detail="Failed to load configuration")

    async def update_configuration(
        self,
        update_request: UpdateConfigurationRequest,
        credentials: Annotated[
            HTTPBasicCredentials, Depends(igen_deps.get_security_service)
        ],
    ) -> dict:
        """Update configuration."""
        try:
            # This is a simplified implementation
            # In practice, you'd want to validate the configuration structure
            # and handle the update properly

            # TODO: Implement proper configuration update logic
            # For now, return a placeholder response

            logger.info(
                f"Configuration update requested for path: {update_request.config_path}"
            )

            return {
                "success": True,
                "message": "Configuration update requested (not implemented yet)",
                "config_path": update_request.config_path,
            }

        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=500, detail="Failed to update configuration"
            )

    async def get_secret(
        self,
        secret_name: str,
        credentials: Annotated[
            HTTPBasicCredentials, Depends(igen_deps.get_security_service)
        ],
    ) -> dict:
        """Get a secret value."""
        try:
            await self._secret_service.get_secret(secret_name)

            # Never return the actual secret value in logs
            logger.info(f"Secret '{secret_name}' retrieved successfully")

            return {
                "secret_name": secret_name,
                "exists": True,
                "message": "Secret retrieved successfully",
                # Note: We don't return the actual value for security reasons
                # In practice, you might return it only to authorized consumers
            }

        except Exception as e:
            logger.exception(f"Failed to get secret '{secret_name}': {e}")
            raise HTTPException(
                status_code=404,
                detail=f"Secret '{secret_name}' not found or access denied",
            )

    async def set_secret(
        self,
        secret_request: SecretRequest,
        credentials: Annotated[
            HTTPBasicCredentials, Depends(igen_deps.get_security_service)
        ],
    ) -> dict:
        """Set a secret value."""
        try:
            if not secret_request.secret_value:
                raise HTTPException(status_code=400, detail="Secret value is required")

            await self._secret_service.set_secret(
                secret_request.secret_name, secret_request.secret_value
            )

            logger.info(f"Secret '{secret_request.secret_name}' stored successfully")

            return {
                "success": True,
                "message": f"Secret '{secret_request.secret_name}' stored successfully",
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(
                f"Failed to set secret '{secret_request.secret_name}': {e}"
            )
            raise HTTPException(
                status_code=500,
                detail=f"Failed to store secret '{secret_request.secret_name}'",
            )


# Create router instance for FastAPI integration
# Note: In production, this should be managed by a DI container
# For DDD migration, simplified configuration without Azure dependencies
config_repo = FileSystemConfigurationRepository()
# secret_service = AzureKeyVaultSecretService()  # Commented out for DDD migration

# Create use cases
config_retrieval_use_case = ConfigurationRetrievalUseCase(config_repo)
config_update_use_case = ConfigurationUpdateUseCase(config_repo)
# secret_mgmt_use_case = SecretManagementUseCase(secret_service)  # Commented out for DDD migration

# Create application service
config_app_service = ConfigurationApplicationService(
    config_retrieval_use_case,
    config_update_use_case,
    None,  # None for secret_mgmt_use_case
)

controller = ConfigurationController(config_app_service)
router = controller.router
