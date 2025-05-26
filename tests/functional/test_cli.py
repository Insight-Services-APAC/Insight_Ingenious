"""
Functional tests for the CLI commands.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ingenious.cli import app


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


class TestCLI:
    """Functional tests for CLI commands."""

    def test_initialize_new_project_help(self, runner):
        """Test the help output for initialize-new-project command."""
        result = runner.invoke(app, ["initialize-new-project", "--help"])
        assert result.exit_code == 0
        assert "Generate template folders for a new project" in result.stdout

    def test_run_prompt_tuner_help(self, runner):
        """Test the help output for run-prompt-tuner command."""
        result = runner.invoke(app, ["run-prompt-tuner", "--help"])
        assert result.exit_code == 0
        assert "Run the prompt tuner web application" in result.stdout

    @pytest.mark.skip(reason="Requires actual project setup and may have side effects")
    def test_initialize_new_project(self, runner):
        """Test initializing a new project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Change to the temporary directory
            original_dir = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Run the command
                result = runner.invoke(app, ["initialize-new-project"])

                # Check the result
                assert result.exit_code == 0

                # Check that the expected directories and files were created
                project_dir = Path(tmpdir)
                assert (project_dir / "config.yml").exists()
                assert (project_dir / "templates").exists()
                assert (project_dir / "templates" / "prompts").exists()
            finally:
                # Change back to the original directory
                os.chdir(original_dir)

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
