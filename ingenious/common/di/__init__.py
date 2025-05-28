"""
Dependency Injection package for Ingenious.

This package provides tools for dependency injection, including
a container, bindings, and a service provider factory.
"""

from ingenious.common.di.bindings import register_bindings
from ingenious.common.di.container import DIContainer, get_container
from ingenious.common.di.service_provider_factory import ServiceProviderFactory

__all__ = [
    "DIContainer",
    "get_container",
    "register_bindings",
    "ServiceProviderFactory",
]
