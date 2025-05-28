"""
Service Provider Factory module.

This module provides a factory for creating service providers with proper dependency injection.
It follows the Factory and Service Locator patterns.
"""

from typing import Dict, Generic, Type, TypeVar

from ingenious.common.errors.common import ServiceError
from ingenious.domain.model.config import Config

T = TypeVar("T")
S = TypeVar("S")


class ServiceProviderFactory(Generic[T, S]):
    """
    Factory for creating service providers with appropriate configuration.

    This class follows the Factory pattern and uses dependency injection for better testability.
    It is generic over the interface type and the parameter type.
    """

    def __init__(
        self, interface_type: Type[T], implementation_resolver: callable, config: Config
    ):
        """
        Initialize the ServiceProviderFactory.

        Args:
            interface_type: The interface type this factory provides
            implementation_resolver: Function to resolve implementation instances
            config: The application configuration
        """
        self.interface_type = interface_type
        self.implementation_resolver = implementation_resolver
        self.config = config
        self._instances: Dict[str, T] = {}

    def register_provider(self, provider: T) -> None:
        """
        Register a service provider.

        Args:
            provider: The provider instance to register
        """
        self._instances[provider.name] = provider

    def get_provider(self, name: str) -> T:
        """
        Get a registered provider.

        Args:
            name: The name of the provider

        Returns:
            The provider instance

        Raises:
            ServiceError: If no provider is found with the given name
        """
        if name not in self._instances:
            raise ServiceError(f"No provider found with name '{name}'")
        return self._instances[name]

    def create_provider(self, provider_class: Type[T], *args, **kwargs) -> T:
        """
        Create a provider from a class.

        Args:
            provider_class: The class to create the provider from
            *args: Positional arguments for provider instantiation
            **kwargs: Keyword arguments for provider instantiation

        Returns:
            The created provider instance
        """
        provider = provider_class(*args, **kwargs)
        self.register_provider(provider)
        return provider

    def get_or_create_provider(
        self, name: str, provider_class: Type[T], *args, **kwargs
    ) -> T:
        """
        Get a registered provider or create it if it doesn't exist.

        Args:
            name: The name of the provider
            provider_class: The class to create the provider from if needed
            *args: Positional arguments for provider instantiation
            **kwargs: Keyword arguments for provider instantiation

        Returns:
            The provider instance
        """
        try:
            return self.get_provider(name)
        except ServiceError:
            provider = self.create_provider(provider_class, *args, **kwargs)
            self.register_provider(provider)
            return provider

    @property
    def providers(self):
        """
        Get the registered providers.

        Returns:
            A dictionary of registered providers indexed by name
        """
        return self._instances
