"""
Configuration bounded context for the Ingenious application.

This module contains all configuration-related functionality organized according to
Domain-Driven Design principles:

- domain: Configuration models and business logic
- application: Configuration use cases and application services
- infrastructure: Configuration repositories and adapters
- interfaces: Configuration API controllers
"""

from .application.services import ConfigurationApplicationService
from .application.use_cases import (
    ConfigurationRetrievalUseCase,
    ConfigurationUpdateUseCase,
)
from .domain.models import (
    AppConfiguration,
    AuthenticationConfig,
    FileStorageConfig,
    LLMConfig,
    MinimalConfig,
)
from .domain.services import IConfigurationRepository, IProfileService, ISecretService
from .infrastructure.repositories import (
    AzureKeyVaultSecretService,
    FileSystemConfigurationRepository,
    HybridConfigurationRepository,
)

__all__ = [
    # Domain
    "AppConfiguration",
    "AuthenticationConfig",
    "FileStorageConfig",
    "LLMConfig",
    "MinimalConfig",
    "IConfigurationRepository",
    "IProfileService",
    "ISecretService",
    # Application
    "ConfigurationApplicationService",
    "ConfigurationRetrievalUseCase",
    "ConfigurationUpdateUseCase",
    # Infrastructure
    "AzureKeyVaultSecretService",
    "FileSystemConfigurationRepository",
    "HybridConfigurationRepository",
]
