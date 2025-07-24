# tests/utils/test_soft_delimiter_fuzz.py
from hypothesis import given, strategies as st
from ingenious.chunk.utils.overlap import inject_overlap


@given(
    left=st.text(min_size=1, max_size=10).filter(lambda s: not s[-1].isspace()),
    right=st.text(min_size=1, max_size=10).filter(lambda s: not s[0].isspace()),
)
def test_soft_delimiter_space_injected(left, right):
    out = inject_overlap([left, right], k=len(left), unit="characters")
    # out[1] should begin with left + SINGLE space + right[0]
    assert out[1].startswith(left + " " + right[0])
