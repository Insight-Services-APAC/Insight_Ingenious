"""
Insight Ingenious – *document-processing* package bootstrap
==========================================================

This module exposes a **single public helper**—:pyfunc:`extract`—that acts as
the canonical entry-point for *all* document-processing workflows.  Callers
should import directly from :pymod:`ingenious.document_processing` without
knowing (or caring) about the underlying engine hierarchy:

>>> from ingenious.document_processing import extract
>>> for element in extract("contract.pdf"):
...     process(element)

Motivation
----------

* **Discoverability** – IDEs reveal ``extract`` immediately after typing
  ``document_processing.``.
* **Encapsulation** – Engine selection and configuration remain internal.
* **Testability** – A dedicated alias for :pymod:`requests` allows unit tests
  to monkey-patch network I/O *before* any engine code is imported.

"""

from __future__ import annotations

# ──────────────── standard library ────────────────
import sys
from importlib import import_module
from typing import Any, Callable, Iterable

# ──────────────── third-party ────────────────
import requests


def _expose_requests_for_testing() -> None:
    """
    Inject the :pymod:`requests` client under the current package namespace.

    The alias ``ingenious.document_processing.requests`` is *always* created,
    allowing test suites to monkey-patch the HTTP layer *before* any downstream
    import triggers real network traffic.

    The operation is **idempotent**—calling the function multiple times has no
    side effects beyond the first invocation.
    """
    alias: str = f"{__name__}.requests"

    # Make the alias importable: ``import ingenious.document_processing.requests``
    if alias not in sys.modules:
        sys.modules[alias] = requests

    # Expose the same object as an attribute on this package for easy patching
    if not hasattr(sys.modules[__name__], "requests"):
        setattr(sys.modules[__name__], "requests", requests)


# Ensure the patch-point is available as early as possible
_expose_requests_for_testing()

# --------------------------------------------------------------------------- #
# Public lazy re-export                                                       #
# --------------------------------------------------------------------------- #

extract: Callable[..., Iterable[dict[str, Any]]] = getattr(  # type: ignore[index]
    import_module("ingenious.document_processing.extractor"),
    "extract",
)

__all__: list[str] = ["extract"]
