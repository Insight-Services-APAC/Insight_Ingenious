import pytest

_SAMPLE_TXT = "The quick brown fox jumps over the lazy dog.\n" * 80
_SAMPLE_MD = "# Title\n\nParagraph\n\n## Subtitle\n\nMore text."
_SAMPLE_UNICODE = "日本語123 😀 " * 40

@pytest.fixture(scope="session")
def sample_text(tmp_path_factory):
    p = tmp_path_factory.mktemp("data for test") / "doc.txt"
    p.write_text(_SAMPLE_TXT, encoding="utf-8")
    return p

@pytest.fixture(scope="session")
def sample_md(tmp_path_factory):
    p = tmp_path_factory.mktemp("data") / "doc.md"
    p.write_text(_SAMPLE_MD, encoding="utf-8")
    return p

@pytest.fixture(scope="session")
def unicode_text():
    return _SAMPLE_UNICODE
