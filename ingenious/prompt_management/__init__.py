"""
Prompt Management bounded context for the Ingenious application.

This module contains all prompt template management functionality
organized according to Domain-Driven Design principles:

- domain: Core business logic and entities for prompt templates
- infrastructure: External adapters for template storage and rendering
- interfaces: REST API controllers for prompt operations
"""

from .domain.entities import PromptLibrary, PromptTemplate, TemplateVersion
from .domain.services import (
    IPromptTemplateRepository,
    IPromptVersioningService,
    ITemplateRenderingService,
)
from .infrastructure.services import (
    FileSystemPromptRepository,
    GitPromptVersioningService,
    Jinja2RenderingService,
)
from .interfaces.rest_controllers import PromptManagementController, UpdatePromptRequest

__all__ = [
    # Domain
    "PromptTemplate",
    "PromptLibrary",
    "TemplateVersion",
    "IPromptTemplateRepository",
    "ITemplateRenderingService",
    "IPromptVersioningService",
    # Infrastructure
    "Jinja2RenderingService",
    "FileSystemPromptRepository",
    "GitPromptVersioningService",
    # Interfaces
    "PromptManagementController",
    "UpdatePromptRequest",
]
