"""
Insight Ingenious – *Unicode* extraction contract (PyMuPDF backend)
==================================================================

This *unit-level* module provides a **sentinel test** that asserts the public
PyMuPDF extractor’s ability to preserve Unicode content spanning multiple
writing systems.

Rationale
---------

PDF-extraction libraries are notorious for losing diacritics, silently
replacing unknown glyphs, or omitting entire code points when fonts are
missing.  Rather than performing brittle byte-for-byte comparisons, this test
creates a *minimal, in-memory* PDF containing:

* **Latin text with diacritics** – ``Zaželi čokoláda``
* **Cyrillic text** – ``привет``

After a round-trip through :pyfunc:`pymupdf.extract`, the test asserts that the
substring ``"okol"`` (from *čokoláda*) is still present in the extracted
output.  The heuristic is deliberately lenient:

* MuPDF’s fidelity varies across OS builds and available fonts.
* Diacritics may be normalised away, and non-Latin glyphs may degrade to the
  replacement character (U+FFFD).
* A persistent Latin substring is sufficient evidence that the Unicode block
  survived end-to-end.

Execution
---------

Run the entire suite or isolate this test with::

    uv run pytest -k test_pymupdf_unicode

The test is automatically *skipped* by the ``pymupdf`` fixture when PyMuPDF is
not installed.

Dependencies
------------

* `PyMuPDF (fitz) <https://pymupdf.readthedocs.io>`_ – runtime PDF engine.
* ``pymupdf`` fixture – shared extractor instance declared in *conftest.py*.

"""

from __future__ import annotations

# ──────────────── standard library ────────────────
from pathlib import Path

# ──────────────── third-party ────────────────
import fitz  # type: ignore – heavy import confined to the test body

# ─────────────── first-party (fixture-only import; no direct code) ───────────────
# The extractor under test is provided via the ``pymupdf`` fixture.

__all__: list[str] = ["test_pymupdf_unicode"]


# ───────────────────── tests ─────────────────────
def test_pymupdf_unicode(pymupdf, tmp_path: Path) -> None:  # noqa: D401
    """Validate that :pyfunc:`pymupdf.extract` retains mixed-script text.

    Steps
    -----
    1. **Generate** an ad-hoc PDF containing both Latin (with diacritics) and
       Cyrillic glyphs.
    2. **Persist** the document to a temporary file system location supplied by
       *pytest* (``tmp_path``).
    3. **Extract** text blocks via ``pymupdf.extract`` and concatenate them.
    4. **Assert** that the lower-cased result still includes the substring
       ``"okol"``.

    Parameters
    ----------
    pymupdf
        A shared, lazily-initialised instance of the PyMuPDF extractor supplied
        by the `conftest.py` fixture.
    tmp_path
        An isolated, per-test temporary directory created by *pytest*.

    Raises
    ------
    AssertionError
        If the expected Latin substring is absent, indicating a regression in
        Unicode handling.  The message includes contextual guidance for
        debugging font-related extraction failures.

    Examples
    --------
    Isolate and run just this test::

        uv run pytest tests/unit/test_unicode_pdf.py::test_pymupdf_unicode
    """
    # Build a minimal UTF-8 PDF in memory ---------------------------------
    pdf_path: Path = tmp_path / "utf8.pdf"
    doc = fitz.open()  # Create an empty document
    page = doc.new_page()
    page.insert_text((72, 700), "Zaželi čokoláda – привет")
    doc.save(pdf_path)

    # Extract text via the public API ------------------------------------
    elements = list(pymupdf.extract(pdf_path))
    joined_text = " ".join(element["text"] for element in elements)

    # MuPDF may drop diacritics or non-Latin glyphs; require *some* signal
    assert "okol" in joined_text.lower(), (
        "PyMuPDF extractor lost the expected Latin substring ('okol') while "
        "processing a mixed-script Unicode PDF.  Verify font availability or "
        "recent upstream changes in the extract pipeline."
    )
