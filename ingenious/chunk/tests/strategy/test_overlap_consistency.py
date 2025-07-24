# ingenious/chunk/tests/strategy/test_overlap_consistency.py
import pytest
from tiktoken import get_encoding

from unittest.mock import patch, MagicMock
from ingenious.chunk.config import ChunkConfig
from ingenious.chunk.factory import build_splitter
_fake_embed = MagicMock()
_fake_embed.embed_documents.side_effect = lambda texts: [[0.0] * 5 for _ in texts]

@patch("ingenious.chunk.strategy.langchain_semantic.OpenAIEmbeddings", return_value=_fake_embed)
@pytest.mark.parametrize("strategy", ["recursive", "markdown", "token", "semantic"])
def test_token_overlap_consistency(_, strategy):
    cfg = ChunkConfig(
        strategy=strategy,
        chunk_size=20,
        chunk_overlap=5,
        overlap_unit="tokens",
    )
    splitter = build_splitter(cfg)

    text = "foo bar baz qux " * 20
    chunks = splitter.split_text(text)

    enc = get_encoding(cfg.encoding_name)
    for i in range(1, len(chunks)):
        prev_tail = enc.encode(chunks[i - 1])[-5:]
        curr_head = enc.encode(chunks[i])[:5]
        assert prev_tail == curr_head
