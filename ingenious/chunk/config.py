# ingenious/chunk/config.py
from typing import List, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ChunkConfig(BaseModel):
    """
    User-facing configuration for content chunking.

    * Mirrors CLI arguments 1-1.
    * The model is **frozen** (immutable) so invariants cannot be broken after
      instantiation.
    """

    # ------------------------------------------------------------------
    # Pydantic model settings
    # ------------------------------------------------------------------
    model_config = ConfigDict(frozen=True)

    # ------------------------------------------------------------------
    # Strategy selector
    # ------------------------------------------------------------------
    strategy: Literal["recursive", "markdown", "token", "semantic"] = "recursive"

    # ------------------------------------------------------------------
    # Shared knobs
    # ------------------------------------------------------------------
    chunk_size: int = Field(
        1024,
        ge=1,
        description="Max tokens/characters allowed in a single chunk.",
    )
    chunk_overlap: int = Field(
        128,
        ge=0,
        description="Number of tokens/characters shared between consecutive chunks.",
    )

    overlap_unit: Literal["tokens", "characters"] = "tokens"

    # ------------------------------------------------------------------
    # Strategy-specific options
    # ------------------------------------------------------------------
    # recursive / markdown
    separators: List[str] | None = None

    # token splitter
    encoding_name: str = "cl100k_base"

    # semantic splitter
    embed_model: str | None = None
    azure_openai_deployment: str | None = None

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------
    @model_validator(mode="after")
    def _validate_overlap(self):
        """
        Enforce ``chunk_overlap < chunk_size``.

        *Why raise instead of clamping?*  
        Silent correction hides configuration mistakes and makes results
        unpredictable across environments.  By surfacing an explicit
        `ValidationError` we fail fast and give users immediate feedback.
        """
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                f"chunk_overlap ({self.chunk_overlap}) must be smaller than "
                f"chunk_size ({self.chunk_size})"
            )
        return self

    @model_validator(mode="after")
    def _semantic_warn_backend(self):
        """
        Allow the semantic strategy to run when *neither* an Azure deployment
        nor an explicit embed model is supplied.  We fall back to the public
        OpenAI endpoint and emit a warning so users remember to set
        OPENAI_API_KEY.
        """
        if self.strategy == "semantic" and not (
            self.azure_openai_deployment or self.embed_model
        ):
            import warnings

            warnings.warn(
                "Semantic splitter: no `azure_openai_deployment` or "
                "`embed_model` supplied – falling back to the public "
                "OpenAI endpoint with model 'text-embedding-3-small'. "
                "Make sure OPENAI_API_KEY is set.",
                stacklevel=2,
            )
        return self
