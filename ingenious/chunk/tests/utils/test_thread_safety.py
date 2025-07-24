"""
Basic thread-safety smoke test – helpers should be re-entrant.
"""
import concurrent.futures

from ingenious.chunk.utils.token_len import token_len
from ingenious.chunk.utils.overlap import inject_overlap


def _task(idx: int):
    txt = f"lorem ipsum {idx} " * 40
    token_len(txt)
    inject_overlap([txt[:100], txt[100:]], k=5)


def test_helpers_thread_safe():
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
        list(pool.map(_task, range(250)))
