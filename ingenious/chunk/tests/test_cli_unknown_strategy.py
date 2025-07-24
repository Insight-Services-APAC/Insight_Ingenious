from typer.testing import CliRunner
from ingenious.chunk.cli import cli


def test_cli_unknown_strategy(tmp_path):
    src = tmp_path / "doc.txt"
    src.write_text("oops")

    result = CliRunner().invoke(
        cli,
        ["run", str(src), "--strategy", "does-not-exist"],
    )

    assert result.exit_code != 0
    # Validation error from Pydantic must surface
    assert result.exception is not None
