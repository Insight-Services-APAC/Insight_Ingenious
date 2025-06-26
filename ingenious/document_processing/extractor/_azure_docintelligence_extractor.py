"""
Insight Ingenious – Azure AI Document Intelligence extractor
===========================================================

Wrapper around Azure AI **prebuilt-document v3.2 (GA)** that fulfils the
:class:`~ingenious.document_processing.extractor.base.DocumentExtractor`
protocol.  It can be swapped in wherever a local extractor
(PDFMiner, PyMuPDF, Unstructured, …) is used.

Responsibilities
----------------
* **Upload** the source file *or* in-memory bytes to the Azure endpoint.
* **Poll** the *operation-location* URL until the job finishes, **or** until a
  budget of **300 requests / 600 s** (defaults) is exhausted.
  Limits are configurable via ``AZDOCINT_MAX_POLLS`` and
  ``AZDOCINT_MAX_SECS``.
* **Stream** paragraphs and tables as lightweight ``Element`` mappings so even
  very large documents can be processed on commodity hardware.
* **Fail-soft** – network/API errors are logged and the generator returns
  early; no exception is propagated.

Environment
-----------
``AZURE_DOC_INTEL_ENDPOINT``  – endpoint URL
``AZURE_DOC_INTEL_KEY``       – API key
``AZDOCINT_MAX_POLLS``        – *(optional)* max polling attempts (default 300)
``AZDOCINT_MAX_SECS``         – *(optional)* max wall-clock seconds (default 600)

*Credentials are read **once at import time**; set the variables **before**
 importing this module.*

Example
-------
>>> from ingenious.document_processing.extractor import _load
>>> di = _load("azdocint")
>>> for block in di.extract("contract.pdf"):
...     print(block["text"])

Notes
-----
* Accepts **PDF plus common image formats (PNG / JPEG / TIFF)**; Azure performs
  OCR automatically for scanned pages.
* Table cells are **not** flattened – only table-level metadata is emitted so
  callers can render complex spans as they see fit.
* Path inputs are read fully into memory before upload; extremely large files
  may consume significant RAM until streaming uploads are implemented.
"""

from __future__ import annotations

import logging
import mimetypes
import os
import time
from pathlib import Path
from typing import Final, Iterable, Sequence, TypeAlias, cast

import requests

from ingenious.document_processing.fetcher import is_url, fetch
from .base import DocumentExtractor, Element

logger: logging.Logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Type aliases & constants
# ---------------------------------------------------------------------------
Src: TypeAlias = str | bytes | os.PathLike[str]

_ENV_ENDPOINT: Final[str | None] = os.getenv("AZURE_DOC_INTEL_ENDPOINT") or os.getenv(
    "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"
)
_ENV_KEY: Final[str | None] = os.getenv("AZURE_DOC_INTEL_KEY") or os.getenv(
    "AZURE_DOCUMENT_INTELLIGENCE_KEY"
)

_API_VERSION: Final[str] = "2023-07-31"
_POLLER_DELAY_SEC: Final[float] = 2.0
_REQUEST_TIMEOUT_SEC: Final[int] = 360

_SUPPORTED_MIME_TYPES: set[str] = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/tiff",
}

_MAX_POLL_ATTEMPTS: Final[int] = int(os.getenv("AZDOCINT_MAX_POLLS", "300"))
_MAX_POLL_SECONDS: Final[int] = int(os.getenv("AZDOCINT_MAX_SECS", "600"))

# ---------------------------------------------------------------------------
# Helper functions (private)
# ---------------------------------------------------------------------------


def _build_url(endpoint: str, model_id: str = "prebuilt-document") -> str:
    """Compose the *analyze‑document* endpoint URL.

    Parameters
    ----------
    endpoint:
        Fully qualified endpoint (scheme + host).
    model_id:
        Azure model identifier.  Defaults to the GA
        **prebuilt‑document** model.

    Returns
    -------
    str
        Analyse URL including the ``api-version`` query parameter.
    """
    base = "/".join(
        [
            endpoint.rstrip("/"),
            "formrecognizer",
            "documentModels",
            f"{model_id}:analyze",
        ]
    )
    return f"{base}?api-version={_API_VERSION}"


def _poly_to_bbox(poly: Sequence[object] | None) -> tuple[float, float, float, float]:
    """Return a bounding box ``(xmin, ymin, xmax, ymax)`` for DI v3 *and* v4.

    Azure uses two polygon encodings:
    * **v3** – list of ``{"x": float, "y": float}`` dicts
    * **v4** – flat list ``[x0, y0, x1, y1, …]``

    The helper normalises both so callers need not branch.

    Notes
    -----
    When *poly* is *None* or empty an all‑zero box is returned so that the
    caller can rely on the tuple length.
    """
    if not poly:
        return 0.0, 0.0, 0.0, 0.0

    if isinstance(poly[0], dict):  # v3 – list[dict[str, float]]
        xs = [cast(dict[str, float], pt)["x"] for pt in poly]
        ys = [cast(dict[str, float], pt)["y"] for pt in poly]
    else:  # v4 – flat list[float]
        xs = list(poly)[::2]  # even indices
        ys = list(poly)[1::2]  # odd  indices
    return min(xs), min(ys), max(xs), max(ys)


def _read_bytes(src: Src) -> bytes | None:
    """Return *src* as raw ``bytes``.

    Accepted input types
    --------------------
    * ``bytes`` / ``bytearray`` – returned unchanged.
    * Path‑like – file opened in *rb* mode.

    On failure the function logs a warning and returns *None* so that the
    caller can skip the item rather than crash the entire batch.
    """
    if isinstance(src, (bytes, bytearray)):
        return cast(bytes, src)

    try:
        with open(Path(str(src)), "rb") as fp:
            return fp.read()
    except OSError as exc:  # pragma: no cover – logging only
        logger.warning("Cannot read %s – %s", src, exc)
        return None


# ---------------------------------------------------------------------------
# Extractor implementation
# ---------------------------------------------------------------------------


class AzureDocIntelligenceExtractor(DocumentExtractor):
    """Azure AI Document Intelligence *prebuilt‑document* wrapper.

    The heavy lifting is delegated to the cloud service; this class merely
    manages I/O, polling, and *Element* normalisation.
    """

    #: Short, unique identifier used by the factory helper ``_load``.
    name: str = "azdocint"

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def supports(self, src: Src) -> bool:
        """Tell whether *src* looks consumable by the Azure service.

        The check is deliberately *permissive*: any *bytes* blob is
        accepted because the caller may have streamed data from an API
        whose content‑type was already validated upstream.
        """
        if isinstance(src, (bytes, bytearray)):
            return True

        if isinstance(src, str) and is_url(src):  # Accept any HTTP/S URL
            return True

        mime, _ = mimetypes.guess_type(str(src))
        return bool(mime and mime in _SUPPORTED_MIME_TYPES)

    # ------------------------------------------------------------------
    # Main extraction pipeline
    # ------------------------------------------------------------------

    def extract(self, src: Src) -> Iterable[Element]:
        """Yield paragraphs and table metadata extracted by Azure.

        The coroutine‑like generator follows the steps below:

        1. **Credential check** – abort early if env vars are missing.
        2. **Payload** – load the file (or use the provided bytes).
        3. **Submit** – POST to *…/analyze* and capture the *operation‑location*.
        4. **Poll** – GET the URL until ``status == succeeded``.
        5. **Normalise** – walk ``paragraphs`` and ``tables`` arrays and
           yield lightweight *Element* dictionaries.

        Yields
        ------
        dict
            Canonical *Element* mapping understood by Insight Ingenious
            pipelines.  Paragraphs contain text and coordinates; tables
            expose only high‑level shape information.
        """
        if not _ENV_ENDPOINT or not _ENV_KEY:
            logger.error(
                "Azure credentials missing – set AZURE_DOC_INTEL_ENDPOINT and AZURE_DOC_INTEL_KEY"
            )
            return

        if isinstance(src, (bytes, bytearray)):
            payload = src
        elif isinstance(src, str) and is_url(src):
            payload = fetch(src)
        else:
            payload = _read_bytes(src)

        if payload is None:  # fail-soft on network / I/O errors
            return

        azure_doc_intel_url = _build_url(_ENV_ENDPOINT)
        headers = {
            "Ocp-Apim-Subscription-Key": _ENV_KEY,
            "Content-Type": "application/octet-stream",
        }

        try:
            submit = requests.post(
                azure_doc_intel_url,
                headers=headers,
                data=payload,
                timeout=_REQUEST_TIMEOUT_SEC,
            )
        except requests.RequestException as exc:  # pragma: no cover – network hiccup
            logger.warning("Request failed for %s – %s", src, exc)
            return

        if submit.status_code != 202:
            logger.warning(
                "Analyze call returned %s – %s", submit.status_code, submit.text
            )
            return

        poll_url = submit.headers.get("operation-location")
        if not poll_url:
            logger.warning("No operation-location header in response")
            return

        # ------------------------------------------------------------------
        # Poll until the job is done (succeeded / failed)
        # ------------------------------------------------------------------
        attempts: int = 0  # start at zero requests
        start_ts = time.monotonic()

        while True:
            elapsed = time.monotonic() - start_ts
            if attempts >= _MAX_POLL_ATTEMPTS or elapsed > _MAX_POLL_SECONDS:
                logger.error(
                    "Azure analysis for %r exceeded polling budget "
                    "(%s attempts, %.0f s); aborting",
                    src,
                    attempts,
                    elapsed,
                )
                return

            # 1️⃣ Network call
            try:
                poll = requests.get(
                    poll_url, headers=headers, timeout=_REQUEST_TIMEOUT_SEC
                )
                poll.raise_for_status()  # 🔸 ensure HTTP 2xx before JSON parse
            except requests.RequestException as exc:  # pragma: no cover
                logger.warning("Polling error – %s", exc)
                return

            attempts += 1  # 2️⃣ count the call *after* it happened

            # 🔸 JSON guard
            try:
                data = poll.json()
            except ValueError as exc:  # malformed JSON
                logger.warning("Invalid JSON in polling response – %s", exc)
                return

            status = data.get("status")

            if status == "succeeded":
                break
            if status in {"failed", "error"}:
                logger.warning("Azure analysis failed – %s", poll.text)
                return

            time.sleep(_POLLER_DELAY_SEC)  # polite back-off

        result: dict = poll.json().get("analyzeResult", {})

        # ------------------------- stream paragraphs --------------------
        for para in result.get("paragraphs", []):
            text = para.get("content", "").rstrip()
            if not text:
                continue

            regions = para.get("boundingRegions") or []
            first_region = regions[0] if regions else {}
            page_no = first_region.get("pageNumber", 1)

            poly = first_region.get("polygon") or first_region.get("boundingBox")
            bbox = _poly_to_bbox(poly) if poly else None

            element: Element = {
                "page": page_no,
                "type": "Paragraph",
                "text": text,
                "coords": bbox,
            }
            if "role" in para:  # sectionHeading, title, …
                element["role"] = para["role"]
            yield element

        # ------------------------- stream tables (metadata) -------------
        for tbl in result.get("tables", []):
            first_region = tbl.get("boundingRegions", [{}])[0]
            page_no = first_region.get("pageNumber", 1)
            poly = first_region.get("polygon") or first_region.get("boundingBox")
            bbox = _poly_to_bbox(poly) if poly else None

            yield {
                "page": page_no,
                "type": "Table",
                "rows": tbl.get("rowCount"),
                "cols": tbl.get("columnCount"),
                "coords": bbox,
            }


__all__: list[str] = ["AzureDocIntelligenceExtractor"]
