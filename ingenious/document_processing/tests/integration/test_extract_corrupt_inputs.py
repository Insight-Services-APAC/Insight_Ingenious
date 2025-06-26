"""
Insight Ingenious – Extraction-layer Resilience Tests
====================================================

This integration suite deliberately feeds **corrupted byte streams** to the
public helper :pyfunc:`ingenious.document_processing.extractor.extract` and
asserts that each registered extractor honours its **documented failure
contract**.

Behavioural contracts
---------------------
1. **Fail-soft engines**
   Engines listed in :pydata:`LOSSLESS_ENGINES` must *never* raise on malformed
   input.  Instead, they return an **empty iterator** (no parsed blocks).

2. **Strict engines**
   The ``unstructured`` backend is *expected* to propagate the underlying
   parser error (usually ``pdf2image.PDFPageCountError``).  A probe marked
   ``xfail`` ensures that any silent change to this contract is surfaced as a
   regression.

Design choices
--------------
* A *synthetic* two-line PDF stub is embedded via a fixture so that the tests
  remain self-contained – no external sample files are required.
* Contracts are expressed declaratively:
  – An empty list for fail-soft engines.
  – An ``xfail`` marker for the strict engine.

Running the tests
-----------------
Simply execute

.. code-block:: bash

   uv run pytest -k corrupt_inputs

from the project root.
"""

from __future__ import annotations

# ──────────── standard library ────────────
from typing import Final

# ──────────── third-party ────────────
import pytest

# ──────────── first-party ────────────
from ingenious.document_processing.extractor import _ENGINES, extract

# --------------------------------------------------------------------------- #
# fixtures                                                                    #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="function")
def corrupt_pdf_bytes() -> bytes:
    """
    Return a minimal yet *invalid* PDF byte payload.

    The in-memory bytes consist of
    - a dummy header matching the pattern ``%PDF-1.7`` and
    - an immediate ``%%EOF`` marker.

    Any standards-compliant PDF parser must reject this sequence, making it
    ideal for negative-path testing.

    Returns
    -------
    bytes
        Hard-coded malformed PDF data.
    """
    return b"%PDF-1.7 corrupted\n%%EOF"


# --------------------------------------------------------------------------- #
# engines that *guarantee* “empty list, no exception” on corrupt input        #
# --------------------------------------------------------------------------- #

LOSSLESS_ENGINES: Final[list[str]] = [
    engine for engine in _ENGINES if engine != "unstructured"
]
"""
Extractor names that implement the **fail-soft** contract:

*Corrupted payload ➜ empty iterator (no exception raised).*
"""


@pytest.mark.parametrize("engine", LOSSLESS_ENGINES)
def test_extract_corrupt_bytes_returns_empty(
    engine: str,
    corrupt_pdf_bytes: bytes,
) -> None:
    """
    Ensure fail-soft engines degrade gracefully on malformed input.

    Parameters
    ----------
    engine
        The extractor under test.  Populated automatically by *pytest* via
        ``@pytest.mark.parametrize``.
    corrupt_pdf_bytes
        Invalid PDF data supplied by the *corrupt_pdf_bytes* fixture.

    Expectations
    ------------
    The call to :pyfunc:`extract` must **not** raise and must yield **zero**
    blocks.
    """
    assert list(extract(corrupt_pdf_bytes, engine=engine)) == []


# --------------------------------------------------------------------------- #
# “unstructured” follows a strict contract: it escalates the upstream error   #
# --------------------------------------------------------------------------- #


@pytest.mark.xfail(
    reason=(
        "The unstructured backend pipelines bytes through pdf2image, which "
        "raises pdf2image.PDFPageCountError when the payload is invalid."
    ),
    raises=Exception,
)
def test_unstructured_corrupt_bytes_raises(corrupt_pdf_bytes: bytes) -> None:
    """
    Verify that *unstructured* propagates the parser-level exception.

    The **xfail** marker flips the test outcome semantics:
    raising an exception is considered a **success** for this probe, whereas
    silent acceptance would flag a regression.
    """
    extract(corrupt_pdf_bytes, engine="unstructured")
