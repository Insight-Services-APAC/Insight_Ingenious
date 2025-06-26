"""
Insight Ingenious – PDFMiner‑based extractor (URL‑aware)
=======================================================

Concrete :class:`PDFMinerExtractor` implementation of the
:class:`ingenious.document_processing.extractor.DocumentExtractor` protocol.
It delegates all heavy lifting to **pdfminer.six** while offering a
stream‑friendly, fail‑soft wrapper that now supports **HTTP/S URLs** in
addition to local paths and in‑memory *bytes* buffers.

Why a dedicated extractor?
--------------------------
* **Pure‑Python dependency tree** – avoids heavyweight native libraries.
* **Streaming** – yields one :pyclass:`Element` at a time so multi‑hundred‑page
  PDFs stay memory‑light.
* **Flexible I/O** – accepts ``Path`` / ``str`` (local), **HTTP/S URL** strings
  (auto‑downloaded) or raw ``bytes``/``bytearray``.
* **Fail‑soft contract** – any parser or network error is logged at WARNING
  level; the generator then returns an empty iterator.

Quick start
-----------
>>> from ingenious.document_processing.extractor import _load
>>> pdfminer = _load("pdfminer")
>>> for blk in pdfminer.extract("https://example.com/contract.pdf"):
...     print(f"p{blk['page']:>3}: {blk['text'][:60]}…")

When to use
-----------
* PDFs that already contain a **text layer** (word‑processor output or
  post‑OCR).
* Pipelines that need to ingest PDFs directly from presigned links or public
  web locations without a separate download step.
* If the PDF is image‑only, route it to an OCR‑capable backend such as
  *pymupdf* + Tesseract.

Element schema
--------------
Every yielded mapping contains:

=================  ==========================================================
``page``           1‑based page index.
``type``           Always ``"NarrativeText"`` for this extractor.
``text``           Raw text, trailing whitespace stripped.
``coords``         ``(x0, y0, x1, y1)`` in PDF points (origin bottom‑left).
=================  ==========================================================

Values are emitted in **natural reading order** (left→right, top→bottom per
page, page order preserved).
"""

from __future__ import annotations


import io
import logging
import mimetypes
import os
from contextlib import suppress
from pathlib import Path
from typing import Iterable, TypeAlias

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from pdfminer.pdfdocument import PDFPasswordIncorrect
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFSyntaxError


from .base import DocumentExtractor, Element
from ingenious.document_processing.fetcher import is_url, fetch

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Type aliases & constants
# ---------------------------------------------------------------------------
Src: TypeAlias = str | bytes | os.PathLike[str] | io.BytesIO


class PDFMinerExtractor(DocumentExtractor):
    """Stream text from *born‑digital* PDFs using **pdfminer.six**."""

    #: Registry identifier understood by the factory loader.
    name: str = "pdfminer"

    # ------------------------------------------------------------------
    # Capability probe
    # ------------------------------------------------------------------
    def supports(self, src: Src) -> bool:
        if isinstance(src, (bytes, bytearray, io.BytesIO)):
            return True

        if isinstance(src, str) and is_url(src):
            return True  # Accept any HTTP/S URL

        string_like = str(src).lower()
        return string_like.endswith(".pdf") or (
            mimetypes.guess_type(string_like)[0] == "application/pdf"
        )

    # ------------------------------------------------------------------
    # Main extraction pipeline
    # ------------------------------------------------------------------
    def extract(self, src: Src) -> Iterable[Element]:  # noqa: C901 – complex but readable
        """Yield :pydata:`Element` objects in natural reading order."""
        logger.debug("PDFMinerExtractor.extract(src=%r, type=%s)", src, type(src))

        # ── 0. Normalise input ------------------------------------------------
        if isinstance(src, Path):
            src = str(src)

        file_obj: io.IOBase | None = None  # closeable BytesIO we own
        iterable = None  # will hold *pdfminer* page iterator

        # ── 1. Pick code‑path based on *src* type -----------------------------
        if isinstance(src, (bytes, bytearray)):
            file_obj = io.BytesIO(src)
            iterable = extract_pages(file_obj)
        elif isinstance(src, io.BytesIO):
            file_obj = src
            iterable = extract_pages(file_obj)
        elif isinstance(src, (str, os.PathLike)):
            src_str = str(src)
            path = Path(src_str)

            # Local file on disk
            if path.is_file():
                iterable = extract_pages(src_str)

            # Remote URL → download + BytesIO
            elif is_url(src_str):
                payload = fetch(src_str)
                if payload is None:  # network failure or size guard triggered
                    return
                file_obj = io.BytesIO(payload)
                iterable = extract_pages(file_obj)
            else:
                logger.warning("Unsupported src %r – skipping", src)
                return
        else:  # unexpected type
            logger.warning("Unsupported src %r – skipping", src)
            return

        # At this point *iterable* is a pdfminer page iterator
        # ── 2. Parse lazily; fail‑soft on corruption ---------------------------
        try:
            with suppress(
                PDFSyntaxError,
                PDFPasswordIncorrect,
                PDFTextExtractionNotAllowed,
                ValueError,  # truncated / zero‑byte file
                TypeError,  # wrong buffer type routed here by mistake
            ):
                for page_no, page in enumerate(iterable, start=1):
                    for obj in page:
                        if isinstance(obj, LTTextContainer):
                            text = obj.get_text().strip()
                            if not text:
                                continue

                            x0, y0, x1, y1 = obj.bbox
                            yield {
                                "page": page_no,
                                "type": "NarrativeText",
                                "text": text,
                                "coords": (x0, y0, x1, y1),
                            }
        finally:
            # Close only buffers we created; respect caller-owned BytesIO.
            if file_obj is not None and file_obj is not src:
                file_obj.close()

        logger.debug("Finished streaming pages from %r", src)


__all__: list[str] = ["PDFMinerExtractor"]
