"""
CLI domain value objects.

This module contains the value objects for the CLI bounded context.
"""

from pydantic import BaseModel, Field, validator


class HostAddress(BaseModel):
    """Value object representing a host address."""

    value: str = Field(..., description="Host address value")

    @validator("value")
    def validate_host(cls, v):
        if not v:
            raise ValueError("Host address cannot be empty")
        # Basic validation - could be enhanced with IP/hostname validation
        return v

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other) -> bool:
        if isinstance(other, HostAddress):
            return self.value == other.value
        return False


class Port(BaseModel):
    """Value object representing a network port."""

    value: int = Field(..., description="Port number", ge=1, le=65535)

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other) -> bool:
        if isinstance(other, Port):
            return self.value == other.value
        return False


class ProjectName(BaseModel):
    """Value object representing a project name."""

    value: str = Field(..., description="Project name value")

    @validator("value")
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Project name cannot be empty")
        # Remove invalid characters for filesystem
        invalid_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
        if any(char in v for char in invalid_chars):
            raise ValueError(
                f"Project name contains invalid characters: {invalid_chars}"
            )
        return v.strip()

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other) -> bool:
        if isinstance(other, ProjectName):
            return self.value == other.value
        return False
