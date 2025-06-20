"""
CLI dependency injection and application setup.

This module sets up the dependency injection container and creates the CLI application
using the DDD structure.
"""

import asyncio
from functools import wraps
from typing import Any, Callable

import typer

from .application.services import CLIApplicationService
from .infrastructure.services import (
    FileSystemProjectService,
    TemplateGenerationService,
    UvicornServerService,
)
from .interfaces.cli_controllers import CLIController


def async_command(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to handle async commands in typer."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


def create_cli_app() -> typer.Typer:
    """Create and configure the CLI application with DDD structure."""

    # Create infrastructure services
    project_service = FileSystemProjectService()
    server_service = UvicornServerService()
    template_service = TemplateGenerationService()

    # Create application service
    cli_service = CLIApplicationService(
        project_service=project_service,
        server_service=server_service,
        template_service=template_service,
    )

    # Create controller
    controller = CLIController(cli_service)

    # Wrap async commands with new sleek names
    controller.app.command()(async_command(controller.run))
    controller.app.command()(async_command(controller.dev))
    controller.app.command()(async_command(controller.init))

    return controller.app


# Create the main CLI application
app = create_cli_app()
