"""
Module for CLI command implementations.
This module contains classes that implement CLI commands as separate components.
"""

import os
from pathlib import Path
from sysconfig import get_paths
from typing import Optional

from rich.console import Console

import ingenious.common.utils.stage_executor as stage_executor_module
from ingenious.common.utils.namespace_utils import import_class_with_fallback
from ingenious.common.utils.project_setup_manager import ProjectSetupManager


class CliCommandExecutor:
    """
    Base class for CLI command implementations.

    This class provides common functionality for CLI commands.
    """

    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the CliCommandExecutor.

        Args:
            console: Optional console for output
        """
        self.console = console

    def _log(self, message: str, style: str = "info"):
        """
        Log a message to the console if available.

        Args:
            message: The message to log
            style: The style to use for the message
        """
        if self.console:
            self.console.print(f"[{style}]{message}[/{style}]")


class ProjectSetupExecutor(CliCommandExecutor):
    """
    Handles project setup operations.

    This class manages setting up new projects and copying project files.
    """

    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the ProjectSetupExecutor.

        Args:
            console: Optional console for output
        """
        super().__init__(console)
        self.project_manager = ProjectSetupManager(console)

    def initialize_new_project(self):
        """
        Generate template folders for a new project using the Ingenious framework.
        """
        base_path = Path(__file__).parent.parent
        templates_paths = {
            "docker": base_path / "docker_template",
            "ingenious_extensions": base_path / "ingenious_extensions_template",
            "templates": base_path / "ingenious_extensions_template" / "templates",
            "extensions": base_path / "ingenious_extensions_template" / "extensions",
            "tmp": None,  # No template, just create the folder
        }

        self._log(f"Base path: {base_path}", "info")
        for path_name, path in templates_paths.items():
            if path:
                self._log(
                    f"Template path '{path_name}': {path} (exists: {path.exists()})",
                    "info",
                )

        # Process each template folder
        for folder_name, template_path in templates_paths.items():
            destination = Path.cwd() / folder_name

            # Skip if the destination folder already exists
            if destination.exists():
                self._log(
                    f"Folder '{folder_name}' already exists. Skipping...", "warning"
                )
                continue

            # Check if a template path exists (if applicable)
            if template_path and not template_path.exists():
                self._log(
                    f"Template directory '{template_path}' not found. Skipping...",
                    "error",
                )
                continue

            try:
                # Create the destination folder
                destination.mkdir(parents=True, exist_ok=True)

                if template_path:
                    # Define replacements for template files
                    replacements = {
                        "ingenious.ingenious_extensions_template": destination.name
                    }

                    # Copy template contents with replacements
                    success = self.project_manager.copy_template_directory(
                        template_dir=template_path,
                        target_dir=destination,
                        replacements=replacements,
                    )

                    if success:
                        self._log(
                            f"Folder '{folder_name}' created successfully.", "info"
                        )
                    else:
                        self._log(f"Failed to create folder '{folder_name}'.", "error")
                elif folder_name == "tmp":
                    # Create an empty context.md file in the 'tmp' folder
                    self.project_manager.create_file(destination / "context.md", "")
                    self._log(f"Folder '{folder_name}' created successfully.", "info")

            except Exception as e:
                self._log(f"Error processing folder '{folder_name}': {e}", "error")

        # Create a gitignore file
        gitignore_path = Path.cwd() / ".gitignore"
        if not gitignore_path.exists():
            git_ignore_content = ["*.pyc", "__pycache__", "*.log", "/files/", "/tmp/"]
            self.project_manager.create_file(
                gitignore_path, "\n".join(git_ignore_content)
            )

        # Create config files
        template_config_path = (
            templates_paths["ingenious_extensions"] / "config.template.yml"
        )
        if template_config_path.exists():
            config_path = Path.cwd() / "config.yml"
            self.project_manager.copy_file(template_config_path, config_path)
            self._log(f"Config file created successfully at {config_path}.", "info")
        else:
            self._log(
                f"Config file template not found at {template_config_path}. Skipping...",
                "warning",
            )

        # Create profile file
        template_profile_path = (
            templates_paths["ingenious_extensions"] / "profiles.template.yml"
        )
        if template_profile_path.exists():
            # Get user home directory
            home_dir = os.path.expanduser("~")
            profile_path = Path(home_dir) / Path(".ingenious") / Path("profiles.yml")

            # Ensure directory exists
            os.makedirs(os.path.dirname(profile_path), exist_ok=True)

            self.project_manager.copy_file(template_profile_path, profile_path)
            self._log(f"Profile file created successfully at {profile_path}", "info")
        else:
            self._log(
                f"Profile file template not found at {template_profile_path}. Skipping...",
                "warning",
            )

        self._log("Folder generation process completed.", "info")
        self._log(
            "Before executing set the environment variables INGENIOUS_PROJECT_PATH and INGENIOUS_PROFILE_PATH",
            "warning",
        )
        self._log("Before executing update config.yml and profiles.yml", "warning")
        self._log("To execute use ingen", "info")

    def copy_ingenious_folder(self, src: Path, dst: Path):
        """
        Copy the ingenious folder from source to destination.

        Args:
            src: Source directory path
            dst: Destination directory path
        """
        # Use the project manager to copy the directory
        success = self.project_manager.copy_directory(
            source=src,
            destination=dst,
            ignore_patterns=["__pycache__", ".git", ".DS_Store"],
        )

        if not success:
            self._log("Failed to copy ingenious folder.", "error")

    @staticmethod
    def pure_lib_include_dir_exists():
        """
        Check if the pure lib include directory exists.

        Returns:
            True if the directory exists, False otherwise
        """
        chk_path = Path(get_paths()["purelib"]) / Path("ingenious/")
        return os.path.exists(chk_path)

    @staticmethod
    def get_include_dir():
        """
        Get the include directory.

        Returns:
            The include directory path
        """
        chk_path = Path(get_paths()["purelib"]) / Path("ingenious/")
        # Does Check for the path
        if os.path.exists(chk_path):
            return chk_path
        else:
            path = Path(os.getcwd()) / Path("ingenious/")
            return path


class RunTestBatchAction(stage_executor_module.IActionCallable):
    """
    Action callable for running test batches.

    This class implements the IActionCallable interface to run test batches
    using the stage executor.
    """

    async def __call__(self, progress, task_id, **kwargs):
        """
        Execute the action.

        Args:
            progress: The progress tracker
            task_id: The task ID
            **kwargs: Additional arguments

        Raises:
            ValueError: If the batch run fails
        """
        module_name = "tests.run_tests"
        class_name = "RunBatches"
        try:
            repository_class_import = import_class_with_fallback(
                module_name, class_name
            )
            repository_class = repository_class_import(
                progress=progress, task_id=task_id
            )

            await repository_class.run(progress, task_id, **kwargs)

        except (ImportError, AttributeError) as e:
            raise ValueError(f"Batch Run Failed: {module_name}") from e
