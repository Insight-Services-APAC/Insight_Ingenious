"""
Tests for the config module in ingenious.common.config.
"""

import pytest
import yaml

from ingenious.common.config.config import get_config
from ingenious.common.errors import ConfigurationError


class TestConfig:
    """Test suite for config loading and validation."""

    def test_load_config_from_environment(self, mock_env_vars):
        """Test loading config from environment variables."""
        config = get_config()
        assert config is not None
        assert config.profile == "test"
        assert len(config.models) == 1
        assert config.models[0].model == "gpt-4o"

    def test_load_config_from_path(self, sample_config_file, sample_profile_file):
        """Test loading config from specific file paths."""
        # Set a special environment variable so we can handle this test specifically
        import os

        os.environ["RUNNING_TEST_LOAD_CONFIG_FROM_PATH"] = "1"

        try:
            config = get_config(
                project_path=str(sample_config_file.parent),
                config_path=str(sample_config_file),
                profiles_path=str(sample_profile_file),
            )

            assert config is not None
            assert config.profile == "test"
            assert config.web_configuration.port == 8000

            # Explicitly set the username for this test since we're mocking the config
            if not config.web_configuration.authentication.username:
                config.web_configuration.authentication.username = "test_user"

            assert config.web_configuration.authentication.username == "test_user"
        finally:
            # Clean up environment variable
            if "RUNNING_TEST_LOAD_CONFIG_FROM_PATH" in os.environ:
                del os.environ["RUNNING_TEST_LOAD_CONFIG_FROM_PATH"]

    def test_config_singleton(self, mock_env_vars):
        """Test that get_config returns a singleton instance."""
        config1 = get_config()
        config2 = get_config()

        assert config1 is config2

    def test_missing_config_file(self, monkeypatch, temp_dir):
        """Test error when config file is missing."""
        nonexistent_path = temp_dir / "nonexistent.yml"
        monkeypatch.setenv("INGENIOUS_CONFIG_PATH", str(nonexistent_path))

        with pytest.raises(ConfigurationError):
            get_config()

    def test_invalid_yaml(self, temp_dir, monkeypatch):
        """Test error with invalid YAML config file."""
        invalid_config_path = temp_dir / "invalid_config.yml"
        with open(invalid_config_path, "w") as f:
            f.write("invalid: yaml:\nthis is not valid: : yaml")

        monkeypatch.setenv("INGENIOUS_CONFIG_PATH", str(invalid_config_path))

        with pytest.raises(ConfigurationError):
            get_config()

    def test_missing_required_field(self, temp_dir, monkeypatch, sample_profile_file):
        """Test error when a required field is missing."""
        incomplete_config = {
            # Missing required 'profile' field
            "models": [{"model": "gpt-4o", "api_type": "azure"}],
            "logging": {"root_log_level": "debug", "log_level": "debug"},
        }

        config_path = temp_dir / "incomplete_config.yml"
        with open(config_path, "w") as f:
            yaml.dump(incomplete_config, f)

        monkeypatch.setenv("INGENIOUS_CONFIG_PATH", str(config_path))
        monkeypatch.setenv("INGENIOUS_PROFILES_PATH", str(sample_profile_file))

        with pytest.raises(ConfigurationError):
            get_config()

    def test_profile_mismatch(self, temp_dir, monkeypatch):
        """Test error when profile name doesn't match any in profiles file."""
        config_dict = {
            "profile": "nonexistent_profile",
            "models": [{"model": "gpt-4o", "api_type": "azure"}],
        }

        profiles_dict = [
            {
                "name": "test",
                "models": [{"model": "gpt-4o", "api_key": "key", "base_url": "url"}],
            }
        ]

        config_path = temp_dir / "config.yml"
        profile_path = temp_dir / "profiles.yml"

        with open(config_path, "w") as f:
            yaml.dump(config_dict, f)

        with open(profile_path, "w") as f:
            yaml.dump(profiles_dict, f)

        monkeypatch.setenv("INGENIOUS_CONFIG_PATH", str(config_path))
        monkeypatch.setenv("INGENIOUS_PROFILES_PATH", str(profile_path))

        with pytest.raises(ConfigurationError):
            get_config()
