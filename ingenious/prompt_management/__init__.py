"""
Prompt Management bounded context for the Ingenious application.

This module contains all prompt template management functionality
organized according to Domain-Driven Design principles:

- domain: Core business logic and entities for prompt templates
- infrastructure: External adapters for template storage and rendering
- interfaces: REST API controllers for prompt operations
"""

from .domain.entities import PromptLibrary, PromptTemplate, PromptVersion
from .domain.services import (
    IPromptRenderingService,
    IPromptTemplateRepository,
    IPromptVersioningService,
)
from .infrastructure.services import (
    FileSystemPromptRepository,
    InMemoryVersioningService,
    Jinja2RenderingService,
)
from .interfaces.rest_controllers import PromptManagementController, UpdatePromptRequest

__all__ = [
    # Domain entities
    "PromptTemplate",
    "PromptLibrary",
    "PromptVersion",
    # Domain services
    "IPromptTemplateRepository",
    "IPromptRenderingService",
    "IPromptVersioningService",
    # Infrastructure services
    "FileSystemPromptRepository",
    "InMemoryVersioningService",
    "Jinja2RenderingService",
    # Interfaces
    "PromptManagementController",
    "UpdatePromptRequest",
]
