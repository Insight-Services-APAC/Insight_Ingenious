# ingenious/chunk/tests/utils/test_overlap_edgecases.py
import pytest
from ingenious.chunk.utils.overlap import inject_overlap


def test_inject_overlap_invalid_unit():
    with pytest.raises(ValueError, match="unit must be 'tokens'"):
        inject_overlap(["a", "b"], k=1, unit="bytes")


def test_inject_overlap_zero_k_returns_original():
    original = ["foo", "bar"]
    assert inject_overlap(original, k=0) == original


def test_soft_delimiter_guard():
    """
    When the boundary has two non‑whitespace chars the helper must insert
    exactly **one** space.
    """
    res = inject_overlap(["abc", "def"], k=3, unit="characters")
    # chunk[1] == 'abc def'
    assert res[1][:4] == "abc "
    assert res[0].endswith("abc")
