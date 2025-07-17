import os
from unittest.mock import patch

import pytest

from ingenious.utils.env_substitution import (
    substitute_env_vars,
)


@pytest.mark.unit
class TestEnvSubstitution:
    """Test environment variable substitution functionality"""

    def test_substitute_env_vars_with_existing_var(self):
        """Test substitution with existing environment variable"""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            result = substitute_env_vars("${TEST_VAR:default}")
            assert result == "test_value"

    def test_substitute_env_vars_with_default(self):
        """Test substitution with default value when var doesn't exist"""
        with patch.dict(os.environ, {}, clear=True):
            result = substitute_env_vars("${MISSING_VAR:default_value}")
            assert result == "default_value"

    def test_substitute_env_vars_without_default(self):
        """Test substitution without default value"""
        with patch.dict(os.environ, {}, clear=True):
            result = substitute_env_vars("${MISSING_VAR}")
            assert result == ""

    def test_substitute_env_vars_with_existing_var_no_default(self):
        """Test substitution with existing var and no default"""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            result = substitute_env_vars("${TEST_VAR}")
            assert result == "test_value"

    def test_substitute_env_vars_multiple_vars(self):
        """Test substitution with multiple environment variables"""
        with patch.dict(os.environ, {"VAR1": "value1", "VAR2": "value2"}):
            result = substitute_env_vars("${VAR1:default1} and ${VAR2:default2}")
            assert result == "value1 and value2"

    def test_substitute_env_vars_mixed_existing_and_missing(self):
        """Test substitution with mix of existing and missing vars"""
        with patch.dict(os.environ, {"EXISTING_VAR": "exists"}, clear=True):
            result = substitute_env_vars(
                "${EXISTING_VAR:default1} and ${MISSING_VAR:default2}"
            )
            assert result == "exists and default2"

    def test_substitute_env_vars_empty_default(self):
        """Test substitution with empty default value"""
        with patch.dict(os.environ, {}, clear=True):
            result = substitute_env_vars("${MISSING_VAR:}")
            assert result == ""

    def test_substitute_env_vars_no_placeholders(self):
        """Test substitution with no placeholders"""
        result = substitute_env_vars("plain text without variables")
        assert result == "plain text without variables"

    def test_substitute_env_vars_special_characters_in_default(self):
        """Test substitution with special characters in default value"""
        with patch.dict(os.environ, {}, clear=True):
            result = substitute_env_vars("${VAR:default:with:colons}")
            assert result == "default:with:colons"

    def test_substitute_env_vars_nested_braces(self):
        """Test that nested braces are handled correctly"""
        with patch.dict(os.environ, {"VAR": "value"}):
            result = substitute_env_vars("${VAR:default} and {not_a_var}")
            assert result == "value and {not_a_var}"
