"""
Insight Ingenious — *extract()* URL‑branch fail‑soft unit tests
==============================================================

This module houses **unit‑level** tests that assert the *fail‑soft* contract
of the public helper :pyfunc:`ingenious.document_processing.extract` when it
is asked to download a document from an HTTP/S URL.

Fail‑soft contract
------------------
* **Never raise** — *all* parsing / network errors are swallowed internally.
* **Return an empty list** — signalling that no elements were extracted.

Test scenario
-------------
A stubbed *HTTP 200 OK* response delivers deliberately corrupted PDF bytes.
The test verifies that ``extract``

1. downloads the payload via the usual fetcher pathway,
2. detects the corruption, and
3. yields ``[]`` without raising any exception.

Why it matters
--------------
`extract` acts as a **safety boundary** for higher‑level RAG pipelines and web
handlers: network glitches or malformed documents must never crash a long‑
running batch job or an API request.
"""

from __future__ import annotations

# ──────────── Standard Library ────────────
from typing import Any, Final, Iterator

# ────────────── Third‑Party ───────────────
import pytest
from requests.models import Response

# ────────────── First‑Party ───────────────
from ingenious.document_processing import extract

__all__: list[str] = [
    "test_extract_downloads_and_fails_soft",
]

# --------------------------------------------------------------------------- #
# Constants                                                                   #
# --------------------------------------------------------------------------- #
_CORRUPT_PDF_BYTES: Final[bytes] = b"%PDF-1.7 broken\n%%EOF"


# --------------------------------------------------------------------------- #
# Helper objects                                                              #
# --------------------------------------------------------------------------- #
class _FakeResp(Response):
    """Minimal stub of :class:`requests.Response` for HTTP stubbing.

    Only the attributes/methods consumed by
    :pyfunc:`ingenious.document_processing.fetcher.fetch` are implemented.

    Parameters
    ----------
    body:
        Raw payload returned by :pymeth:`iter_content`.
    status:
        HTTP status code to mimic (defaults to *200 OK*).
    """

    def __init__(self, body: bytes, status: int = 200) -> None:  # noqa: D401 – imperative mood is fine for __init__
        super().__init__()
        self.status_code = status
        self._content = body
        # Only *Content‑Length* is inspected upstream, so a single header suffices.
        self.headers = {"Content-Length": str(len(body))}

    # --------------------------------------------------------------------- #
    # Public shim API                                                       #
    # --------------------------------------------------------------------- #
    def iter_content(self, chunk_size: int = 1 << 14) -> Iterator[bytes]:  # noqa: D401 – clear enough without “Returns”.
        """Yield the entire *body* once to emulate a streamed download."""

        yield self._content


# --------------------------------------------------------------------------- #
# Tests                                                                       #
# --------------------------------------------------------------------------- #


def test_extract_downloads_and_fails_soft(monkeypatch: pytest.MonkeyPatch) -> None:
    """``extract`` should return ``[]`` *and* raise nothing for corrupt bytes."""

    fake_resp: Response = _FakeResp(_CORRUPT_PDF_BYTES)

    # ── Stub the global HTTP GET used by the fetcher. ────────────────────
    monkeypatch.setattr(
        "ingenious.document_processing.fetcher.requests.get",
        lambda *_a, **_k: fake_resp,
        raising=True,
    )

    # ── Exercise the URL branch. ─────────────────────────────────────────
    result: list[dict[str, Any]] = list(extract("http://example.com/bad.pdf"))

    # ── Expectations. ────────────────────────────────────────────────────
    assert result == [], "extract() should fail‑soft and yield an empty list"
