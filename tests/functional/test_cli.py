"""
Functional tests for the CLI commands.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from ingenious.cli import app


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


class TestCLI:
    """Functional tests for CLI commands."""

    def test_init_help(self, runner):
        """Test the help output for init command."""
        result = runner.invoke(app, ["init", "--help"])
        assert result.exit_code == 0
        assert "Generate template folders for a new project" in result.stdout

    def test_run_prompt_tuner_help(self, runner):
        """Test the help output for run-prompt-tuner command."""
        result = runner.invoke(app, ["run-prompt-tuner", "--help"])
        assert result.exit_code == 0
        assert "Run the prompt tuner web application" in result.stdout

    @pytest.mark.skip(reason="Requires actual project setup and may have side effects")
    def test_init(self, runner):
        """Test initializing a new project."""
        # Mock the ProjectSetupExecutor to avoid actual file operations
        with patch(
            "ingenious.common.utils.cli_command_executor.ProjectSetupExecutor"
        ) as mock_executor:
            # Set up mock instance
            mock_instance = MagicMock()
            mock_executor.return_value = mock_instance

            # Run the command
            result = runner.invoke(app, ["init"])

            # Check the result
            assert result.exit_code == 0

            # Verify the initialize_new_project method was called
            mock_instance.initialize_new_project.assert_called_once()

    @pytest.mark.skip(
        reason="Requires actual project setup and would start a web server"
    )
    def test_run_prompt_tuner(self, runner):
        """Test running the prompt tuner."""
        with patch("ingenious.cli.importlib.import_module") as mock_import:
            # Mock the tuner module
            mock_tuner = mock_import.return_value

            # Run the command
            result = runner.invoke(app, ["run-prompt-tuner"])

            # Check the result
            assert result.exit_code == 0

            # Check that the tuner was started
            mock_import.assert_called_once_with("ingenious_prompt_tuner.cli")
            mock_tuner.main.assert_called_once()
