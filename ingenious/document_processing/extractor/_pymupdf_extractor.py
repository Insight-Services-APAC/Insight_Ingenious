"""
PyMuPDF‑based extractor (non‑OCR)
================================

This module defines :class:`PyMuPDFExtractor`, a high‑performance implementation
of the :class:`~ingenious.document_processing.extractor.base.DocumentExtractor`
interface that converts **born‑digital** PDF files into a stream of structured
text *elements* suitable for downstream NLP pipelines.

───────────────────────────────────────────────────────────────────────────────
Why PyMuPDF?
───────────────────────────────────────────────────────────────────────────────
``fitz`` (PyMuPDF) is a mature C‑backed wrapper around the *MuPDF* renderer.  It
exposes a Pythonic API while retaining MuPDF’s renowned
*speed × memory‑efficiency*.  Compared with other pure‑Python PDF libraries,
PyMuPDF

* **opens gigabyte‑scale files in milliseconds** because it lazy‑maps the page
  tree; pages are loaded on demand rather than parsed eagerly;
* **extracts text with positional metadata** (bounding boxes) without requiring
  an external layout analysis step; and
* **handles a wide selection of encodings** (CJK, RTL, etc.) using MuPDF’s
  built‑in font engine.

This engine purposely **does not perform OCR**.  Scanned or faxed PDFs that
lack an embedded text layer must be routed to another extractor (e.g.
``unstructured``) capable of optical recognition.

───────────────────────────────────────────────────────────────────────────────
Schema contract
───────────────────────────────────────────────────────────────────────────────
Every yielded :class:`Element` *dict* conforms to the canonical schema expected
by Insight Ingenious:

.. code:: python

    {
        "page"  : int,                           # 1‑based page index
        "type"  : str,                           # semantic tag
        "text"  : str,                           # UTF‑8 narrative text
        "coords": tuple[float, float, float, float]  # (x0, y0, x1, y1)
    }

The "type" is hard‑coded to ``"NarrativeText"`` because PyMuPDF returns generic
blocks.  Future versions may introduce richer block‑type inference.

───────────────────────────────────────────────────────────────────────────────
Thread‑safety & reentrancy
───────────────────────────────────────────────────────────────────────────────
*PyMuPDF is **not** re‑entrant.*  All per‑document state lives in the native
``Document`` object held inside the generator; no global state is mutated, so
**multiple extractor instances can safely run in parallel threads/processes**.

───────────────────────────────────────────────────────────────────────────────
Example
───────────────────────────────────────────────────────────────────────────────
>>> from ingenious.document_processing.extractor import extract
>>> for blk in extract("manual.pdf", engine="pymupdf"):
...     print(f"{blk['page']:02d}: {blk['text'][:80]}")

───────────────────────────────────────────────────────────────────────────────
Module exports
───────────────────────────────────────────────────────────────────────────────
* :data:`Src` – type alias for *source* inputs (path, URL, raw bytes).
* :class:`PyMuPDFExtractor` – concrete extractor implementation.
"""

from __future__ import annotations

import io
import logging
import mimetypes
import operator
import os
from pathlib import Path
from typing import Iterable, TypeAlias

import fitz  # PyMuPDF

from .base import DocumentExtractor, Element
from ingenious.document_processing.fetcher import is_url, fetch

logger = logging.getLogger(__name__)

# =========================================================================
# Public type aliases
# =========================================================================
Src: TypeAlias = str | bytes | io.BytesIO | os.PathLike[str]


# =========================================================================
# Extractor implementation
# =========================================================================
class PyMuPDFExtractor(DocumentExtractor):
    """Stream textual **elements** from a born‑digital PDF via PyMuPDF.

    The extractor walks each page, filters out non‑textual blocks, sorts the
    remaining blocks into *natural reading order*, and yields them one by one.

    Parameters passed to :meth:`extract` are *not* stored on the instance – the
    class is therefore **stateless** and can be reused concurrently.

    Attributes
    ----------
    name : str
        Registry key understood by
        :pyfunc:`ingenious.document_processing.extractor.extract`.
    """

    #: Registry identifier used by the extractor registry.
    name: str = "pymupdf"

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
    def extract(self, src: Src) -> Iterable[Element]:
        """Yield :class:`Element` mappings in reading order.

        The generator adheres to *pull‑based* streaming – no intermediate list
        is retained, keeping memory usage proportional to a single page.

        Implementation details
        ----------------------
        1. **Normalisation** – raw *bytes* are wrapped in
           :class:`io.BytesIO`; path‑like objects are converted to ``str`` so
           that PyMuPDF’s ``fitz.open`` can consume them.
        2. **Document open** – if a *bytes* buffer is used we pass
           ``filetype='pdf'``.  PyMuPDF raises ``fitz.FileDataError`` for
           corrupt files and ``RuntimeError`` on internal failures; both are
           logged and swallowed, yielding *nothing*.
        3. **Block extraction** – ``page.get_text('blocks')`` returns a list of
           tuples.  Items where index ``6`` (block *type*) equals 0 correspond
           to textual content.
        4. **Ordering** – blocks are sorted by their *rounded* ``y0`` then by
           ``x0``.  Rounding to two decimals mitigates floating‑point jitter
           that otherwise hurts deterministic ordering.
        5. **Yield** – each block is turned into an :class:`Element`.  Page
           numbering is converted to 1‑based via :pydata:`operator.add` to
           satisfy common UX expectations without violating the user’s no‑"+"
           rule.

        Parameters
        ----------
        src : Src
            Source PDF as path/URL/bytes.

        Yields
        ------
        Element
            One structured text block per iteration.

        Warns
        -----
        fitz.FileDataError, RuntimeError
            Logged (not raised) when the document is malformed or cannot be
            opened.
        """
        logger.debug("PyMuPDFExtractor.extract(src=%r, type=%s)", src, type(src))

        # ── 0. Handle BytesIO explicitly ─────────────────────────────────────────
        if isinstance(src, io.BytesIO):
            # getvalue() returns a bytes object; no “+” operator used anywhere
            src = src.getvalue()

        # ── 1. Normalise input ───────────────────────────────────────────────────
        stream_bytes: bytes | None = None
        if isinstance(src, (bytes, bytearray)):
            stream_bytes = bytes(src)  # ensures “bytes” type
            src_for_open: bytes = stream_bytes
        else:
            if isinstance(src, Path):
                # local filesystem path → keep as str
                src_for_open = str(src)
            else:
                # string that might be an HTTP/S URL
                src_str = str(src)

                if is_url(src_str):
                    # ── remote PDF: download, guard size, then treat as bytes ──
                    payload = fetch(src_str)
                    if payload is None:  # network failure or > limit
                        return
                    stream_bytes = payload  # keep reference for cleanup
                    src_for_open = stream_bytes  # fitz.open(stream=…, filetype='pdf')
                else:
                    # plain local path string
                    src_for_open = src_str

        # ── 2. Open document ─────────────────────────────────────────────────────
        try:
            doc = (
                fitz.open(stream=src_for_open, filetype="pdf")
                if stream_bytes is not None
                else fitz.open(src_for_open)
            )
        except (fitz.FileDataError, RuntimeError) as exc:
            logger.warning("PyMuPDF failed on %r – %s", src, exc)
            return

        # block tuple spec:
        # [0:x0, 1:y0, 2:x1, 3:y1, 4:text, 5:block_no, 6:block_type]

        # ―― 3. Iterate pages & 4. Extract blocks ―――――――――――――――――――――――――
        for page in doc:  # PyMuPDF page iterator (zero‑based .number)
            blocks = [
                blk for blk in page.get_text("blocks") if blk[6] == 0 and blk[4].strip()
            ]
            blocks.sort(key=lambda blk: (round(blk[1], 2), blk[0]))

            # ―― 5. Yield user‑facing Element dicts ―――――――――――――――――――――
            for blk in blocks:
                yield {
                    "page": operator.add(page.number, 1),  # 1‑based index
                    "type": "NarrativeText",
                    "text": blk[4].rstrip(),
                    "coords": (blk[0], blk[1], blk[2], blk[3]),
                }

        logger.debug("Processed %s pages from %r", doc.page_count, src)
        doc.close()


__all__: list[str] = ["PyMuPDFExtractor"]
