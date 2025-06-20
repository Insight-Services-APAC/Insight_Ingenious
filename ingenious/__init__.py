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

Legacy modules (to be migrated):
- api: REST API routes (will be moved to interfaces layers)
- services: Application services (will be moved to application layers)
- models: Data models (will be moved to domain layers)
- utils: Utility functions (will be moved to shared kernel)
"""

__version__ = "1.0.0"
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

# Export main bounded context modules for easy importing
from . import chat
from . import configuration
from . import diagnostics
from . import external_integrations
from . import file_management
from . import prompt_management
from . import security

__all__ = [
    "chat",
    "configuration",
    "diagnostics",
    "external_integrations",
    "file_management",
    "prompt_management",
    "security",
]
