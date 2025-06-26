"""Base protocol for document extractors
=================================================

This module exposes :class:`DocumentExtractor`, the **canonical abstract
interface** that every *born‑digital* extractor engine inside *Insight Ingenious*
must implement.  Back‑ends such as *PyMuPDF*, *PDFMiner*, and
*unstructured* inherit from this class so that downstream components—RAG
pipelines, conversational agents, analytics helpers—can consume their output
uniformly.

Why a dedicated protocol?
-------------------------
* **Loose coupling** – higher‑level logic manipulates a generic stream of
  :pydata:`Element` dictionaries instead of backend‑specific objects.
* **Hot‑swappable engines** – adding a new parser is as simple as registering
  it in ``ingenious.document_processing.extractor._ENGINES``.
* **Stable schema guarantees** – all extractors emit the *exact same* keys and
  value types, eliminating brittle conditional code.

Element schema
--------------
Every extractor yields dictionaries that respect the following contract::

    {
        "page"  : int | None,          # 1‑based page index (None for plain‑text)
        "type"  : str,                # semantic category, e.g. "Title", "Text"
        "text"  : str,                # raw textual payload (may be empty)
        "coords": tuple[float, float,  # bounding box in PDF points
                          float, float]  | None
    }

Coordinates are expressed in **PDF points** *(72 pt = 1 inch)* using the origin
(top‑left) coordinate system native to PDF viewers.

Usage example
~~~~~~~~~~~~~
>>> from ingenious.document_processing.extractor import extract
>>> for block in extract("quarterly_report.pdf", engine="pdfminer"):
...     print(block["page"], block["type"], "→", block["text"][:40])

Implementation contract
~~~~~~~~~~~~~~~~~~~~~~~
* **Statelessness** – instances should avoid holding mutable state so they can
  be reused concurrently.
* **Streaming** – yield elements as soon as they are available; do not buffer
  entire documents in memory.
* **Fault tolerance** – log recoverable errors and continue; reserve
  exceptions for irrecoverable conditions.

Thread‑safety & re‑entrancy
---------------------------
Implementations must be safe to call from multiple threads provided the caller
creates *one extractor instance per thread* **or** the implementation guards
shared resources internally.

"""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypedDict, TypeAlias, Generator

# ────────────────────────────────────────────────────────────────────────────
# Public type aliases
# ────────────────────────────────────────────────────────────────────────────
Coords: TypeAlias = tuple[float, float, float, float]
"""Bounding box given as ``(x0, y0, x1, y1)`` in PDF points."""

Src: TypeAlias = str | bytes | os.PathLike[str] | Path
"""Union of *source* types accepted by every extractor engine."""


class Element(TypedDict, total=False):
    """Single structural block emitted by an extractor.

    Attributes
    ----------
    page
        1‑based page index.  ``None`` is permissible for formats lacking page
        semantics (e.g. plain‑text files).
    type
        High‑level semantic category such as ``"Title"``, ``"NarrativeText"``,
        or ``"Table"``.  Downstream logic should not assume a fixed taxonomy.
    text
        Raw textual payload in logical reading order.  Empty strings are
        allowed when an element conveys only positional metadata.
    coords
        Optional :pydata:`Coords` tuple specifying the element's bounding box
        in PDF points.
    """


# ────────────────────────────────────────────────────────────────────────────
# Logger
# ────────────────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)


# ────────────────────────────────────────────────────────────────────────────
# Abstract base class
# ────────────────────────────────────────────────────────────────────────────
class DocumentExtractor(ABC):
    """Abstract strategy for parsing *born‑digital* documents.

    Sub‑classes *must* specify a :pyattr:`name`, implement the capability probe
    :meth:`supports`, and perform the heavy lifting in :meth:`extract`.

    Notes
    -----
    * Implementations *should* cache heavyweight initialisation (e.g. model
      loading) at the **module level** or via ``functools.lru_cache`` to avoid
      repeated start‑up cost.
    * Avoid mutating yielded :pydata:`Element` instances after they leave the
      generator—shared mutable state can break downstream consumers.
    """

    #: Registry identifier consumed by
    #: ``ingenious.document_processing.extractor._ENGINES``.
    name: str

    # ------------------------------------------------------------------
    # Capability probe
    # ------------------------------------------------------------------
    @abstractmethod
    def supports(self, src: Src) -> bool:  # noqa: D401 (imperative docstring OK)
        """Return **True** if *src* is compatible with this extractor.

        The check should be inexpensive—typically inspecting the path suffix,
        MIME type, or leading *magic bytes*—and must **not** modify global
        state or perform heavy I/O.

        Parameters
        ----------
        src
            File path / URL string / :class:`pathlib.Path` or an in‑memory
            ``bytes`` payload representing the document.

        Returns
        -------
        bool
            ``True`` when the extractor *can* process *src*; otherwise
            ``False``.
        """

    # ------------------------------------------------------------------
    # Extraction
    # ------------------------------------------------------------------
    @abstractmethod
    def extract(self, src: Src) -> Generator[Element, None, None]:  # noqa: C901
        """Yield :pydata:`Element` objects in *logical reading order*.

        Implementations should:

        * Stream results—yield as soon as a block is ready.
        * Preserve human reading order (top‑down, left‑to‑right for LTR
          languages) wherever feasible.
        * Log recoverable errors at **WARNING** level and skip the affected
          portion; avoid raising unless continued processing is impossible.

        Parameters
        ----------
        src
            Path‑like object, URL string, or bytes‑like buffer containing the
            document to parse.

        Yields
        ------
        Element
            Structured content blocks extracted from *src*.

        Raises
        ------
        RuntimeError
            Implementations *may* raise for unrecoverable conditions such as
            missing native libraries.  Common, recoverable parsing errors
            should instead be logged.
        """


__all__ = [
    "DocumentExtractor",
    "Element",
    "Coords",
    "Src",
]
