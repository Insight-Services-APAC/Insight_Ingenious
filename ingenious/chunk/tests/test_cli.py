# Insight_Ingenious/ingenious/chunk/tests/test_cli.py
from typer.testing import CliRunner
from ingenious.chunk.cli import cli

def test_cli_writes_jsonl(sample_text, tmp_path):
    out_file = tmp_path / "out.jsonl"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "run",
            str(sample_text),
            "--strategy",
            "recursive",
            "--chunk-size",
            "80",
            "--chunk-overlap", 
            "10",
            "--output",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert out_file.exists() and out_file.stat().st_size > 0

def test_cli_ids_unique(sample_text, tmp_path):
    from collections import Counter
    out_file = tmp_path / "out.jsonl"
    runner = CliRunner()
    runner.invoke(
        cli,
        ["run", str(sample_text), "--chunk-size", "80", "--chunk-overlap", "10", "-o", str(out_file)],
        catch_exceptions=False,
    )
    import jsonlines, itertools
    with jsonlines.open(out_file) as reader:
        ids = [rec["id"] for rec in reader]
    assert not any(v > 1 for v in Counter(ids).values()), "Duplicate IDs detected"
