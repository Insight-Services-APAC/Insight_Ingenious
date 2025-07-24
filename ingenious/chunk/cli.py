from __future__ import annotations

"""
Ingenious Chunking CLI
======================

Usage example::

    ingen chunk run test_files/pages_azdocint_pdf_scanned.jsonl \
        --strategy recursive --chunk-size 64 --chunk-overlap 32 \
        --output azdocint_chunks.jsonl
"""

from collections import defaultdict
from enum import Enum
import hashlib
import pathlib
from typing import Iterable

import jsonlines
import typer

from .config import ChunkConfig
from .factory import build_splitter
from .loader import load_documents

# --------------------------------------------------------------------------- #
# Enum with the allowed strategies                                            #
# --------------------------------------------------------------------------- #
class Strategy(str, Enum):
    recursive = "recursive"
    markdown = "markdown"
    token = "token"
    semantic = "semantic"


# --------------------------------------------------------------------------- #
# Shared “input‑file contract” text                                           #
# --------------------------------------------------------------------------- #
_CONTRACT = (
    "[bold]Input‑file contract[/bold]\n"
    "• .txt / .md / .markdown – entire file becomes one document\n"
    "• .json      – an OBJECT or ARRAY of objects; each object must have a\n"
    "               'text' | 'page_content' | 'body' key containing the page text\n"
    "• .jsonl / .ndjson – **one object per line** with the same keys above"
)

# --------------------------------------------------------------------------- #
# Typer app                                                                   #
# --------------------------------------------------------------------------- #
cli = typer.Typer(
    add_completion=False,
    rich_markup_mode="rich",
    help=f"Split files into chunked JSONL for RAG pipelines.\n\n{_CONTRACT}",
)

# --------------------------------------------------------------------------- #
# Root callback – nothing to do, but keeps Typer happy                        #
# --------------------------------------------------------------------------- #
@cli.callback(invoke_without_command=True, no_args_is_help=True)
def main() -> None:  # pragma: no cover
    """See sub‑commands for usage."""
    # No body required


# --------------------------------------------------------------------------- #
# `run` sub‑command                                                           #
# --------------------------------------------------------------------------- #
@cli.command(
    "run",
    help=f"Chunk files and write a JSONL output file.\n\n{_CONTRACT}",
)
def run(  # noqa: PLR0913 – many CLI knobs by design
    # -------------- positional input ------------------------------------
    path: str = typer.Argument(
        ...,
        metavar="PATH",
        help="File, directory, or glob pattern",
        rich_help_panel="Input‑file contract",
    ),
    # -------------- core knobs ------------------------------------------
    strategy: Strategy = typer.Option(
        Strategy.recursive,
        "--strategy",
        "-s",
        help="Chunking strategy to use.",
    ),
    chunk_size: int = typer.Option(
        1024, "--chunk-size", help="Max tokens/characters per chunk"
    ),
    chunk_overlap: int = typer.Option(
        128, "--chunk-overlap", help="Overlap between chunks (< size)"
    ),
    overlap_unit: str = typer.Option(
        "tokens",
        "--overlap-unit",
        help="Unit for overlap window: tokens | characters",
        rich_help_panel="Advanced",
    ),
    # -------------- advanced knobs --------------------------------------
    separators: str = typer.Option(
        "", help="Custom separators (join with '|') for recursive splitter"
    ),
    encoding_name: str = typer.Option(
        "cl100k_base", help="Tokenizer encoding for token splitter"
    ),
    embed_model: str = typer.Option(
        "", help="Embedding model for semantic splitter"
    ),
    azure_deployment: str = typer.Option(
        "", help="Azure OpenAI deployment for semantic splitter"
    ),
    # -------------- output ----------------------------------------------
    output: str = typer.Option(
        "chunks.jsonl", "--output", "-o", help="Output JSONL filepath"
    ),
) -> None:
    """Read files, split into chunks, and write them as JSONL."""

    # ------------------------------------------------------------------ #
    # Build config & splitter                                            #
    # ------------------------------------------------------------------ #
    cfg = ChunkConfig(
        strategy=strategy,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        overlap_unit=overlap_unit,
        separators=separators.split("|") if separators else None,
        encoding_name=encoding_name,
        embed_model=embed_model or None,
        azure_openai_deployment=azure_deployment or None,
    )
    splitter = build_splitter(cfg)

    # ------------------------------------------------------------------ #
    # Load documents                                                     #
    # ------------------------------------------------------------------ #
    docs = load_documents(path)

    # ------------------------------------------------------------------ #
    # Prepare output path                                                #
    # ------------------------------------------------------------------ #
    out_path = pathlib.Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    # Chunk                                                              #
    # ------------------------------------------------------------------ #
    try:
        chunks = splitter.split_documents(docs)
    except Exception as exc:  # pragma: no cover
        typer.secho(f"❌  Chunking failed: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

    # ------------------------------------------------------------------ #
    # Write                                                              #
    # ------------------------------------------------------------------ #
    try:
        _write_chunks_jsonl(chunks, out_path)
        typer.secho(
            f"✅ Wrote {len(chunks)} chunks → {out_path}",
            fg=typer.colors.GREEN,
        )
    except (OSError, jsonlines.Error) as exc:  # pragma: no cover
        typer.secho(
            f"❌  Failed to write output file: {exc}",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1) from exc


# --------------------------------------------------------------------------- #
# Helper – separated for isolated testing & mutation‑testing                  #
# --------------------------------------------------------------------------- #
def _write_chunks_jsonl(chunks: Iterable, out_path: pathlib.Path) -> None:
    """
    Persist *chunks* to *out_path* in deterministic‑ID JSONL format.

    • ID format:  ``<abs‑src>#p<page>.<pos>-<hash48>``
      – *abs‑src* : absolute, POSIX‑style source path (portable)  
      – *page*    : zero‑based page index from metadata (default 0)  
      – *pos*     : deterministic ordinal of the chunk within that page  
      – *hash48*  : first 12 hex chars (48 bits) of SHA‑256(page_content)

    The scheme stays **stable across reruns** yet guarantees uniqueness even
    when two chunks share identical text.
    """
    # Counter keyed by (source_path, page) → next position integer
    position_ctr: defaultdict[tuple[str, int], int] = defaultdict(int)

    with jsonlines.open(out_path, mode="w") as writer:
        for chunk in chunks:
            # 1️⃣ Normalised source path (portable, repeatable)
            src_path = (
                pathlib.Path(chunk.metadata.get("source", ""))
                .resolve()
                .as_posix()
            )

            # 2️⃣ Page number – default 0 when missing
            page = int(chunk.metadata.get("page", 0))

            # 3️⃣ Per‑page deterministic position
            pos = position_ctr[(src_path, page)]
            position_ctr[(src_path, page)] += 1

            # 4️⃣ Content hash (first 12 hex = 48 bits)
            digest = hashlib.sha256(
                chunk.page_content.encode("utf-8", "surrogatepass")
            ).hexdigest()[:12]

            # 5️⃣ Stable, globally‑unique ID
            chunk_id = f"{src_path}#p{page}.{pos}-{digest}"

            writer.write(
                {
                    "id": chunk_id,
                    "text": chunk.page_content,
                    "meta": chunk.metadata,
                }
            )
