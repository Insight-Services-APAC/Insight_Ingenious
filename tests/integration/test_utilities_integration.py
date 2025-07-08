import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ingenious.utils.env_substitution import (
    load_yaml_with_env_substitution,
    substitute_env_vars,
)
from ingenious.utils.namespace_utils import (
    get_file_from_namespace_with_fallback,
    get_path_from_namespace_with_fallback,
    import_class_with_fallback,
    import_module_with_fallback,
)


@pytest.mark.integration
class TestNamespaceUtilsIntegration:
    """Integration tests for namespace utilities"""

    @patch("ingenious.utils.namespace_utils.get_namespaces")
    @patch("ingenious.utils.namespace_utils.importlib.import_module")
    @patch("ingenious.utils.namespace_utils.importlib.util.find_spec")
    def test_module_import_fallback_chain(
        self, mock_find_spec, mock_import_module, mock_get_namespaces
    ):
        """Test complete module import fallback chain"""
        mock_get_namespaces.return_value = [
            "ingenious_extensions",
            "ingenious.ingenious_extensions_template",
            "ingenious",
        ]

        # Simulate first namespace fails, second succeeds
        mock_find_spec.side_effect = [
            None,
            Mock(),
            None,
        ]  # Only second namespace has the module
        mock_module = Mock()
        mock_import_module.return_value = mock_module

        with (
            patch("ingenious.utils.namespace_utils.Path.cwd") as mock_cwd,
            patch("builtins.print"),
        ):  # Mock print to avoid output
            mock_cwd.return_value = Path("/test/dir")

            result = import_module_with_fallback("test.module")

            assert result == mock_module
            # Should try to import the second namespace
            mock_import_module.assert_called_with(
                "ingenious.ingenious_extensions_template.test.module"
            )

    @patch("ingenious.utils.namespace_utils.import_module_with_fallback")
    def test_class_import_with_fallback_integration(self, mock_import_module_fallback):
        """Test complete class import with fallback integration"""
        mock_module = Mock()
        mock_class = Mock()
        mock_module.TestClass = mock_class
        mock_import_module_fallback.return_value = mock_module

        result = import_class_with_fallback("test.module", "TestClass")

        assert result == mock_class
        mock_import_module_fallback.assert_called_once_with("test.module")

    @patch("ingenious.utils.namespace_utils.get_dir_roots")
    def test_file_retrieval_fallback_chain(self, mock_get_dir_roots):
        """Test complete file retrieval fallback chain"""
        # Set up multiple directories, only third one has the file
        dir1 = Path("/nonexistent/dir1")
        dir2 = Path("/nonexistent/dir2")
        dir3 = Path("/existent/dir3")

        mock_get_dir_roots.return_value = [dir1, dir2, dir3]

        file_content = "test file content from third directory"

        def mock_exists(path):
            return str(path) == str(dir3 / "test.module" / "test_file.txt")

        with (
            patch(
                "ingenious.utils.namespace_utils.os.path.exists",
                side_effect=mock_exists,
            ),
            patch("builtins.open") as mock_open,
        ):
            mock_file = Mock()
            mock_file.read.return_value = file_content
            mock_open.return_value.__enter__.return_value = mock_file

            result = get_file_from_namespace_with_fallback(
                "test.module", "test_file.txt"
            )

            assert result == file_content
            # Should open the file from the third directory
            expected_path = dir3 / "test.module" / "test_file.txt"
            mock_open.assert_called_once_with(expected_path, "r")

    @patch("ingenious.utils.namespace_utils.get_dir_roots")
    def test_path_retrieval_fallback_chain(self, mock_get_dir_roots):
        """Test complete path retrieval fallback chain"""
        dir1 = Path("/nonexistent/dir1")
        dir2 = Path("/existent/dir2")
        dir3 = Path("/existent/dir3")

        mock_get_dir_roots.return_value = [dir1, dir2, dir3]

        def mock_exists(path):
            return str(path) == str(dir2 / "test/path") or str(path) == str(
                dir3 / "test/path"
            )

        with patch(
            "ingenious.utils.namespace_utils.os.path.exists", side_effect=mock_exists
        ):
            result = get_path_from_namespace_with_fallback("test/path")

            # Should return the first matching path (dir2)
            expected_path = dir2 / "test/path"
            assert result == expected_path

    def test_namespace_utils_real_sys_path_manipulation(self):
        """Test that namespace utils properly manipulate sys.path"""
        original_sys_path = sys.path.copy()

        try:
            with (
                patch("ingenious.utils.namespace_utils.os.getcwd") as mock_getcwd,
                patch(
                    "ingenious.utils.namespace_utils.get_namespaces"
                ) as mock_get_namespaces,
                patch(
                    "ingenious.utils.namespace_utils.importlib.util.find_spec"
                ) as mock_find_spec,
                patch("builtins.print"),
            ):  # Mock print to avoid output
                test_cwd = Path("/test/working/directory")
                mock_getcwd.return_value = str(test_cwd)
                mock_get_namespaces.return_value = ["test_namespace"]
                mock_find_spec.return_value = None  # No modules found

                # Ensure test directory is not in sys.path initially
                if str(test_cwd) in sys.path:
                    sys.path.remove(str(test_cwd))

                import_module_with_fallback("nonexistent.module")

                # Should have added the working directory to sys.path
                assert str(test_cwd) in sys.path

        finally:
            # Restore original sys.path
            sys.path[:] = original_sys_path


@pytest.mark.integration
class TestEnvSubstitutionIntegration:
    """Integration tests for environment variable substitution"""

    def test_env_substitution_with_file_operations(self):
        """Test environment substitution with actual file operations"""
        import tempfile

        yaml_content = """
database:
  host: ${DB_HOST:localhost}
  port: ${DB_PORT:5432}
  user: ${DB_USER:testuser}

api:
  endpoint: ${API_ENDPOINT:https://api.example.com}
  key: ${API_KEY:default_key}

features:
  enabled: ${FEATURES_ENABLED:true}
  debug: ${DEBUG_MODE:false}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            yaml_file = f.name

        try:
            with patch.dict(
                os.environ,
                {
                    "DB_HOST": "production.db.com",
                    "API_KEY": "prod_api_key_123",
                    "DEBUG_MODE": "true",
                },
                clear=True,
            ):
                result = load_yaml_with_env_substitution(yaml_file)

                # Verify substitutions
                assert "production.db.com" in result
                assert "5432" in result  # Default value
                assert "testuser" in result  # Default value
                assert "https://api.example.com" in result  # Default value
                assert "prod_api_key_123" in result
                assert (
                    "true" in result
                )  # Both FEATURES_ENABLED default and DEBUG_MODE env

        finally:
            os.unlink(yaml_file)

    def test_env_substitution_complex_yaml_structure(self):
        """Test environment substitution with complex YAML structure"""
        import tempfile

        complex_yaml_content = """
environments:
  development:
    database:
      host: ${DEV_DB_HOST:dev.localhost}
      port: ${DEV_DB_PORT:5432}
    services:
      - name: auth
        url: ${DEV_AUTH_URL:http://localhost:3001}
      - name: api
        url: ${DEV_API_URL:http://localhost:3000}

  production:
    database:
      host: ${PROD_DB_HOST:prod.db.company.com}
      port: ${PROD_DB_PORT:5432}
    services:
      - name: auth
        url: ${PROD_AUTH_URL:https://auth.company.com}
      - name: api
        url: ${PROD_API_URL:https://api.company.com}

agents:
  - name: ${AGENT_1_NAME:default_agent}
    model: ${AGENT_1_MODEL:gpt-4}
    config:
      temperature: ${AGENT_1_TEMP:0.7}
      max_tokens: ${AGENT_1_TOKENS:1000}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(complex_yaml_content)
            yaml_file = f.name

        try:
            with patch.dict(
                os.environ,
                {
                    "DEV_DB_HOST": "dev.test.com",
                    "PROD_AUTH_URL": "https://auth.prod.com",
                    "AGENT_1_NAME": "production_agent",
                    "AGENT_1_TEMP": "0.3",
                },
                clear=True,
            ):
                result = load_yaml_with_env_substitution(yaml_file)

                # Verify various types of substitutions
                assert "dev.test.com" in result  # Environment override
                assert "prod.db.company.com" in result  # Default value
                assert "https://auth.prod.com" in result  # Environment override
                assert "https://api.company.com" in result  # Default value
                assert "production_agent" in result  # Environment override
                assert "gpt-4" in result  # Default value
                assert "0.3" in result  # Environment override
                assert "1000" in result  # Default value

        finally:
            os.unlink(yaml_file)

    def test_env_substitution_edge_cases_integration(self):
        """Test environment substitution edge cases in integration"""
        test_cases = [
            # Test case: (content, env_vars, expected_in_result, not_expected_in_result)
            ("value: ${EMPTY_VAR:}", {"EMPTY_VAR": ""}, ["value: "], []),
            (
                "complex: ${URL:https://user:pass@host:8080/path?param=value}",
                {},
                ["https://user:pass@host:8080/path?param=value"],
                ["${URL"],
            ),
            (
                "nested: ${OUTER:prefix-${INNER:default}-suffix}",
                {"INNER": "middle"},
                ["prefix-middle-suffix"],  # Full nested substitution
                ["${INNER", "${OUTER"],
            ),
            (
                "multiple: ${VAR1:default1} ${VAR2:default2} ${VAR3:default3}",
                {"VAR2": "value2"},
                ["default1", "value2", "default3"],
                ["${VAR1", "${VAR2", "${VAR3"],
            ),
        ]

        for content, env_vars, expected, not_expected in test_cases:
            with patch.dict(os.environ, env_vars, clear=True):
                result = substitute_env_vars(content)

                for expected_item in expected:
                    assert expected_item in result, (
                        f"Expected '{expected_item}' in result for content: {content}"
                    )

                for not_expected_item in not_expected:
                    assert not_expected_item not in result, (
                        f"Did not expect '{not_expected_item}' in result for content: {content}"
                    )
