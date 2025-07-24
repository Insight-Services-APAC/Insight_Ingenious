# ingenious/chunk/tests/test_cli_custom_separators.py
from pathlib import Path
from typer.testing import CliRunner
import jsonlines

from ingenious.chunk.cli import cli

def test_cli_respects_custom_separator(tmp_path: Path):
    text = "A---B---C---D---E"
    src = tmp_path / "src.txt"
    src.write_text(text)

    out_file = tmp_path / "out.jsonl"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "run",
            str(src),
            "--strategy",      "recursive",
            "--chunk-size",    "4",          # small char budget
            "--chunk-overlap", "0",
            "--overlap-unit",  "characters",
            "--separators",    "---",
            "--output",        str(out_file),
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0

    with jsonlines.open(out_file) as rdr:
        chunks = [rec["text"] for rec in rdr]

    # Expect exactly 5 chunks: A, B, C, D, E
    assert [c.strip("-") for c in chunks] == ["A", "B", "C", "D", "E"]
