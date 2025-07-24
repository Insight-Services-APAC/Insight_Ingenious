"""
End‑to‑end test: CLI honours --overlap-unit characters.
"""
import jsonlines
from typer.testing import CliRunner

from ingenious.chunk.cli import cli

K = 5  # overlap window


def test_cli_character_overlap(tmp_path):
    # -------------- prepare a tiny text file ---------------------------- #
    text = "abcde " * 40                     # ~240 chars, will give many chunks
    source_file = tmp_path / "document.txt"
    source_file.write_text(text, encoding="utf-8")

    output_file = tmp_path / "out.jsonl"

    # -------------- run CLI -------------------------------------------- #
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "run",
            str(source_file),
            "--strategy",
            "recursive",
            "--chunk-size",
            "25",
            "--chunk-overlap",
            str(K),
            "--overlap-unit",
            "characters",
            "--output",
            str(output_file),
        ],
    )
    assert result.exit_code == 0, result.output
    assert output_file.exists() and output_file.stat().st_size > 0

    # -------------- validate overlap ----------------------------------- #
    with jsonlines.open(output_file) as reader:
        chunks = [obj["text"] for obj in reader]

    assert len(chunks) >= 2  # should have split
    for i in range(1, len(chunks)):
        assert chunks[i - 1][-K:] == chunks[i][:K]
