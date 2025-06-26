"""
Insight Ingenious — Integration test‑suite for *PDFMinerExtractor*
===============================================================

This module contains **black‑box** integration tests that assert the public
contract of :class:`ingenious.document_processing.extractor.pdfminer.PDFMinerExtractor`.
It covers every officially supported input flavour and the two canonical error
cases recognised by the engine.  Concretely, the suite guarantees that the
extractor

1. **Accepts** the full input surface area:
   • local :class:`pathlib.Path` objects
   • in‑memory :class:`bytes` buffers
   • :class:`io.BytesIO` streams
   • **HTTP/S URL** strings (downloaded internally by the framework)
2. **Extracts** at least one text‑bearing element from a well‑formed PDF.
3. Is **deterministic** – two invocations over the *same* file yield a
   bit‑for‑bit identical sequence of element mappings.
4. **Fails soft** – instead of raising, the extractor returns an **empty
   iterator** when
   • the remote server responds with an HTTP error (4xx/5xx), or
   • the remote PDF exceeds the 20 MiB safety guard.

These properties protect higher‑level RAG pipelines from nondeterminism and
propagation of network errors.
"""

from __future__ import annotations

# ──────────── Standard Library ────────────
import io
from pathlib import Path
from typing import Any, Callable, Final, Iterator

# ────────────── Third‑Party ───────────────
import pytest
import requests

# ────────────── First‑Party ───────────────
from ingenious.document_processing.extractor import _load

__all__: list[str] = [
    "test_extract_happy_paths",
    "test_extract_idempotent",
    "test_url_404_fail_soft",
    "test_url_oversize_guard",
]

# --------------------------------------------------------------------------- #
# Constants                                                                   #
# --------------------------------------------------------------------------- #
EXTRACTOR_NAME: Final[str] = "pdfminer"
_CHUNK: Final[int] = 1 << 14  # 16 KiB – mirrors Requests’ default stream size.
_OVERSIZE_THRESHOLD: Final[int] = 20 << 20  # 20 MiB safety guard.


# --------------------------------------------------------------------------- #
# Helper objects & functions                                                  #
# --------------------------------------------------------------------------- #
class _StubResp:  # noqa: D101 – internal helper class.
    """A *very* small shim that mimics the parts of :class:`requests.Response`
    touched by the extractor.

    Parameters
    ----------
    content
        The byte payload returned when the extractor iterates over the
        response’s content.
    status_code
        The HTTP status with which to initialise the stub.  Codes ≥ 400 cause
        :pymeth:`raise_for_status` to raise :class:`requests.HTTPError`,
        exactly like the real object does.
    """

    def __init__(self, content: bytes, status_code: int = 200) -> None:  # noqa: D401 – imperative mood acceptable.
        self.content: bytes = content
        self.status_code: int = status_code
        # The extractor occasionally inspects *headers* for content‑length.
        # Providing an empty mapping is sufficient for the tests.
        self.headers: dict[str, str] = {}
        self._raw: io.BytesIO = io.BytesIO(content)

    # --------------------------------------------------------------------- #
    # Public shim API                                                       #
    # --------------------------------------------------------------------- #
    def iter_content(self, chunk_size: int = _CHUNK) -> Iterator[bytes]:
        """Yield *content* in ``chunk_size`` slices to emulate streaming."""

        while True:
            chunk = self._raw.read(chunk_size)
            if not chunk:
                break
            yield chunk

    def raise_for_status(self) -> None:
        """Reproduce the behaviour of :pymeth:`requests.Response.raise_for_status`."""

        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")


def _monkey_download(monkeypatch: pytest.MonkeyPatch, payload: _StubResp) -> None:  # noqa: D401
    """Redirect *all* `requests.get` calls inside the fetcher to *payload*.

    The Insight Ingenious fetcher keeps a module‑level reference to
    :func:`requests.get`.  Overwriting that symbol ensures **every** extractor
    – regardless of its internal implementation – receives the same stubbed
    response, making the tests completely deterministic and free of external
    I/O.
    """

    target = "ingenious.document_processing.fetcher.requests.get"
    monkeypatch.setattr(target, lambda *_a, **_k: payload, raising=True)


# --------------------------------------------------------------------------- #
# Test‑probe builders                                                         #
# --------------------------------------------------------------------------- #
ProbeBuilder = Callable[[Path], Any]

_PROBES: list[tuple[str, ProbeBuilder]] = [
    ("path", lambda p: p),
    ("bytes", lambda p: p.read_bytes()),
    ("bytesio", lambda p: io.BytesIO(p.read_bytes())),
    ("url", lambda p: f"https://example.com/{p.name}"),
]


# --------------------------------------------------------------------------- #
# Fixtures                                                                    #
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="module")
def pdfminer():  # noqa: D401 – fixture names should be lowercase nouns.
    """Return a *single* PDFMiner extractor instance for the whole module."""

    return _load(EXTRACTOR_NAME)


# --------------------------------------------------------------------------- #
# 1. Happy‑path matrix                                                        #
# --------------------------------------------------------------------------- #
@pytest.mark.usefixtures("pdfminer_available")
@pytest.mark.parametrize(
    ("kind", "probe_fn"),
    _PROBES,
    ids=[k for k, _ in _PROBES],
)
def test_extract_happy_paths(
    kind: str,
    probe_fn: ProbeBuilder,
    pdf_path: Path,
    pdfminer,
    pdfminer_available: bool,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Extract **some** text for each supported input type.

    For URL probes, the remote download is stubbed so the test suite never
    touches the network.
    """

    if not pdfminer_available:
        pytest.skip("pdfminer.six not installed")

    probe = probe_fn(pdf_path)

    if isinstance(probe, str) and probe.startswith("http"):
        _monkey_download(monkeypatch, _StubResp(pdf_path.read_bytes()))

    texts: list[str] = [blk["text"] for blk in pdfminer.extract(probe)]
    assert any(texts), f"No text extracted for {kind!r} input"


# --------------------------------------------------------------------------- #
# 2. Determinism across runs                                                  #
# --------------------------------------------------------------------------- #


def test_extract_idempotent(
    pdfminer,
    pdf_path: Path,
    pdfminer_available: bool,
) -> None:
    """Verify that two extractions over the *same* file are identical."""

    if not pdfminer_available:
        pytest.skip("pdfminer.six not installed")

    run1 = list(pdfminer.extract(pdf_path))
    run2 = list(pdfminer.extract(pdf_path))

    assert run1 == run2, "Extractor output is not deterministic"


# --------------------------------------------------------------------------- #
# 3. Fail‑soft: HTTP error                                                    #
# --------------------------------------------------------------------------- #


def test_url_404_fail_soft(
    pdfminer,
    pdf_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    pdfminer_available: bool,
) -> None:
    """Return an *empty iterator* when the server responds with **404 Not Found**."""

    if not pdfminer_available:
        pytest.skip("pdfminer.six not installed")

    url = f"https://example.com/{pdf_path.name}"
    _monkey_download(monkeypatch, _StubResp(b"", status_code=404))

    assert list(pdfminer.extract(url)) == []


# --------------------------------------------------------------------------- #
# 4. Fail‑soft: oversized downloads                                          #
# --------------------------------------------------------------------------- #


def test_url_oversize_guard(
    pdfminer,
    monkeypatch: pytest.MonkeyPatch,
    pdfminer_available: bool,
) -> None:
    """Skip **oversized** remote PDFs (> 20 MiB) and yield nothing."""

    if not pdfminer_available:
        pytest.skip("pdfminer.six not installed")

    url = "https://example.com/huge.pdf"
    big_payload = b"%PDF-1.7\n" + b"0" * (_OVERSIZE_THRESHOLD + 1)

    _monkey_download(monkeypatch, _StubResp(big_payload))

    assert list(pdfminer.extract(url)) == []
