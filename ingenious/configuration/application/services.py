"""
Configuration application services.

This module contains the application services that orchestrate business logic
for configuration management.
"""

from typing import Any, Dict, Optional

from ..domain.services import IConfigurationRepository, ISecretService


class ConfigurationRetrievalUseCase:
    """Use case for retrieving configuration values."""

    def __init__(self, config_repo: IConfigurationRepository):
        self._config_repo = config_repo

    async def get_configuration(self, key: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve configuration by key or all configuration."""
        if key:
            return {key: await self._config_repo.get_config_value(key)}
        return await self._config_repo.get_all_config()


class ConfigurationUpdateUseCase:
    """Use case for updating configuration values."""

    def __init__(self, config_repo: IConfigurationRepository):
        self._config_repo = config_repo

    async def update_configuration(self, key: str, value: Any) -> bool:
        """Update a configuration value."""
        return await self._config_repo.set_config_value(key, value)


class SecretManagementUseCase:
    """Use case for managing secrets."""

    def __init__(self, secret_service: ISecretService):
        self._secret_service = secret_service

    async def get_secret(self, key: str) -> Optional[str]:
        """Retrieve a secret value."""
        return await self._secret_service.get_secret(key)

    async def set_secret(self, key: str, value: str) -> bool:
        """Set a secret value."""
        return await self._secret_service.set_secret(key, value)


class ConfigurationApplicationService:
    """Main application service for configuration operations."""

    def __init__(
        self,
        config_retrieval_use_case: ConfigurationRetrievalUseCase,
        config_update_use_case: ConfigurationUpdateUseCase,
        secret_mgmt_use_case: SecretManagementUseCase,
    ):
        self._config_retrieval = config_retrieval_use_case
        self._config_update = config_update_use_case
        self._secret_mgmt = secret_mgmt_use_case

    async def get_configuration(self, key: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration values."""
        return await self._config_retrieval.get_configuration(key)

    async def update_configuration(self, key: str, value: Any) -> bool:
        """Update configuration value."""
        return await self._config_update.update_configuration(key, value)

    async def get_secret(self, key: str) -> Optional[str]:
        """Get secret value."""
        return await self._secret_mgmt.get_secret(key)

    async def set_secret(self, key: str, value: str) -> bool:
        """Set secret value."""
        return await self._secret_mgmt.set_secret(key, value)
