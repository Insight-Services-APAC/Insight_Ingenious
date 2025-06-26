# tests/test_extractors_url_roundtrip.py
"""
Sanity-check: every Insight Ingenious extractor should be able
to take an HTTP/S URL and yield ≥ 1 Element.

Engines currently covered
-------------------------
* pdfminer      – already URL-aware
* pymupdf       – expected to **fail** until URL fetch logic is added
* unstructured  – expected to **fail** until URL fetch logic is added
* azdocint      – requires valid Azure credentials (skips otherwise)

To run:
    pytest -q tests/test_extractors_url_roundtrip.py
"""

from __future__ import annotations

import os
from typing import Final

import pytest

from ingenious.document_processing.extractor import extract

# --------------------------------------------------------------------------- #
# constants & helpers                                                         #
# --------------------------------------------------------------------------- #

PDF_URL: Final[str] = (
    "https://densebreast-info.org/wp-content/uploads/2024/06/"
    "Patient-Fact-Sheet-English061224.pdf"
)

ENGINES: Final[list[str]] = ["pdfminer", "pymupdf", "unstructured", "azdocint"]


def _has_azure_creds() -> bool:
    """Return True when both endpoint & key are present in the env."""
    return bool(
        os.getenv("AZURE_DOC_INTEL_ENDPOINT")
        or os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    ) and bool(
        os.getenv("AZURE_DOC_INTEL_KEY") or os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
    )


# --------------------------------------------------------------------------- #
# parameterised smoke test                                                    #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("engine", ENGINES)
def test_url_roundtrip(engine: str) -> None:
    """
    Assert that *engine* yields at least one Element from the remote PDF.

    The check is deliberately coarse—this is a routing/IO test, not content QA.
    """
    if engine == "azdocint" and not _has_azure_creds():
        pytest.skip("Azure credentials not configured; skipping azdocint URL test")

    try:
        blocks = list(extract(PDF_URL, engine=engine))
    except Exception as exc:
        pytest.fail(f"{engine} raised an exception on URL input: {exc!r}")

    assert blocks, f"{engine} produced no output for {PDF_URL!s}"
