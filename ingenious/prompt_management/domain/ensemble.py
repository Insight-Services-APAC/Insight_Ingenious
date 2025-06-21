"""
Domain entities and models for Prompt Ensemble functionality.

This module defines the core domain concepts for orchestrating multiple AI agents
in a prompt ensemble pattern, where a main prompt is decomposed into sub-prompts,
processed by multiple agents, and then aggregated.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class EnsembleStrategy(str, Enum):
    """Strategies for processing ensemble prompts."""

    PARALLEL = "parallel"  # All sub-prompts processed simultaneously
    SEQUENTIAL = "sequential"  # Sub-prompts processed in order
    HIERARCHICAL = "hierarchical"  # Sub-prompts processed in tree structure


class AgentRole(str, Enum):
    """Roles that agents can play in an ensemble."""

    ANALYZER = "analyzer"
    CRITIC = "critic"
    SYNTHESIZER = "synthesizer"
    SPECIALIST = "specialist"
    REVIEWER = "reviewer"


class EnsemblePromptTemplate(BaseModel):
    """Template for generating sub-prompts in an ensemble."""

    template_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    content: str  # Jinja2 template content
    role: AgentRole
    priority: int = 1  # Processing priority (lower = higher priority)
    dependencies: List[str] = Field(
        default_factory=list
    )  # Template IDs this depends on
    variables: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class EnsembleConfiguration(BaseModel):
    """Configuration for a prompt ensemble."""

    config_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: Optional[str] = None
    strategy: EnsembleStrategy = EnsembleStrategy.PARALLEL
    main_prompt_template: str  # Jinja2 template for the main prompt
    sub_prompt_templates: List[EnsemblePromptTemplate]
    reduce_prompt_template: str  # Template for aggregating results
    max_concurrent_agents: int = 5
    timeout_seconds: int = 300
    retry_count: int = 3
    variables: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class AgentExecution(BaseModel):
    """Represents a single agent's execution in an ensemble."""

    execution_id: str = Field(default_factory=lambda: str(uuid4()))
    agent_role: AgentRole
    template_id: str
    prompt: str
    response: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    token_usage: Dict[str, int] = Field(default_factory=dict)

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate execution duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def is_successful(self) -> bool:
        """Check if execution was successful."""
        return self.error is None and self.response is not None

    class Config:
        use_enum_values = True


class EnsembleExecution(BaseModel):
    """Represents the execution of an entire ensemble."""

    execution_id: str = Field(default_factory=lambda: str(uuid4()))
    config_id: str
    input_data: Dict[str, Any]
    agent_executions: List[AgentExecution] = Field(default_factory=list)
    final_response: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    status: str = "running"  # running, completed, failed, cancelled
    error: Optional[str] = None
    total_tokens_used: int = 0
    total_cost_estimate: float = 0.0

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate total execution duration in seconds."""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def successful_executions(self) -> List[AgentExecution]:
        """Get all successful agent executions."""
        return [exec for exec in self.agent_executions if exec.is_successful]

    @property
    def failed_executions(self) -> List[AgentExecution]:
        """Get all failed agent executions."""
        return [exec for exec in self.agent_executions if not exec.is_successful]

    def add_agent_execution(self, execution: AgentExecution) -> None:
        """Add an agent execution to this ensemble execution."""
        self.agent_executions.append(execution)
        if execution.token_usage:
            try:
                # Safely sum token usage values
                token_sum = sum(
                    int(v) if not hasattr(v, "__len__") else 0
                    for v in execution.token_usage.values()
                )
                self.total_tokens_used += token_sum
            except (TypeError, ValueError):
                # Skip token counting if values are not numeric
                pass


class EnsembleResult(BaseModel):
    """Final result of an ensemble execution."""

    execution_id: str
    config_name: str
    final_response: str
    agent_responses: Dict[str, str]  # role -> response
    metadata: Dict[str, Any] = Field(default_factory=dict)
    execution_stats: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def from_execution(
        cls, execution: EnsembleExecution, config: EnsembleConfiguration
    ) -> "EnsembleResult":
        """Create result from execution and config."""
        agent_responses = {
            exec.agent_role: exec.response
            for exec in execution.successful_executions
            if exec.response
        }

        execution_stats = {
            "total_duration_seconds": execution.duration_seconds,
            "total_tokens_used": execution.total_tokens_used,
            "successful_agents": len(execution.successful_executions),
            "failed_agents": len(execution.failed_executions),
            "total_cost_estimate": execution.total_cost_estimate,
        }

        return cls(
            execution_id=execution.execution_id,
            config_name=config.name,
            final_response=execution.final_response or "",
            agent_responses=agent_responses,
            execution_stats=execution_stats,
        )
