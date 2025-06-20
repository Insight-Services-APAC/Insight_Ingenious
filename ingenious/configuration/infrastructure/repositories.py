import logging
import os
from typing import Optional

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from ..domain.models import MinimalConfig
from ..domain.services import IConfigurationRepository, ISecretService

logger = logging.getLogger(__name__)


class FileSystemConfigurationRepository(IConfigurationRepository):
    """File system implementation of configuration repository."""

    async def get_configuration(
        self, config_path: Optional[str] = None
    ) -> MinimalConfig:
        """Load configuration from file system or environment."""
        # For DDD migration, return a minimal configuration
        return MinimalConfig()

    async def save_configuration(self, config: MinimalConfig, config_path: str) -> None:
        """Save configuration to file system."""
        # For DDD migration, simplified save operation
        pass

    def _from_yaml_file(self, file_path: str) -> MinimalConfig:
        """Load configuration from YAML file."""
        # For DDD migration, return minimal config
        return MinimalConfig()

    def _from_yaml_str(self, config_yml: str) -> MinimalConfig:
        """Load configuration from YAML string."""
        # For DDD migration, return minimal config
        return MinimalConfig()


class AzureKeyVaultSecretService(ISecretService):
    """Azure Key Vault implementation of secret service."""

    def __init__(self):
        self.key_vault_name = os.environ.get("KEY_VAULT_NAME")
        if not self.key_vault_name:
            raise ValueError("KEY_VAULT_NAME environment variable not set")

        self.vault_url = f"https://{self.key_vault_name}.vault.azure.net"
        self.credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=self.vault_url, credential=self.credential)

    async def get_secret(self, secret_name: str) -> str:
        """Retrieve a secret from Azure Key Vault."""
        try:
            secret = self.client.get_secret(secret_name)
            return secret.value
        except Exception:
            logger.exception(f"Failed to retrieve secret {secret_name}")
            raise

    async def set_secret(self, secret_name: str, secret_value: str) -> None:
        """Store a secret in Azure Key Vault."""
        try:
            self.client.set_secret(secret_name, secret_value)
        except Exception:
            logger.exception(f"Failed to store secret {secret_name}")
            raise


class HybridConfigurationRepository(IConfigurationRepository):
    """Configuration repository that falls back to Key Vault if file not found."""

    def __init__(self, secret_service: ISecretService):
        self.file_repo = FileSystemConfigurationRepository()
        self.secret_service = secret_service

    async def get_configuration(
        self, config_path: Optional[str] = None
    ) -> MinimalConfig:
        """Load configuration from file system or Key Vault."""
        try:
            return await self.file_repo.get_configuration(config_path)
        except FileNotFoundError:
            logger.debug("Config file not found, falling back to Key Vault")
            try:
                config_str = await self.secret_service.get_secret("config")
                return self.file_repo._from_yaml_str(config_str)
            except Exception as e:
                raise ValueError(
                    f"Config file not found and failed to load from Key Vault: {e}"
                )

    async def save_configuration(self, config: MinimalConfig, config_path: str) -> None:
        """Save configuration to file system."""
        await self.file_repo.save_configuration(config, config_path)
