"""
Character-budget path of the *semantic* splitter with patched embeddings.
"""
from unittest.mock import patch, MagicMock

from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.factory import build_splitter


def _fake_embedder():
    stub = MagicMock()
    stub.embed_documents.side_effect = lambda texts: [[0.0] * 5 for _ in texts]
    return stub


@patch("ingenious.chunk.strategy.langchain_semantic.OpenAIEmbeddings",
       return_value=_fake_embedder())
def test_semantic_character_overlap(_, sample_text):
    text = (sample_text.read_text())[:600]   # deterministic small corpus
    K = 7
    cfg = ChunkConfig(
        strategy="semantic",
        chunk_size=50,
        chunk_overlap=K,
        overlap_unit="characters",
    )
    splitter = build_splitter(cfg)
    chunks = splitter.split_text(text)

    assert len(chunks) >= 2
    for i in range(1, len(chunks)):
        assert chunks[i - 1][-K:] == chunks[i][:K]
