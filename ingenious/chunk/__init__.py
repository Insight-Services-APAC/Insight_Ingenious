"""
Top‑level convenience exports for the Ingenious chunking feature.
Keeps public symbols stable regardless of internal refactors.
"""
from .config import ChunkConfig    
from .factory import build_splitter
