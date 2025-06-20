from typing import Optional, Dict, Any
from datetime import datetime
from uuid import uuid4


class PromptTemplate:
    """Domain entity representing a prompt template."""

    def __init__(
        self,
        name: str,
        template_content: str,
        template_id: Optional[str] = None,
        version: str = "1.0.0",
        description: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.template_id = template_id or str(uuid4())
        self.name = name
        self.template_content = template_content
        self.version = version
        self.description = description
        self.variables = variables or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def render(self, **kwargs) -> str:
        """Render the template with provided variables."""
        # Basic template rendering - in real implementation would use Jinja2
        content = self.template_content
        for key, value in kwargs.items():
            content = content.replace(f"{{{{{key}}}}}", str(value))
        return content

    def update_content(self, new_content: str) -> None:
        """Update template content and timestamp."""
        self.template_content = new_content
        self.updated_at = datetime.utcnow()


class PromptVersion:
    """Value object representing a version of a prompt template."""

    def __init__(self, version: str, template_content: str, created_at: datetime):
        self.version = version
        self.template_content = template_content
        self.created_at = created_at

    def __eq__(self, other):
        if not isinstance(other, PromptVersion):
            return False
        return self.version == other.version


class PromptLibrary:
    """Domain entity representing a collection of prompt templates."""

    def __init__(self, library_id: Optional[str] = None, name: str = "Default"):
        self.library_id = library_id or str(uuid4())
        self.name = name
        self.templates: Dict[str, PromptTemplate] = {}
        self.created_at = datetime.utcnow()

    def add_template(self, template: PromptTemplate) -> None:
        """Add a template to the library."""
        self.templates[template.name] = template

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a template by name."""
        return self.templates.get(name)

    def remove_template(self, name: str) -> bool:
        """Remove a template from the library."""
        if name in self.templates:
            del self.templates[name]
            return True
        return False

    def list_templates(self) -> list[str]:
        """List all template names in the library."""
        return list(self.templates.keys())
