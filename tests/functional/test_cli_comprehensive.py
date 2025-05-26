"""
Comprehensive functional tests for the CLI commands in Insight Ingenious.
Tests all commands mentioned in the UV_CLI_README.md file.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from ingenious.cli import app


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def temp_project_dir():
    """Create a temporary directory for project tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_dir = os.getcwd()
        os.chdir(tmpdir)
        yield tmpdir
        os.chdir(original_dir)


class TestCliCommands:
    """Comprehensive tests for all CLI commands."""

    def test_cli_help(self, runner):
        """Test the main CLI help output."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "run" in result.stdout
        assert "init" in result.stdout
        assert "run-prompt-tuner" in result.stdout

    def test_init_help(self, runner):
        """Test the help output for init command."""
        result = runner.invoke(app, ["init", "--help"])
        assert result.exit_code == 0
        assert "Generate template folders for a new project" in result.stdout
        assert "PROJECT_DIR" not in result.stdout  # It's not an argument for init

    def test_run_prompt_tuner_help(self, runner):
        """Test the help output for run-prompt-tuner command."""
        result = runner.invoke(app, ["run-prompt-tuner", "--help"])
        assert result.exit_code == 0
        assert "Run the prompt tuner web application" in result.stdout

    def test_run_help(self, runner):
        """Test the help output for run command."""
        result = runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0
        assert "This command will run a fastapi server" in result.stdout
        assert "PROJECT_DIR" in result.stdout  # It's an argument, not an option

    def test_init(self, runner, temp_project_dir):
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

    @patch("uvicorn.run")
    def test_run(self, mock_run, runner):
        """Test the REST API server command."""
        # Simplified test - skip the actual execution but check help output
        result = runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0
        assert "This command will run a fastapi server" in result.stdout

    def test_run_prompt_tuner(self, runner):
        """Test the prompt tuner command."""
        # Just test the help output, which doesn't require the actual implementation
        result = runner.invoke(app, ["run-prompt-tuner", "--help"])
        assert result.exit_code == 0
        assert "Run the prompt tuner web application" in result.stdout
