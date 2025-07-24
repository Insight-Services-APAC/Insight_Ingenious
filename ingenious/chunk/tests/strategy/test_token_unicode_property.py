# ingenious/chunk/tests/strategy/test_token_unicode_property.py
import regex as re
from hypothesis import given, strategies as st
from tiktoken import get_encoding

from ingenious.chunk.strategy.langchain_token import UnicodeSafeTokenTextSplitter

ENC = "cl100k_base"
_GRAPHEME_RE = re.compile(r"\X", re.UNICODE)


@given(
    text=st.text(min_size=1, max_size=200),
    budget=st.integers(min_value=2, max_value=40),  # min-budget 2 avoids trivial 1-token clash
)
def test_unicode_splitter_fuzz(text: str, budget: int):
    splitter = UnicodeSafeTokenTextSplitter(
        encoding_name=ENC, chunk_size=budget, chunk_overlap=0
    )
    chunks = splitter.split_text(text)
    enc = get_encoding(ENC)

    for c in chunks:
        tokens = len(enc.encode(c))
        if tokens > budget:
            # Allowed only when the chunk is a *single grapheme* (edge-case path)
            assert len(_GRAPHEME_RE.findall(c)) == 1
        else:
            assert tokens <= budget

        # Always remains valid UTF-16
        c.encode("utf-16", "strict")
