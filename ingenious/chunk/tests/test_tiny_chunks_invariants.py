# ingenious/chunk/tests/test_tiny_chunks_invariants.py
import json
from pathlib import Path
from tiktoken import get_encoding

ENC = get_encoding("cl100k_base")
CHUNK = 20
K = 10
HARD_CAP = CHUNK + K + 1           # 31

def _load(path: Path):
    with path.open(encoding="utf-8") as fp:
        return [json.loads(line) for line in fp]

def test_chunk_size_and_overlap():
    recs = _load(Path("tiny_chunks.jsonl"))

    # 1️⃣ every chunk ≤ 31 tokens
    assert all(len(ENC.encode(r["text"])) <= HARD_CAP for r in recs)

    # 2️⃣ overlap only within the *same* source + page
    for prev, curr in zip(recs, recs[1:]):
        if prev["meta"]["page"] == curr["meta"]["page"]:
            tail = ENC.encode(prev["text"])[-K:]
            head = ENC.encode(curr["text"])[:K]       # exactly K, no +2 needed
            assert tail == head, (
                f"overlap mismatch within page {prev['meta']['page']}"
            )
