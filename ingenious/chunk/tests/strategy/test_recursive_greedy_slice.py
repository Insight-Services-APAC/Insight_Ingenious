"""
Validate the *greedy slice* branch of `RecursiveTokenSplitter`.
"""
from tiktoken import get_encoding

from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.factory import build_splitter


def test_recursive_greedy_slice():
    text = "A" * 500            # one extremely long “paragraph”
    cfg = ChunkConfig(strategy="recursive", chunk_size=50, chunk_overlap=5)
    splitter = build_splitter(cfg)
    chunks = splitter.split_text(text)

    enc = get_encoding(cfg.encoding_name)
    max_allowed = cfg.chunk_size + 2 * cfg.chunk_overlap

    assert chunks and all(len(enc.encode(c)) <= max_allowed for c in chunks)

    # overlap invariant
    for i in range(1, len(chunks)):
        tail = enc.encode(chunks[i - 1])[-cfg.chunk_overlap :]
        head = enc.encode(chunks[i])[: cfg.chunk_overlap]
        assert tail == head
