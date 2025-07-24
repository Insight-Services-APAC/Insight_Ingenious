# ingenious/chunk/tests/test_loader_heavy.py
from pathlib import Path
import pytest

import ingenious.chunk.loader as loader


def test_load_pdf_uses_partition(tmp_path, monkeypatch):
    """
    `.pdf` path should invoke the heavyweight _partition_with_unstructured
    helper exactly once and propagate the returned text.
    """
    pdf_file = tmp_path / "doc.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n%Mock PDF\n")

    called = {"times": 0}

    def _fake_partition(p: Path) -> str:  # noqa: D401
        assert p == pdf_file
        called["times"] += 1
        return "EXTRACTED"

    monkeypatch.setattr(loader, "_partition_with_unstructured", _fake_partition)

    docs = loader.load_documents(str(pdf_file))
    assert called["times"] == 1
    assert docs[0].page_content == "EXTRACTED"
    assert docs[0].metadata["source"].endswith("doc.pdf")


def test_loader_skips_corrupt_file(tmp_path, monkeypatch):
    """
    When partitioning fails **and** there are no other valid files, the helper
    must raise FileNotFoundError after logging the warning.
    """
    bad = tmp_path / "bad.pdf"
    bad.write_bytes(b"%PDF bad")

    def _boom(_):
        raise RuntimeError("cannot parse")

    monkeypatch.setattr(loader, "_partition_with_unstructured", _boom)
    with pytest.raises(FileNotFoundError):
        loader.load_documents(str(bad))
