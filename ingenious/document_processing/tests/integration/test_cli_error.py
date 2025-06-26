"""
Insight Ingenious – Integration test-suite for document-processing CLI
=====================================================================

This module exercises *negative-path* behaviour of the document-processing
command-line interface.  Each test intentionally drives the executable into
error conditions and validates that

* the process exits with a non-zero status,
* the raised exception type is appropriate, and
* the error message is informative for the user.

Covered scenarios
-----------------
1. **Unknown extractor engine** – passing an invalid ``--engine`` argument
   must raise ``ValueError`` and propagate the explanatory message upstream.

2. **Unwritable output destination** – directing ``--out`` to a path without
   write permission must abort the run rather than silently ignoring the
   failure.
"""

from __future__ import annotations

# ──────────── standard library ────────────
import os
import stat
from pathlib import Path

# ──────────── third-party ────────────
import pytest

# --------------------------------------------------------------------------- #
# helpers                                                                     #
# --------------------------------------------------------------------------- #


def _make_unwritable_dir(parent: Path) -> Path:
    """
    Create a child directory that the current process cannot write to.

    The helper is intended for negative-path I/O tests where an unwritable
    destination is required.  On Windows the permission model differs
    significantly, so the test invoking this helper is skipped rather than
    attempting unreliable permission juggling.

    Parameters
    ----------
    parent:
        A writable directory under which the helper will create an
        *unwritable* sub-directory named ``no_write``.

    Returns
    -------
    Path
        The *Path* object pointing to the newly created, unwritable directory.

    Notes
    -----
    * On POSIX the helper toggles the mode bits to read-and-execute only.
    * On Windows the function invokes ``pytest.skip`` because
      *chmod*-based permission editing cannot guarantee the same effect.
    """
    target = parent / "no_write"
    target.mkdir(exist_ok=True)

    if os.name == "nt":  # pragma: no cover – permission tweak unreliable on Windows
        pytest.skip("chmod-based unwritable directory not reliable on Windows")

    target.chmod(stat.S_IREAD | stat.S_IEXEC)
    return target


# --------------------------------------------------------------------------- #
# negative-path scenarios                                                     #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("cli_target", ["sub", "root"], ids=["doc_app", "root_app"])
def test_cli_unknown_engine(
    _cli, cli_target: str, pdf_path: Path, tmp_path: Path
) -> None:
    """
    Ensure an invalid ``--engine`` value aborts execution with *ValueError*.

    The test calls the CLI through the parametrised entry-point (either the
    standalone *doc_app* or the root aggregator) and confirms that:

    * exit code is non-zero,
    * ``ValueError`` is propagated, and
    * the error message contains the phrase “Unknown engine”.

    Parameters
    ----------
    _cli:
        Fixture supplied by *conftest.py* that executes the chosen Typer
        application via ``CliRunner``.
    cli_target:
        Either ``"sub"`` (direct call to document-processing app) or ``"root"``
        (invocation through the project-wide root app).
    pdf_path:
        Path to a small, valid PDF used as input.
    tmp_path:
        Temporary directory for test isolation.
    """
    out_file = tmp_path / "bad.jsonl"
    result = _cli(
        str(pdf_path),  # source
        engine="does_not_exist",
        out_file=out_file,
        entry=cli_target,  # "sub" or "root"
    )

    assert result.exit_code != 0
    assert isinstance(result.exception, ValueError)
    assert "Unknown engine" in str(result.exception)


@pytest.mark.parametrize("cli_target", ["sub", "root"], ids=["doc_app", "root_app"])
def test_cli_unwritable_out(
    _cli, cli_target: str, pdf_path: Path, tmp_path: Path
) -> None:
    """
    Verify that writing to an unwritable destination fails gracefully.

    The helper ``_make_unwritable_dir`` constructs an output directory with
    read-and-execute permission only.  The CLI should detect the inability to
    create or write the requested file and exit with a non-zero status code.

    Parameters
    ----------
    _cli, cli_target, pdf_path, tmp_path
        See *test_cli_unknown_engine* for field descriptions.
    """
    unwritable_dir = _make_unwritable_dir(tmp_path)
    result = _cli(
        str(pdf_path),  # source
        out_file=unwritable_dir,
        entry=cli_target,  # "sub" or "root"
    )

    assert result.exit_code != 0
