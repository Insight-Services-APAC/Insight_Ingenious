# tests/test_cli_global_id_uniqueness.py
from collections import Counter
import jsonlines
from typer.testing import CliRunner
from ingenious.chunk.cli import cli


def test_cli_ids_globally_unique(tmp_path):
    # two files with identical content
    for n in (1, 2):
        (tmp_path / f"{n}.txt").write_text("repeat me", encoding="utf-8")

    out_file = tmp_path / "out.jsonl"
    res = CliRunner().invoke(
        cli,
        [
            "run",
            str(tmp_path),
            "--chunk-size",
            "32",
            "--chunk-overlap",
            "8",
            "--output",
            str(out_file),
        ],
        catch_exceptions=False,
    )
    assert res.exit_code == 0, res.output

    with jsonlines.open(out_file) as rdr:
        ids = [rec["id"] for rec in rdr]

    duplicates = [c for c, v in Counter(ids).items() if v > 1]
    assert not duplicates, f"duplicate IDs: {duplicates}"