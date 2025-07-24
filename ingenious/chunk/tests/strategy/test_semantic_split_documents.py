"""
Smoke‑test `SemanticOverlapChunker.split_documents` including metadata
round‑trip and overlap invariant.
"""
from unittest.mock import MagicMock, patch

from langchain_core.documents import Document
from tiktoken import get_encoding

from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.factory import build_splitter


def _fake_embedder():
    stub = MagicMock()
    stub.embed_documents.side_effect = lambda texts: [[0.0] * 5 for _ in texts]
    return stub


class _DummySemanticChunker:
    def __init__(self, *_, **__):
        pass

    def split_documents(self, docs):
        return docs                      # passthrough – keeps test simple


@patch("ingenious.chunk.strategy.langchain_semantic.SemanticChunker", new=_DummySemanticChunker)
@patch("ingenious.chunk.strategy.langchain_semantic.OpenAIEmbeddings", return_value=_fake_embedder())
def test_semantic_split_documents(mock_openai):
    cfg = ChunkConfig(strategy="semantic", chunk_size=20, chunk_overlap=5)
    splitter = build_splitter(cfg)

    docs = [
        Document(page_content="AAA BBB CCC.", metadata={"id": 1}),
        Document(page_content="DDD EEE FFF.", metadata={"id": 2}),
    ]
    out = splitter.split_documents(docs)

    # 1️⃣ metadata intact
    for original, new in zip(docs, out):
        assert new.metadata == original.metadata

    # 2️⃣ overlap invariant
    enc = get_encoding(cfg.encoding_name)
    for i in range(1, len(out)):
        tail_text = enc.decode(
            enc.encode(out[i - 1].page_content)[-cfg.chunk_overlap :]
        )
        # Allow an optional leading space that manifests as one extra token
        head_tokens = enc.encode(out[i].page_content)[: cfg.chunk_overlap + 2]
        head_text = enc.decode(head_tokens).lstrip()
        assert head_text.startswith(tail_text.lstrip())
