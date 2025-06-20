"""
Simple configuration models for the DDD migration.

These replace the legacy config models and provide a clean interface.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel


class ConfigurationItem(BaseModel):
    """A single configuration item."""

    key: str
    value: Any
    description: Optional[str] = None


class AppConfiguration(BaseModel):
    """Main application configuration."""

    items: Dict[str, Any] = {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.items.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self.items[key] = value


class AuthenticationConfig(BaseModel):
    """Authentication configuration."""

    enable: bool = False
    username: str = ""
    password: str = ""


class LLMConfig(BaseModel):
    """LLM service configuration."""

    provider: str = "openai"
    api_key: str = ""
    endpoint: str = ""
    model: str = "gpt-3.5-turbo"
    api_version: str = "2023-05-15"


class FileStorageConfig(BaseModel):
    """File storage configuration."""

    type: str = "local"
    path: str = "./data"


class MinimalConfig(BaseModel):
    """Minimal configuration for breaking backward compatibility."""

    authentication: AuthenticationConfig = AuthenticationConfig()
    llm: LLMConfig = LLMConfig()
    file_storage: FileStorageConfig = FileStorageConfig()
    app: AppConfiguration = AppConfiguration()
