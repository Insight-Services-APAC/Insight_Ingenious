# ingenious/chunk/tests/test_cli_failures.py
from typer.testing import CliRunner
from pydantic import ValidationError

from ingenious.chunk.cli import cli


def test_cli_invalid_overlap(tmp_path):
    """CLI should fail fast when chunk_overlap == chunk_size (invalid)."""
    src = tmp_path / "doc.txt"
    src.write_text("hello")

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["run", str(src), "--chunk-size", "10", "--chunk-overlap", "10"],
        catch_exceptions=True,
    )

    # --- assertions ---------------------------------------------------- #
    assert result.exit_code != 0
    # Typer wraps the raised ValidationError into Result.exception
    assert isinstance(result.exception, ValidationError)
