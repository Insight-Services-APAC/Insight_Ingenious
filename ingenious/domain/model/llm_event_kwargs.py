from typing import Any, Dict

from pydantic import BaseModel, Field


class LLMEventKwargs(BaseModel):
    """Represents keyword arguments for LLM event handlers."""

    model: str = Field("", description="The model name")
    prompt_tokens: int = Field(0, description="Number of prompt tokens")
    completion_tokens: int = Field(0, description="Number of completion tokens")
    total_tokens: int = Field(0, description="Total number of tokens")
    cost: float = Field(0.0, description="Cost of the request")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary."""
        return self.model_dump()
