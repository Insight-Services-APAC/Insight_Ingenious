# ingenious/__init__.py
"""
Ingenious Application - A Domain-Driven Design implementation

This application is organized into bounded contexts following DDD principles:

Bounded Contexts:
- chat: Chat and conversation management
- configuration: System configuration and settings
- diagnostics: System health and monitoring
- external_integrations: Third-party service integrations
- file_management: File operations and storage
- prompt_management: Prompt templates and management
- security: Authentication and authorization
- shared: Cross-cutting concerns and shared kernel

Core Components:
- core: Core infrastructure (dependency injection, logging)
- cli: Command-line interface
- main: FastAPI application entry point
- dependencies: Dependency injection configuration
"""

__version__ = "1.0.0"
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

# Note: Bounded context modules are available as:
# - ingenious.chat
# - ingenious.configuration
# - ingenious.diagnostics
# - ingenious.external_integrations
# - ingenious.file_management
# - ingenious.prompt_management
# - ingenious.security
# - ingenious.shared

__all__ = [
    "chat",
    "configuration",
    "diagnostics",
    "external_integrations",
    "file_management",
    "prompt_management",
    "security",
    "shared",
]
