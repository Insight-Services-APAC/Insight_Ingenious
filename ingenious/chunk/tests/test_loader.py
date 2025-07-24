from ingenious.chunk.loader import load_documents

def test_load_txt(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("hello world", encoding="utf-8")
    docs = load_documents(str(f))
    assert len(docs) == 1
    assert docs[0].page_content == "hello world"
    assert docs[0].metadata["source"].endswith("a.txt")

def test_load_directory(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.md").write_text("# Title\nBody", encoding="utf-8")
    docs = load_documents(str(tmp_path))
    assert len(docs) == 1
    assert "# Title" in docs[0].page_content

def test_load_glob(tmp_path):
    for n in range(3):
        (tmp_path / f"{n}.txt").write_text(str(n), encoding="utf-8")
    docs = load_documents(str(tmp_path / "*.txt"))
    assert {d.page_content for d in docs} == {"0", "1", "2"}

def test_load_empty(tmp_path):
    import pytest
    with pytest.raises(FileNotFoundError):
        load_documents(str(tmp_path / "no_files_here"))
