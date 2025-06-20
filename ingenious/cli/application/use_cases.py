"""
CLI application use cases.

This module contains the use cases that represent specific application workflows
for CLI operations.
"""

from pathlib import Path
from typing import Optional

from ..domain.entities import ProjectConfig, ServerConfig
from ..domain.services import IProjectService, IServerService, ITemplateService


class CreateProjectUseCase:
    """Use case for creating a new project."""

    def __init__(
        self,
        project_service: IProjectService,
        template_service: ITemplateService,
    ):
        self._project_service = project_service
        self._template_service = template_service

    async def execute(self, project_name: str, project_path: Path) -> None:
        """Execute the create project use case."""
        config = ProjectConfig(name=project_name, path=str(project_path), profile="dev")

        await self._project_service.create_project(config)
        await self._template_service.generate_config_template(
            project_name, project_path
        )
        await self._template_service.generate_gitignore(project_path)
        await self._template_service.generate_readme(project_name, project_path)


class StartServerUseCase:
    """Use case for starting the server."""

    def __init__(self, server_service: IServerService):
        self._server_service = server_service

    async def execute(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        project_dir: Optional[str] = None,
        profile_dir: Optional[str] = None,
    ) -> None:
        """Execute the start server use case."""
        config = ServerConfig(
            host=host,
            port=port,
            project_dir=project_dir,
            profile_dir=profile_dir,
        )

        if not await self._server_service.validate_server_config(config):
            raise ValueError("Invalid server configuration")

        await self._server_service.start_server(config)


class RunProjectUseCase:
    """Use case for running a project."""

    def __init__(
        self,
        project_service: IProjectService,
        server_service: IServerService,
    ):
        self._project_service = project_service
        self._server_service = server_service

    async def execute(self, project_path: Path) -> None:
        """Execute the run project use case."""
        if not await self._project_service.validate_project(project_path):
            raise ValueError("No valid project found in the specified directory")

        config = ServerConfig(
            host="127.0.0.1",
            port=8000,
            project_dir=str(project_path),
        )

        await self._server_service.start_server(config)
