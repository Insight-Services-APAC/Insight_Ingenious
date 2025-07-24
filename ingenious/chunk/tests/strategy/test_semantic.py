"""
Unit-tests for the *semantic* chunking strategy.

• `test_semantic_openai_fallback` – public OpenAI path
• `test_semantic_azure_path`     – Azure OpenAI path
• `test_semantic_overlap_applied`– character-overlap post-processing
"""
from unittest.mock import MagicMock, patch

from langchain_core.documents import Document

from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.factory import build_splitter
from ingenious.chunk.utils.overlap import inject_overlap


# ---------------------------------------------------------------------------
# Common helpers
# ---------------------------------------------------------------------------
def _fake_embedder():
    stub = MagicMock()
    stub.embed_documents.side_effect = lambda texts: [[0.0] * 1536 for _ in texts]
    return stub


# ---------------------------------------------------------------------------
# 1. Public OpenAI fallback
# ---------------------------------------------------------------------------
@patch("ingenious.chunk.strategy.langchain_semantic.OpenAIEmbeddings")
def test_semantic_openai_fallback(mock_openai):
    mock_openai.return_value = _fake_embedder()

    cfg = ChunkConfig(
        strategy="semantic",
        chunk_size=100,
        chunk_overlap=10,
        embed_model="fake-model",
    )
    splitter = build_splitter(cfg)

    chunks = splitter.split_text("Sentence 1. Sentence 2. Sentence 3.")
    assert mock_openai.return_value.embed_documents.called
    assert chunks  # non-empty


# ---------------------------------------------------------------------------
# 2. Azure path
# ---------------------------------------------------------------------------
@patch("ingenious.chunk.strategy.langchain_semantic.AzureOpenAIEmbeddings")
def test_semantic_azure_path(mock_azure):
    mock_azure.return_value = _fake_embedder()

    cfg = ChunkConfig(
        strategy="semantic",
        chunk_size=100,
        chunk_overlap=10,
        embed_model="fake-model",
        azure_openai_deployment="my-deployment",
    )
    splitter = build_splitter(cfg)

    chunks = splitter.split_text("Sentence 1. Sentence 2. Sentence 3.")
    assert mock_azure.return_value.embed_documents.called
    assert chunks  # non-empty


# ---------------------------------------------------------------------------
# 3. Overlap logic
# ---------------------------------------------------------------------------
# We patch *SemanticChunker* with a tiny, deterministic stub so we can
# predict the expected overlap result without invoking heavy ML code.
class _DummySemanticChunker:
    """Splits input into 4-character slices."""

    def __init__(self, *_, **__):
        pass

    def split_documents(self, docs):
        out = []
        for doc in docs:
            txt = doc.page_content
            for i in range(0, len(txt), 4):
                out.append(
                    Document(page_content=txt[i : i + 4], metadata=doc.metadata)
                )
        return out


@patch("ingenious.chunk.strategy.langchain_semantic.SemanticChunker", new=_DummySemanticChunker)
@patch("ingenious.chunk.strategy.langchain_semantic.OpenAIEmbeddings")
def test_semantic_overlap_applied(mock_openai):
    """
    Ensure that every chunk **contains** the correct number of overlapping
    characters from its neighbours.
    """
    mock_openai.return_value = _fake_embedder()

    cfg = ChunkConfig(strategy="semantic", chunk_size=4, chunk_overlap=2)
    splitter = build_splitter(cfg)

    text = "ABCDEFGHIJKLMNOP"
    actual = splitter.split_text(text)

    # Build the expected output via the shared overlap helper.
    base_chunks = _DummySemanticChunker().split_documents(
        [Document(page_content=text)]
    )
    
    expected = [
        c.page_content
        for c in inject_overlap(base_chunks, cfg.chunk_overlap,
                                unit="tokens", enc_name=cfg.encoding_name)
    ]

    assert actual == expected
