"""
Hypothesis: mixed directory trees (valid TXT/MD, invalid PDFs) should
yield documents only for the *non‑blank* valid files, with no unhandled
exceptions.  Both loader output and reference text are LF‑normalised.
"""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4
from typing import List

from hypothesis import given, strategies as st, settings, HealthCheck, assume

from ingenious.chunk.loader import load_documents
import ingenious.chunk.loader as loader


def _norm(s: str) -> str:
    """Convert CR/LF variants → LF so comparisons are portable."""
    return s.replace("\r\n", "\n").replace("\r", "\n")


@settings(
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    max_examples=40,
)
@given(
    texts=st.lists(
        st.text(min_size=1, max_size=50),
        min_size=1,
        max_size=6,
    ),
    bad_pdfs=st.integers(min_value=0, max_value=3),
    use_glob=st.booleans(),
)
def test_loader_mixed_formats(
    tmp_path,
    monkeypatch,
    texts: List[str],
    bad_pdfs: int,
    use_glob: bool,
):
    # ───────── filter out whitespace‑only strings ───────── #
    valid_texts = [t for t in texts if not t.isspace()]
    assume(valid_texts)  # Hypothesis: skip examples with no real text

    # Each example gets its own isolated working dir
    work_dir = tmp_path / str(uuid4())
    work_dir.mkdir(parents=True)

    # ------------------ create valid TXT / MD ---------------- #
    for idx, content in enumerate(valid_texts):
        ext = ".md" if idx % 2 else ".txt"
        (work_dir / f"good_{idx}{ext}").write_text(content, encoding="utf-8")

    # ------------------ create *invalid* heavy PDFs ----------- #
    for j in range(bad_pdfs):
        (work_dir / f"bad_{j}.pdf").write_bytes(b"%PDF-1.4 bad")

    # Heavy‑format parser always explodes → exercises skip‑logic
    def _boom(_: Path) -> str:  # noqa: D401
        raise RuntimeError("cannot parse")

    monkeypatch.setattr(loader, "_partition_with_unstructured", _boom)

    pattern = str(work_dir / "**/*") if use_glob else str(work_dir)
    docs = load_documents(pattern)

    # ---- compare LF‑normalised content only for valid files ---- #
    expected = {_norm(t) for t in valid_texts}
    actual = {_norm(d.page_content) for d in docs}

    assert actual == expected
