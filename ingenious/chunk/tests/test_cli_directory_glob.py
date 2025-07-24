"""
End‑to‑end CLI test covering directory recursion *and* glob patterns.
"""
import jsonlines
from typer.testing import CliRunner

from ingenious.chunk.cli import cli


def test_cli_directory_and_glob(tmp_path):
    data_dir = tmp_path / "docs"
    data_dir.mkdir()
    for i in range(3):
        (data_dir / f"{i}.txt").write_text(str(i), encoding="utf-8")

    out_file = tmp_path / "out.jsonl"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "run",
            f"{data_dir}/**/*.txt",   # glob retained (no shell expansion)
            "--chunk-size",
            "10",
            "--chunk-overlap",
            "2",
            "--output",
            str(out_file),
        ],
    )

    assert result.exit_code == 0, result.output
    with jsonlines.open(out_file) as rdr:
        stripped = {rec["text"].strip() for rec in rdr}
        assert stripped == {"0", "1", "2"}
