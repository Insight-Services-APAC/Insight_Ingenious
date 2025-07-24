import pytest
import pydantic
from ingenious.chunk.config import ChunkConfig


def test_defaults():
    cfg = ChunkConfig()
    assert cfg.strategy == "recursive"
    assert cfg.chunk_size == 1024
    assert cfg.chunk_overlap == 128


def test_validation_error():
    # 1️⃣  negative size still invalid
    with pytest.raises(pydantic.ValidationError):
        ChunkConfig(chunk_size=-1)

    # 2️⃣  overlap must now be strictly smaller than size
    with pytest.raises(ValueError):
        ChunkConfig(chunk_size=10, chunk_overlap=10)
