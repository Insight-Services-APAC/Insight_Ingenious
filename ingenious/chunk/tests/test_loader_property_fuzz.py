"""
Quick Hypothesis check: arbitrary UTF‑8 text survives the TXT loader path.
"""
from __future__ import annotations

from hypothesis import given, settings, HealthCheck, strategies as st, assume

from ingenious.chunk.loader import load_documents


def _norm(s: str) -> str:  # replace CR and CRLF with LF
    return s.replace("\r\n", "\n").replace("\r", "\n")


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(payload=st.text(min_size=1, max_size=80))
def test_loader_random_txt(tmp_path, payload: str):
    f = tmp_path / "rand.txt"
    f.write_text(payload, encoding="utf-8")

    assume(not payload.isspace())          # loader skips blank/white‑only pages
    docs = load_documents(str(f))

    assert _norm(docs[0].page_content) == _norm(payload)
