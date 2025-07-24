"""
Strategy plug‑in registry.

Each module under this folder should `register("name")(factory_fn)`.
`factory_fn(cfg: ChunkConfig) -> BaseTextSplitter` (LangChain interface)
"""
from typing import Callable, Dict
from importlib import import_module
from pathlib import Path

from ..config import ChunkConfig

_SPLITTER_REGISTRY: Dict[str, Callable[[ChunkConfig], "TextSplitter"]] = {}

def register(name: str):
    """Decorator used by strategy modules."""
    def _decorator(fn):
        _SPLITTER_REGISTRY[name] = fn
        return fn
    return _decorator

def get(name: str):
    try:
        return _SPLITTER_REGISTRY[name]
    except KeyError as exc:
        raise ValueError(f"Unknown chunking strategy: {name}") from exc

# --- auto‑import sibling strategy modules so decorators execute ------------
_cur_dir = Path(__file__).parent
for path in _cur_dir.glob("*.py"):
    if path.stem not in {"__init__"}:
        import_module(f"{__name__}.{path.stem}")
