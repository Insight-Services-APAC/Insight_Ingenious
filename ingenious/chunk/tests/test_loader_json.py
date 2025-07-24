import json, jsonlines
from ingenious.chunk.loader import load_documents


def test_loader_single_json_object(tmp_path):
    f = tmp_path / "single.json"
    f.write_text(json.dumps({"text": "hello"}), encoding="utf‑8")
    docs = load_documents(str(f))
    assert len(docs) == 1
    assert docs[0].page_content == "hello"
    assert docs[0].metadata["page"] == 0


def test_loader_json_array(tmp_path):
    payload = [{"text": "a"}, {"page_content": "b"}, {"body": "c"}]
    f = tmp_path / "array.json"
    f.write_text(json.dumps(payload), encoding="utf‑8")
    docs = load_documents(str(f))
    assert [d.page_content for d in docs] == ["a", "b", "c"]


def test_loader_jsonl(tmp_path):
    f = tmp_path / "stream.jsonl"
    with jsonlines.open(f, mode="w") as w:
        for k in ["foo", "bar", "baz"]:
            w.write({"body": k})
    docs = load_documents(str(f))
    assert [d.page_content for d in docs] == ["foo", "bar", "baz"]
