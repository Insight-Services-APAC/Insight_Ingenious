"""
Configuration module for DDD-based configuration management.

This module provides access to the DDD configuration services.
"""

from ingenious.configuration.domain.models import MinimalConfig


def get_minimal_config():
    """Get a minimal configuration for DDD migration."""
    return MinimalConfig()
