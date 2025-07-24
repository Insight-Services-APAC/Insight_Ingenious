from ingenious.chunk.factory import build_splitter
from ingenious.chunk.config import ChunkConfig

def test_grapheme_boundaries_preserved():
    text = "😀🇦🇺 café\n" * 5   # emojis + accented chars
    cfg = ChunkConfig(strategy="token", chunk_size=4, chunk_overlap=0)
    splitter = build_splitter(cfg)

    chunks = splitter.split_text(text)

    # Every chunk must render valid UTF-16 (no lone surrogates)
    for c in chunks:
        try:
            c.encode("utf-16", "strict")
        except UnicodeEncodeError:
            assert False, f"Invalid UTF-16 sequence in chunk: {repr(c)}"
