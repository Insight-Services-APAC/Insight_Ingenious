# ingenious/chunk/tests/test_cli_writer_failure.py
from unittest.mock import patch, MagicMock
import jsonlines
from typer.testing import CliRunner
from ingenious.chunk.cli import cli


def test_cli_write_failure(monkeypatch, sample_text, tmp_path):
    """Simulate disk‑write OSError → CLI must exit 1 with friendly message."""
    def _boom(*_, **__):
        raise OSError("disk full")

    monkeypatch.setattr(jsonlines, "open", _boom)
    result = CliRunner().invoke(
        cli,
        [
            "run",
            str(sample_text),
            "--chunk-size",
            "64",
            "--chunk-overlap",
            "8",
            "--output",
            str(tmp_path / "out.jsonl"),
        ],
    )

    assert result.exit_code == 1
    assert "disk full" in result.output.lower()
    assert "❌" in result.output  # coloured error prefix
