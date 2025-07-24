"""
A *single* grapheme that itself exceeds `chunk_size`
must be emitted intact and remain valid UTF‑16.
"""
from tiktoken import get_encoding

from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.factory import build_splitter


def test_unicode_single_grapheme_overbudget():
    emoji = "😀"                # 2–3 tokens, depending on encoding
    enc = get_encoding("cl100k_base")
    budget = len(enc.encode(emoji)) - 1     # guarantee “over budget”

    cfg = ChunkConfig(strategy="token", chunk_size=budget, chunk_overlap=0)
    splitter = build_splitter(cfg)

    chunks = splitter.split_text(emoji)
    # Drop empty strings that some strategies prepend
    non_empty = [c for c in chunks if c]
    assert non_empty == [emoji]
    non_empty[0].encode("utf-16", "strict")  # still valid UTF‑16
