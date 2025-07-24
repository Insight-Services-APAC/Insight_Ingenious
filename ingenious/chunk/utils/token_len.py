"""Fast, cached token‑length helper used by multiple strategies."""
from __future__ import annotations

from functools import lru_cache

from tiktoken import get_encoding


@lru_cache(maxsize=None)
def _enc(name: str):
    """Return (and memoise) a tiktoken encoding instance."""
    return get_encoding(name)


def token_len(text: str, enc_name: str = "cl100k_base") -> int:
    """Number of tokens in *text* for the requested encoding."""
    return len(_enc(enc_name).encode(text))
