import os
import tempfile
from unittest.mock import patch

import pytest

from ingenious.config.config import Config, substitute_environment_variables


@pytest.mark.integration
class TestConfigIntegration:
    """Integration tests for configuration loading and processing"""

    def test_complete_config_workflow(self):
        """Test complete configuration workflow from file to object"""
        config_content = """
chat_history:
  database_type: sqlite
  database_path: ./tmp/test.db
  memory_path: ./tmp

profile: test_profile

models:
  - model: ${MODEL_NAME:gpt-4}
    api_type: rest
    api_version: ${API_VERSION:2023-03-15-preview}
    deployment: ${DEPLOYMENT:gpt-4}

logging:
  root_log_level: info
  log_level: info

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

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(config_content)
            config_file = f.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False
        ) as profile_f:
            profile_f.write(profile_content)
            profile_file = profile_f.name

        try:
            with patch.dict(
                os.environ,
                {
                    "MODEL_NAME": "gpt-3.5-turbo",
                    "API_VERSION": "2023-03-15-preview",
                    "DEPLOYMENT": "gpt-35-turbo",
                    "INGENIOUS_PROFILE_PATH": profile_file,
                },
                clear=True,
            ):
                config = Config.from_yaml(config_file)

                # Verify the configuration was loaded and processed correctly
                assert config is not None
                assert len(config.models) == 1
                assert config.models[0].model == "gpt-3.5-turbo"
                assert config.models[0].api_version == "2023-03-15-preview"
                assert config.models[0].deployment == "gpt-35-turbo"

        finally:
            os.unlink(config_file)
            os.unlink(profile_file)

    def test_environment_variable_cascade(self):
        """Test environment variable substitution cascade behavior"""
        config_content = """
database:
  host: ${DB_HOST:${FALLBACK_HOST:localhost}}
  port: ${DB_PORT:5432}
  name: ${DB_NAME:testdb}

services:
  api_endpoint: ${API_ENDPOINT:https://api.${DOMAIN:example.com}/v1}
  timeout: ${TIMEOUT:30}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(config_content)
            config_file = f.name

        try:
            # Test with partial environment variables
            with patch.dict(
                os.environ, {"DOMAIN": "test.com", "TIMEOUT": "60"}, clear=True
            ):
                # Read and substitute variables
                with open(config_file, "r") as file:
                    content = file.read()

                result = substitute_environment_variables(content)

                # Verify substitutions
                assert "localhost" in result  # DB_HOST fallback
                assert "5432" in result  # DB_PORT default
                assert "testdb" in result  # DB_NAME default
                assert "https://api.test.com/v1" in result  # API_ENDPOINT with DOMAIN
                assert "60" in result  # TIMEOUT from env

        finally:
            os.unlink(config_file)

    def test_config_validation_errors_with_context(self):
        """Test configuration validation provides helpful error context"""
        invalid_config_content = """
profile: test_profile
models: []  # Empty models list - this should cause validation error
logging:
  root_log_level: info
  log_level: info
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(invalid_config_content)
            config_file = f.name

        try:
            # This should raise a validation error with helpful context
            with pytest.raises(
                Exception
            ):  # Could be ValidationError or other config-specific error
                Config.from_yaml(config_file)

        finally:
            os.unlink(config_file)

    def test_config_with_missing_optional_fields(self):
        """Test configuration with missing optional fields uses defaults"""
        minimal_config_content = """
profile: test_profile

models:
  - model: gpt-4
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
    - model: gpt-4
      api_key: test-key
      base_url: https://test.openai.azure.com/
      deployment: gpt-4
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

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(minimal_config_content)
            config_file = f.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False
        ) as profile_f:
            profile_f.write(profile_content)
            profile_file = profile_f.name

        try:
            with patch.dict(
                os.environ, {"INGENIOUS_PROFILE_PATH": profile_file}, clear=True
            ):
                config = Config.from_yaml(config_file)

                # Verify the minimal configuration is accepted
                assert config is not None
                assert len(config.models) == 1
                assert config.models[0].model == "gpt-4"

        finally:
            os.unlink(config_file)
            os.unlink(profile_file)

    def test_config_with_complex_nested_substitutions(self):
        """Test configuration with complex nested environment variable substitutions"""
        complex_config_content = """
environments:
  development:
    database:
      host: ${DEV_DB_HOST:dev.${BASE_DOMAIN:example.com}}
      credentials:
        username: ${DEV_DB_USER:dev_user}
        password: ${DEV_DB_PASS:dev_pass}

  production:
    database:
      host: ${PROD_DB_HOST:prod.${BASE_DOMAIN:example.com}}
      credentials:
        username: ${PROD_DB_USER:prod_user}
        password: ${PROD_DB_PASS:prod_pass}

agents:
  - name: env_agent
    description: "Agent configured via environment"
    model: ${AGENT_MODEL:gpt-4}

workflows:
  env_workflow:
    agents:
      - env_agent
    environment: ${DEPLOY_ENV:development}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(complex_config_content)
            config_file = f.name

        try:
            with patch.dict(
                os.environ,
                {
                    "BASE_DOMAIN": "test-company.com",
                    "DEV_DB_USER": "test_dev_user",
                    "AGENT_MODEL": "gpt-3.5-turbo",
                    "DEPLOY_ENV": "development",
                },
                clear=True,
            ):
                # Read and process the configuration
                with open(config_file, "r") as file:
                    content = file.read()

                result = substitute_environment_variables(content)

                # Verify complex substitutions
                assert "dev.test-company.com" in result
                assert "prod.test-company.com" in result
                assert "test_dev_user" in result
                assert "prod_user" in result  # Default value
                assert "gpt-3.5-turbo" in result
                assert "development" in result

        finally:
            os.unlink(config_file)

    def test_config_file_not_found_handling(self):
        """Test graceful handling of missing configuration files"""
        non_existent_file = "non_existent_config.yaml"

        with pytest.raises(FileNotFoundError):
            Config.from_yaml(non_existent_file)

    def test_config_with_yaml_syntax_errors(self):
        """Test handling of YAML syntax errors"""
        invalid_yaml_content = """
agents:
  - name: test_agent
    model: gpt-4
    invalid_yaml: [unclosed bracket
workflows:
  test: {unclosed brace
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(invalid_yaml_content)
            config_file = f.name

        try:
            with pytest.raises(Exception):  # YAML parsing error
                Config.from_yaml(config_file)

        finally:
            os.unlink(config_file)

    def test_config_with_special_characters_in_env_vars(self):
        """Test configuration with special characters in environment variables"""
        config_content = """
database:
  connection_string: "${DB_CONNECTION:postgresql://user:pass@localhost:5432/db?sslmode=require}"

api:
  key: "${API_KEY:sk-1234567890abcdef!@#$%^&*()}"
  url: "${API_URL:https://api.example.com/v1?param=value&other=123}"
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(config_content)
            config_file = f.name

        try:
            with patch.dict(
                os.environ,
                {
                    "DB_CONNECTION": "postgresql://test:secret@testhost:5432/testdb",
                    "API_KEY": "sk-test-key-with-special-chars!@#",
                },
                clear=True,
            ):
                with open(config_file, "r") as file:
                    content = file.read()

                result = substitute_environment_variables(content)

                # Verify special characters are preserved
                assert "postgresql://test:secret@testhost:5432/testdb" in result
                assert "sk-test-key-with-special-chars!@#" in result
                assert (
                    "https://api.example.com/v1?param=value&other=123" in result
                )  # Default with special chars

        finally:
            os.unlink(config_file)
