import logging
from typing import List, Optional
import uuid
from abc import ABC, abstractmethod

from openai.types.chat import ChatCompletionMessageParam
import ingenious.config.config as ig_config
from ingenious.db.chat_history_repository import ChatHistoryRepository
from ingenious.dependencies import get_openai_service
from ingenious.errors.content_filter_error import ContentFilterError
from ingenious.files.files_repository import FileStorage
from ingenious.models.chat import IChatRequest, IChatResponse
from ingenious.models.message import Message
from ingenious.utils.conversation_builder import (build_user_message)
from ingenious.utils.namespace_utils import import_class_with_fallback, get_path_from_namespace_with_fallback
import os
from jinja2 import Environment, FileSystemLoader
from pathlib import Path


logger = logging.getLogger(__name__)


class multi_agent_chat_service:
    config: ig_config.Config
    chat_history_repository: ChatHistoryRepository
    conversation_flow: str
    openai_service: Optional[ChatCompletionMessageParam]
    
    def __init__(
            self,
            config: ig_config.Config, 
            chat_history_repository: ChatHistoryRepository,
            conversation_flow: str):
        self.config = config
        self.chat_history_repository = chat_history_repository
        self.conversation_flow = conversation_flow
        self.openai_service = get_openai_service()

    async def get_chat_response(self, chat_request: IChatRequest) -> IChatResponse:
        if not chat_request.conversation_flow:
            raise ValueError(f"conversation_flow not set {chat_request}")

        if isinstance(chat_request.topic, str):
            chat_request.topic = [topic.strip() for topic in chat_request.topic.split(',')]

        # Initialize additional response fields - to be populated later
        chat_request.thread_chat_history = [{"role": "user", "content": ""}]
        thread_memory = ''

        # Check if thread exists
        if not chat_request.thread_id:
            chat_request.thread_id = str(uuid.uuid4())
        else:
            # Get thread messages & add to messages list
            thread_messages = await self.chat_history_repository.get_thread_messages(chat_request.thread_id)
            chat_request.thread_memory = 'no existing context.'

            msg = f'current_memory: {chat_request.thread_memory}'
            logger.log(level=logging.INFO, msg=msg)
            # print(msg)

            for thread_message in thread_messages:
                # Validate user_id
                # if thread_message.user_id != chat_request.user_id:
                #     raise ValueError("User ID does not match thread messages.")

                # Validate content_filter_results not present
                if thread_message.content_filter_results:
                    raise ContentFilterError(content_filter_results=thread_message.content_filter_results)

                chat_request.thread_chat_history.append({"role": thread_message.role, "content": thread_message.content})

        # Add latest user message
        user_message = build_user_message(chat_request.user_prompt, chat_request.user_name)
        _ = await self.chat_history_repository.add_message(
            Message(
                user_id=chat_request.user_id,
                thread_id=chat_request.thread_id,
                role=user_message["role"],
                content=str(user_message["content"]))
        )

        try:
            # call specific agent flow here and get final response
            if not self.conversation_flow:
                self.conversation_flow = chat_request.conversation_flow
            if not self.conversation_flow:
                raise ValueError(f"conversation_flow4 not set {chat_request}")
            module_name = f"services.chat_services.multi_agent.conversation_flows.{self.conversation_flow.lower()}.{self.conversation_flow.lower()}"
            class_name = "ConversationFlow"

            conversation_flow_service_class: IConversationFlow = import_class_with_fallback(module_name, class_name)

            conversation_flow_service_class_instance = conversation_flow_service_class()
            
            response_task = conversation_flow_service_class_instance.get_conversation_response(
                chat_request=chat_request
            )
    
            agent_response = await response_task

        except Exception as e:
            logger.error(f"Error occurred while processing conversation flow: {e}")
            raise e

        return agent_response


class IConversationPattern(ABC):
    _config: ig_config.Config
    _memory_path: str
    _memory_file_path: str
    
    def __init__(self):
        super().__init__()
        self._config = ig_config.get_config()
        self._memory_path = self.GetConfig().chat_history.memory_path
        self._memory_file_path = f"{self._memory_path}/context.md"
    
    def GetConfig(self):
        return self._config
    
    def Get_Models(self):
        return self._config.models.__dict__

    def Get_Memory_Path(self):
        return self._memory_path
    
    def Get_Memory_File(self):
        return self._memory_file_path

    def Maintain_Memory(self, new_content, max_words=150):
        file_path = self._memory_file_path()
        if os.path.exists(file_path):
            with open(file_path, "r") as memory_file:
                current_content = memory_file.read()
        else:
            current_content = ""

        # Combine the current content and the new content
        combined_content = current_content + " " + new_content
        words = combined_content.split()

        # Keep only the last `max_words` words
        truncated_content = " ".join(words[-max_words:])

        # Write the truncated content back to the file
        with open(file_path, "w") as memory_file:
            memory_file.write(truncated_content)

    async def write_llm_responses_to_file(
            self,
            response_array: List[dict],
            event_type: str,
            output_path: str
    ):
        fs = FileStorage(self.config)
        for res in response_array:
            make_llm_calls = True
            if make_llm_calls:
                this_response = res["chat_response"]
            else:
                this_response = "Insight not yet generated"

            await fs.write_file(this_response, f"agent_response_{event_type}_{res['chat_title']}.md", output_path)

    @abstractmethod
    async def get_conversation_response(self, message: str, thread_memory: str) -> IChatResponse:
        pass


class IConversationFlow(ABC):
    _config: ig_config.Config
    _memory_path: str
    _memory_file_path: str
    _logger: logging.Logger

    def __init__(self):
        super().__init__()
        self._config = ig_config.get_config()
        self._memory_path = self.GetConfig().chat_history.memory_path
        self._memory_file_path = f"{self._memory_path}/context.md"
        self._logger = logging.getLogger(__name__)
        
    def GetConfig(self):
        return self._config
    
    async def Get_Template(self, revision_id: str = None, file_name: str = "user_prompt.md"):
        if revision_id:
            template_path = str(Path("templates")/Path("prompts")/Path(revision_id))
        else: 
            template_path = str(Path("templates")/Path("prompts"))

        fs = FileStorage(self._config)
        content = await fs.read_file(file_name=file_name, file_path=template_path)
        if content is None:
            print(f"Prompt file {file_name} not found in {template_path}")
            return ""
        env = Environment()
        template = env.from_string(content)
        return template.render()
    
    def Get_Models(self):
        return self._config.models

    def Get_Memory_Path(self):
        return self._memory_path
    
    def Get_Memory_File(self):
        return self._memory_file_path

    def Maintain_Memory(self, new_content, max_words=150):
        file_path = self._memory_file_path()
        if os.path.exists(file_path):
            with open(file_path, "r") as memory_file:
                current_content = memory_file.read()
        else:
            current_content = ""

        # Combine the current content and the new content
        combined_content = current_content + " " + new_content
        words = combined_content.split()

        # Keep only the last `max_words` words
        truncated_content = " ".join(words[-max_words:])

        # Write the truncated content back to the file
        with open(file_path, "w") as memory_file:
            memory_file.write(truncated_content)

    async def write_llm_responses_to_file(
            self,
            response_array: List[dict],
            event_type: str,
            identifier: str,
            revison_id: str
    ):
        output_path = f"functional_test_outputs/{revison_id}"
        fs = FileStorage(self._config)
        for res in response_array:
            make_llm_calls = True
            if make_llm_calls:
                this_response = res["chat_response"]
            else:
                this_response = "Insight not yet generated"

            await fs.write_file(this_response, f"agent_response_{event_type}_{res['chat_title']}_{identifier}.md", output_path)

    @abstractmethod
    async def get_conversation_response(self, chat_request: IChatRequest) -> IChatResponse:
        pass



# Save agent response
        # agent_message_id = await self.chat_history_repository.add_message(
        #     Message(
        #         user_id=chat_request.user_id,
        #         thread_id=chat_request.thread_id,
        #         role="assistant",
        #         content=agent_response[0])
        # )

        # # print("the response:", agent_response)
        # _ = await self.chat_history_repository.add_memory(
        #     Message(
        #         user_id=chat_request.user_id,
        #         thread_id=chat_request.thread_id,
        #         role="memory_assistant",
        #         content=agent_response[1]),
        # )