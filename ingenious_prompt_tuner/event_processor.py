import datetime
import json
from typing import List

import jsonpickle
from ingenious.models.chat import ChatRequest
from ingenious.models.config import Config
from ingenious.files.files_repository import FileStorage
from ingenious.models.test_data import Events
from ingenious.services.chat_service import ChatService
import ingenious.dependencies as ingen_deps
from ingenious.utils.namespace_utils import get_path_from_namespace_with_fallback
import os
from ingenious.models.agent import Agent


class functional_tests:

    def __init__(
        self,
        config: Config,
        revision_prompt_folder: str,
        revision_id: str,
        make_llm_calls: bool,
    ):
        self.config = config
        self.fs = FileStorage(self.config)
        self.revision_prompt_folder = revision_prompt_folder
        self.revision_id = revision_id
        self.make_llm_calls = make_llm_calls

    async def pre_process_file(self, file_name, file_path, revision_id):
        # copy files from
        pass
    
    async def get_prompt_template_folder(self):
        source_prompt_folder = get_path_from_namespace_with_fallback("templates/prompts")
        target_prompt_folder = f"templates/prompts/{self.revision_id}"
        if await self.fs.list_files(target_prompt_folder) is None:
            print("No prompts found in the revision prompts folder")
            print("Copying prompts from the template folder to the prompts folder")
            for file in os.listdir(source_prompt_folder):
                # read the file and write it to the local_files
                with open(f"{source_prompt_folder}/{file}", "r") as f:
                    content = f.read()
                    await self.fs.write_file(content, file, target_prompt_folder)
        
        return target_prompt_folder

    async def run_event_from_pre_processed_file(
        self, event_type, identifier, file_name, agents: List[Agent], conversation_flow: str
    ):
        events = Events(self.fs)
        # Note sample data is loaded from the revision folder
        file_path = f"functional_test_outputs/{self.revision_id}"
        await Events.load_events_from_file(events, file_path)
        # Get payload file from the file system
        file_contents = await self.fs.read_file(
            file_name=file_name, file_path=file_path
        )
        json_object = json.loads(file_contents)

        # Need to put flow into the test data object
        self.chat_service = ChatService(
            chat_service_type="multi_agent",
            chat_history_repository=ingen_deps.get_chat_history_repository(),
            conversation_flow=conversation_flow,
            config=self.config
        )

        # Make sure that the prompt template folder exists
        await self.get_prompt_template_folder()

        print(f"Processing {file_name}")

        # thread_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        json_object["identifier"] = identifier
        json_object["revision_id"] = self.revision_id
        if self.make_llm_calls:
            chat_request = ChatRequest(
                thread_id=identifier,
                user_prompt=jsonpickle.dumps(json_object, unpicklable=False),
                conversation_flow=conversation_flow,
                event_type=event_type
            )

            response = await self.chat_service.get_chat_response(chat_request)

            # print(response)
