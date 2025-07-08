import json
import os
import tempfile
from unittest.mock import Mock, mock_open, patch

import pytest
import yaml
from pydantic import ValidationError

from ingenious.config.config import Config, substitute_environment_variables


@pytest.mark.unit
class TestSubstituteEnvironmentVariables:
    """Test environment variable substitution in config"""

    def test_substitute_with_existing_var(self):
        """Test substitution with existing environment variable"""
        yaml_content = "endpoint: ${TEST_ENDPOINT}"

        with patch.dict(os.environ, {"TEST_ENDPOINT": "https://test.endpoint.com"}):
            result = substitute_environment_variables(yaml_content)
            assert result == "endpoint: https://test.endpoint.com"

    def test_substitute_with_default_value(self):
        """Test substitution with default value when var doesn't exist"""
        yaml_content = "endpoint: ${MISSING_ENDPOINT:https://default.endpoint.com}"

        with patch.dict(os.environ, {}, clear=True):
            result = substitute_environment_variables(yaml_content)
            assert result == "endpoint: https://default.endpoint.com"

    def test_substitute_azure_openai_warning(self):
        """Test substitution with Azure OpenAI variables shows warning"""
        yaml_content = "api_key: ${AZURE_OPENAI_API_KEY:default_key}"

        with (
            patch.dict(os.environ, {}, clear=True),
            patch("ingenious.config.config.logger") as mock_logger,
        ):
            result = substitute_environment_variables(yaml_content)

            assert result == "api_key: default_key"
            mock_logger.warning.assert_called_once()
            assert "AZURE_OPENAI_API_KEY" in str(mock_logger.warning.call_args)

    def test_substitute_placeholder_info(self):
        """Test substitution with placeholder value shows info"""
        yaml_content = "service: ${OPTIONAL_SERVICE:placeholder_service}"

        with (
            patch.dict(os.environ, {}, clear=True),
            patch("ingenious.config.config.logger") as mock_logger,
        ):
            result = substitute_environment_variables(yaml_content)

            assert result == "service: placeholder_service"
            mock_logger.info.assert_called_once()
            assert "OPTIONAL_SERVICE" in str(mock_logger.info.call_args)

    def test_substitute_missing_var_no_default(self):
        """Test substitution with missing var and no default shows error"""
        yaml_content = "required: ${REQUIRED_VAR}"

        with (
            patch.dict(os.environ, {}, clear=True),
            patch("ingenious.config.config.logger") as mock_logger,
        ):
            result = substitute_environment_variables(yaml_content)

            assert result == "required: ${REQUIRED_VAR}"  # Returns original
            mock_logger.error.assert_called_once()
            assert "REQUIRED_VAR" in str(mock_logger.error.call_args)

    def test_substitute_multiple_variables(self):
        """Test substitution with multiple environment variables"""
        yaml_content = """
        endpoint: ${API_ENDPOINT:https://default.com}
        key: ${API_KEY}
        optional: ${OPTIONAL_VAR:default_value}
        """

        with patch.dict(os.environ, {"API_KEY": "secret_key"}, clear=True):
            result = substitute_environment_variables(yaml_content)

            assert "https://default.com" in result
            assert "secret_key" in result
            assert "default_value" in result

    def test_substitute_no_variables(self):
        """Test substitution with no variables to substitute"""
        yaml_content = """
        plain_config:
          value: "no variables here"
          number: 42
        """

        result = substitute_environment_variables(yaml_content)
        assert result == yaml_content

    def test_substitute_complex_default_value(self):
        """Test substitution with complex default value containing colons"""
        yaml_content = "url: ${DATABASE_URL:postgresql://user:pass@localhost:5432/db}"

        with patch.dict(os.environ, {}, clear=True):
            result = substitute_environment_variables(yaml_content)
            assert result == "url: postgresql://user:pass@localhost:5432/db"

    def test_substitute_existing_var_overrides_default(self):
        """Test that existing environment variable overrides default"""
        yaml_content = "value: ${TEST_VAR:default_value}"

        with patch.dict(os.environ, {"TEST_VAR": "actual_value"}):
            result = substitute_environment_variables(yaml_content)
            assert result == "value: actual_value"

    def test_substitute_empty_default(self):
        """Test substitution with empty default value"""
        yaml_content = "empty: ${EMPTY_VAR:}"

        with patch.dict(os.environ, {}, clear=True):
            result = substitute_environment_variables(yaml_content)
            assert result == "empty: "


@pytest.mark.unit
class TestConfig:
    """Test Config class functionality"""

    def test_config_from_yaml_str_valid(self):
        """Test creating Config from valid YAML string"""
        yaml_content = """
        test_key: test_value
        """

        with (
            patch(
                "ingenious.config.config.config_ns_models.Config.model_validate_json"
            ) as mock_validate,
            patch("ingenious.config.config.Profiles") as mock_profiles,
            patch("ingenious.config.config.config_models.Config") as mock_config_model,
        ):
            mock_config = Mock()
            mock_config.profile = "test_profile"
            mock_validate.return_value = mock_config
            mock_profiles.return_value.get_profile_by_name.return_value = Mock()
            mock_config_model.return_value = Mock()

            _result = Config.from_yaml_str(yaml_content)

            # Verify that validation was called
            mock_validate.assert_called_once()

            # Verify the JSON data structure
            call_args = mock_validate.call_args[0][0]
            parsed_data = json.loads(call_args)
            assert "test_key" in parsed_data
            assert parsed_data["test_key"] == "test_value"

    def test_config_from_yaml_str_with_env_substitution(self):
        """Test creating Config from YAML string with environment variables"""
        yaml_content = """
profile: ${TEST_PROFILE:test_profile}

models:
  - model: ${TEST_MODEL:gpt-4}
    api_type: rest
    api_version: 2023-03-15-preview

logging:
  root_log_level: info
  log_level: info

chat_history:
  database_type: sqlite
  database_path: ./tmp/test.db
  memory_path: ./tmp

tool_service:
  enable: false

chat_service:
  type: multi_agent

chainlit_configuration:
  enable: false

prompt_tuner:
  mode: fast_api
  enable: true

web_configuration:
  ip_address: 0.0.0.0
  port: 8000
  type: fastapi
  asynchronous: false

local_sql_db:
  database_path: /tmp/test_db
  sample_csv_path: ""
  sample_database_name: test_db
"""

        # Create a temporary profile file
        profile_content = """
- name: test_profile
  models:
    - model: gpt-3.5-turbo
      api_key: test-key
      base_url: https://test.openai.azure.com/
      deployment: gpt-35-turbo
      api_version: 2023-03-15-preview
  chat_history:
    database_connection_string: ""
  receiver_configuration:
    enable: false
    api_url: ""
    api_key: "DevApiKey"
  chainlit_configuration:
    enable: false
    authentication:
      enable: false
      github_secret: ""
      github_client_id: ""
  web_configuration:
    authentication:
      enable: false
      username: "admin"
      password: "admin123"
      type: "basic"
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False
        ) as profile_f:
            profile_f.write(profile_content)
            profile_file = profile_f.name

        try:
            with patch.dict(
                os.environ,
                {
                    "TEST_PROFILE": "test_profile",
                    "TEST_MODEL": "gpt-3.5-turbo",
                    "INGENIOUS_PROFILE_PATH": profile_file,
                },
                clear=True,
            ):
                config = Config.from_yaml_str(yaml_content)

                # Verify environment variable substitution occurred
                assert config is not None
                assert len(config.models) == 1
                assert (
                    config.models[0].model == "gpt-3.5-turbo"
                )  # Environment variable was substituted

        finally:
            os.unlink(profile_file)

    def test_config_from_yaml_str_validation_error(self):
        """Test Config creation with validation error"""
        yaml_content = """
        invalid_structure:
          missing_required_fields: true
        """

        validation_errors = [
            {"loc": ("agents",), "msg": "Field required", "type": "missing"}
        ]

        mock_validation_error = ValidationError.from_exception_data(
            "Config", validation_errors
        )

        with patch(
            "ingenious.config.config.config_ns_models.Config.model_validate_json"
        ) as mock_validate:
            mock_validate.side_effect = mock_validation_error

            with pytest.raises(ValidationError):
                Config.from_yaml_str(yaml_content)

    def test_config_from_yaml_str_validation_error_with_suggestions(self):
        """Test Config creation with validation error containing helpful suggestions"""
        yaml_content = """
        agents:
          - name: test
            endpoint: null
        """

        validation_errors = [
            {
                "loc": ("agents", 0, "endpoint"),
                "msg": "Input should be a valid string",
                "type": "string_type",
            }
        ]

        mock_validation_error = ValidationError.from_exception_data(
            "Config", validation_errors
        )

        with patch(
            "ingenious.config.config.config_ns_models.Config.model_validate_json"
        ) as mock_validate:
            mock_validate.side_effect = mock_validation_error

            with pytest.raises(ValidationError):
                Config.from_yaml_str(yaml_content)

    def test_config_from_yaml_file(self):
        """Test creating Config from YAML file"""
        yaml_content = """
        agents:
          - name: file_agent
            description: Agent from file
            model: gpt-3.5-turbo
        """

        with (
            patch("builtins.open", mock_open(read_data=yaml_content)),
            patch("ingenious.config.config.Config.from_yaml_str") as mock_from_yaml_str,
        ):
            mock_config = Mock()
            mock_from_yaml_str.return_value = mock_config

            result = Config.from_yaml("test_config.yaml")

            mock_from_yaml_str.assert_called_once_with(yaml_content)
            assert result == mock_config

    def test_config_from_yaml_file_with_env_vars(self):
        """Test creating Config from YAML file with environment variables"""
        yaml_content = """
profile: ${TEST_PROFILE:test_profile}

models:
  - model: ${TEST_MODEL:gpt-4}
    api_type: rest
    api_version: 2023-03-15-preview

logging:
  root_log_level: info
  log_level: info

chat_history:
  database_type: sqlite
  database_path: ./tmp/test.db
  memory_path: ./tmp

tool_service:
  enable: false

chat_service:
  type: multi_agent

chainlit_configuration:
  enable: false

prompt_tuner:
  mode: fast_api
  enable: true

web_configuration:
  ip_address: 0.0.0.0
  port: 8000
  type: fastapi
  asynchronous: false

local_sql_db:
  database_path: /tmp/test_db
  sample_csv_path: ""
  sample_database_name: test_db
"""

        # Create a temporary profile file
        profile_content = """
- name: test_profile
  models:
    - model: gpt-3.5-turbo
      api_key: test-key
      base_url: https://test.openai.azure.com/
      deployment: gpt-35-turbo
      api_version: 2023-03-15-preview
  chat_history:
    database_connection_string: ""
  receiver_configuration:
    enable: false
    api_url: ""
    api_key: "DevApiKey"
  chainlit_configuration:
    enable: false
    authentication:
      enable: false
      github_secret: ""
      github_client_id: ""
  web_configuration:
    authentication:
      enable: false
      username: "admin"
      password: "admin123"
      type: "basic"
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False
        ) as profile_f:
            profile_f.write(profile_content)
            profile_file = profile_f.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as config_f:
            config_f.write(yaml_content)
            config_file = config_f.name

        try:
            with patch.dict(
                os.environ,
                {
                    "TEST_PROFILE": "test_profile",
                    "TEST_MODEL": "gpt-3.5-turbo",
                    "INGENIOUS_PROFILE_PATH": profile_file,
                },
                clear=True,
            ):
                config = Config.from_yaml(config_file)

                # Verify environment variable substitution occurred
                assert config is not None
                assert len(config.models) == 1
                assert (
                    config.models[0].model == "gpt-3.5-turbo"
                )  # Environment variable was substituted

        finally:
            os.unlink(profile_file)
            os.unlink(config_file)

    def test_config_double_substitution(self):
        """Test that environment variables are substituted correctly when called multiple times"""
        yaml_content = "value: ${TEST_VAR:default}"

        with patch.dict(os.environ, {"TEST_VAR": "substituted"}, clear=True):
            # First substitution
            result1 = substitute_environment_variables(yaml_content)
            # Second substitution (should not change the result)
            result2 = substitute_environment_variables(result1)

            assert result1 == "value: substituted"
            assert result2 == "value: substituted"

    def test_config_from_yaml_str_empty_yaml(self):
        """Test creating Config from empty YAML string"""
        yaml_content = ""

        with (
            patch(
                "ingenious.config.config.config_ns_models.Config.model_validate_json"
            ) as mock_validate,
            patch("ingenious.config.config.Profiles") as mock_profiles,
            patch("ingenious.config.config.config_models.Config") as mock_config_model,
        ):
            mock_config = Mock()
            mock_config.profile = "test_profile"
            mock_validate.return_value = mock_config
            mock_profiles.return_value.get_profile_by_name.return_value = Mock()
            mock_config_model.return_value = Mock()

            Config.from_yaml_str(yaml_content)

            # Should still try to validate even with empty content
            mock_validate.assert_called_once()

    def test_config_from_yaml_str_invalid_yaml(self):
        """Test creating Config from invalid YAML string"""
        yaml_content = """
        invalid: yaml: content:
          - unmatched: [brackets
        """

        with pytest.raises(yaml.YAMLError):
            Config.from_yaml_str(yaml_content)
