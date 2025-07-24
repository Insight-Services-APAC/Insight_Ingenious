# ingenious/chunk/tests/strategy/test_semantic_warning.py
import pytest
from ingenious.chunk.config import ChunkConfig


def test_semantic_emits_fallback_warning():
    """
    A *semantic* config without embed‑model **and** Azure deployment must raise
    the documented UserWarning about falling back to the public OpenAI endpoint.
    """
    with pytest.warns(UserWarning, match="Semantic splitter: no .* supplied"):
        ChunkConfig(strategy="semantic", chunk_size=64, chunk_overlap=8)
