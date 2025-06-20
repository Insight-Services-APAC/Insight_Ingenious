"""
CLI domain services.

This module contains the domain service interfaces for the CLI bounded context.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from .entities import ProjectConfig, ServerConfig


class IProjectService(ABC):
    """Domain service interface for project operations."""

    @abstractmethod
    async def create_project(self, config: ProjectConfig) -> None:
        """Create a new project with the given configuration."""
        pass

    @abstractmethod
    async def validate_project(self, project_path: Path) -> bool:
        """Validate if a project exists and is properly configured."""
        pass

    @abstractmethod
    async def project_exists(self, project_path: Path) -> bool:
        """Check if a project exists at the given path."""
        pass

    @abstractmethod
    async def get_project_config(self, project_path: Path) -> ProjectConfig:
        """Get project configuration from the given path."""
        pass


class IServerService(ABC):
    """Domain service interface for server operations."""

    @abstractmethod
    async def start_server(self, config: ServerConfig) -> None:
        """Start the server with the given configuration."""
        pass

    @abstractmethod
    async def stop_server(self) -> bool:
        """Stop the running server."""
        pass

    @abstractmethod
    async def is_running(self) -> bool:
        """Check if the server is currently running."""
        pass

    @abstractmethod
    async def validate_server_config(self, config: ServerConfig) -> bool:
        """Validate server configuration."""
        pass


class ITemplateService(ABC):
    """Domain service interface for template operations."""

    @abstractmethod
    async def generate_config_template(
        self, project_name: str, output_path: Path
    ) -> None:
        """Generate configuration template files."""
        pass

    @abstractmethod
    async def generate_gitignore(self, output_path: Path) -> None:
        """Generate .gitignore file."""
        pass

    @abstractmethod
    async def generate_readme(self, project_name: str, output_path: Path) -> None:
        """Generate README file."""
        pass

    @abstractmethod
    async def generate_template(self, template_name: str, output_path: Path) -> bool:
        """Generate a project template."""
        pass

    @abstractmethod
    async def list_templates(self) -> List[str]:
        """List available project templates."""
        pass
