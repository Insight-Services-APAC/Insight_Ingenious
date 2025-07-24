"""
Token‑aware *or* character‑aware recursive splitter.

Differences from the vanilla character‑based version
----------------------------------------------------
• Enforces a strict **size budget** in the unit chosen by the user: 
  – `overlap_unit="tokens"` → budget is measured in tokens (original behaviour)  
  – `overlap_unit="characters"` → budget is measured in raw characters (new path
    now delegates to LangChain’s word‑aware splitter).  
• Adds configurable bidirectional overlap in the same unit.  
• Re‑uses the shared :pyfunc:`ingenious.chunk.utils.overlap.inject_overlap`
  helper so behaviour is consistent across all strategies.
"""

from __future__ import annotations

from typing import Callable, List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from ingenious.chunk.utils.token_len import token_len  # fast, cached
from ingenious.chunk.utils.overlap import inject_overlap  # shared helper
from ..config import ChunkConfig
from . import register

__all__: list[str] = ["create", "_OverlapWrapper"]


# --------------------------------------------------------------------------- #
# Shared “add overlap” thin wrapper                                           #
# --------------------------------------------------------------------------- #
class _OverlapWrapper:
    """
    Decorator that injects **left‑side** overlap into the output of any
    LangChain‑compatible splitter (character‑ or semantic‑based).

    This keeps the overlap implementation consistent across all strategies.
    """

    def __init__(
        self,
        base: RecursiveCharacterTextSplitter,
        k: int,
        enc: str,
        unit: str = "tokens",
    ):
        self._base = base
        self._k = k
        self._enc = enc
        self._unit = unit

    # ------------------------- delegated interface ------------------------ #
    def split_text(self, text: str):
        raw = self._base.split_text(text)
        return inject_overlap(raw, self._k, unit=self._unit, enc_name=self._enc)

    def split_documents(self, docs):
        chunks = self._base.split_documents(docs)
        return inject_overlap(chunks, self._k, unit=self._unit, enc_name=self._enc)

    def __getattr__(self, item):
        # Delegate every other attribute/method to the underlying splitter
        return getattr(self._base, item)


# --------------------------------------------------------------------------- #
# Strict token‑budget implementation (unchanged)                              #
# --------------------------------------------------------------------------- #
class RecursiveTokenSplitter(RecursiveCharacterTextSplitter):
    """Preserve the *recursive* hierarchy while enforcing a strict size budget.

    The *unit* (tokens vs characters) is selected by ``overlap_unit``.
    """

    def __init__(
        self,
        encoding_name: str,
        chunk_size: int,
        chunk_overlap: int,
        overlap_unit: str = "tokens",
        separators: list[str] | None = None,
    ) -> None:
        super().__init__(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self._encoding_name = encoding_name
        self._separators = separators or ["\n\n", "\n", " ", ""]
        self._overlap_unit = overlap_unit

        # --------------------------------------------------------------
        # Measurement function – maps text → length in the chosen unit.
        # --------------------------------------------------------------
        if overlap_unit == "characters":
            self._measure: Callable[[str], int] = len
        else:  # "tokens" (default)
            self._measure = lambda s: token_len(s, encoding_name)

    # ------------------------------------------------------------------ #
    # Core algorithm – flush buffer when the budget is exceeded          #
    # ------------------------------------------------------------------ #
    def split_text(self, text: str) -> List[str]:  # type: ignore[override]
        chunks: list[str] = []
        buf = ""
        sep0 = self._separators[0]

        for paragraph in text.split(sep0):
            prospective = f"{buf}{paragraph}{sep0}"
            if self._measure(prospective) > self._chunk_size:
                if buf:  # flush current buffer
                    chunks.append(buf)

                # Paragraph alone still exceeds the budget → greedy slice.
                if self._measure(paragraph) > self._chunk_size:
                    start = 0
                    while start < len(paragraph):
                        window = paragraph[start:]
                        # progressively shrink until it fits the budget
                        while self._measure(window) > self._chunk_size:
                            window = window[:-1]
                        chunks.append(f"{window}{sep0}")
                        start += len(window)
                    buf = ""
                else:
                    buf = f"{paragraph}{sep0}"  # start new buffer
            else:
                buf = prospective

        if buf:
            chunks.append(buf)

        # Inject bidirectional overlap using the user‑selected unit
        return inject_overlap(
            chunks,
            self._chunk_overlap,
            unit=self._overlap_unit,
            enc_name=self._encoding_name,
        )


# ---------------------------------------------------------------------- #
# Factory registration                                                   #
# ---------------------------------------------------------------------- #
@register("recursive")
def create(cfg: ChunkConfig):
    """
    Factory entry‑point discovered via the plug‑in registry.

    • Character budgets → use LangChain’s word‑aware
      ``RecursiveCharacterTextSplitter`` and wrap with overlap logic.
    • Token budgets     → fall back to the strict ``RecursiveTokenSplitter``.
    """
    # -------- character‑budget path (word‑aware) ----------------------- #
    if cfg.overlap_unit == "characters":
        base = RecursiveCharacterTextSplitter(
            chunk_size=cfg.chunk_size,
            chunk_overlap=0,  # overlap added by the wrapper
            separators=cfg.separators or ["\n\n", "\n", " ", ""],
        )
        return _OverlapWrapper(
            base,
            cfg.chunk_overlap,
            cfg.encoding_name,
            unit="characters",
        )

    # -------- token‑budget path (strict) ------------------------------- #
    return RecursiveTokenSplitter(
        encoding_name=cfg.encoding_name,
        chunk_size=cfg.chunk_size,
        chunk_overlap=cfg.chunk_overlap,
        overlap_unit="tokens",
        separators=cfg.separators,
    )
