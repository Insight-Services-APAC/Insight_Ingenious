# ingenious/chunk/tests/test_factory.py
from tiktoken import get_encoding

from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.factory import build_splitter

ENC = "cl100k_base"


def test_factory_dispatch_recursive():
    """
    Factory should build a recursive splitter that

    1. Produces at least one chunk.
    2. Never exceeds chunk_size + 2*chunk_overlap tokens after overlap injection.
    """
    cfg = ChunkConfig(
        strategy="recursive",
        chunk_size=50,
        chunk_overlap=10,
        encoding_name=ENC,
    )
    splitter = build_splitter(cfg)
    chunks = splitter.split_text("foo\n\nbar" * 50)

    enc = get_encoding(ENC)
    max_allowed = cfg.chunk_size + 2 * cfg.chunk_overlap  # ← allow both windows
    assert chunks and all(len(enc.encode(c)) <= max_allowed for c in chunks)
