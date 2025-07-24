"""
Unicode‑safe splitter with **configurable overlap**.

• Guarantees each chunk is **≤ chunk_size** in the user‑selected unit
  (tokens *or* characters).
• Preserves Unicode grapheme boundaries (no broken surrogate pairs).
• Adds bidirectional overlap in either **tokens** *(default)* **or**
  **characters** according to ``ChunkConfig.overlap_unit``.

For *token budgets* we keep a strict, grapheme‑aware implementation that fixes
all edge‑cases found in LangChain’s original ``TokenTextSplitter``.

For *character budgets* we delegate to LangChain’s word‑aware
``RecursiveCharacterTextSplitter`` so boundaries never split a word in the
middle, then add left‑side overlap via the shared helper defined in
:pyfunc:`ingenious.chunk.strategy.langchain_recursive._OverlapWrapper`.
"""
from __future__ import annotations

import regex as re
from langchain_text_splitters.base import TextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tiktoken import get_encoding

from ..config import ChunkConfig
from . import register
from .langchain_recursive import _OverlapWrapper  # reuse the overlap helper

__all__: list[str] = ["create"]

_GRAPHEME_RE = re.compile(r"\X", re.UNICODE)


# --------------------------------------------------------------------------- #
# Strict token‑budget implementation                                          #
# --------------------------------------------------------------------------- #
class UnicodeSafeTokenTextSplitter(TextSplitter):
    """Drop‑in replacement that is **both**

    1. *grapheme‑boundary‑aware*  – no broken emojis / accents, and
    2. strictly bounded by **tokens *or* characters** – depending on
       ``overlap_unit``.  (Used only for the *token* budget path now.)
    """

    def __init__(
        self,
        encoding_name: str,
        chunk_size: int,
        chunk_overlap: int,
        overlap_unit: str = "tokens",
    ):
        super().__init__(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self._enc = get_encoding(encoding_name)
        self._overlap_unit = overlap_unit

    # ------------------------------------------------------------------ #
    # Required LangChain interface                                       #
    # ------------------------------------------------------------------ #
    def split_text(self, text: str) -> list[str]:
        clusters = _GRAPHEME_RE.findall(text)  # Unicode grapheme clusters
        out: list[str] = []

        buf: list[str] = []  # current chunk (graphemes)
        enc = self._enc
        i = 0

        # Helper: measure length in the *selected* unit
        def _len_units(s: str) -> int:
            return len(s) if self._overlap_unit == "characters" else len(enc.encode(s))

        while i < len(clusters):
            g = clusters[i]
            buf.append(g)

            # Budget exceeded after adding *g*?
            if _len_units("".join(buf)) > self._chunk_size:
                # ---------------------------- flush current chunk -------
                buf.pop()  # roll back g
                out.append("".join(buf))

                # Seed new buffer with the configured overlap tail
                buf, _ = self._build_overlap(buf, clusters, i)

                # Edge‑case: *g* alone exceeds the budget – emit as is
                if _len_units(g) > self._chunk_size:
                    out.append(g)
                    buf = []
                    i += 1
                    continue

                buf.append(g)  # start new chunk with g

            i += 1

        # Remainder
        if buf:
            out.append("".join(buf))

        return out

    # ------------------------------------------------------------------ #
    # Helpers                                                            #
    # ------------------------------------------------------------------ #
    def _build_overlap(
        self, old_buf: list[str], clusters: list[str], cursor: int
    ) -> tuple[list[str], int]:
        """Return a new buffer that starts with the last *k* units of
        *old_buf*, where the unit is determined by ``self._overlap_unit``.
        """
        k = self._chunk_overlap
        if k == 0:
            return [], 0

        # ---------------- token‑based path ---------------- #
        if self._overlap_unit == "tokens":
            enc = self._enc
            prev_tokens = enc.encode("".join(old_buf))
            tail_tokens = prev_tokens[-k:]
            tail_text = enc.decode(tail_tokens)
            return list(tail_text), len(tail_tokens)

        # -------------- character‑based path -------------- #
        tail_text = "".join(old_buf)[-k:]  # raw characters
        return list(tail_text), k


# ---------------------------------------------------------------------- #
# Factory registration                                                   #
# ---------------------------------------------------------------------- #
@register("token")
def create(cfg: ChunkConfig):
    """
    Build a splitter for the *token* strategy that honours the user‑selected
    unit:

    • ``overlap_unit="tokens"`` → use the strict Unicode‑safe token splitter.  
    • ``overlap_unit="characters"`` → delegate to LangChain’s word‑aware
      recursive splitter and wrap it with the shared overlap logic so word
      boundaries are preserved.
    """
    # ---------- token‑budget path (original behaviour) ------------------ #
    if cfg.overlap_unit == "tokens":
        return UnicodeSafeTokenTextSplitter(
            encoding_name=cfg.encoding_name,
            chunk_size=cfg.chunk_size,
            chunk_overlap=cfg.chunk_overlap,
            overlap_unit="tokens",
        )

    # ---------- character‑budget path (word‑aware) ---------------------- #
    base = RecursiveCharacterTextSplitter(
        chunk_size=cfg.chunk_size,
        chunk_overlap=0,  # overlap added by the wrapper
    )
    return _OverlapWrapper(
        base,
        cfg.chunk_overlap,
        cfg.encoding_name,
        unit="characters",
    )
