"""
CLI application services.

This module contains the application services that orchestrate business logic
for CLI operations.
"""

from pathlib import Path
from typing import Optional

from ..domain.entities import ProjectConfig, ServerConfig
from ..domain.services import IProjectService, IServerService, ITemplateService


class CLIApplicationService:
    """Application service for CLI operations."""

    def __init__(
        self,
        project_service: IProjectService,
        server_service: IServerService,
        template_service: ITemplateService,
    ):
        self._project_service = project_service
        self._server_service = server_service
        self._template_service = template_service

    async def initialize_new_project(self) -> None:
        """Initialize a new project in the current directory."""
        current_dir = Path.cwd()
        project_name = current_dir.name

        config = ProjectConfig(name=project_name, path=str(current_dir), profile="dev")

        await self._project_service.create_project(config)
        await self._template_service.generate_config_template(project_name, current_dir)
        await self._template_service.generate_gitignore(current_dir)
        await self._template_service.generate_readme(project_name, current_dir)

    async def start_rest_api_server(
        self,
        project_dir: Optional[str] = None,
        profile_dir: Optional[str] = None,
        host: str = "127.0.0.1",
        port: int = 8000,
    ) -> None:
        """Start the REST API server."""
        config = ServerConfig(
            host=host,
            port=port,
            project_dir=project_dir,
            profile_dir=profile_dir,
        )

        # Validate configuration
        if not await self._server_service.validate_server_config(config):
            raise ValueError("Invalid server configuration")

        await self._server_service.start_server(config)

    async def run_project(self) -> None:
        """Run the current project."""
        current_dir = Path.cwd()

        # Validate project exists
        if not await self._project_service.validate_project(current_dir):
            raise ValueError("No valid project found in current directory")

        # Start server with default configuration
        await self.start_rest_api_server(
            project_dir=str(current_dir),
            host="127.0.0.1",
            port=8000,
        )
