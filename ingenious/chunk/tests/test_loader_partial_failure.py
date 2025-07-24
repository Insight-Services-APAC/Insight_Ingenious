"""
Ensure `load_documents` still returns good pages when *some* files fail.
"""
from pathlib import Path

import ingenious.chunk.loader as loader
from ingenious.chunk.loader import load_documents


def test_loader_partial_failure(tmp_path: Path, monkeypatch):
    good = tmp_path / "good.txt"
    good.write_text("hello", encoding="utf-8")

    bad = tmp_path / "bad.pdf"
    bad.write_bytes(b"%PDF-1.4 bad")

    # Simulate partition failure for the PDF
    def _boom(_: Path) -> str:  # noqa: D401
        raise RuntimeError("cannot parse")

    monkeypatch.setattr(loader, "_partition_with_unstructured", _boom)

    docs = load_documents(str(tmp_path))
    assert len(docs) == 1
    assert docs[0].metadata["source"].endswith("good.txt")
