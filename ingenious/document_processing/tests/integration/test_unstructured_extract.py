"""
Insight Ingenious – *UnstructuredExtractor* integration tests
============================================================

A concise, high‑value regression suite for
:class:`~ingenious.document_processing.extractor.unstructured.UnstructuredExtractor`.

Why these tests exist
---------------------
The *UnstructuredExtractor* sits on the critical path of several
human‑in‑the‑loop and batch pipelines. A silent failure would stall document
flows across the organisation.  This suite therefore verifies the public
**behavioural contract** – not implementation details – so refactors remain
safe:

1. **Happy‑path extraction** – every accepted input flavour (`Path`, `bytes`,
   `BytesIO`) must yield at least one mapping that conforms to the public
   *Element* schema.
2. **Determinism** – extraction is a pure function of its input; two successive
   calls on identical data must produce byte‑identical output.
3. **Fail‑soft semantics** – invalid or unsupported data must *never* raise;
   the extractor returns an empty iterator so upstream pipelines continue
   uninterrupted.
4. **Coordinate serialisation** – :py:meth:`_coords_to_jsonable` converts
   vendor‑specific coordinate containers into JSON‑serialisable primitives.
5. **Suffix gate‑keeping** – :py:meth:`supports` only accepts documented file
   extensions and gracefully rejects everything else.

The checks remain intentionally lightweight to keep CI fast while still
catching high‑impact regressions.
"""

from __future__ import annotations

# ────────────── standard library ──────────────
import io
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Final, Iterable, Tuple

# ────────────── third‑party ──────────────
import pytest

# ────────────── first‑party ──────────────
from ingenious.document_processing.extractor import _load

# --------------------------------------------------------------------------- #
# constants                                                                   #
# --------------------------------------------------------------------------- #
_EXTRACTOR_NAME: Final[str] = "unstructured"
# Minimal but invalid PDF payload – useful for fail‑soft testing
_CORRUPT_PDF: Final[bytes] = b"%PDF-1.7 broken\n%%EOF"

# Block types that MUST carry text content
_TEXT_REQUIRED: Final[set[str]] = {
    "narrativetext",
    "paragraph",
    "title",
    "head",
}

# Probe matrix: (human‑readable id, fixture name, requires python‑pptx?)
_PROBES: Final[Iterable[Tuple[str, str, bool]]] = [
    ("pdf-path", "sample_pdf_path", False),
    ("pdf-bytes", "sample_pdf_bytes", False),
    ("pdf-bytesio", "sample_pdf_bytes", False),
    ("docx-path", "sample_docx_path", False),
    ("docx-bytes", "sample_docx_bytes", False),
    ("pptx-path", "pptx_path", True),
    ("pptx-bytes", "pptx_bytes", True),
]

# --------------------------------------------------------------------------- #
# helper assertions                                                           #
# --------------------------------------------------------------------------- #


def _assert_valid_element(element: dict[str, Any]) -> None:
    """Assert that *element* minimally satisfies the public *Element* contract.

    Only those schema fields consumed by downstream components are validated
    here; deeper structural checks belong in the extractor‑specific unit
    tests.
    """
    page = element["page"]
    assert page is None or (isinstance(page, int) and page >= 1), (
        "`page` must be ≥ 1 or None"
    )

    el_type = element["type"]
    assert isinstance(el_type, str) and el_type, "`type` must be a non‑empty str"

    text = element["text"]
    assert isinstance(text, str), "`text` must be str"

    # Narrative‑style blocks require non‑empty text content
    if el_type.lower() in _TEXT_REQUIRED:
        assert text, "`text` required for narrative element"


# --------------------------------------------------------------------------- #
# fixtures                                                                    #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def ux(unstructured_available: bool):
    """Provide a singleton :class:`UnstructuredExtractor` instance.

    The fixture is module‑scoped to avoid paying the relatively expensive
    import‑and‑initialisation cost on every test case. If the external
    *unstructured* dependency is missing the entire module is skipped.
    """
    if not unstructured_available:
        pytest.skip("unstructured not installed")
    return _load(_EXTRACTOR_NAME)


@pytest.fixture
def src(request):  # noqa: D401 – simple fixture wrapper
    """Resolve the indirect *src* fixture used by parametrised probes.

    `pytest.mark.parametrize` sets *request.param* to the name of the fixture
    that should supply the actual source object; this helper performs that
    lookup.
    """
    return request.getfixturevalue(request.param)


# --------------------------------------------------------------------------- #
# 1. Happy‑path extraction + determinism                                      #
# --------------------------------------------------------------------------- #


@pytest.mark.integration
@pytest.mark.parametrize(
    ("label", "fixture_name", "needs_pptx"), _PROBES, ids=[lbl for lbl, *_ in _PROBES]
)
def test_extract_happy_and_deterministic(
    label: str,
    fixture_name: str,
    needs_pptx: bool,
    ux,  # extractor fixture
    pptx_available: bool,
    request: pytest.FixtureRequest,
) -> None:
    """Verify happy‑path extraction and determinism for a given *probe*.

    Smoke‑tests that the extractor:
    * Produces at least one valid *Element* mapping for the input.
    * Returns byte‑identical output on consecutive runs (pure function).
    """
    if needs_pptx and not pptx_available:
        pytest.skip("python-pptx not installed")

    probe = request.getfixturevalue(fixture_name)

    # Convert bytes → BytesIO when explicitly requested by the probe label
    if label.endswith("bytesio"):
        probe = io.BytesIO(probe)  # type: ignore[arg-type]

    first_run = list(ux.extract(probe))
    assert first_run, f"extractor returned 0 elements for {label}"
    for element in first_run[:10]:  # light spot‑check
        _assert_valid_element(element)

    # Determinism check – second extraction must match exactly
    second_run = list(ux.extract(probe))
    assert first_run == second_run, f"non‑deterministic output for {label}"


# --------------------------------------------------------------------------- #
# 2. Fail‑soft behaviour on corrupt bytes                                     #
# --------------------------------------------------------------------------- #


def test_extract_corrupt_bytes_returns_empty(ux) -> None:
    """Invalid PDF bytes must yield an empty iterator and raise **no** exceptions."""
    assert list(ux.extract(_CORRUPT_PDF)) == []


# --------------------------------------------------------------------------- #
# 3. _coords_to_jsonable coverage                                             #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "coords, expected",
    [
        (None, None),
        (
            SimpleNamespace(
                points=[SimpleNamespace(x=1, y=2), SimpleNamespace(x=3, y=4)]
            ),
            [(1, 2), (3, 4)],
        ),
        (type("C", (), {"to_dict": lambda self: {"k": 1}})(), {"k": 1}),
        (type("W", (), {"__str__": lambda self: "weird"})(), "weird"),
    ],
    ids=["None", "points", "to_dict", "fallback"],
)
def test_coords_to_jsonable_paths(ux, coords: Any, expected: Any) -> None:
    """Ensure *_coords_to_jsonable* normalises every coordinate shape."""
    assert ux._coords_to_jsonable(coords) == expected  # type: ignore[attr-defined]


# --------------------------------------------------------------------------- #
# 4. supports truth‑table                                                     #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "suffix, supported",
    [(".pdf", True), (".docx", True), (".pptx", True), (".foo", False)],
)
def test_supports_suffix_probe(
    tmp_path: Path, ux, suffix: str, supported: bool
) -> None:
    """Truth‑table for :py:meth:`supports` across common and unknown suffixes."""
    dummy = tmp_path / f"sample{suffix}"
    dummy.write_bytes(b"x")

    # Path‑like and str inputs must behave identically
    assert ux.supports(dummy) is supported
    assert ux.supports(str(dummy)) is supported


# --------------------------------------------------------------------------- #
# 5. extract rejects unknown suffix                                           #
# --------------------------------------------------------------------------- #


def test_extract_rejects_unknown_suffix(tmp_path: Path, ux) -> None:
    """Unsupported formats must be skipped **gracefully**.

    Behaviour
    ---------
    * ``supports`` returns ``False``.
    * ``extract`` yields an empty iterator (converted to ``[]``).
    """
    dummy = tmp_path / "sample.foo"
    dummy.write_text("irrelevant")

    assert not ux.supports(dummy)
    assert list(ux.extract(dummy)) == []
