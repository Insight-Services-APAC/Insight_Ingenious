import asyncio
import json
import os
from flask import Flask, render_template, request, redirect, url_for, session, send_file, Response, stream_with_context
from functools import wraps
from ingenious.files.files_repository import FileStorage
from ingenious.models.test_data import Events
from ingenious.utils.namespace_utils import get_path_from_namespace_with_fallback


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated


def requires_selected_revision(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        selected_revision = get_selected_revision_direct_call()
        if not selected_revision:
            return redirect(url_for('index.home'))
        return f(*args, **kwargs)

    return decorated_function


def get_selected_revision_direct_call():
    selected_revision = request.cookies.get('selected_revision')
    if selected_revision:
        return selected_revision
    return None


def set_selected_revision_direct_call(revision_id):
    response = Response()
    response.set_cookie('selected_revision', revision_id)
    return response


class utils_class:
    def __init__(self, config):
        self.config = config
        self.fs: FileStorage = FileStorage(config, Category="revisions")
        self.fs_data: FileStorage = FileStorage(config, Category="data")
        self.events: Events = Events(fs=self.fs)
        self.prompt_template_folder: str = None
        self.functional_tests_folder: str = None
        self.data_folder: str = None

    def read_file(self, file_name, file_path):
        self.fs.read_file(file_name=file_name, file_path=file_path)

    def get_config(self):
        return self.config

    async def get_prompt_template_folder(self, revision_id=None, force_copy_from_source=False):
        if revision_id is None:
            revision_id = get_selected_revision_direct_call()

        source_prompt_folder = get_path_from_namespace_with_fallback("templates/prompts")        
        target_prompt_folder = await self.fs.get_prompt_template_path(revision_id)
        no_existing_prompts = False

        if not self.prompt_template_folder == target_prompt_folder:
            self.prompt_template_folder = target_prompt_folder
            # Revision has changed so we need to recheck the prompt folder
            existing_prompts = await self.fs.list_files(target_prompt_folder)
            if len(existing_prompts) == 0:
                no_existing_prompts = True
        
        if force_copy_from_source:
            print("Force copying prompts from the source")

        if self.prompt_template_folder is None:
            print("Prompt folder is not set")

        if no_existing_prompts:
            print("Prompt folder is Empty")

        # Copy the prompts from source    
        if self.prompt_template_folder is None or force_copy_from_source or no_existing_prompts:
            if no_existing_prompts or force_copy_from_source:
                print("Copying prompts from the template folder to the prompts folder")
                for file in os.listdir(source_prompt_folder):
                    if ".jinja" in file:
                        # read the file and write it to the local_files
                        with open(f"{source_prompt_folder}/{file}", "r", encoding="utf-8") as f:
                            content = f.read()
                            await self.fs.write_file(content, file, target_prompt_folder)
            self.prompt_template_folder = target_prompt_folder

        return self.prompt_template_folder

    async def get_functional_tests_folder(self, revision_id=None, force_copy_from_source=False):
        if revision_id is None:
            revision_id = get_selected_revision_direct_call()
        
        target_folder = f"functional_test_outputs/{revision_id}"
        no_existing_events = []
        if not self.functional_tests_folder == target_folder:
            self.functional_tests_folder = target_folder
            # Revision has changed so we need to recheck the prompt folder
            existing_events = await self.fs.list_files(target_folder)
            if len(existing_events) == 0:
                no_existing_events = True

        if self.functional_tests_folder is None or force_copy_from_source or no_existing_events:
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
                    if ".md" in file or ".yml" or '.json' in file:
                        # read the file and write it to the local_files
                        with open(f"{source_folder_code}/{file}", "r", encoding='utf-8') as f:
                            content = f.read()
                            if file == "events.yml":
                                # write the event file to the same location as the prompts
                                await self.fs.write_file(content, file, target_folder)
                            else:
                                # write any data files to the data folder
                                await self.fs_data.write_file(content, file, target_folder)
            self.functional_tests_folder = target_folder

        return self.functional_tests_folder
    
    async def get_data_folder(self, revision_id=None, force_copy_from_source=False):
        if revision_id is None:
            revision_id = get_selected_revision_direct_call()

        source_folder = get_path_from_namespace_with_fallback("sample_data")
        target_folder = f"functional_test_outputs/{revision_id}"
        no_existing_data = []

        if not self.data_folder == target_folder:
            self.data_folder = target_folder
            # Revision has changed so we need to recheck the prompt folder
            existing_data = await self.fs.list_files(target_folder)
            if len(existing_data) == 0:
                no_existing_data = True
        
        if self.data_folder is None or force_copy_from_source or no_existing_data == 0:
            source_folder = get_path_from_namespace_with_fallback("sample_data")
            target_folder = f"functional_test_outputs/{revision_id}"
            if (await self.fs_data.list_files(target_folder) is None) or force_copy_from_source:
                for file in os.listdir(source_folder):
                    if ".json" in file:
                        # read the file and write it to the local_files
                        with open(f"{source_folder}/{file}", "r", encoding='utf-8') as f:
                            content = f.read()
                            await self.fs_data.write_file(content, file, target_folder)
            self.data_folder = target_folder

        return self.data_folder

    async def get_events(self, revision_id) -> Events:

        await self.events.load_events_from_file(f"functional_test_outputs/{revision_id}")
        return self.events


