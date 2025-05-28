import logging
from typing import TYPE_CHECKING

from pydantic import BaseModel

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class AgentConfig(BaseModel):
    """Agent Configuration"""

    name: str
    system_message: str
    model: str = "gpt-3.5-turbo"


class Agent(BaseModel):
    """Stub for Agent model."""

    name: str = "stub"


class Agents(BaseModel):
    """Stub for Agents collection."""

    agents: list[Agent] = []


class AgentChat(BaseModel):
    """Stub for AgentChat model."""

    chat_id: str = "stub"


class AgentChats(BaseModel):
    """Stub for AgentChats collection."""

    chats: list[AgentChat] = []


class AgentMessage(BaseModel):
    """Stub for AgentMessage model."""

    message: str = "stub"


class LLMUsageTracker(BaseModel):
    """Stub for LLMUsageTracker."""

    usage: int = 0


class IProjectAgents(BaseModel):
    """Stub for IProjectAgents interface."""

    project: str = "stub"
