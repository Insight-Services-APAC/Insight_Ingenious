"""
Character-budget overlap invariant for the *token* strategy.
"""
from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.factory import build_splitter

# Re-use unicode fixture defined in tests/conftest.py
K = 5


def test_token_character_overlap(unicode_text):
    cfg = ChunkConfig(
        strategy="token",
        chunk_size=40,
        chunk_overlap=K,
        overlap_unit="characters",
    )
    chunks = build_splitter(cfg).split_text(unicode_text)

    assert len(chunks) >= 2
    for i in range(1, len(chunks)):
        assert chunks[i - 1][-K:] == chunks[i][:K]
