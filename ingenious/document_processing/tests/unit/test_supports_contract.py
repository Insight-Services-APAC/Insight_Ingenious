"""
Insight Ingenious — *supports* contract test-matrix
===================================================

Every concrete extractor in *Insight Ingenious* must expose a reliable
:meth:`~ingenious.document_processing.extractor.Extractor.supports` method so
that higher-level entry points (e.g. the CLI) can **route inputs to the right
engine without trial-and-error**.  This module defines a *single parametrised
test* that runs the same matrix of probes against **all registered engines**:

================ ================================= ============================
Probe kind       Example                              Expected outcome
================ ================================= ============================
``bytes``        ``b"%PDF-…"``                       ``True`` for **all**
``pdf_path``     ``Path("sample.pdf")``              ``True`` for **all**
``str_path``     ``"sample.pdf"``                    ``True`` for **all**
``url``          ``"http://example.com/a.pdf"``      ``True`` for **all**
``docx``         ``"file.docx"``                     ``True`` *only* for
                                                     the *unstructured* engine
``txt``          ``"file.txt"``                      ``False`` for **all**
================ ================================= ============================

A deviation from this truth-table would either *reject* a valid input
prematurely or *accept* an unsupported one, both of which would surface later
as harder-to-debug failures.

Type aliases
------------
``ProbeBuilder``
    ``Callable[[Path], object]`` – converts the *pdf_path* fixture into the
    probe passed to :pymeth:`Extractor.supports`.

``Expectation``
    Either a boolean literal *or* a predicate ``Callable[[str], bool]`` that
    receives the engine name and returns the expected boolean.
"""

from __future__ import annotations

# ──────────── standard library ────────────
from pathlib import Path
from typing import Callable, List

# ────────────── third-party ──────────────
import pytest

# ─────────────── first-party ───────────────
from ingenious.document_processing.extractor import _ENGINES, _load

# --------------------------------------------------------------------------- #
# constants                                                                   #
# --------------------------------------------------------------------------- #
ENGINES: List[str] = sorted(_ENGINES)  # deterministic order for pytest output

ProbeBuilder = Callable[[Path], object]
Expectation = bool | Callable[[str], bool]


# --------------------------------------------------------------------------- #
# parametrised contract                                                       #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("engine_name", ENGINES, ids=ENGINES)
@pytest.mark.parametrize(
    ("kind", "probe_builder", "expected"),
    [
        ("bytes", lambda pdf: pdf.read_bytes(), True),
        ("pdf_path", lambda pdf: pdf, True),
        ("str_path", lambda pdf: str(pdf), True),
        ("url", lambda pdf: f"http://example.com/{pdf.name}", True),
        (
            "docx",
            lambda _pdf: "file.docx",
            lambda eng: eng == "unstructured",
        ),
        ("txt", lambda _pdf: "file.txt", False),
    ],
    ids=[
        "bytes",
        "pdf-path",
        "str-path",
        "url",
        "docx-probe",
        "txt-probe",
    ],
)
def test_supports_contract(
    engine_name: str,
    kind: str,
    probe_builder: ProbeBuilder,
    expected: Expectation,
    pdf_path: Path,
) -> None:
    """
    Validate that :pymeth:`Extractor.supports` fulfils the contract matrix.

    Workflow
    --------
    1. Load the extractor instance via the private factory :pyfunc:`_load`.
    2. Build the probe using ``probe_builder`` (may depend on *pdf_path*).
    3. Resolve the expected boolean:
       * If *expected* is a **callable**, invoke it with *engine_name*.
       * Otherwise treat *expected* as a literal.
    4. Assert that ``extractor.supports`` returns the resolved value.

    Parameters
    ----------
    engine_name
        Registry key of the extractor under test.
    kind
        Human-readable label for the probe variant (appears in pytest-ids).
    probe_builder
        Callable that converts *pdf_path* into the concrete probe object.
    expected
        Boolean literal or predicate returning the expected outcome.
    pdf_path
        Fixture providing a sample, well-formed PDF on disk.
    """
    extractor = _load(engine_name)
    probe = probe_builder(pdf_path)
    expected_bool = expected(engine_name) if callable(expected) else expected

    assert extractor.supports(probe) is expected_bool, (
        f"{engine_name}.supports({kind}) returned "
        f"{not expected_bool} instead of {expected_bool}"
    )
