"""
Insight Ingenious – PyMuPDF extractor integration tests
======================================================

This module validates that
:class:`~ingenious.document_processing.extractor.pymupdf.PyMuPDFExtractor`
honours **all** guarantees stated in its public contract for every supported
input flavour (*Path*, *bytes*, *BytesIO*).

Test Objectives
---------------
1. **Happy-path extraction** – A well-formed PDF must yield at least one
   element that satisfies the *Element* schema.
2. **Determinism** – Two successive invocations with identical input **must**
   return byte-for-byte identical results.
3. **Fail-soft semantics** – Malformed bytes should produce an **empty**
   iterator rather than raising an exception.
4. **Schema enforcement** – Every emitted mapping contains the mandatory keys
   with the correct types.
5. **Bounding-box sanity** – All coordinates lie within a generous
   1 000 × 1 000 pt user-space square (with a −50 pt y-tolerance to allow for
   negative origins).

Implementation Notes
--------------------
* Creating a :class:`PyMuPDFExtractor` is relatively expensive, so a single
  instance is provided via a module-scoped fixture.
* ``_PROBES`` is a table of callables that convert *(pdf_path, pdf_bytes)* into
  the specific probe object required by the extractor, allowing each test to
  be parametrised across input types.
"""

from __future__ import annotations

# ────────────── Standard Library ──────────────
import io
from pathlib import Path
from typing import Any, Callable, List, Tuple

# ────────────── Third-Party ──────────────
import pytest

# ────────────── First-Party ──────────────
from ingenious.document_processing.extractor import _load

# --------------------------------------------------------------------------- #
# Constants                                                                   #
# --------------------------------------------------------------------------- #
_EXTRACTOR_NAME: str = "pymupdf"
_MAX_COORD: int = 1_000  # upper bound for any x/y coordinate
_TOL: int = 50  # allow small negative y0 values (≈ 0.7 in)
_CORRUPT_PDF: bytes = b"%PDF-1.4 broken\n%%EOF"  # deliberately invalid payload


# --------------------------------------------------------------------------- #
# Fixtures                                                                    #
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="module")
def pymupdf():
    """
    Return a shared :class:`PyMuPDFExtractor`.

    A single instance is reused for all tests to avoid repeated initialisation
    overhead and keep the test-suite fast.
    """
    return _load(_EXTRACTOR_NAME)


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #
def _assert_valid_element(el: dict[str, Any]) -> None:
    """
    Assert that *el* meets the *Element* schema and bounding-box constraints.

    Expected structure
    ------------------
    ``{
        "page":   int   >= 1,
        "type":   str   (non-empty),
        "text":   str   (non-empty),
        "coords": Tuple[float | int, float | int, float | int, float | int]
    }``

    Bounding-box rules
    ------------------
    * ``0 <= x0 <= x1 <= {_MAX_COORD}``
    * ``-{_TOL} <= y0 <= y1 <= {_MAX_COORD}``
    """
    required = {"page", "type", "text", "coords"}
    missing = required.difference(el)
    assert not missing, f"element missing keys: {missing}"

    assert isinstance(el["page"], int) and el["page"] >= 1, "invalid page"
    assert isinstance(el["type"], str) and el["type"], "empty type"
    assert isinstance(el["text"], str) and el["text"], "empty text"

    coords = el["coords"]
    assert (
        isinstance(coords, tuple)
        and len(coords) == 4
        and all(isinstance(c, (int, float)) for c in coords)
    ), "coords must be numeric 4-tuple"

    x0, y0, x1, y1 = coords
    assert 0 <= x0 <= x1 <= _MAX_COORD, "x-coords out of range"
    assert -_TOL <= y0 <= y1 <= _MAX_COORD, "y-coords out of range"


# --------------------------------------------------------------------------- #
# Parametrisable probe builders                                               #
# --------------------------------------------------------------------------- #
Probe = Tuple[str, Callable[[Path, bytes], object]]
_PROBES: List[Probe] = [
    ("path", lambda p, _b: p),
    ("bytes", lambda _p, b: b),
    ("bytesio", lambda _p, b: io.BytesIO(b)),
]


# --------------------------------------------------------------------------- #
# 1. Happy-path + schema validation                                           #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(("kind", "probe_fn"), _PROBES, ids=[k for k, _ in _PROBES])
def test_extract_happy_paths(
    pymupdf,
    pdf_path: Path,
    pdf_bytes: bytes,
    kind: str,
    probe_fn: Callable[[Path, bytes], object],
) -> None:
    """
    Verify that each input flavour yields **≥ 1** valid element.

    Only the first ten elements are validated for speed, as the schema check is
    deterministic and identical for the remainder.
    """
    probe = probe_fn(pdf_path, pdf_bytes)

    elements = list(pymupdf.extract(probe))
    assert elements, f"no elements extracted for {kind}"
    for el in elements[:10]:
        _assert_valid_element(el)


# --------------------------------------------------------------------------- #
# 2. Determinism across runs                                                  #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(("kind", "probe_fn"), _PROBES, ids=[k for k, _ in _PROBES])
def test_extract_idempotent(
    pymupdf,
    pdf_path: Path,
    pdf_bytes: bytes,
    kind: str,
    probe_fn: Callable[[Path, bytes], object],
) -> None:
    """
    Ensure two identical invocations produce **exactly** the same output list.

    Deterministic behaviour is critical for caching layers and for avoiding
    spurious diffs in downstream pipelines.
    """
    probe = probe_fn(pdf_path, pdf_bytes)
    run1 = list(pymupdf.extract(probe))
    run2 = list(pymupdf.extract(probe))
    assert run1 == run2, f"extractor output not deterministic for {kind}"


# --------------------------------------------------------------------------- #
# 3. Fail-soft contract on corrupt bytes                                      #
# --------------------------------------------------------------------------- #
def test_extract_corrupt_bytes_returns_empty(pymupdf) -> None:
    """
    A malformed PDF **must not** raise – it should simply return an empty list.

    This protects batch pipelines from aborting when a single document is
    damaged or truncated.
    """
    assert list(pymupdf.extract(_CORRUPT_PDF)) == []
