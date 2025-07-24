"""
Universal file-to-LangChain-Document loader used by the chunk CLI.

Features
--------
• Lightweight formats: TXT, Markdown, JSON Lines / ND-JSON, plain JSON  
• Heavyweight formats: PDF, DOCX, etc. via `unstructured.partition.auto`  
• Returns a `list[Document]` ready for LangChain splitters.
"""
from __future__ import annotations

import json
from glob import glob
from pathlib import Path
from typing import Iterable, List

import jsonlines
from langchain_core.documents import Document


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #
def _partition_with_unstructured(path: Path) -> str:
    """Heavy-weight parser for complex formats (PDF, DOCX, etc.)."""
    from unstructured.partition.auto import partition  # type: ignore

    elements = partition(filename=str(path))
    return "\n".join(el.text for el in elements if getattr(el, "text", None))


def _iter_files(pattern: str) -> Iterable[Path]:
    """
    Expand a single glob / path into concrete files.

    • Existing file       → yield it  
    • Existing directory  → yield all **files** beneath (recursively)  
    • Otherwise treat pattern as a glob (supports ** recursion)
    """
    p = Path(pattern)
    if p.exists():
        if p.is_file():
            yield p
        else:  # directory – filter out sub-directories early
            for fp in p.rglob("*"):
                if fp.is_file():
                    yield fp
    else:  # glob pattern
        for match in glob(pattern, recursive=True):
            mp = Path(match)
            if mp.is_file():
                yield mp


# --------------------------------------------------------------------------- #
# Public API                                                                  #
# --------------------------------------------------------------------------- #
def load_documents(pattern: str) -> List[Document]:
    """
    Parse files matching *pattern* into LangChain `Document` objects.

    Parameters
    ----------
    pattern : str
        File path, directory, or glob pattern (e.g. ``docs/**/*.pdf``).

    Returns
    -------
    list[Document]
        Parsed documents ready for chunking.
    """
    docs: List[Document] = []

    for file_path in _iter_files(pattern):
        # Secondary guard – skip directories that slipped through
        if file_path.is_dir():
            continue

        try:
            ext = file_path.suffix.lower()

            # ───────────────── light-weight JSON variants ────────────────── #
            if ext in {".jsonl", ".ndjson"}:
                # ND-JSON: each line is an object describing one “page”
                with jsonlines.open(file_path) as rdr:
                    for i, rec in enumerate(rdr):
                        txt = (
                            rec.get("text")
                            or rec.get("page_content")
                            or rec.get("body", "")
                        )
                        if txt.strip():
                            docs.append(
                                Document(
                                    page_content=txt,
                                    metadata={
                                        "source": str(file_path),
                                        "page": i,
                                    },
                                )
                            )
                continue  # file consumed → next file

            if ext == ".json":
                # Either a single object OR a list/array of objects
                payload = json.loads(file_path.read_text(encoding="utf-8"))
                records = payload if isinstance(payload, list) else [payload]

                for i, rec in enumerate(records):
                    txt = (
                        rec.get("text")
                        or rec.get("page_content")
                        or rec.get("body", "")
                    )
                    if txt.strip():
                        docs.append(
                            Document(
                                page_content=txt,
                                metadata={
                                    "source": str(file_path),
                                    "page": i,
                                },
                            )
                        )
                continue  # file consumed

            # ───────────────── traditional plain-text formats ────────────── #
            if ext in {".txt", ".md", ".markdown"}:
                text = file_path.read_text(encoding="utf-8", errors="ignore")
            else:  # heavyweight formats (PDF, DOCX, …)
                text = _partition_with_unstructured(file_path)

            if not text.strip():
                continue  # skip empty parses

            docs.append(
                Document(
                    page_content=text,
                    metadata={"source": str(file_path.resolve())},
                )
            )

        except Exception as exc:  # log-and-continue robustness
            print(f"[load_documents] Warning: {file_path} skipped ({exc})")

    if not docs:
        raise FileNotFoundError(f"No parsable documents found for {pattern!r}")

    return docs
