"""
Configuration use cases.

This module contains individual use cases for configuration management operations.
"""

# For now, use cases are defined in services.py
# This module can be expanded later if more complex use cases are needed

from .services import (
    ConfigurationRetrievalUseCase,
    ConfigurationUpdateUseCase,
    SecretManagementUseCase,
)

__all__ = [
    "ConfigurationRetrievalUseCase",
    "ConfigurationUpdateUseCase",
    "SecretManagementUseCase",
]
