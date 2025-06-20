from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, Template, TemplateSyntaxError

from ..domain.entities import PromptTemplate
from ..domain.services import (
    IPromptRenderingService,
    IPromptTemplateRepository,
    IPromptVersioningService,
)


class FileSystemPromptRepository(IPromptTemplateRepository):
    """File system implementation of prompt template repository."""

    def __init__(self, templates_path: str = "templates/prompts"):
        self.templates_path = Path(templates_path)
        self.templates_path.mkdir(parents=True, exist_ok=True)

    async def save_template(self, template: PromptTemplate) -> None:
        """Save template to file system."""
        file_path = self.templates_path / f"{template.name}.jinja"
        with open(file_path, "w") as f:
            f.write(template.template_content)

    async def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Get template by ID (not supported in file system implementation)."""
        # File system implementation doesn't have ID concept
        return None

    async def get_template_by_name(self, name: str) -> Optional[PromptTemplate]:
        """Get template by name from file system."""
        file_path = self.templates_path / f"{name}.jinja"
        if not file_path.exists():
            return None

        with open(file_path, "r") as f:
            content = f.read()

        return PromptTemplate(
            name=name,
            template_content=content,
            template_id=name,  # Use name as ID for file system
        )

    async def list_templates(self) -> List[PromptTemplate]:
        """List all templates from file system."""
        templates = []
        for file_path in self.templates_path.glob("*.jinja"):
            name = file_path.stem
            template = await self.get_template_by_name(name)
            if template:
                templates.append(template)
        return templates

    async def delete_template(self, template_id: str) -> bool:
        """Delete template by ID (using name for file system)."""
        file_path = self.templates_path / f"{template_id}.jinja"
        if file_path.exists():
            file_path.unlink()
            return True
        return False


class Jinja2RenderingService(IPromptRenderingService):
    """Jinja2 implementation of prompt rendering service."""

    def __init__(self, templates_path: str = "templates/prompts"):
        self.templates_path = templates_path
        self.env = Environment(
            loader=FileSystemLoader(templates_path),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    async def render_template(
        self, template: PromptTemplate, variables: Dict[str, Any]
    ) -> str:
        """Render template using Jinja2."""
        try:
            jinja_template = self.env.from_string(template.template_content)
            return jinja_template.render(**variables)
        except Exception as e:
            raise ValueError(f"Error rendering template: {e}")

    async def validate_template(self, template_content: str) -> bool:
        """Validate Jinja2 template syntax."""
        try:
            Template(template_content)
            return True
        except TemplateSyntaxError:
            return False


class InMemoryVersioningService(IPromptVersioningService):
    """In-memory implementation of prompt versioning service."""

    def __init__(self):
        self.versions: Dict[str, Dict[str, str]] = {}

    async def create_version(
        self, template_id: str, version: str, content: str
    ) -> None:
        """Create a new version of a template."""
        if template_id not in self.versions:
            self.versions[template_id] = {}
        self.versions[template_id][version] = content

    async def get_versions(self, template_id: str) -> List[str]:
        """Get all versions for a template."""
        return list(self.versions.get(template_id, {}).keys())

    async def get_version_content(
        self, template_id: str, version: str
    ) -> Optional[str]:
        """Get content for a specific version."""
        return self.versions.get(template_id, {}).get(version)
