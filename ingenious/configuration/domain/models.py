"""
Simple configuration models for the DDD migration.

These replace the legacy config models and provide a clean interface.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ConfigurationItem(BaseModel):
    """A single configuration item."""

    key: str = Field(..., min_length=1, description="Configuration key cannot be empty")
    value: Any
    description: Optional[str] = None
    is_secret: bool = False
    environment: Optional[str] = None


class AppConfiguration(BaseModel):
    """Main application configuration."""

    name: str = Field(
        "Insight Ingenious",
        min_length=1,
        description="Application name cannot be empty",
    )
    version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    description: Optional[str] = None
    items: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v

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
    token_expiry: int = Field(3600, gt=0, description="Token expiry must be positive")
    issuer: Optional[str] = None
    audience: Optional[str] = None

    # Legacy fields for compatibility
    enable: bool = False
    username: str = ""
    password: str = ""

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v):
        valid_providers = ["local", "oauth2", "saml", "ldap"]
        if v not in valid_providers:
            raise ValueError(f"provider must be one of {valid_providers}")
        return v


class LLMConfig(BaseModel):
    """LLM service configuration."""

    provider: str = "openai"
    model: str = "gpt-3.5-turbo"
    api_key: Optional[str] = None
    endpoint: str = ""
    api_version: str = "2023-05-15"
    temperature: float = Field(
        0.7, ge=0.0, le=2.0, description="Temperature must be between 0.0 and 2.0"
    )
    max_tokens: int = Field(1000, gt=0, description="max_tokens must be positive")
    timeout: Optional[int] = None
    retry_attempts: int = 3
    base_url: Optional[str] = None

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v):
        valid_providers = ["openai", "azure", "anthropic", "local"]
        if v not in valid_providers:
            raise ValueError(f"provider must be one of {valid_providers}")
        return v


class FileStorageConfig(BaseModel):
    """File storage configuration."""

    provider: str = "local"
    base_path: str = "./uploads"
    bucket_name: Optional[str] = None
    region: Optional[str] = None
    max_file_size: int = Field(
        10485760, gt=0, description="max_file_size must be positive"
    )  # 10MB default
    allowed_extensions: List[str] = Field(
        default_factory=lambda: [".txt", ".pdf", ".doc", ".docx"]
    )
    access_key: Optional[str] = None
    secret_key: Optional[str] = None

    # Legacy fields for compatibility
    type: str = "local"
    path: str = "./data"


class MinimalConfig(BaseModel):
    """Minimal configuration for the DDD-based application."""

    project_name: str = Field(
        "ingenious-project", min_length=1, description="project_name cannot be empty"
    )
    environment: str = "development"
    log_level: str = "INFO"
    debug: bool = False
    authentication: AuthenticationConfig = Field(default_factory=AuthenticationConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    file_storage: FileStorageConfig = Field(default_factory=FileStorageConfig)
    app: AppConfiguration = Field(
        default_factory=lambda: AppConfiguration(name="ingenious-project")
    )
