import json
import logging
import os
from pathlib import Path
from typing import Optional

import yaml
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from ingenious.config.profile import Profiles
from ingenious.models import config as config_models
from ingenious.models import config_ns as config_ns_models

from ..domain.services import IConfigurationRepository, ISecretService

logger = logging.getLogger(__name__)


class FileSystemConfigurationRepository(IConfigurationRepository):
    """File system implementation of configuration repository."""

    async def get_configuration(
        self, config_path: Optional[str] = None
    ) -> config_models.Config:
        """Load configuration from file system or environment."""
        # Check if configuration is in environment variable
        if os.getenv("APPSETTING_INGENIOUS_CONFIG"):
            config_string = os.getenv("APPSETTING_INGENIOUS_CONFIG", "")
            config_object = json.loads(config_string)
            config_yml = yaml.dump(config_object)
            return self._from_yaml_str(config_yml)

        # Determine config path
        if config_path is None:
            env_config_path = os.getenv("INGENIOUS_PROJECT_PATH")
            if env_config_path:
                config_path = env_config_path
            else:
                current_path = Path.cwd()
                config_path = current_path / "config.yml"

        path = Path(config_path)

        if path.exists() and path.is_file():
            logger.debug("Config loaded from file")
            return self._from_yaml_file(config_path)
        else:
            logger.debug(f"No config file found at {config_path}")
            raise FileNotFoundError(f"Configuration file not found at {config_path}")

    async def save_configuration(
        self, config: config_models.Config, config_path: str
    ) -> None:
        """Save configuration to file system."""
        # Convert config to dictionary and then to YAML
        config_dict = config.model_dump()
        with open(config_path, "w") as file:
            yaml.dump(config_dict, file, default_flow_style=False)

    def _from_yaml_file(self, file_path: str) -> config_models.Config:
        """Load configuration from YAML file."""
        with open(file_path, "r") as file:
            file_str = file.read()
            return self._from_yaml_str(file_str)

    def _from_yaml_str(self, config_yml: str) -> config_models.Config:
        """Load configuration from YAML string."""
        yaml_data = yaml.safe_load(config_yml)
        json_data = json.dumps(yaml_data)

        try:
            config_ns = config_ns_models.Config.model_validate_json(json_data)
        except config_models.ValidationError as e:
            for error in e.errors():
                logger.debug(
                    f"Validation error in field '{error['loc']}': {error['msg']}"
                )
            raise e
        except Exception as e:
            logger.debug(f"Unexpected error during validation: {e}")
            raise e

        # Load profile data
        profile_data = Profiles(os.getenv("INGENIOUS_PROFILE_PATH", ""))
        profile_object = profile_data.get_profile_by_name(config_ns.profile)

        if profile_object is None:
            raise ValueError(f"Profile {config_ns.profile} not found in profiles.yml")

        return config_models.Config(config_ns, profile_object)


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
    ) -> config_models.Config:
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

    async def save_configuration(
        self, config: config_models.Config, config_path: str
    ) -> None:
        """Save configuration to file system."""
        await self.file_repo.save_configuration(config, config_path)
