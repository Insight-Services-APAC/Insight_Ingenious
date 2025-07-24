"""
Verify that *character‑level* overlap works the same way for every splitter.

We patch the embedding backend for the semantic strategy to avoid real
network calls.
"""
from unittest.mock import MagicMock, patch

import pytest

from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.factory import build_splitter

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_TEXT = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 4  # long enough to create many chunks
K = 3                                     # overlap window

def _fake_embedder():
    stub = MagicMock()
    stub.embed_documents.side_effect = lambda texts: [[0.0] * 5 for _ in texts]
    return stub

# ---------------------------------------------------------------------------
# Parametrised test over all strategies
# ---------------------------------------------------------------------------
@patch("ingenious.chunk.strategy.langchain_semantic.OpenAIEmbeddings",
       return_value=_fake_embedder())
@pytest.mark.parametrize("strategy", ["recursive", "markdown", "token", "semantic"])
def test_character_overlap_consistency(_, strategy):
    """
    For `overlap_unit="characters"` the last *K* characters of chunk *i*
    must equal the first *K* characters of chunk *i+1*.
    """
    cfg = ChunkConfig(
        strategy=strategy,
        chunk_size=15,          # intentionally tiny to force many chunks
        chunk_overlap=K,
        overlap_unit="characters",
    )
    splitter = build_splitter(cfg)
    chunks = splitter.split_text(_TEXT)

    # At least two chunks must be produced
    assert len(chunks) >= 2

    for i in range(1, len(chunks)):
        assert chunks[i - 1][-K:] == chunks[i][:K]
