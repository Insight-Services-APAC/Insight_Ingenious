from hypothesis import given, strategies as st
import tiktoken

from ingenious.chunk.utils.overlap import inject_overlap


@given(
    chunks=st.lists(
        st.text(min_size=1, max_size=120),
        min_size=2,
        max_size=6,
    ),
    k=st.integers(min_value=1, max_value=10),
)
def test_inject_overlap_token_invariant(chunks, k):
    """
    Invariant: the *decoded* text of the final ``k`` tokens of chunk *i‑1*
    must be replicated at the start of chunk *i* (except for an optional
    extra leading‑space token that some splitters introduce).

    We compare **text** rather than raw token IDs to align with other
    overlap‑consistency tests in the suite.
    """
    out = inject_overlap(chunks, k, unit="tokens")
    enc = tiktoken.get_encoding("cl100k_base")

    for prev, curr in zip(out, out[1:]):
        tail_text = enc.decode(enc.encode(prev)[-k:])
        # Allow an extra leading‑space token in the head segment
        head_text = curr[: len(tail_text) + 2]
        assert head_text.lstrip().startswith(tail_text.lstrip())
