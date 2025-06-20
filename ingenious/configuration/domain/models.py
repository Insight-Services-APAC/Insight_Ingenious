"""
Simple configuration models for the DDD migration.

These replace the legacy config models and provide a clean interface.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ConfigurationItem(BaseModel):
    """A single configuration item."""

    key: str
    value: Any
    description: Optional[str] = None
    is_secret: bool = False
    environment: Optional[str] = None


class AppConfiguration(BaseModel):
    """Main application configuration."""

    name: str
    version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    description: Optional[str] = None
    items: Dict[str, Any] = Field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.items.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self.items[key] = value


class AuthenticationConfig(BaseModel):
    """Authentication configuration."""

    enabled: bool = True
    provider: str = "local"
    secret_key: Optional[str] = None
    token_expiry: int = 3600
    issuer: Optional[str] = None
    audience: Optional[str] = None

    # Legacy fields for compatibility
    enable: bool = False
    username: str = ""
    password: str = ""


class LLMConfig(BaseModel):
    """LLM service configuration."""

    provider: str = "openai"
    model: str = "gpt-3.5-turbo"
    api_key: str = ""
    endpoint: str = ""
    api_version: str = "2023-05-15"
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout: Optional[int] = None
    retry_attempts: int = 3
    base_url: Optional[str] = None


class FileStorageConfig(BaseModel):
    """File storage configuration."""

    provider: str = "local"
    base_path: str = "./uploads"
    bucket_name: Optional[str] = None
    region: Optional[str] = None
    max_file_size: int = 10485760  # 10MB default
    allowed_extensions: List[str] = Field(
        default_factory=lambda: [".txt", ".pdf", ".jpg", ".png"]
    )
    access_key: Optional[str] = None
    secret_key: Optional[str] = None

    # Legacy fields for compatibility
    type: str = "local"
    path: str = "./data"


class MinimalConfig(BaseModel):
    """Minimal configuration for the DDD-based application."""

    project_name: str = "ingenious-project"
    environment: str = "development"
    log_level: str = "INFO"
    debug: bool = False
    authentication: AuthenticationConfig = Field(default_factory=AuthenticationConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    file_storage: FileStorageConfig = Field(default_factory=FileStorageConfig)
    app: AppConfiguration = Field(
        default_factory=lambda: AppConfiguration(name="ingenious-project")
    )
