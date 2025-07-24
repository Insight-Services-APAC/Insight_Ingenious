from unittest.mock import patch, MagicMock

from typer.testing import CliRunner

from ingenious.chunk.cli import cli


def _fake_embedder():
    stub = MagicMock()
    stub.embed_documents.side_effect = lambda texts: [[0.0] * 8 for _ in texts]
    return stub


@patch(
    "ingenious.chunk.strategy.langchain_semantic.AzureOpenAIEmbeddings",
    return_value=_fake_embedder(),
)
def test_cli_semantic_azure(mock_azure, sample_text, tmp_path):
    """
    End-to-end smoke test: CLI honours --azure-deployment wiring and writes JSONL.
    """
    out_file = tmp_path / "out.jsonl"
    runner = CliRunner()

    result = runner.invoke(
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
            "--azure-deployment",
            "my-dep",
            "--output",
            str(out_file),
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0, result.output
    assert out_file.exists() and out_file.stat().st_size > 0
    # Fake embedder should have been used
    assert mock_azure.return_value.embed_documents.called
