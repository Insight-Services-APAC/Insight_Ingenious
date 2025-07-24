"""
Factory helper: build_splitter(cfg) → LangChain‑compatible TextSplitter
"""
# pragma: no cover
from __future__ import annotations

import json
import os
from functools import lru_cache

from .config import ChunkConfig
from .strategy import _SPLITTER_REGISTRY, get as _get_strategy

__all__ = ["build_splitter"]

# --------------------------------------------------------------------------- #
# Cache size control                                                          #
# --------------------------------------------------------------------------- #
# Bound the number of cached splitter instances to avoid unbounded memory
# usage in long‑running services.  The default (64) targets typical multi‑
# tenant API workers but can be tuned via the environment variable
# ``INGENIOUS_SPLITTER_CACHE``.
_CACHE_SIZE: int = int(os.getenv("INGENIOUS_SPLITTER_CACHE", "64"))

# --------------------------------------------------------------------------- #
# Internal – LRU‑cached constructor                                           #
# --------------------------------------------------------------------------- #
@lru_cache(maxsize=_CACHE_SIZE)
def _cached_build_splitter(cfg_json: str):
    """Return a cached (or freshly built) splitter for *cfg_json*.

    Parameters
    ----------
    cfg_json : str
        Canonical JSON representation (sorted keys, no ``None`` fields) of a
        :class:`~ingenious.chunk.config.ChunkConfig`.  Using a JSON string
        sidesteps hashability issues caused by mutable types such as ``list``.
    """
    cfg_dict = json.loads(cfg_json)
    cfg = ChunkConfig(**cfg_dict)
    return _get_strategy(cfg.strategy)(cfg)


# --------------------------------------------------------------------------- #
# Public façade                                                               #
# --------------------------------------------------------------------------- #
def build_splitter(cfg: ChunkConfig):
    """Return a splitter instance for *cfg*.

    * Non‑semantic strategies are cached (bounded by ``_CACHE_SIZE``).
    * Semantic strategy always returns a **fresh** instance so that tests that
      monkey‑patch the embedding backend get deterministic results.

    Raises
    ------
    ValueError
        When ``cfg.strategy`` is not one of the registered names.
    """
    # ── 1. Fast‑fail on unknown strategy ───────────────────────────────────
    if cfg.strategy not in _SPLITTER_REGISTRY:
        raise ValueError(f"Unknown chunking strategy: {cfg.strategy}")

    # ── 2. Always create a fresh semantic splitter ─────────────────────────
    if cfg.strategy == "semantic":
        return _get_strategy(cfg.strategy)(cfg)

    # ── 3. Cached path for pure‑Python strategies ──────────────────────────
    cfg_dict = cfg.model_dump(exclude_none=True)
    key = json.dumps(cfg_dict, sort_keys=True, separators=(",", ":"))
    return _cached_build_splitter(key)
