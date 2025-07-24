from tiktoken import get_encoding
from ingenious.chunk.factory import build_splitter
from ingenious.chunk.config import ChunkConfig

def test_token_split_counts(unicode_text):
    cfg = ChunkConfig(strategy="token", chunk_size=10, chunk_overlap=0, encoding_name="cl100k_base")
    splitter = build_splitter(cfg)
    enc = get_encoding("cl100k_base")
    chunks = splitter.split_text(unicode_text)
    for c in chunks:
        assert len(enc.encode(c)) <= 10
