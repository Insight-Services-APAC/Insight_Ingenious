def test_simple_mock():
    """A test with a simple mock of Config."""

    # Create a mock class
    class MockConfig:
        @staticmethod
        def get_config(*args, **kwargs):
            return MockConfig()

        def __init__(self):
            self.models = [MockModel()]

    class MockModel:
        def __init__(self):
            self.model = "mock-model"
            self.api_version = "mock-version"
            self.base_url = "https://mock-url.com"
            self.api_key = "mock-key"

    # Now use it in our test
    assert MockConfig is not None
    config = MockConfig.get_config()
    assert config is not None
    assert config.models[0].model == "mock-model"
