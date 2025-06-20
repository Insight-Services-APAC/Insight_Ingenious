"""
CLI domain layer.

This module contains the domain entities, value objects, and domain services
for the CLI bounded context.
"""

from .entities import CLICommand, ProjectConfig, ServerConfig
from .services import IProjectService, IServerService, ITemplateService
from .value_objects import HostAddress, Port, ProjectName

__all__ = [
    # Entities
    "CLICommand",
    "ProjectConfig",
    "ServerConfig",
    # Value Objects
    "HostAddress",
    "Port",
    "ProjectName",
    # Services
    "IProjectService",
    "IServerService",
    "ITemplateService",
]
