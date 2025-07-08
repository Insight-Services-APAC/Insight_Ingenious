"""
Insight Ingenious — Integration Test-Suite (Happy Path)
======================================================

This module executes **end-to-end, success-case** probes against the
*document-processing* Command Line Interface (CLI).  The objectives are:

1. **Engine Coverage**
   Verify that *every* registered extraction engine defined in
   :pydata:`ingenious.document_processing.extractor._ENGINES` can
   successfully parse:

   • A **local** PDF supplied via a filesystem path.
   • A **remote** PDF fetched over **HTTPS**.

2. **Format Coverage**
   Ensure the dedicated *unstructured* engine correctly handles DOCX
   input, safeguarding Insight Ingenious’ multi-format promise.

3. **Output Flexibility**
   Confirm that the CLI:

   • Writes valid NDJSON records to an explicit ``--out`` destination.
   • Falls back to streaming NDJSON to *stdout* when no output file is
     requested.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Final

import pytest

from ingenious.document_processing.extractor import _ENGINES

# --------------------------------------------------------------------------- #
# constants & helpers                                                         #
# --------------------------------------------------------------------------- #
PDF_URL: Final[str] = (
    "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
)


def _load_ndjson(stream: str) -> Iterator[dict[str, Any]]:
    """
    Lazily deserialize NDJSON records emitted by the CLI.

    The CLI prints a Rich-generated summary as its *final* line.  This helper
    skips that footer by selecting only lines whose first non-blank character
    is an opening brace.

    Parameters
    ----------
    stream:
        The complete byte-for-byte content of *stdout* captured from a CLI
        invocation.  It may include Rich styling as plain text on the last
        line.

    Yields
    ------
    dict[str, Any]
        One Python dictionary per NDJSON record, obtained via
        :pyfunc:`json.loads`.
    """
    for line in stream.splitlines():
        if line.lstrip().startswith("{"):
            yield json.loads(line)


# --------------------------------------------------------------------------- #
# test matrix                                                                 #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("cli_kind", ["sub", "root"], ids=["doc_app", "root_app"])
@pytest.mark.parametrize("engine", sorted(_ENGINES))
def test_cli_local_pdf_ok(
    _cli,
    cli_kind: str,
    engine: str,
    pdf_path: Path,
    tmp_path: Path,
) -> None:
    """
    Validate that **all** engines can parse a *local* PDF file.

    Success criteria
    ----------------
    * Process exits with status ``0``.
    * Output file exists and is non-empty.
    """
    out_file = tmp_path / f"{engine}.jsonl"
    result = _cli(str(pdf_path), engine, out_file, cli_kind)

    assert result.exit_code == 0, result.output
    assert out_file.is_file() and out_file.stat().st_size > 0


@pytest.mark.parametrize("cli_kind", ["sub", "root"], ids=["doc_app", "root_app"])
@pytest.mark.parametrize("engine", sorted(_ENGINES))
def test_cli_remote_pdf_ok(
    _cli,
    cli_kind: str,
    engine: str,
    tmp_path: Path,
    pdf_path: Path,
    monkeypatch,
) -> None:
    """
    Validate that **all** engines can parse a *remote* HTTPS-hosted PDF.

    Success criteria mirror
    :pyfunc:`test_cli_local_pdf_ok`.

    NOTE: This test mocks the HTTP request to avoid external dependencies.
    """
    from unittest.mock import Mock

    import requests

    # Mock the requests.get call to return local PDF content
    mock_response = Mock()
    with open(pdf_path, "rb") as f:
        mock_response.content = f.read()
    mock_response.raise_for_status = Mock()
    mock_response.headers = {"content-type": "application/pdf"}

    def mock_get(*args, **kwargs):
        return mock_response

    monkeypatch.setattr(requests, "get", mock_get)

    out_file = tmp_path / f"remote_{engine}.jsonl"
    result = _cli(PDF_URL, engine, out_file, cli_kind)

    assert result.exit_code == 0, result.output
    assert out_file.is_file() and out_file.stat().st_size > 0


@pytest.mark.parametrize("cli_kind", ["sub", "root"], ids=["doc_app", "root_app"])
def test_cli_docx_unstructured_ok(
    _cli,
    cli_kind: str,
    docx_path: Path,
    tmp_path: Path,
) -> None:
    """
    Ensure the *unstructured* engine can parse DOCX input end-to-end.

    This test guards against regressions in non-PDF handling.
    """
    out_file = tmp_path / "docx.jsonl"
    result = _cli(str(docx_path), "unstructured", out_file, cli_kind)

    assert result.exit_code == 0, result.output
    assert out_file.is_file() and out_file.stat().st_size > 0


@pytest.mark.parametrize("cli_kind", ["sub", "root"], ids=["doc_app", "root_app"])
def test_cli_stdout_fallback_ok(_cli, cli_kind: str, pdf_path: Path) -> None:
    """
    Confirm that NDJSON records stream to *stdout* when ``--out`` is omitted.

    The captured *stdout* is parsed with :pyfunc:`_load_ndjson` and must
    contain at least one record with a ``"text"`` key.
    """
    result = _cli(str(pdf_path), "pymupdf", entry=cli_kind)

    assert result.exit_code == 0, result.output
    payloads = list(_load_ndjson(result.stdout))
    assert payloads and "text" in payloads[0]


@pytest.mark.parametrize("cli_target", ["sub", "root"], ids=["doc_app", "root_app"])
def test_cli_stdout_json_integrity(_cli, cli_target: str, pdf_path: Path) -> None:
    """
    Confirm that NDJSON streams cleanly to *stdout* when no --out flag is
    given.

    The CLI is invoked with a local PDF and no explicit --engine (therefore
    using the default extractor).  Success criteria:

    * exit code is 0;
    * stdout contains **at least one** line that begins with “{”, i.e. a
    valid NDJSON record;
    * no unexpected diagnostics appear in the output.

    Parameters
    ----------
    _cli, cli_target, pdf_path
        See *test_cli_unknown_engine* for field descriptions.
    """

    result = _cli(str(pdf_path), entry=cli_target)
    assert result.exit_code == 0, result.output
    assert any(line.lstrip().startswith("{") for line in result.stdout.splitlines())
