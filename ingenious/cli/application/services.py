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

    def create_project(
        self, project_name: str, project_path: Path, profile: str = "dev"
    ) -> bool:
        """Synchronous wrapper for creating a project."""
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Check if project already exists
            if loop.run_until_complete(
                self._project_service.project_exists(project_path)
            ):
                raise ValueError(f"Project already exists at {project_path}")

            config = ProjectConfig(
                name=project_name, path=str(project_path), profile=profile
            )
            loop.run_until_complete(self._project_service.create_project(config))
            loop.run_until_complete(
                self._template_service.generate_template(project_name, project_path)
            )
            return True
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception:
            return False
        finally:
            loop.close()

    def start_server(self, config: ServerConfig) -> bool:
        """Synchronous wrapper for starting the server."""
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Check if server is already running
            if loop.run_until_complete(self._server_service.is_running()):
                raise RuntimeError("Server is already running")

            loop.run_until_complete(self._server_service.start_server(config))
            return True
        except RuntimeError:
            # Re-raise runtime errors
            raise
        except Exception:
            return False
        finally:
            loop.close()

    def stop_server(self) -> bool:
        """Synchronous wrapper for stopping the server."""
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Check if server is not running
            if not loop.run_until_complete(self._server_service.is_running()):
                raise RuntimeError("Server is not running")

            loop.run_until_complete(self._server_service.stop_server())
            return True
        except RuntimeError:
            # Re-raise runtime errors
            raise
        except Exception:
            return False
        finally:
            loop.close()

    def get_server_status(self) -> dict:
        """Check if server is running and return status."""
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            is_running = loop.run_until_complete(self._server_service.is_running())
            return {
                "is_running": is_running,
                "status": "running" if is_running else "stopped",
            }
        except Exception:
            return {"is_running": False, "status": "error"}
        finally:
            loop.close()

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

    def get_project_info(self, project_path: Path) -> ProjectConfig:
        """Get information about a project."""
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self._project_service.get_project_config(project_path)
            )
        finally:
            loop.close()

    def generate_project_template(self, template_name: str, output_path: Path) -> bool:
        """Generate a project template."""
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Check if template is valid
            available_templates = loop.run_until_complete(
                self._template_service.list_templates()
            )
            if template_name not in available_templates:
                raise ValueError(f"Invalid template: {template_name}")

            loop.run_until_complete(
                self._template_service.generate_template(template_name, output_path)
            )
            return True
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception:
            return False
        finally:
            loop.close()

    def list_available_templates(self) -> list[str]:
        """List available project templates."""
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._template_service.list_templates())
        finally:
            loop.close()

    def _validate_project_path(self, project_path: Optional[Path]) -> None:
        """Validate project path."""
        if project_path is None:
            raise ValueError("Project path is required")

    def _validate_project_name(self, project_name: str) -> None:
        """Validate project name."""
        if not project_name or not project_name.strip():
            raise ValueError("Project name cannot be empty")

        # Check for invalid characters
        invalid_chars = {" ", "@"}
        if any(char in project_name for char in invalid_chars):
            raise ValueError(
                f"Project name contains invalid characters: {project_name}"
            )
