"""
Insight Ingenious — public ``extract`` wrapper equivalence tests
===============================================================

The public convenience function :pyfunc:`ingenious.document_processing.extract`
is intended to be a **thin pass-through** to the package’s default extractor
(currently *PyMuPDF*).  A silent divergence between the explicit engine path
and the implicit default would manifest as:

* Unexpected preprocessing or postprocessing steps being executed twice.
* Subtle behavioural drift if maintainers switch the default engine but forget
  to update callers.
* Bug reports that are hard to reproduce because the namespace import and the
  fully qualified call no longer match.

This unit test therefore asserts **functional equivalence** between:

1. An explicit engine selection (``engine="pymupdf"``).
2. The implicit default engine (no ``engine`` argument supplied).

Any inequality in the resulting element lists demands an immediate code
review.
"""

from ingenious.document_processing import extract


# --------------------------------------------------------------------------- #
# tests                                                                       #
# --------------------------------------------------------------------------- #
def test_public_extract_is_thin_wrapper(pdf_path):
    """
    Assert that explicit and implicit engine selection produce *identical*
    output.

    Procedure
    ---------
    1. Invoke :pyfunc:`ingenious.document_processing.extract` with
       ``engine="pymupdf"``.
    2. Invoke the same helper again *without* the ``engine`` argument,
       thereby relying on the package-level default.
    3. Compare the two element lists for deep equality.

    Parameters
    ----------
    pdf_path
        Fixture-provided path to a representative PDF document.

    Raises
    ------
    AssertionError
        If the lists differ, indicating that the wrapper performs extra work
        or that the default engine has drifted away from *pymupdf*.
    """
    els_engine = list(extract(pdf_path, engine="pymupdf"))
    els_default = list(extract(pdf_path))  # default engine

    assert els_engine == els_default, "explicit and default extractor outputs differ"
