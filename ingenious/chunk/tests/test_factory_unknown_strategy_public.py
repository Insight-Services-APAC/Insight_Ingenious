import pytest

from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.factory import build_splitter


def test_build_splitter_unknown_strategy():
    """
    The public helper must raise ValueError when the *strategy* field is
    corrupted at runtime (e.g. deserialised from un‑trusted JSON).
    """
    cfg = ChunkConfig()                    # valid default instance
    object.__setattr__(cfg, "strategy", "does-not-exist")   # bypass immutability

    with pytest.raises(ValueError, match="Unknown chunking strategy"):
        build_splitter(cfg)
