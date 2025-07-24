"""
Hypothesis fuzzing – verify the overlap invariant for arbitrary inputs.
"""
import regex as re
from hypothesis import given, strategies as st
import tiktoken

from ingenious.chunk.utils.overlap import inject_overlap


@given(
    chunks=st.lists(
        st.text(min_size=1, max_size=60), min_size=2, max_size=6
    ),
    k=st.integers(min_value=1, max_value=12),
    unit=st.sampled_from(["tokens", "characters"]),
)
def test_inject_overlap_fuzz(chunks, k, unit):
    out = inject_overlap(chunks, k, unit=unit)
    enc = tiktoken.get_encoding("cl100k_base")

    assert len(out) == len(chunks)

    for i in range(1, len(out)):
        if unit == "characters":
            tail = out[i - 1][-k:]
            head = out[i][: k + 2]          # allow possible extra space
            assert head.lstrip().startswith(tail.lstrip())
        else:  # tokens
            tail_text = enc.decode(enc.encode(out[i - 1])[-k:])
            head_text = out[i][: len(tail_text) + 2]  # allow space token
            assert head_text.lstrip().startswith(tail_text.lstrip())

    # Ensure no broken Unicode graphemes were introduced
    grapheme = re.compile(r"\X", re.UNICODE)
    for s in out:
        for g in grapheme.findall(s):
            g.encode("utf-16", "strict")
