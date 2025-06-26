"""
Insight Ingenious — extractor-registry unit tests
================================================

The **extractor registry** in
:pydata:`ingenious.document_processing.extractor._ENGINES` connects human-readable
engine keys (``"pymupdf"``, ``"pdfminer"``, …) with *fully qualified* import
specifiers in the ``"pkg.mod:Class"`` format.  The mapping powers dynamic
resolution in the document-processing stack, so any corruption would surface as
run-time import errors or duplicate extractor instances.

This test-suite guards against three failure classes:

1. **Importability**

   • Every dotted path must be importable.
   • The module must expose the advertised class.

2. **Singleton cache integrity**

   :pyfunc:`ingenious.document_processing.extractor._load` must behave like a
   memoised factory, returning **the same Python object** on successive calls
   with an identical key.

3. **Error handling**

   Passing an unknown key to :pyfunc:`_load` must raise :class:`ValueError`
   rather than a cryptic import error or ``KeyError``.
"""

from __future__ import annotations

from importlib import import_module
from typing import List

import pytest

from ingenious.document_processing.extractor import _ENGINES, _load

# --------------------------------------------------------------------------- #
# constants                                                                   #
# --------------------------------------------------------------------------- #
ENGINES: List[str] = sorted(_ENGINES)  # deterministic parametrisation order


# --------------------------------------------------------------------------- #
# 1. every dotted path must be importable                                     #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    ("engine_name", "dotted_path"),
    sorted(_ENGINES.items()),
    ids=lambda kv: kv[0],
)
def test_registry_importable(engine_name: str, dotted_path: str) -> None:
    """
    Validate that registry entry *dotted_path* is importable.

    Parameters
    ----------
    engine_name
        Registry key (e.g. ``"pymupdf"``) used for assertion messaging.
    dotted_path
        Value from :pydata:`_ENGINES` in ``"module:Class"`` form.

    Raises
    ------
    AssertionError
        If the module cannot be imported or if it does not expose the
        advertised class.
    """
    module_path, class_name = dotted_path.split(":", 1)
    module = import_module(module_path)

    assert hasattr(module, class_name), (
        f"{engine_name}: expected attribute {class_name!r} in module {module_path!r}"
    )


# --------------------------------------------------------------------------- #
# 2. _load must act as a **singleton cache**                                  #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("engine_name", ENGINES, ids=ENGINES)
def test_registry_singleton(engine_name: str) -> None:
    """
    Confirm that :pyfunc:`_load` is memoised per engine key.

    Parameters
    ----------
    engine_name
        Key from the extractor registry.
    """
    first = _load(engine_name)
    second = _load(engine_name)

    assert first is second, (
        f"_load({engine_name!r}) returned different objects — singleton cache broken"
    )


# --------------------------------------------------------------------------- #
# 3. unknown engine names must raise ValueError                               #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "bad_name",
    ["", "does-not-exist", "pymUDF", "123"],
    ids=["empty", "nonsense", "typo", "numeric"],
)
def test_registry_rejects_unknown(bad_name: str) -> None:
    """
    Ensure that unknown keys produce a clean :class:`ValueError`.

    Parameters
    ----------
    bad_name
        Engine name *not* present in the registry.

    Raises
    ------
    AssertionError
        If :pyfunc:`_load` fails to raise the expected exception.
    """
    with pytest.raises(ValueError):
        _load(bad_name)
