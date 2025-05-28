"""
Tests for the dependency injection module in ingenious.common.di.
"""

from unittest.mock import MagicMock

import pytest

from ingenious.common.di.bindings import register_bindings
from ingenious.common.di.container import DIContainer, get_container
from ingenious.common.errors import ServiceError


class TestDIContainer:
    """Test suite for dependency injection container."""

    def setup_method(self):
        """Reset the container before each test."""
        # Create a new container instead of using the singleton to isolate tests
        self.container = DIContainer()

    def test_register_service(self):
        """Test registering a service in the container."""

        # Define a simple service interface and implementation
        class IService:
            def get_value(self):
                pass

        class ServiceImpl(IService):
            def get_value(self):
                return "test_value"

        # Register the service
        self.container.register(IService, ServiceImpl)

        # Verify the registration
        assert IService in self.container._registry

    def test_get_service(self):
        """Test retrieving a service from the container."""

        # Define a simple service interface and implementation
        class IService:
            def get_value(self):
                pass

        class ServiceImpl(IService):
            def get_value(self):
                return "test_value"

        # Register the service
        self.container.register(IService, ServiceImpl)

        # Get the service
        service = self.container.get(IService)

        # Verify the service
        assert isinstance(service, ServiceImpl)
        assert service.get_value() == "test_value"

    def test_get_service_with_dependencies(self):
        """Test retrieving a service with dependencies."""

        # Define services with dependencies
        class ILogger:
            def log(self, message):
                pass

        class Logger(ILogger):
            def log(self, message):
                return f"LOG: {message}"

        class IService:
            def process(self, data):
                pass

        class Service(IService):
            def __init__(self, logger: ILogger):
                self.logger = logger

            def process(self, data):
                self.logger.log(f"Processing {data}")
                return f"Processed: {data}"

        # Register the services
        self.container.register(ILogger, Logger)
        self.container.register(IService, Service)

        # Get the service with dependencies
        service = self.container.get(IService)

        # Verify the service and its dependencies
        assert isinstance(service, Service)
        assert isinstance(service.logger, Logger)
        assert service.process("data") == "Processed: data"

    def test_get_service_not_registered(self):
        """Test error when getting an unregistered service."""

        class IService:
            pass

        # Try to get an unregistered service
        with pytest.raises(ServiceError):
            self.container.get(IService)

    def test_register_singleton(self):
        """Test registering a service as a singleton."""

        # Define a simple service
        class ICounter:
            def increment(self):
                pass

        class Counter(ICounter):
            def __init__(self):
                self.count = 0

            def increment(self):
                self.count += 1
                return self.count

        # Register the service as a singleton
        self.container.register_singleton(ICounter, Counter)

        # Get the service multiple times
        counter1 = self.container.get(ICounter)
        counter2 = self.container.get(ICounter)

        # Verify they are the same instance
        assert counter1 is counter2
        assert counter1.increment() == 1
        assert counter2.increment() == 2  # Same instance, so count is now 2

    def test_register_instance(self):
        """Test registering a specific instance."""

        # Define a simple service
        class IService:
            def get_value(self):
                pass

        class ServiceImpl(IService):
            def __init__(self, value):
                self.value = value

            def get_value(self):
                return self.value

        # Create an instance
        instance = ServiceImpl("specific_instance")

        # Register the instance
        self.container.register_instance(IService, instance)

        # Get the service
        service = self.container.get(IService)

        # Verify it's the same instance
        assert service is instance
        assert service.get_value() == "specific_instance"

    def test_get_container_singleton(self):
        """Test that get_container returns a singleton instance."""
        container1 = get_container()
        container2 = get_container()

        assert container1 is container2


class TestBindings:
    """Test suite for service bindings."""

    def test_register_bindings(self, mock_env_vars):
        """Test registering all bindings."""
        from ingenious.common.config.config import get_config

        # Get the config and container
        config = get_config()
        container = get_container()

        # Register the bindings
        register_bindings(config)

        # Verify some key bindings
        from ingenious.domain.interfaces.repository.file_repository import (
            IFileRepository,
        )
        from ingenious.domain.model.config import Config

        # The config should be registered
        registered_config = container.get(Config)
        assert registered_config is config

        # File repository should be registered and injectable
        file_repository = container.get(IFileRepository)
        assert file_repository is not None


@pytest.fixture
def mock_config():
    """Mock configuration object."""
    mock_config = MagicMock()
    mock_config.chat_service = MagicMock()
    mock_config.chat_service.type = "basic"
    # Add web_configuration with port attribute for config tests
    mock_web_config = MagicMock()
    mock_web_config.port = 8000
    mock_web_config.authentication = MagicMock()
    mock_web_config.authentication.username = "test_user"
    mock_web_config.authentication.password = "test_password"
    mock_config.web_configuration = mock_web_config
    # Add file_storage with storage_type for DI tests
    mock_file_storage = MagicMock()
    mock_file_storage.storage_type = "local"
    mock_file_storage.revisions = MagicMock()
    mock_file_storage.revisions.storage_type = "local"
    mock_file_storage.data = MagicMock()
    mock_file_storage.data.storage_type = "local"
    mock_config.file_storage = mock_file_storage
    return mock_config
