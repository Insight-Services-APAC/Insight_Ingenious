from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .entities import PromptTemplate


class IPromptTemplateRepository(ABC):
    """Repository interface for prompt template persistence."""

    @abstractmethod
    async def save_template(self, template: PromptTemplate) -> None:
        """Save a prompt template."""
        pass

    @abstractmethod
    async def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Get a template by ID."""
        pass

    @abstractmethod
    async def get_template_by_name(self, name: str) -> Optional[PromptTemplate]:
        """Get a template by name."""
        pass

    @abstractmethod
    async def list_templates(self) -> List[PromptTemplate]:
        """List all templates."""
        pass

    @abstractmethod
    async def delete_template(self, template_id: str) -> bool:
        """Delete a template by ID."""
        pass


class IPromptRenderingService(ABC):
    """Service interface for rendering prompt templates."""

    @abstractmethod
    async def render_template(
        self, template: PromptTemplate, variables: Dict[str, Any]
    ) -> str:
        """Render a template with variables."""
        pass

    @abstractmethod
    async def validate_template(self, template_content: str) -> bool:
        """Validate template syntax."""
        pass


class IPromptVersioningService(ABC):
    """Service interface for managing prompt template versions."""

    @abstractmethod
    async def create_version(
        self, template_id: str, version: str, content: str
    ) -> None:
        """Create a new version of a template."""
        pass

    @abstractmethod
    async def get_versions(self, template_id: str) -> List[str]:
        """Get all versions for a template."""
        pass

    @abstractmethod
    async def get_version_content(
        self, template_id: str, version: str
    ) -> Optional[str]:
        """Get content for a specific version."""
        pass
