# ingenious/chunk/tests/utils/test_inject_overlap_doc.py
from langchain_core.documents import Document
from ingenious.chunk.utils.overlap import inject_overlap

def test_inject_overlap_documents_preserve_metadata():
    """Every output Document keeps its original metadata and overlap invariant."""
    docs = [
        Document(page_content="ABCDEFGHIJ", metadata={"id": 0}),
        Document(page_content="KLMNOPQRST", metadata={"id": 1}),
    ]
    k = 3
    out = inject_overlap(docs, k=k, unit="characters")

    # 1️⃣ metadata round-trip
    assert out[0].metadata == docs[0].metadata
    assert out[1].metadata == docs[1].metadata

    # 2️⃣ overlap invariant for documents
    assert out[0].page_content[-k:] == out[1].page_content[:k]
