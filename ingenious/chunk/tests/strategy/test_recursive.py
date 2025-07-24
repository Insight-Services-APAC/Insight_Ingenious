from tiktoken import get_encoding
from ingenious.chunk.factory import build_splitter
from ingenious.chunk.config import ChunkConfig

def test_recursive_respects_overlap():
    text = "A " * 300
    cfg = ChunkConfig(strategy="recursive", chunk_size=20, chunk_overlap=5)
    chunks = build_splitter(cfg).split_text(text)
    enc = get_encoding(cfg.encoding_name)
    for i in range(1, len(chunks)):
        assert enc.encode(chunks[i-1])[-5:] == enc.encode(chunks[i])[:5]
