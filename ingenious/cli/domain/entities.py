"""
CLI domain entities.

This module contains the core business entities for the CLI bounded context.
"""

from typing import Optional

from pydantic import BaseModel, Field


class ProjectConfig(BaseModel):
    """Domain entity representing a project configuration."""

    name: str = Field(..., description="Project name")
    path: str = Field(..., description="Project directory path")
    profile: str = Field(default="dev", description="Configuration profile")

    def __str__(self) -> str:
        return f"Project '{self.name}' at {self.path}"


class ServerConfig(BaseModel):
    """Domain entity representing server configuration."""

    host: str = Field(default="127.0.0.1", description="Server host address")
    port: int = Field(default=8000, description="Server port", ge=1, le=65535)
    project_dir: Optional[str] = Field(None, description="Project directory path")
    profile_dir: Optional[str] = Field(None, description="Profile directory path")

    def __str__(self) -> str:
        return f"Server {self.host}:{self.port}"


class CLICommand(BaseModel):
    """Domain entity representing a CLI command execution context."""

    command_name: str = Field(..., description="Name of the command")
    arguments: dict = Field(default_factory=dict, description="Command arguments")
    options: dict = Field(default_factory=dict, description="Command options")

    def __str__(self) -> str:
        return f"Command '{self.command_name}'"
