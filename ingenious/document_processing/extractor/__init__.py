"""
Pluggable text extractors
====================================

Insight Ingenious separates **document‑I/O** concerns from higher‑level natural
language processing by funnelling every *born‑digital* file through a narrow,
engine‑agnostic interface.  Each *extractor engine* knows how to turn its
respective file type into a sequence of structured "elements" (paragraphs,
form fields, table cells …) while *this* module concerns itself with:

1. **Registry management** – mapping succinct engine names such as
   ``"pymupdf"`` or ``"pdfminer"`` to the fully‑qualified Python import path of
   the implementation class.
2. **Lazy loading & caching** – deferring the actual import *and* object
   instantiation until the very first time the engine is used, then keeping a
   *singleton* instance alive for the lifetime of the interpreter.  This avoids
   repeated start‑up costs of heavy C‑extensions (e.g. MuPDF) *and* ensures that
   configuration/state that lives on the extractor object (e.g. tokenisers,
   font caches) is re‑used across calls.
3. **Ergonomic helpers** – a tiny :func:`extract` wrapper that lets downstream
   code write

   >>> from ingenious.document_processing.extractor import extract
   >>> for block in extract("paper.pdf", engine="pdfminer"):
   ...     print(block["text"])

   without worrying about engine classes, import strings, or caching nuances.

---------------------------------------------------------------------------
Element schema
--------------
Every extractor yields *dict‑like* :class:`~ingenious.document_processing.extractor.base.Element`
objects with the canonical keys::

    {
        "page":   int,                               # 1‑based page number
        "type":   str,                               # "paragraph", "cell", …
        "text":   str,                               # human‑readable payload
        "coords": tuple[int, int, int, int] | None,  # (x0, y0, x1, y1) in pts
    }

The co‑ordinates follow the PDF convention: origin at the **bottom‑left** of the
page, units in PostScript points (1 pt = 1/72 inch).  Engines that cannot supply
accurate positional data set ``coords`` to *None*.

---------------------------------------------------------------------------
Extending the registry
----------------------
New engines may be registered at runtime::

    from ingenious.document_processing.extractor import _ENGINES
    _ENGINES["mylib"] = "my.package.pdf:MyPdfExtractor"

The next call to ``extract(engine="mylib")`` will automatically discover and
instantiate your class.

---------------------------------------------------------------------------
Thread‑safety & concurrency
---------------------------
Instances are created **once** per process.  Extractor classes **should** be
stateless or protect all mutable per‑document state behind method boundaries so
they remain safe when called from multiple threads or async tasks.  If an
engine is *not* re‑entrant it must implement its own locking.

"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from importlib import import_module
from typing import Iterable

from .base import DocumentExtractor, Element  # re‑export for typing

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Registry of extractor back‑ends                                             #
# --------------------------------------------------------------------------- #
# Key   → short user‑facing engine name (what appears in CLI / kwargs)        #
# Value → "dotted.path.to.module:ClassName" import string                     #
# --------------------------------------------------------------------------- #
_ENGINES: dict[str, str] = {
    "pymupdf": "ingenious.document_processing.extractor._pymupdf_extractor:PyMuPDFExtractor",
    "pdfminer": "ingenious.document_processing.extractor._pdfminer_extractor:PDFMinerExtractor",
    "unstructured": "ingenious.document_processing.extractor._unstructured_extractor:UnstructuredExtractor",
    "azdocint": "ingenious.document_processing.extractor._azure_docintelligence_extractor:AzureDocIntelligenceExtractor",
}


@lru_cache(maxsize=None)
def _load(name: str) -> DocumentExtractor:
    """Get (and memoise) the extractor implementation for *name*.

    This helper performs **three** actions in one go:

    1. Validate that *name* is known – otherwise raising :class:`ValueError` to
       fail fast with a clear message.
    2. Dynamically import the module referenced in :data:`_ENGINES` using
       :pyfunc:`importlib.import_module` *only* when first requested.
    3. Instantiate the extractor class and cache the resulting object via
       :pyfunc:`functools.lru_cache`, guaranteeing a *singleton* per engine.

    The single‑instance policy has two advantages:

    * **Performance** – heavyweight libraries (e.g. MuPDF, Tesseract) perform
      global initialisation that would otherwise repeat on every call.
    * **Resource sharing** – internal caches (glyph tables, ML tokenisers) are
      re‑used across extraction invocations.

    Parameters
    ----------
    name
        One of the keys defined in :data:`_ENGINES` (case‑sensitive).

    Returns
    -------
    DocumentExtractor
        A ready‑to‑use extractor object whose :pymeth:`~ingenious.document_processing.extractor.base.DocumentExtractor.extract`
        method can be called immediately.

    Raises
    ------
    ValueError
        If *name* is not present in :data:`_ENGINES`.

    Examples
    --------
    >>> pymupdf = _load("pymupdf")
    >>> list(pymupdf.extract(b"%PDF‑1.4 …"))
    []
    """
    if name not in _ENGINES:
        raise ValueError(f"Unknown engine {name!r}. Choose from {list(_ENGINES)}")

    module_path, class_name = _ENGINES[name].split(":", 1)
    extractor_cls = getattr(import_module(module_path), class_name)
    extractor: DocumentExtractor = extractor_cls()  # type: ignore[call‑arg]
    logger.debug("Loaded document extractor %s → %s", name, extractor_cls.__name__)
    return extractor


# Accepts str, bytes, or a Path‑like object
Src = str | bytes | os.PathLike[str]


def extract(src: Src, *, engine: str = "pymupdf") -> Iterable[Element]:
    """High‑level convenience wrapper around :pymeth:`DocumentExtractor.extract`.

    The helper is intentionally *thin* – its sole purpose is to avoid the
    boilerplate of manual engine lookup and to provide a consistent type hint
    in downstream code.  All heavy lifting (file I/O, parsing, layout analysis)
    happens inside the engine implementation.

    Parameters
    ----------
    src
        • **Path‑like** – a local file path to a PDF or other supported format.
        • **URL string** – *http[s]://…*; engines may download the resource or
          rely on an external helper.
        • **Bytes** – already‑loaded binary payload (useful in serverless /
          stream‑processing scenarios).
    engine
        Registry key of the backend to use.  Falls back to ``"pymupdf"`` when
        omitted.

    Returns
    -------
    Iterable[Element]
        A generator/iterator that yields :pyclass:`Element` objects **in the
        order they appear in the source document**.

    Notes
    -----
    *The function itself performs **no** network I/O, file reading, or
    decoding*.  Engines handle those details, which means that:
    – Network failures bubble up as whatever exception the engine raises
      (typically :class:`urllib.error.URLError` or :class:`requests.RequestException`).
    – Invalid file formats yield an **empty iterator** rather than raising,
      unless the underlying library errors out first.

    Examples
    --------
    >>> from pathlib import Path
    >>> elements = list(extract(Path("report.pdf")))
    >>> len(elements)
    42
    """
    return _load(engine).extract(src)  # type: ignore[arg‑type]


__all__ = [
    "extract",
    "DocumentExtractor",
    "Element",
]
