from pathlib import Path
from unittest.mock import patch, MagicMock
from tiktoken import get_encoding

import jsonlines
from typer.testing import CliRunner

from ingenious.chunk.cli import cli

STRATEGIES = ["recursive", "markdown", "token", "semantic"]


def _fake_embedder():
    stub = MagicMock()
    stub.embed_documents.side_effect = lambda texts: [[0.0] * 5 for _ in texts]
    return stub


def _run_cli(tmp_path: Path, strategy: str):
    src = tmp_path / "doc.txt"
    src.write_text("hello world " * 60, encoding="utf-8")
    out = tmp_path / f"out_{strategy}.jsonl"

    with patch(
        "ingenious.chunk.strategy.langchain_semantic.OpenAIEmbeddings",
        return_value=_fake_embedder(),
    ), patch(
        "ingenious.chunk.strategy.langchain_semantic.AzureOpenAIEmbeddings",
        return_value=_fake_embedder(),
    ):
        result = CliRunner().invoke(
            cli,
            [
                "run",
                str(src),
                "--strategy",
                strategy,
                "--chunk-size",
                "64",
                "--chunk-overlap",
                "8",
                "--output",
                str(out),
            ],
            catch_exceptions=False,
        )

    assert result.exit_code == 0, result.output
    with jsonlines.open(out) as rdr:
        chunks = [rec["text"] for rec in rdr]
    # --- invariant: last k tokens of chunk[i‑1] == first k tokens of chunk[i]
    enc = get_encoding("cl100k_base")
    k = 8
    for i in range(1, len(chunks)):
        tail_text = enc.decode(enc.encode(chunks[i - 1])[-k:])
        # allow one extra leading‑space token in the head (same pattern as other tests)
        head_text = chunks[i][: len(tail_text) + 2]
        assert head_text.lstrip().startswith(tail_text.lstrip())

def test_cli_all_strategies(tmp_path):
    for s in STRATEGIES:
        _run_cli(tmp_path, s)
