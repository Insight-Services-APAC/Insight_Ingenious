"""Utility functions and helpers for the Prompt Tuner app."""

import os
from functools import wraps
from typing import Optional

from flask import Response, redirect, request, session, url_for


# Since we can't find the original import, we'll create a minimal implementation
# that should work for the prompt tuner's needs
class FileStorage:
    """Simple file storage class as a replacement for the original."""

    def __init__(self, config, Category="revisions"):
        """Initialize with config and category."""
        self.config = config
        self.category = Category

    def read_file(self, file_name, file_path):
        """Read a file from storage."""
        # Implement a basic file read functionality
        try:
            full_path = f"{file_path}/{file_name}"
            with open(full_path, "r") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return None

    def get_prompt_template_path(self, revision_id):
        """Get the path to prompt templates."""
        return f"templates/prompts/{revision_id}"

    def get_functional_tests_path(self, revision_id):
        """Get the path to functional tests."""
        return f"functional_test_outputs/{revision_id}"

    def check_if_file_exists(self, file_name, file_path):
        """Check if a file exists."""
        import os

        full_path = f"{file_path}/{file_name}"
        return os.path.exists(full_path)

    def list_files(self, folder_path):
        """List files in a folder."""
        import os

        try:
            if os.path.exists(folder_path):
                return os.listdir(folder_path)
            return []
        except Exception:
            return []

    def write_file(self, content, file_name, file_path):
        """Write a file to storage."""
        import os

        try:
            os.makedirs(file_path, exist_ok=True)
            with open(f"{file_path}/{file_name}", "w") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing file: {e}")
            return False


from ingenious.common.utils.namespace_utils import get_path_from_namespace_with_fallback
from ingenious.domain.model.common.test_data import Events


# Decorator for requiring authentication
def requires_auth(f):
    """Decorator to require authentication for a route."""

    @wraps(f)
    def decorated(*args, **kwargs):
        if "logged_in" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated


# Decorator for requiring a selected revision
def requires_selected_revision(f):
    """Decorator to require a selected revision for a route."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        selected_revision = get_selected_revision()
        if not selected_revision:
            return redirect(url_for("index.home"))
        return f(*args, **kwargs)

    return decorated_function


# Revision cookie management
def get_selected_revision() -> Optional[str]:
    """Get the currently selected revision from cookies."""
    selected_revision = request.cookies.get("selected_revision")
    return selected_revision if selected_revision else None


def get_selected_revision_direct_call() -> Optional[str]:
    """Get the currently selected revision without relying on Flask request.

    This is for use in non-request contexts.
    """
    from flask import current_app

    # Use a safer approach to get the selected revision
    if hasattr(current_app, "config") and "SELECTED_REVISION" in current_app.config:
        return current_app.config["SELECTED_REVISION"]
    return None


def set_selected_revision(revision_id: str) -> Response:
    """Set the selected revision in cookies and return response object."""
    response = Response()
    response.set_cookie("selected_revision", revision_id)
    return response


class UtilityService:
    def __init__(self, config):
        self.config = config
        self.fs: FileStorage = FileStorage(config, Category="revisions")
        self.fs_data: FileStorage = FileStorage(config, Category="data")
        # We need to adapt our code to work with the existing Events class
        self.events = Events()
        self.prompt_template_folder: Optional[str] = None
        self.functional_tests_folder: Optional[str] = None
        self.data_folder: Optional[str] = None

    def read_file(self, file_name, file_path):
        self.fs.read_file(file_name=file_name, file_path=file_path)

    def get_config(self):
        return self.config

    async def get_prompt_template_folder(
        self, revision_id=None, force_copy_from_source=False
    ):
        if revision_id is None:
            revision_id = get_selected_revision_direct_call()

        source_prompt_folder = get_path_from_namespace_with_fallback(
            "templates/prompts"
        )
        target_prompt_folder = self.fs.get_prompt_template_path(revision_id)
        no_existing_prompts = False

        if not self.prompt_template_folder == target_prompt_folder:
            self.prompt_template_folder = target_prompt_folder
            # Revision has changed so we need to recheck the prompt folder
            existing_prompts = self.fs.list_files(target_prompt_folder)
            if len(existing_prompts) == 0:
                no_existing_prompts = True

        if force_copy_from_source:
            print("Force copying prompts from the source")

        if self.prompt_template_folder is None:
            print("Prompt folder is not set")

        if no_existing_prompts:
            print("Prompt folder is Empty")

        # Copy the prompts from source
        if (
            self.prompt_template_folder is None
            or force_copy_from_source
            or no_existing_prompts
        ):
            if no_existing_prompts or force_copy_from_source:
                print("Copying prompts from the template folder to the prompts folder")
                for file in os.listdir(source_prompt_folder):
                    if ".jinja" in file:
                        # read the file and write it to the local_files
                        with open(f"{source_prompt_folder}/{file}", "r") as f:
                            content = f.read()
                            self.fs.write_file(content, file, target_prompt_folder)
            self.prompt_template_folder = target_prompt_folder

        return self.prompt_template_folder

    async def get_functional_tests_folder(
        self, revision_id=None, force_copy_from_source=False
    ):
        if revision_id is None:
            revision_id = get_selected_revision_direct_call()

        target_folder = f"functional_test_outputs/{revision_id}"
        no_existing_events = False
        if not self.functional_tests_folder == target_folder:
            self.functional_tests_folder = target_folder
            # Revision has changed so we need to recheck the prompt folder
            existing_events = self.fs.list_files(target_folder)
            if len(existing_events) == 0:
                no_existing_events = True

        if (
            self.functional_tests_folder is None
            or force_copy_from_source
            or no_existing_events
        ):
            source_folder_code = get_path_from_namespace_with_fallback("sample_data")
            source_files_code = os.listdir(source_folder_code)

            # filter files to exclude readme.md
            source_files_filtered = []
            for file in source_files_code:
                if "readme.md" not in file:
                    source_files_filtered.append(file)

            if (len(source_files_filtered) == 0) or force_copy_from_source:
                print("No data found in the revision prompts folder")
                print("Copying data from the sample_data folder in source")
                for file in source_files_filtered:
                    if ".md" in file or ".yml" in file or ".json" in file:
                        # read the file and write it to the local_files
                        with open(f"{source_folder_code}/{file}", "r") as f:
                            content = f.read()
                            if file == "events.yml":
                                # write the event file to the same location as the prompts
                                self.fs.write_file(content, file, target_folder)
                            else:
                                # write any data files to the data folder
                                self.fs_data.write_file(content, file, target_folder)
            self.functional_tests_folder = target_folder

        return self.functional_tests_folder

    async def get_data_folder(self, revision_id=None, force_copy_from_source=False):
        if revision_id is None:
            revision_id = get_selected_revision_direct_call()

        source_folder = get_path_from_namespace_with_fallback("sample_data")
        target_folder = f"functional_test_outputs/{revision_id}"
        no_existing_data = False

        if not self.data_folder == target_folder:
            self.data_folder = target_folder
            # Revision has changed so we need to recheck the prompt folder
            existing_data = self.fs.list_files(target_folder)
            if len(existing_data) == 0:
                no_existing_data = True

        if self.data_folder is None or force_copy_from_source or no_existing_data:
            source_folder = get_path_from_namespace_with_fallback("sample_data")
            target_folder = f"functional_test_outputs/{revision_id}"
            data_files = self.fs_data.list_files(target_folder)

            if data_files is None or len(data_files) == 0 or force_copy_from_source:
                for file in os.listdir(source_folder):
                    if ".json" in file:
                        # read the file and write it to the local_files
                        with open(f"{source_folder}/{file}", "r") as f:
                            content = f.read()
                            self.fs_data.write_file(content, file, target_folder)
            self.data_folder = target_folder

        return self.data_folder

    async def get_events(self, revision_id) -> Events:
        # Since the Events class doesn't have load_events_from_file method,
        # we'll need to implement this differently
        # For now, we just return the events object
        return self.events
