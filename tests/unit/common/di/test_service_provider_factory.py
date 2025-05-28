"""
Tests for service providers in ingenious.common.di.
"""

from unittest.mock import Mock

import pytest

from ingenious.common.di.service_provider_factory import ServiceProviderFactory
from ingenious.common.errors import ServiceError


class TestServiceProviderFactory:
    """Test suite for ServiceProviderFactory."""

    def setup_method(self):
        """Reset the factory before each test."""

        class IService:
            pass

        def resolver(param):
            mock_provider = Mock()
            mock_provider.name = "test_provider"
            return mock_provider

        mock_config = Mock()

        self.factory = ServiceProviderFactory(
            interface_type=IService,
            implementation_resolver=resolver,
            config=mock_config,
        )

    def test_register_provider(self):
        """Test registering a service provider."""
        # Define a mock provider
        mock_provider = Mock()
        mock_provider.name = "test_provider"

        # Register the provider
        self.factory.register_provider(mock_provider)

        # Verify it was registered
        assert "test_provider" in self.factory.providers
        assert self.factory.providers["test_provider"] == mock_provider

    def test_get_provider(self):
        """Test getting a registered provider."""
        # Define a mock provider
        mock_provider = Mock()
        mock_provider.name = "test_provider"

        # Register the provider
        self.factory.register_provider(mock_provider)

        # Get the provider
        provider = self.factory.get_provider("test_provider")

        # Verify it's the same provider
        assert provider == mock_provider

    def test_get_provider_not_found(self):
        """Test error when getting an unregistered provider."""
        with pytest.raises(ServiceError):
            self.factory.get_provider("nonexistent_provider")

    def test_create_provider(self):
        """Test creating a provider from a class."""

        # Define a mock provider class
        class MockProvider:
            def __init__(self, param1, param2=None):
                self.param1 = param1
                self.param2 = param2
                self.name = "created_provider"

            def get_name(self):
                return self.name

        # Create the provider
        provider = self.factory.create_provider(
            MockProvider, "test_param1", param2="test_param2"
        )

        # Verify the provider
        assert provider.name == "created_provider"
        assert provider.param1 == "test_param1"
        assert provider.param2 == "test_param2"

        # Verify it was registered
        assert "created_provider" in self.factory.providers
        assert self.factory.providers["created_provider"] == provider

    def test_get_or_create_provider(self):
        """Test getting or creating a provider."""

        # Define a mock provider class
        class MockProvider:
            def __init__(self, param1, param2=None):
                self.param1 = param1
                self.param2 = param2
                self.name = "test_provider"

            def get_name(self):
                return self.name

        # First call should create the provider
        provider1 = self.factory.get_or_create_provider(
            "test_provider", MockProvider, "test_param1", param2="test_param2"
        )

        # Verify the provider
        assert provider1.name == "test_provider"
        assert provider1.param1 == "test_param1"
        assert provider1.param2 == "test_param2"

        # Second call should return the existing provider
        provider2 = self.factory.get_or_create_provider(
            "test_provider",
            MockProvider,
            "different_param1",  # This should be ignored
            param2="different_param2",  # This should be ignored
        )

        # Verify it's the same provider
        assert provider2 is provider1
        assert provider2.param1 == "test_param1"  # Not updated
        assert provider2.param2 == "test_param2"  # Not updated
