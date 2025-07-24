import concurrent.futures
from unittest.mock import patch, MagicMock

from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.factory import build_splitter


def _fake_embedder():
    stub = MagicMock()
    stub.embed_documents.side_effect = lambda txts: [[0.0] * 5 for _ in txts]
    return stub


@patch("ingenious.chunk.strategy.langchain_semantic.OpenAIEmbeddings", return_value=_fake_embedder())
def test_splitters_threadsafe(_):
    def _run(strategy: str):
        cfg = ChunkConfig(strategy=strategy, chunk_size=64, chunk_overlap=8)
        return build_splitter(cfg).split_text("abc " * 100)

    strategies = ["recursive", "markdown", "token", "semantic"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
        results = list(pool.map(_run, strategies * 8))

    assert all(results)  # no crashes, all non‑empty
