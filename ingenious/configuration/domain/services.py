from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ingenious.models import config as config_models


class IConfigurationRepository(ABC):
    """Repository interface for configuration persistence."""

    @abstractmethod
    async def get_configuration(
        self, config_path: Optional[str] = None
    ) -> config_models.Config:
        """Load configuration from storage."""
        pass

    @abstractmethod
    async def save_configuration(
        self, config: config_models.Config, config_path: str
    ) -> None:
        """Save configuration to storage."""
        pass


class ISecretService(ABC):
    """Service interface for managing secrets."""

    @abstractmethod
    async def get_secret(self, secret_name: str) -> str:
        """Retrieve a secret by name."""
        pass

    @abstractmethod
    async def set_secret(self, secret_name: str, secret_value: str) -> None:
        """Store a secret."""
        pass


class IProfileService(ABC):
    """Service interface for managing profiles."""

    @abstractmethod
    async def get_profile(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Get a profile by name."""
        pass

    @abstractmethod
    async def list_profiles(self) -> list[str]:
        """List all available profiles."""
        pass
