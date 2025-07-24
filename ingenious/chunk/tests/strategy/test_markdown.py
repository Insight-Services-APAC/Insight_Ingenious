from ingenious.chunk.factory import build_splitter
from ingenious.chunk.config import ChunkConfig

def test_markdown_respects_headings(sample_md):
    cfg = ChunkConfig(strategy="markdown", chunk_size=40, chunk_overlap=0)
    splitter = build_splitter(cfg)
    md_text = sample_md.read_text()
    chunks = splitter.split_text(md_text)
    # Ensure heading separators are honoured
    assert chunks[0].startswith("# Title")
    assert any("## Subtitle" in c for c in chunks)
