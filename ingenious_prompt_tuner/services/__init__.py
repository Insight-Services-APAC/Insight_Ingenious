"""Service for managing file operations and prompt templates."""

import os
from typing import List, Optional

import yaml

# We'll define our own Events class below instead of importing a placeholder
# from ingenious.domain.model.common.test_data import Events
from ingenious.common.utils.namespace_utils import get_path_from_namespace_with_fallback

# Fixed imports to use the correct paths
from ingenious_prompt_tuner.utilities import FileStorage


# Create a custom Events class that has the needed functionality
class Events:
    """A simple class to handle events data."""

    def __init__(self, fs: Optional[FileStorage] = None):
        """Initialize with optional file storage."""
        self.fs = fs
        self.events = []

    def load_events_from_file(self, file_path: str, file_name: str = "events.yml"):
        """Load events from a YAML file."""
        if self.fs:
            content = self.fs.read_file(file_name=file_name, file_path=file_path)
            if content:
                self.events = yaml.safe_load(content) or []
        return self.events


class FileService:
    """Handles file operations for the prompt tuner."""

    def __init__(self, config):
        """Initialize with application configuration."""
        self.config = config
        self.fs = FileStorage(config, Category="revisions")
        self.fs_data = FileStorage(config, Category="data")
        self.events = Events(fs=self.fs)
        self.prompt_template_folder = None
        self.functional_tests_folder = None
        self.data_folder = None

    def read_file(self, file_name: str, file_path: str) -> str:
        """Read a file's contents."""
        content = self.fs.read_file(file_name=file_name, file_path=file_path)
        return content or ""  # Return empty string if None

    def write_file(self, file_name: str, file_path: str, content: str) -> bool:
        """Write content to a file."""
        return self.fs.write_file(
            content=content, file_name=file_name, file_path=file_path
        )

    def check_if_file_exists(self, file_name: str, file_path: str) -> bool:
        """Check if a file exists."""
        return self.fs.check_if_file_exists(file_name=file_name, file_path=file_path)

    def list_files(self, file_path: str) -> List[str]:
        """List files in a directory."""
        return self.fs.list_files(file_path)

    def get_prompt_template_path(self, revision_id: str) -> str:
        """Get the prompt template path for a revision."""
        return self.fs.get_prompt_template_path(revision_id)

    def get_functional_tests_path(self, revision_id: str) -> str:
        """Get the functional tests path for a revision."""
        path = self.fs.get_functional_tests_path(revision_id)
        self.functional_tests_folder = path
        return path

    def ensure_prompt_templates(
        self, revision_id: str, force_copy: bool = False
    ) -> str:
        """Ensure prompt templates exist for a revision, copying if needed."""
        source_prompt_folder = get_path_from_namespace_with_fallback(
            "templates/prompts"
        )
        target_prompt_folder = self.fs.get_prompt_template_path(revision_id)

        # Check if folders changed or need initialization
        folder_changed = self.prompt_template_folder != target_prompt_folder
        if folder_changed:
            self.prompt_template_folder = target_prompt_folder

        # Check if prompts exist
        existing_prompts = self.fs.list_files(target_prompt_folder)
        no_existing_prompts = len(existing_prompts) == 0

        # Copy prompts if needed
        if force_copy or no_existing_prompts:
            print(f"Copying prompts to {target_prompt_folder}")
            for file in os.listdir(source_prompt_folder):
                if ".jinja" in file:
                    with open(f"{source_prompt_folder}/{file}", "r") as f:
                        content = f.read()
                        self.fs.write_file(content, file, target_prompt_folder)

        return target_prompt_folder

    def ensure_test_data(self, revision_id: str, force_copy: bool = False) -> str:
        """Ensure test data exists for a revision, copying if needed."""
        target_folder = f"functional_test_outputs/{revision_id}"

        # Check if folder changed
        folder_changed = self.functional_tests_folder != target_folder
        if folder_changed:
            self.functional_tests_folder = target_folder

        # Check if data exists
        existing_files = self.fs.list_files(target_folder)
        no_existing_files = len(existing_files) == 0

        # Copy data if needed
        if force_copy or no_existing_files:
            source_folder = get_path_from_namespace_with_fallback("sample_data")
            source_files = [
                f for f in os.listdir(source_folder) if "readme.md" not in f.lower()
            ]

            for file in source_files:
                if any(ext in file for ext in [".md", ".yml", ".json"]):
                    with open(f"{source_folder}/{file}", "r") as f:
                        content = f.read()

                        if file == "events.yml":
                            # Event file goes to test folder
                            self.fs.write_file(content, file, target_folder)
                        else:
                            # Data files go to data folder
                            self.fs_data.write_file(content, file, target_folder)

        return target_folder

    def get_events(self, revision_id: str) -> Events:
        """Get events for a revision."""
        self.events.load_events_from_file(f"functional_test_outputs/{revision_id}")
        return self.events
