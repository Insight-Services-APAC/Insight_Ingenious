"""Insight Ingenious – Document‑processing CLI
===========================================
Entry‑point for **command‑line** interaction with the document‑processing
sub‑system.  The module registers a :pydata:`~typer.Typer` application
(:pydata:`doc_app`) that forwards user input to the high‑level extractor helper
:pyfunc:`ingenious.document_processing.extractor.extract`.

Quick start
-----------
Run the extractor against a local or remote source and print blocks as NDJSON::

    ingen_cli document-processing <SOURCE> [--engine pymupdf] [--out out.jsonl]

Where *SOURCE* may be one of:

* Absolute or relative **file path** (PDF, DOCX, etc.).
* **Directory** – recursively (case-insensitively) processes allowed files.
* **HTTP/S URL** – downloads the resource first (30‑second timeout).

Design principles
-----------------
1. **Zero‑config** – Sensible defaults allow casual users to extract a document
   with a single command.
2. **Streaming‑friendly** – Each element is written as a single NDJSON line to
   enable Unix pipeline composition and delta uploads.
3. **Backend‑agnostic** – The ``--engine`` flag maps directly to the extractor
   engine keyword, decoupling CLI usability from engine implementation.

High‑level flow
~~~~~~~~~~~~~~~
#. *User* invokes the CLI with a *path/URL* argument.
#. :pyfunc:`_iter_sources` converts that argument into a stream of
   ``(label, src)`` pairs, where *src* is suitable input for the extractor.
#. :pyfunc:`extract_cmd` iterates through every block produced by
   :pydata:`_extract`, appends a ``source`` annotation, and writes the element
   to the NDJSON *sink*.
#. On completion, a Rich‑coloured summary is printed.

Module‑level attributes
~~~~~~~~~~~~~~~~~~~~~~~
URL_RE
    Compiled regular expression used to detect *HTTP/S* URLs.
extract
    Alias to :pyfunc:`ingenious.document_processing.extractor.extract` imported
    lazily at runtime.

Note
----
For OCR needs, use azdocint engine.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Iterable, Tuple, Union

import typer
from rich import print as rprint

from ingenious.document_processing.extractor import extract as _extract

# ---------------------------------------------------------------------------
# Typer application
# ---------------------------------------------------------------------------

doc_app: typer.Typer = typer.Typer(
    no_args_is_help=True,
    help="Extract structured text from local or remote PDFs, DOCX documents, PNG images, and other supported files.",
)

doc_app.__doc__ = "CLI group housing document‑processing commands."

# ---------------------------------------------------------------------------
# Constants & regexes
# ---------------------------------------------------------------------------

URL_RE: re.Pattern[str] = re.compile(r"^https?://", re.I)

_SUPPORTED_SUFFIXES: set[str] = {
    ".pdf",
    ".docx",
    ".pptx",
    ".png",
    ".jpg",
    ".jpeg",
    ".tiff",
    ".tif",
}

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _iter_sources(arg: Union[str, Path]) -> Iterable[Tuple[str, Union[bytes, Path]]]:
    """Yield (label, src) pairs for URLs, files, or directories.

    The directory branch now discovers every file whose suffix
    matches one of the extensions required by the registered
    extractors (see _SUPPORTED_SUFFIXES).
    """
    # 1. Remote URL ------------------------------------------------------
    if isinstance(arg, str) and URL_RE.match(arg):
        from ingenious.document_processing.fetcher import fetch

        payload = fetch(arg)
        if payload is None:
            rprint(f"[red]✗ download failed or exceeds size limit → {arg}[/red]")
            return
        yield arg, payload
        return

    # 2. Local path(s) ---------------------------------------------------
    path = Path(arg)
    if path.is_file():
        yield str(path), path
        return

    # 2 b. Directory – recurse once per pattern
    if path.is_dir():
        for item in path.rglob("*"):
            if item.suffix.lower() in _SUPPORTED_SUFFIXES:
                yield str(item), item

    elif not path.exists():
        rprint(f"[red]✗ no such file or directory: {path}[/red]")


# ---------------------------------------------------------------------------
# CLI command
# ---------------------------------------------------------------------------


@doc_app.command("extract")
def extract_cmd(
    path: str = typer.Argument(..., help="PDF file, directory, or HTTP/S URL"),
    engine: str = typer.Option(
        "pymupdf",
        "--engine",
        "-e",
        help="Extractor backend (pymupdf, pdfminer, unstructured, …)",
    ),
    out: Path | None = typer.Option(
        None,
        "--out",
        "-o",
        help="Write NDJSON lines to this file instead of stdout.",
    ),
) -> None:
    """
    Write extraction results to *stdout* or a file in **NDJSON** format.
    """

    def _stream_blocks(src_path: str, sink) -> int:
        """Inner helper so we can share the write logic."""
        count = 0
        for label, src in _iter_sources(src_path):
            for element in _extract(src, engine=engine):
                element.setdefault("source", label)
                sink.write(f"{json.dumps(element, ensure_ascii=False)}\n")
                count += 1
        return count

    if out is None:
        # Directly stream to stdout – nothing to clean up.
        written = _stream_blocks(path, sys.stdout)
        target_label = "stdout"
    else:
        # 🔸 PRE‑CHECK: prevent IsADirectoryError & give a clear message
        if out.is_dir():
            rprint(f"[red]✗ {out} is a directory; please supply a file path[/red]")
            raise typer.Exit(code=2)

        # Wrap the entire extraction loop in a *with* block so that the file
        # descriptor is closed **even if `_extract` raises** midway through.
        with open(out, "w", encoding="utf-8") as sink:
            written = _stream_blocks(path, sink)
        target_label = out

    colour = "green" if written else "red"
    rprint(f"[{colour}]✓ wrote {written} elements → {target_label}[/{colour}]")
