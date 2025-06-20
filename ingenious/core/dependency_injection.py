"""
Simple dependency injection container for the DDD migration.

This module provides a basic service container to manage dependencies
across bounded contexts without requiring complex DI frameworks.
"""

import os
from typing import Any, Callable, Dict, Optional


class ServiceContainer:
    """Simple service container for dependency injection."""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._config: Optional[Any] = None

    def register_service(self, name: str, service: Any):
        """Register a service instance."""
        self._services[name] = service

    def register_factory(self, name: str, factory: Callable[[], Any]):
        """Register a service factory function."""
        self._factories[name] = factory

    def get_service(self, name: str) -> Any:
        """Get a service by name."""
        if name in self._services:
            return self._services[name]

        if name in self._factories:
            service = self._factories[name]()
            self._services[name] = service  # Cache the instance
            return service

        raise ValueError(f"Service '{name}' not found")

    def get_config(self):
        """Get application configuration (cached)."""
        if self._config is None:
            try:
                from ingenious.config.config import get_config

                self._config = get_config(os.getenv("INGENIOUS_PROJECT_PATH", ""))
            except ValueError:
                # Return a minimal config for testing/development
                self._config = self._create_minimal_config()
        return self._config

    def _create_minimal_config(self):
        """Create a minimal configuration for testing."""
        import ingenious.models.config as config_models

        # Return a basic config object with minimal settings
        # This is a fallback for when no config file is available
        return config_models.Config()


# Global service container instance
container = ServiceContainer()


def get_container() -> ServiceContainer:
    """Get the global service container."""
    return container


def register_default_services():
    """Register default service implementations."""
    # This will be called during application startup
    # For now, we'll keep the manual instantiation in each controller
    # and migrate to this approach gradually
    pass
    pass
