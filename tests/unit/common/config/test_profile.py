"""
Tests for the profile module in ingenious.common.config.
"""

import pytest
import yaml

from ingenious.common.config.profile import Profiles
from ingenious.common.errors import ConfigurationError


class TestProfiles:
    """Test suite for profile configuration."""

    def test_load_profiles_from_file(self, sample_profile_file):
        """Test loading profiles from a file."""
        profiles = Profiles(sample_profile_file)

        assert profiles is not None
        assert len(profiles.profiles) == 1
        assert profiles.profiles[0].name == "test"
        assert profiles.profiles[0].models[0].api_key == "test_api_key"

    def test_from_yaml_str(self):
        """Test creating profiles from YAML string."""
        yaml_str = """
        - name: test
          models:
            - model: gpt-4o
              api_key: test_key
              base_url: https://test.url
          chat_history:
            database_connection_string: ""
          azure_search_services:
            - service: test_service
              key: test_key
          azure_sql_services:
            database_connection_string: ""
          receiver_configuration:
            enable: false
            api_url: ""
            api_key: ""
          chainlit_configuration:
            enable: false
            authentication:
              enable: false
          web_configuration:
            authentication:
              enable: false
        """

        profiles = Profiles.from_yaml_str(yaml_str)

        assert profiles is not None
        assert len(profiles) == 1
        assert profiles[0].name == "test"
        assert profiles[0].models[0].api_key == "test_key"

    def test_get_profile(self, sample_profile_file):
        """Test getting a specific profile by name."""
        profiles = Profiles(sample_profile_file)

        profile = profiles.get_profile("test")
        assert profile is not None
        assert profile.name == "test"

        # Test with non-existent profile
        with pytest.raises(ConfigurationError):
            profiles.get_profile("nonexistent")

    def test_invalid_yaml(self, temp_dir):
        """Test error with invalid YAML profiles file."""
        invalid_profile_path = temp_dir / "invalid_profiles.yml"
        with open(invalid_profile_path, "w") as f:
            f.write("- name: test\n  invalid: : yaml:")

        with pytest.raises(Exception):  # Could be yaml.YAMLError or validation error
            Profiles(invalid_profile_path)

    def test_missing_required_fields(self, temp_dir):
        """Test validation error when required fields are missing."""
        incomplete_profiles = [
            {
                # Missing required 'models' field
                "name": "test",
                "chat_history": {"database_connection_string": ""},
            }
        ]

        profile_path = temp_dir / "incomplete_profiles.yml"
        with open(profile_path, "w") as f:
            yaml.dump(incomplete_profiles, f)

        with pytest.raises(Exception):  # Validation error
            Profiles(profile_path)
