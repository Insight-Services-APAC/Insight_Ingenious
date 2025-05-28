"""
Dependency Injection Container for Ingenious.

This module provides a container for dependency injection, following the
Service Locator pattern while enabling proper dependency management.
"""

from typing import Any, Dict, Type, TypeVar, cast

from ingenious.common.errors.common import ServiceError

T = TypeVar("T")


class DIContainer:
    """
    Dependency Injection Container.

    This container manages dependencies and their instantiation, allowing for
    better inversion of control and testability.
    """

    def __init__(self):
        self._registry: Dict[Type, Type] = {}
        self._singletons: Dict[Type, Any] = {}
        self._instances: Dict[Type, Any] = {}
        self._factories: Dict[Type, Any] = {}

    def register(self, interface: Type[T], implementation: Type[T]) -> None:
        """
        Register a service implementation.

        Args:
            interface: The interface type to register
            implementation: The implementation type to register
        """
        self._registry[interface] = implementation

    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """
        Register a singleton service implementation.

        Args:
            interface: The interface type to register
            implementation: The implementation type to register
        """
        instance = implementation()
        self._singletons[interface] = instance

    def register_instance(self, interface: Type[T], instance: T) -> None:
        """
        Register an existing instance.

        Args:
            interface: The interface type to register
            instance: The instance to register
        """
        self._instances[interface] = instance

    def bind_instance(self, interface: Type[T], instance: T) -> None:
        """
        Bind an instance to an interface.

        Args:
            interface: The interface type to bind to
            instance: The instance to bind
        """
        self.register_instance(interface, instance)

    def bind_factory(self, interface: Type[T], factory: Any) -> None:
        """
        Bind a factory function to an interface.

        Args:
            interface: The interface type to bind the factory to
            factory: The factory function to bind
        """
        self._factories[interface] = factory

    def get(self, interface: Type[T]) -> T:
        """
        Get a service from the container.

        Args:
            interface: The interface type to get

        Returns:
            An instance of the requested service

        Raises:
            ServiceError: If the service is not registered
        """
        if interface in self._instances:
            return cast(T, self._instances[interface])

        if interface in self._singletons:
            return cast(T, self._singletons[interface])

        if interface in self._registry:
            implementation = self._registry[interface]
            # Get the constructor parameters
            import inspect

            constructor_params = inspect.signature(implementation.__init__).parameters
            if len(constructor_params) > 1:  # More than just 'self'
                # We need to inject dependencies
                kwargs = {}
                for param_name, param in list(constructor_params.items())[
                    1:
                ]:  # Skip 'self'
                    if param.annotation != inspect.Parameter.empty:
                        try:
                            # Try to get the dependency from the container
                            kwargs[param_name] = self.get(param.annotation)
                        except ServiceError:
                            # If the dependency is not in the container, we'll get an error later
                            pass
                return implementation(**kwargs)
            return implementation()

        if hasattr(self, "_factories") and interface in self._factories:
            instance = self._factories[interface]()
            self._instances[interface] = instance
            return cast(T, instance)

        raise ServiceError(f"Service {interface.__name__} is not registered")

    def resolve(self, interface: Type[T]) -> T:
        """
        Resolve a service, using the factory if available.

        Args:
            interface: The interface type to resolve

        Returns:
            An instance of the requested service
        """
        if interface in self._factories:
            factory = self._factories[interface]
            return factory()

        return self.get(interface)


# Singleton instance
_container = DIContainer()


def get_container() -> DIContainer:
    """
    Get the global DIContainer instance.

    Returns:
        The global DIContainer instance
    """
    return _container
