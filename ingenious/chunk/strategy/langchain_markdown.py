# ingenious/chunk/strategy/langchain_markdown.py
"""
Markdown splitter with configurable bidirectional overlap.

Extends LangChain’s ``MarkdownTextSplitter`` by adding **token- or
character-accurate** context windows, controlled via
``ChunkConfig.overlap_unit``.

Usage
-----
The factory (`create`) is auto-registered under the strategy name
``"markdown"``.  Construction happens through
:pyfunc:`ingenious.chunk.factory.build_splitter`.
"""

from __future__ import annotations

from langchain_text_splitters import MarkdownTextSplitter

from ingenious.chunk.utils.overlap import inject_overlap
from ..config import ChunkConfig
from . import register


class MarkdownOverlapWrapper:
    """
    Wrap a ``MarkdownTextSplitter`` and inject left/right overlap.

    Parameters
    ----------
    base : MarkdownTextSplitter
        The underlying (character-bounded) splitter from LangChain.
    k : int
        Size of the overlap window.
    enc : str
        tiktoken encoding name (used only when *unit* is ``"tokens"``).
    unit : {"tokens", "characters"}
        Overlap unit selected by the user.
    """

    def __init__(
        self,
        base: MarkdownTextSplitter,
        k: int,
        enc: str,
        unit: str = "tokens",
    ):
        self._base = base
        self._k = k
        self._enc = enc
        self._unit = unit

    # ------------------- delegated LangChain interface ------------------ #
    def split_text(self, text: str):
        raw_chunks = self._base.split_text(text)
        return inject_overlap(
            raw_chunks, self._k, unit=self._unit, enc_name=self._enc
        )

    def split_documents(self, docs):
        chunks = self._base.split_documents(docs)
        return inject_overlap(
            chunks, self._k, unit=self._unit, enc_name=self._enc
        )

    def __getattr__(self, item):
        # Delegate every other attribute/method to the underlying splitter
        return getattr(self._base, item)


# ---------------------------------------------------------------------- #
# Factory registration                                                   #
# ---------------------------------------------------------------------- #
@register("markdown")
def create(cfg: ChunkConfig):
    """
    Build a Markdown splitter that respects the user's overlap settings.
    """
    base = MarkdownTextSplitter(chunk_size=cfg.chunk_size, chunk_overlap=0)
    return MarkdownOverlapWrapper(
        base,
        cfg.chunk_overlap,
        cfg.encoding_name,
        unit=cfg.overlap_unit,
    )
