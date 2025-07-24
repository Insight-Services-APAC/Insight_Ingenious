from ingenious.chunk.strategy import _SPLITTER_REGISTRY, get

def test_all_strategies_registered():
    expected = {"recursive", "markdown", "token", "semantic"}
    assert expected.issubset(_SPLITTER_REGISTRY.keys())

def test_get_unknown_strategy():
    import pytest
    with pytest.raises(ValueError):
        get("does-not-exist")
