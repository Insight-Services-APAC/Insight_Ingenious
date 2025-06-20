"""
CLI bounded context.

This module contains the CLI functionality organized using Domain-Driven Design principles.
It provides command-line interface capabilities for the Insight Ingenious application.
"""

from .application.services import CLIApplicationService
from .domain.entities import CLICommand, ProjectConfig, ServerConfig
from .domain.services import IProjectService, IServerService, ITemplateService
from .domain.value_objects import HostAddress, Port, ProjectName
from .infrastructure.services import (
    FileSystemProjectService,
    TemplateGenerationService,
    UvicornServerService,
)
from .interfaces.cli_controllers import CLIController
from .main import app

__all__ = [
    # Main CLI app
    "app",
    # Application Layer
    "CLIApplicationService",
    # Domain Layer - Entities
    "CLICommand",
    "ProjectConfig",
    "ServerConfig",
    # Domain Layer - Value Objects
    "HostAddress",
    "Port",
    "ProjectName",
    # Domain Layer - Services
    "IProjectService",
    "IServerService",
    "ITemplateService",
    # Infrastructure Layer
    "FileSystemProjectService",
    "TemplateGenerationService",
    "UvicornServerService",
    # Interface Layer
    "CLIController",
]
