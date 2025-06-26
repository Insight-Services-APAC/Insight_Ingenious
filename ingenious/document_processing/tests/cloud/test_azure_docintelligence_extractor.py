"""
Insight Ingenious – Integration tests for AzureDocIntelligenceExtractor
=====================================================================

End‑to‑end ("live") tests that call Azure AI *prebuilt‑document* through the
:class:`~ingenious.document_processing.extractor.azure_doc_intelligence.
AzureDocIntelligenceExtractor` wrapper.

The suite is **skipped automatically** unless *both* conditions hold:

1.  Valid Azure credentials are detected via environment variables – either
    ``AZURE_DOC_INTEL_ENDPOINT``/``AZURE_DOC_INTEL_KEY`` **or**
    ``AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT``/``AZURE_DOCUMENT_INTELLIGENCE_KEY``.
2.  The sample assets exist under
    ``tests/integration/data_azure_doc_intell/``.

Goals
-----
* **Fail‑soft** – missing credentials or assets never raise, they *skip* or
  return an empty iterator.
* **Determinism** – identical input ⇒ identical (byte‑for‑byte) output.
* **Efficiency** – authentication is performed once per test module via a
  scoped fixture.
"""

from __future__ import annotations

import contextlib
import os
from pathlib import Path
from typing import Any, Iterator, List

import pytest

from ingenious.document_processing.extractor import _load

# --------------------------------------------------------------------------- #
# Constants                                                                   #
# --------------------------------------------------------------------------- #

TEST_DATA_DIR: Path = Path(__file__).parent / "data_azure_doc_intell"
SAMPLE_FILES: tuple[str, ...] = (
    "sample.pdf",
    "sample.png",
    "sample.jpg",
    "sample.tiff",
)

# --------------------------------------------------------------------------- #
# Fixtures                                                                    #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def azdocint():
    """Return a single, lazily‑instantiated extractor for the entire module.

    Azure authentication can be an expensive network round‑trip; holding a
    *module‑scoped* instance prevents redundant handshakes in each test case.
    """

    return _load("azdocint")


@pytest.fixture()
def dummy_foo(tmp_path: Path) -> Path:
    """Generate a temporary file with an unsupported ``.foo`` extension.

    The file contents are irrelevant – only the *extension* is used to verify
    that the extractor politely rejects unknown formats without raising.
    """

    path = tmp_path / "dummy.foo"
    path.write_text("irrelevant", encoding="utf-8")
    return path


# --------------------------------------------------------------------------- #
# Helper utilities                                                            #
# --------------------------------------------------------------------------- #


def _has_credentials() -> bool:
    """Return ``True`` when *both* an endpoint **and** a key variable exist.

    The helper checks the two historical variable pairs so local setups using
    either naming convention are supported transparently.
    """

    endpoint_vars = (
        "AZURE_DOC_INTEL_ENDPOINT",
        "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT",
    )
    key_vars = (
        "AZURE_DOC_INTEL_KEY",
        "AZURE_DOCUMENT_INTELLIGENCE_KEY",
    )

    return any(os.getenv(var) for var in endpoint_vars) and any(
        os.getenv(var) for var in key_vars
    )


def _skip_if_invalid(sample: Path) -> None:
    """Skip the *calling* test when credentials or the sample asset are absent.

    Parameters
    ----------
    sample:
        Path to the sample file a test wishes to exercise.  When the required
        pre‑conditions are not satisfied, :pydata:`pytest.skip` is invoked so
        the overall suite still passes without error.
    """

    if not _has_credentials():
        pytest.skip("Azure credentials are not configured")
    if not sample.exists():
        pytest.skip(f"Test asset not found: {sample}")


@contextlib.contextmanager
def _temporarily_clear_credentials() -> Iterator[None]:
    """Context‑manager that removes Azure credential variables *temporarily*.

    All environment variables starting with ``AZURE_DOC_`` or
    ``AZURE_DOCUMENT_INTELLIGENCE_`` are popped for the duration of the context
    in order to validate *fail‑soft* behaviour.  Originals are restored
    afterwards so subsequent tests remain unaffected.
    """

    prefixes = (
        "AZURE_DOC_",
        "AZURE_DOCUMENT_INTELLIGENCE_",
    )
    saved: dict[str, str] = {
        k: os.environ.pop(k) for k in list(os.environ) if k.startswith(prefixes)
    }
    try:
        yield
    finally:
        os.environ.update(saved)


def _collect_elements(extractor: Any, path: Path) -> List[dict[str, Any]]:
    """Eagerly exhaust the extractor’s lazy generator and return a list.

    The helper guarantees a *fully‑materialised* structure so that equality
    comparisons are reliable during determinism checks.

    Parameters
    ----------
    extractor:
        An instance providing an ``extract(Path) -> Iterator[dict]`` interface.
    path:
        Path to the input document to be processed.
    """

    return list(extractor.extract(path))


# --------------------------------------------------------------------------- #
# Happy‑path tests                                                            #
# --------------------------------------------------------------------------- #


@pytest.mark.integration
@pytest.mark.parametrize("sample_name", SAMPLE_FILES)
def test_extract_document_smoke(azdocint, sample_name: str) -> None:
    """Smoke‑test: every sample yields ≥1 non‑table element with page & text."""

    sample = TEST_DATA_DIR / sample_name
    _skip_if_invalid(sample)

    elems = _collect_elements(azdocint, sample)
    assert elems, "0 elements returned"

    non_tables = [e for e in elems if str(e.get("type", "")).lower() != "table"]
    assert all("page" in e and "text" in e for e in non_tables)


@pytest.mark.integration
@pytest.mark.parametrize("sample_name", SAMPLE_FILES)
def test_extract_idempotent(azdocint, sample_name: str) -> None:
    """The extractor must be *deterministic* for identical input."""

    sample = TEST_DATA_DIR / sample_name
    _skip_if_invalid(sample)

    run1 = _collect_elements(azdocint, sample)
    run2 = _collect_elements(azdocint, sample)
    assert run1 == run2, "Extractor output is not deterministic"


# --------------------------------------------------------------------------- #
# Negative‑path tests                                                         #
# --------------------------------------------------------------------------- #


def test_missing_credentials_returns_empty(azdocint, tmp_path: Path) -> None:
    """Extractor returns ``[]`` (no raise) when all credentials are absent."""

    bogus_pdf = tmp_path / "bogus.pdf"
    bogus_pdf.write_bytes(b"%PDF-1.4\n%EOF\n")  # minimal stub

    with _temporarily_clear_credentials():
        assert list(azdocint.extract(bogus_pdf)) == []


def test_unsupported_format_returns_empty(azdocint, dummy_foo: Path) -> None:
    """Unsupported ``.foo`` file → ``supports()``⇒False and ``extract()``⇒[]"""

    assert not azdocint.supports(dummy_foo)
    assert list(azdocint.extract(dummy_foo)) == []
