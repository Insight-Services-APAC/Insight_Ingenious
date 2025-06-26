"""
Insight Ingenious – *unstructured* extractor
===========================================

A **zero-dependency** (beyond `unstructured` itself) backend that converts
*born-digital* PDF, DOCX, and PPTX sources—or their in-memory byte buffers—
into Insight Ingenious-standard :pydata:`Element` dictionaries.

Why this extractor?
-------------------
* **Pure Python** – no Java, no system-level OCR binaries.
* **Fail-soft** – any vendor or I/O error is logged and swallowed,
  guaranteeing that large batch jobs never abort mid-run.
* **Hyphen-safe text** – internal ASCII hyphens (``-``) are replaced by their
  non-breaking counterpart (``\u2011``) to stop downstream renderers from
  splitting compound words.

Walking through a call
----------------------
>>> from ingenious.document_processing.extractor.unstructured import UnstructuredExtractor
>>> blocks = list(UnstructuredExtractor().extract("sample.pdf"))
>>> blocks[0]
{'page': 1, 'type': 'Title', 'text': 'Contract of Sale \u2011 Summary', 'coords': [(94.2, 80.4), ...]}

Exported schema
---------------
Every yielded mapping conforms to the *canonical* ``Element`` protocol:

=============  =============================================================
key            description
-------------  -------------------------------------------------------------
``page``       one-based page index (``None`` for DOCX paragraphs or slides)
``type``       block category – paragraph, title, caption, …
``text``       hyphen-safe text (internal ``-`` ➞ ``\u2011``)
``coords``     bounding box data *(x, y)* pairs, a mapping, or ``None``
=============  =============================================================

Design contracts
----------------
* Only the three mainstream OOXML / PDF MIME types are recognised.
* The public iterator **never raises** – callers may keep iterating even if a
  single document fails to parse.

See Also
--------
* :pymod:`ingenious.document_processing.extractor.base` – common extractor
  interfaces and the ``Element`` data contract.

"""

from __future__ import annotations

import io
import logging
import mimetypes
import os
import re
import zipfile
from pathlib import Path
from typing import Any, Final, Iterable, TypeAlias
from .base import DocumentExtractor, Element
from ingenious.document_processing.fetcher import is_url, fetch

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Type aliases and constants                                                  #
# --------------------------------------------------------------------------- #

#: Accepted *src* argument types for :meth:`UnstructuredExtractor.extract`.
Src: TypeAlias = str | bytes | io.BytesIO | os.PathLike[str]

#: Unicode hyphen that **never** breaks across lines.
_NON_BREAKING_HYPHEN: Final[str] = "\u2011"

#: ASCII hyphen sitting *inside* a lexical token.
_IN_WORD_HYPHEN_RE: Final[re.Pattern[str]] = re.compile(r"(?<=\w)-(?!\s)")

#: Rich-text MIME types that this backend promises to understand.
_SUPPORTED_MIMES: Final[set[str]] = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}

# --------------------------------------------------------------------------- #
# Extractor implementation                                                    #
# --------------------------------------------------------------------------- #


class UnstructuredExtractor(DocumentExtractor):
    """
    Yield Insight-standard elements from PDF / DOCX / PPTX inputs via
    `unstructured`_.

    Instances are **stateless**; you can safely create one and reuse it across
    threads or asynchronous tasks.

    Attributes
    ----------
    name :
        Human-readable identifier used by
        :pyfunc:`ingenious.document_processing.extractor._load` for dynamic
        discovery.

    Notes
    -----
    * All heavy lifting is delegated to the corresponding
      ``unstructured.partition.*`` helper.
    * The implementation purposefully avoids any string concatenation with the
      ``+`` operator to respect project-wide style guidelines.

    """

    name: str = "unstructured"

    # --------------------------------------------------------------------- #
    # Private helpers                                                       #
    # --------------------------------------------------------------------- #

    @staticmethod
    def _coords_to_jsonable(
        coords: Any,  # noqa: ANN401 – vendor returns untyped objects
    ) -> list[tuple[float, float]] | dict | str | None:
        """
        Convert *unstructured* coordinate objects to JSON-serialisable data.

        The coordinate class changes between *unstructured* releases:
        ``Polygon``, ``BBox``, or even a plain :class:`dict`.  Three strategies
        are attempted in order:

        1. Return a list of ``(x, y)`` tuples when the object exposes
           ``.points``.
        2. Call :py:meth:`to_dict` when available.
        3. Fallback to :py:func:`str`.

        Parameters
        ----------
        coords :
            Raw coordinate payload attached to a partitioned element.

        Returns
        -------
        list[tuple[float, float]] | dict | str | None
            JSON-ready representation, or ``None`` when *coords* is falsy.

        """
        if coords is None:
            return None
        try:
            return [(pt.x, pt.y) for pt in coords.points]
        except Exception:  # pragma: no cover – vendor API drifts
            if hasattr(coords, "to_dict"):
                return coords.to_dict()  # type: ignore[attr-defined]
            return str(coords)

    @staticmethod
    def _normalise_text(text: str) -> str:
        """
        Guard against mid-word line breaks by swapping hyphens.

        Parameters
        ----------
        text :
            Raw text emitted by *unstructured*.

        Returns
        -------
        str
            Text where every internal ASCII ``-`` is replaced by
            ``\u2011`` (non-breaking hyphen).

        """
        return _IN_WORD_HYPHEN_RE.sub(_NON_BREAKING_HYPHEN, text)

    # --------------------------------------------------------------------- #
    # DocumentExtractor API                                                 #
    # --------------------------------------------------------------------- #

    def supports(self, src: Src) -> bool:
        """
        Heuristically decide whether *src* looks parseable by this backend.

        Logic
        -----
        * ``bytes`` / :class:`bytearray` are **always** tentatively accepted;
          definitive sniffing happens inside :meth:`extract`.
        * For path-like inputs, :pyfunc:`mimetypes.guess_type` suffices because
          the accepted extensions list is tiny and well-known.

        Parameters
        ----------
        src :
            Path, URL string, raw binary buffer, or any
            :class:`os.PathLike`.

        Returns
        -------
        bool
            ``True`` when *src* is worth passing into :meth:`extract`,
            otherwise ``False``.

        """
        if isinstance(src, (bytes, bytearray, io.BytesIO)):
            return True

        if isinstance(src, str) and is_url(src):
            return True  # Accept any HTTP/S URL

        mime, _ = mimetypes.guess_type(str(src))
        return mime in _SUPPORTED_MIMES

    def extract(self, src: Src) -> Iterable[Element]:  # noqa: C901 – complexity acceptable
        """
        Yield **lazy** :pydata:`Element` dictionaries extracted from *src*.

        The function is generator-based, enabling calling pipelines to process
        gigantic documents on-the-fly without waiting for complete parsing.

        High-level algorithm
        --------------------
        1. Import *unstructured* partition helpers at runtime (cheap unless
           actually used).
        2. Categorise *src* by header bytes (for buffers) or filename suffix
           (for paths).
        3. Partition the input into rich objects.
        4. Canonicalise each object into the four-field ``Element`` contract
           and ``yield`` immediately.

        Robustness contract
        -------------------
        *Any* exception thrown by vendor code is caught and logged; the
        iterator then returns silently.  No consumer is expected to wrap this
        call in a ``try`` block.

        Parameters
        ----------
        src :
            Local path, URL, or in-memory binary buffer.

        Yields
        ------
        Element
            One mapping for every textual block *unstructured* discovers.

        Examples
        --------
        >>> from pathlib import Path
        >>> ext = UnstructuredExtractor()
        >>> blocks = list(ext.extract(Path("slide_deck.pptx")))
        >>> len(blocks)
        42

        """
        try:
            from unstructured.partition.docx import partition_docx
            from unstructured.partition.pdf import partition_pdf
            from unstructured.partition.pptx import partition_pptx
        except ImportError as exc:
            logger.error("Install `unstructured` to enable this extractor: %s", exc)
            return

        # -----------------------------------------------------------------
        # Step 0 – normalise *src*
        #
        # • Convert pathlib.Path → str so later checks work uniformly.
        # • For in-memory data (bytes / bytearray / io.BytesIO) we move the
        #   raw payload into a single `payload` variable.  All subsequent
        #   sniffing and dispatch happens on that buffer.
        # -----------------------------------------------------------------
        if isinstance(src, Path):
            src = str(src)

        # ---------- NEW: remote HTTP/S URL handling ----------------------
        if isinstance(src, str) and is_url(src):
            payload = fetch(src)
            if payload is None:  # network failure or size guard triggered
                return
        else:
            payload: bytes | None = None

        if isinstance(src, io.BytesIO):
            # io.BytesIO → pull the underlying bytes once.
            payload = src.getvalue()
        elif isinstance(src, (bytes, bytearray)):
            # Accept raw bytes or bytearray verbatim.
            payload = bytes(src)

        if payload is not None:
            # Look at the first few bytes to decide whether we have
            #   • a PDF          (“%PDF-” header)
            #   • an OOXML file  (ZIP magic bytes “PK\003\004”)
            head = payload[:8]

            try:  # ← NEW universal guard
                # ---------- PDF bytes ---------------------------------------- #
                if head.startswith(b"%PDF-"):
                    with io.BytesIO(payload) as fp:
                        u_elems = partition_pdf(file=fp)

                # ---------- OOXML bytes (DOCX / PPTX) ------------------------ #
                elif head.startswith(b"PK\x03\x04"):
                    # 1️⃣ Inspect ZIP to decide subtype
                    with io.BytesIO(payload) as fp, zipfile.ZipFile(fp) as zf:
                        roots = {
                            info.filename.split("/", 1)[0] for info in zf.infolist()
                        }

                    # 2️⃣ Re-open for the real parse pass
                    with io.BytesIO(payload) as fp:
                        if "word" in roots:
                            u_elems = partition_docx(file=fp)
                        elif "ppt" in roots:
                            u_elems = partition_pptx(file=fp)
                        else:
                            logger.warning("Unknown OOXML subtype – skipped buffer")
                            return
                else:
                    logger.warning("Unsupported binary buffer – skipped")
                    return

            except Exception as exc:  # ← swallow vendor errors
                logger.warning("Parsing failed for in-memory buffer – %s", exc)
                return

        # -----------------------------------------------------------------
        # File-path inputs
        #
        # For disk-backed files we rely on the filename suffix; that’s enough
        # because the extractor is explicitly scoped to three well-known
        # formats (.pdf, .docx, .pptx).
        # -----------------------------------------------------------------
        else:
            path = str(src)
            try:
                if path.lower().endswith(".pdf"):
                    # The “hi_res” strategy gives sharper page images when
                    # unstructured falls back to OCR.
                    with open(path, "rb") as fp:
                        u_elems = partition_pdf(file=fp, strategy="hi_res")
                elif path.lower().endswith(".docx"):
                    u_elems = partition_docx(filename=path)
                elif path.lower().endswith(".pptx"):
                    u_elems = partition_pptx(filename=path)
                else:
                    logger.warning("Unsupported file type – %s", path)
                    return
            except Exception as exc:
                # Any vendor or I/O failure is swallowed so that batch jobs
                # keep running even if one document is corrupt.
                logger.warning("Parsing failed for %s – %s", src, exc)
                return

        # -------------------- Canonicalise & yield ----------------------- #
        for el in u_elems:
            meta = el.metadata
            yield {
                "page": getattr(meta, "page_number", None),
                "type": getattr(el, "category", type(el).__name__),
                "text": self._normalise_text(el.text),
                "coords": self._coords_to_jsonable(meta.coordinates),
            }

        logger.debug("Extracted %d blocks from %r", len(u_elems), src)


__all__: Final[list[str]] = ["UnstructuredExtractor"]
