from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from ingenious.chunk.cli import cli


class _Boom(Exception):
    pass


@patch("ingenious.chunk.strategy.langchain_semantic.OpenAIEmbeddings")
def test_cli_handles_embedding_failure(mock_embed, tmp_path, sample_text):
    stub = MagicMock()
    stub.embed_documents.side_effect = _Boom("rate‑limit")
    mock_embed.return_value = stub

    res = CliRunner().invoke(
        cli,
        [
            "run",
            str(sample_text),
            "--strategy",
            "semantic",
            "--chunk-size",
            "64",
            "--chunk-overlap",
            "8",
            "--output",
            str(tmp_path / "out.jsonl"),
        ],
    )

    assert res.exit_code != 0
    assert "rate‑limit" in res.output.lower()
