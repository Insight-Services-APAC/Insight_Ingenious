# ingenious/chunk/utils/overlap.py
"""Inject **left‑side** overlap (tail of the previous chunk) into ordered chunks.

Supports both **tokens** and **raw characters** so every strategy can share the
same implementation.

*Input type* may be `list[str]` **or** `list[Document]`; output preserves type.

Soft‑delimiter rule
-------------------
When two chunks are joined and **both** the last character of the left part
*and* the first character of the right part are non‑whitespace, a single space
``" "`` is inserted.  This prevents unwanted byte‑pair‑encoding fusion when an
upstream splitter (traditionally ``MarkdownTextSplitter``) has trimmed
surrounding blanks.
"""
from __future__ import annotations

from typing import List, Sequence, TypeVar, overload

from langchain_core.documents import Document  # type: ignore

from .token_len import _enc

T = TypeVar("T", str, Document)

# --------------------------------------------------------------------------- #
# Public overloads                                                            #
# --------------------------------------------------------------------------- #
@overload
def inject_overlap(  # noqa: D401 (imperative name is intentional)
    chunks: List[str],
    k: int,
    *,
    unit: str = "tokens",
    enc_name: str = "cl100k_base",
) -> List[str]: ...
@overload
def inject_overlap(
    chunks: List[Document],
    k: int,
    *,
    unit: str = "tokens",
    enc_name: str = "cl100k_base",
) -> List[Document]: ...


# --------------------------------------------------------------------------- #
# Implementation                                                              #
# --------------------------------------------------------------------------- #
def inject_overlap(
    chunks: Sequence[T],
    k: int,
    *,
    unit: str = "tokens",
    enc_name: str = "cl100k_base",
) -> List[T]:
    """
    Return a **new** list where each chunk prepends *k* units taken from the
    end of the **previous output** chunk.

    Invariant::

        chunk[i-1][-k:] == chunk[i][:k]     for every i ≥ 1
    """
    if k == 0 or len(chunks) < 2:
        return list(chunks)

    if unit not in {"tokens", "characters"}:
        raise ValueError(
            f"unit must be 'tokens' or 'characters' (got {unit!r})"
        )

    enc = _enc(enc_name)

    def _tail(text: str) -> str:
        """Return the last *k* tokens or characters of *text*."""
        if unit == "characters":
            return text[-k:]
        return enc.decode(enc.encode(text)[-k:])

    def _concat(left: str, right: str) -> str:
        """Join *left* and *right*, inserting a space when both boundary
        characters are non‑whitespace (token‑fusion guard)."""
        if left and right and not left[-1].isspace() and not right[0].isspace():
            return f"{left} {right}"
        return f"{left}{right}"

    # ---------------------------------------------------------------------- #
    out: List[T] = []
    for chunk in chunks:
        content: str = (
            chunk if isinstance(chunk, str) else chunk.page_content
        )

        # Prepend tail from the **last output** chunk, not the raw input.
        if out:
            prev_txt = (
                out[-1]  # already overlapped
                if isinstance(out[-1], str)
                else out[-1].page_content
            )
            content = _concat(_tail(prev_txt), content)

        if isinstance(chunk, str):
            out.append(content)  # type: ignore[arg-type]
        else:  # Document
            out.append(
                Document(page_content=content, metadata=chunk.metadata)
            )  # type: ignore[arg-type]

    return out
