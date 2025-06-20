"""
CLI domain services.

This module contains the domain service interfaces for the CLI bounded context.
"""

from abc import ABC, abstractmethod
from pathlib import Path

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


class IServerService(ABC):
    """Domain service interface for server operations."""

    @abstractmethod
    async def start_server(self, config: ServerConfig) -> None:
        """Start the server with the given configuration."""
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
