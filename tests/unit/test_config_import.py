def test_config_import():
    """Test that we can import Config."""
    from ingenious.common.config.config import Config

    assert Config is not None
