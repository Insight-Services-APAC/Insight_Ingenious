"""
Insight Ingenious – unit tests for ``_iter_sources``
===================================================

This module validates :pyfunc:`ingenious.document_processing.cli._iter_sources`,
a small generator that **normalises arbitrary user input** (file paths,
directories, or URLs) into a pair of objects::

    (label: str, source: Union[bytes, pathlib.Path])

Branches under test
-------------------
1. **Local path**
   • *Single file* – yields exactly that file.
   • *Directory*  – discovers every ``*.pdf`` recursively via
     :pyfunc:`pathlib.Path.rglob`.

2. **Remote URL**
   • Downloads bytes with :pypi:`requests`.
   • Raises :class:`requests.HTTPError` for non-2×× responses.

3. **Directory filtering**
   • Ignores non-PDF files.
   • Yields nothing for an empty directory.

Why it matters
--------------
The helper feeds the *document-processing* CLI; any regression would manifest
as missing inputs or unexpected crashes in production.  Tests therefore stub
out network access and use tiny, synthetic fixture trees to run fast and
deterministically.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterator, Tuple

import pytest
from requests import HTTPError

from ingenious.document_processing.cli import _iter_sources

# --------------------------------------------------------------------------- #
# constants                                                                   #
# --------------------------------------------------------------------------- #
REMOTE_PDF_URL: str = (
    "https://densebreast-info.org/wp-content/uploads/2024/06/"
    "Patient-Fact-Sheet-English061224.pdf"
)


# --------------------------------------------------------------------------- #
# helpers                                                                     #
# --------------------------------------------------------------------------- #
class _StubResp:
    """
    Ultra-light substitute for :class:`requests.Response`.

    Used to monkey-patch :pyfunc:`requests.get` so that the *remote URL* branch
    of ``_iter_sources`` can be exercised **offline**.

    Attributes
    ----------
    content : bytes
        Body returned to client code.

    Notes
    -----
    Only the surface area required by ``_iter_sources`` is implemented
    (:pyattr:`content` and :pymeth:`raise_for_status`).
    """

    def __init__(self, payload: bytes, status_ok: bool = True) -> None:
        """
        Create a stub response.

        Parameters
        ----------
        payload
            Bytes exposed via :pyattr:`content`.
        status_ok, optional
            When *False* :pymeth:`raise_for_status` raises
            :class:`requests.HTTPError`.  Defaults to *True*.
        """
        self.content: bytes = payload
        self._status_ok: bool = status_ok

    def raise_for_status(self) -> None:  # noqa: D401
        """
        Mimic :pymeth:`requests.Response.raise_for_status`.

        Raises
        ------
        requests.HTTPError
            If the instance was created with ``status_ok=False``.
        """
        if not self._status_ok:
            raise HTTPError("404 – Not Found")


# --------------------------------------------------------------------------- #
# 1. local path / recursive directory                                         #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "scenario",
    ["single_file", "nested_dir"],
    ids=["file", "rglob"],
)
def test_iter_sources_local(scenario: str, tmp_path: Path, pdf_path: Path) -> None:
    """
    Validate discovery of **local** sources.

    ``single_file``
        A literal file path must be yielded unchanged.
    ``nested_dir``
        A directory containing the PDF somewhere below it must be searched
        recursively with :pyfunc:`Path.rglob`.

    Parameters
    ----------
    scenario
        Variant identifier.
    tmp_path
        Per-test temporary directory.
    pdf_path
        Fixture providing a reference PDF.
    """
    if scenario == "single_file":
        labels = [lbl for lbl, _ in _iter_sources(pdf_path)]
        assert str(pdf_path) in labels
    else:  # nested directory
        deep_dir = tmp_path / "deep"
        deep_dir.mkdir()
        cloned = deep_dir / pdf_path.name
        cloned.write_bytes(pdf_path.read_bytes())

        labels = [lbl for lbl, _ in _iter_sources(tmp_path)]
        assert str(cloned) in labels


# --------------------------------------------------------------------------- #
# 2. remote URL branch                                                        #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "ok",
    [True, False],
    ids=["200", "404"],
)
def test_iter_sources_remote(
    monkeypatch: pytest.MonkeyPatch,
    pdf_bytes: bytes,
    ok: bool,
) -> None:
    """
    Exercise the **remote URL** code-path.

    Cases
    -----
    *200* – returns a ``(label, bytes)`` tuple.
    *404* – raises :class:`requests.HTTPError`.

    Parameters
    ----------
    monkeypatch
        Pytest fixture for dynamic monkey-patching.
    pdf_bytes
        Raw PDF bytes supplied by a higher-level fixture.
    ok
        Simulated HTTP status (*True* ⇒ 200, *False* ⇒ 404).
    """
    import ingenious.document_processing.cli as cli_mod

    monkeypatch.setattr(
        cli_mod.requests,
        "get",
        lambda *_args, **_kwargs: _StubResp(pdf_bytes, status_ok=ok),
    )

    if ok:
        lbl, src = next(_iter_sources(REMOTE_PDF_URL))
        assert lbl.startswith("http")
        assert isinstance(src, bytes)
    else:
        with pytest.raises(HTTPError):
            next(_iter_sources(f"{REMOTE_PDF_URL}?missing"))


# --------------------------------------------------------------------------- #
# 3. directory filtering & empty dir                                          #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    ("fixture_builder", "expectation"),
    [
        ("empty", 0),
        ("mixed", 1),
    ],
    ids=["empty_dir", "filter_non_pdf"],
)
def test_iter_sources_directory_filter(
    fixture_builder: str,
    expectation: int,
    tmp_path: Path,
    pdf_path: Path,
) -> None:
    """
    Ensure directory filtering behaves as documented.

    ``empty_dir``
        An empty directory must exhaust the iterator.
    ``filter_non_pdf``
        Only ``*.pdf`` files are yielded; spurious suffixes are ignored.

    Parameters
    ----------
    fixture_builder
        Chooses the directory layout to construct.
    expectation
        Expected number of yielded items.
    tmp_path
        Pytest temporary directory.
    pdf_path
        Fixture providing a sample PDF.
    """
    if fixture_builder == "empty":
        root = tmp_path
    else:  # mixed directory: one PDF and one .txt
        root = tmp_path
        (root / "note.txt").write_text("ignore me")
        wanted = root / pdf_path.name
        wanted.write_bytes(pdf_path.read_bytes())

    results: Iterator[Tuple[str, object]] = _iter_sources(root)
    labels = [lbl for lbl, _ in results]

    assert len(labels) == expectation
    if labels:
        assert labels[0].endswith(".pdf")
