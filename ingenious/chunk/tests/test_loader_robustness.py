# tests/test_loader_robustness.py
import os
import pytest
import stat
from pathlib import Path

from ingenious.chunk.loader import load_documents


def test_loader_skips_unreadable(tmp_path):
    unreadable = tmp_path / "secret.txt"
    unreadable.write_text("top‑secret", encoding="utf-8")
    unreadable.chmod(0)           # remove all perms

    readable = tmp_path / "ok.txt"
    readable.write_text("hello", encoding="utf-8")

    # ensure we restore permissions afterwards for CI clean‑up
    try:
        docs = load_documents(str(tmp_path))
        assert len(docs) == 1
        assert docs[0].page_content == "hello"
    finally:
        unreadable.chmod(stat.S_IWUSR | stat.S_IRUSR)


def test_loader_exotic_glob(tmp_path):
    for name in ["α.txt", "β.txt", "γ.md"]:
        (tmp_path / name).write_text(name, encoding="utf-8")

    docs = load_documents(str(tmp_path / "[αβ]*.txt"))
    assert {d.page_content for d in docs} == {"α.txt", "β.txt"}
