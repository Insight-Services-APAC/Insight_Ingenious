import logging
import uuid
from abc import ABC, abstractmethod

from autogen.token_count_utils import count_token, get_max_token_limit
from openai.types.chat import ChatCompletionMessageParam
import ingenious.config.config as config
from ingenious.db.chat_history_repository import ChatHistoryRepository
from ingenious.dependencies import get_openai_service
from ingenious.errors.content_filter_error import ContentFilterError
from ingenious.models.chat import ChatRequest, ChatResponse
from ingenious.models.message import Message
from ingenious.utils.conversation_builder import (build_user_message)
from ingenious.utils.namespace_utils import import_class_with_fallback, get_path_from_namespace_with_fallback
import os
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

logger = logging.getLogger(__name__)


class IConversationPattern(ABC):
    _config: config.Config
    _memory_path: str
    _memory_file_path: str

    def __init__(self):
        super().__init__()
        self._config = config.get_config()
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

    @abstractmethod
    async def get_conversation_response(self, message: str, thread_memory: str) -> ChatResponse:
        pass


class IConversationFlow(ABC):
    _config: config.Config
    _memory_path: str
    _memory_file_path: str
    _logger: logging.Logger

    def __init__(self):
        super().__init__()
        self._config = config.get_config()
        self._memory_path = self.GetConfig().chat_history.memory_path
        self._memory_file_path = f"{self._memory_path}/context.md"
        self._logger = logging.getLogger(__name__)
        template_path = get_path_from_namespace_with_fallback(str(Path("templates") / Path("prompts")))
        self._logger.debug(f"Loading templates from: {template_path}")
        self._prompt_template_env = Environment(loader=FileSystemLoader(template_path), autoescape=True)

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

    @abstractmethod
    async def get_conversation_response(self, message: str, thread_memory: str) -> ChatResponse:
        pass


class multi_agent_chat_service:
    def __init__(
            self,
            chat_history_repository: ChatHistoryRepository,
            conversation_flow: str):
        self.chat_history_repository = chat_history_repository
        self.conversation_flow = conversation_flow
        self.openai_service = get_openai_service()

    async def get_chat_response(self, chat_request: ChatRequest) -> ChatResponse:
        if not chat_request.conversation_flow:
            raise ValueError(f"conversation_flow not set {chat_request}")

        if isinstance(chat_request.topic, str):
            chat_request.topic = [topic.strip() for topic in chat_request.topic.split(',')]

        # Initialize additional response fields - to be populated later
        thread_chat_history = [{"role": "user", "content": ""}]
        thread_memory = ''
        await self.chat_history_repository.update_memory()

        # Check if thread exists
        if not chat_request.thread_id:
            chat_request.thread_id = str(uuid.uuid4())
        else:
            # Get thread messages & add to messages list
            thread_messages = await self.chat_history_repository.get_thread_messages(chat_request.thread_id)
            thread_memory_list = await self.chat_history_repository.get_thread_memory(chat_request.thread_id)
            thread_memory = 'no existing context.'

            if chat_request.memory_record:
                if thread_memory_list:
                    for thread_memory in thread_memory_list:
                        if thread_memory != '':
                            thread_memory = thread_memory.content  # only one row is retrieved per thread
            else:
                await self.chat_history_repository.delete_user_memory(user_id=chat_request.user_id)

            msg = f'current_memory: {thread_memory}'
            logger.log(level=logging.INFO, msg=msg)
            print(msg)

            for thread_message in thread_messages:
                # Validate user_id
                # if thread_message.user_id != chat_request.user_id:
                #     raise ValueError("User ID does not match thread messages.")

                # Validate content_filter_results not present
                if thread_message.content_filter_results:
                    raise ContentFilterError(content_filter_results=thread_message.content_filter_results)

                thread_chat_history.append({"role": thread_message.role, "content": thread_message.content})

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

            conversation_flow_service_class = import_class_with_fallback(module_name, class_name)

            if chat_request.event_type:
                response_task = conversation_flow_service_class.get_conversation_response(
                    self,
                    message=chat_request.user_prompt,
                    memory_record_switch=chat_request.memory_record,
                    event_type=chat_request.event_type,
                    thread_memory=thread_memory,
                    thread_chat_history=thread_chat_history
                )
            else:
                response_task = conversation_flow_service_class.get_conversation_response(
                    self,
                    message=chat_request.user_prompt,
                    memory_record_switch=chat_request.memory_record,
                    thread_memory=thread_memory,
                    thread_chat_history=thread_chat_history
                )
            agent_response = await response_task

        # except ContentFilterError as cfe:
        #     # Update user message with content filter results
        #     await self.chat_history_repository.update_message_content_filter_results(
        #         user_message_id, chat_request.thread_id, cfe.content_filter_results)
        #     raise

        except Exception as e:
            logger.error(f"Error occurred while processing conversation flow: {e}")
            raise e

        # Save agent response
        agent_message_id = await self.chat_history_repository.add_message(
            Message(
                user_id=chat_request.user_id,
                thread_id=chat_request.thread_id,
                role="assistant",
                content=agent_response[0])
        )

        print("the response:", agent_response)
        _ = await self.chat_history_repository.add_memory(
            Message(
                user_id=chat_request.user_id,
                thread_id=chat_request.thread_id,
                role="memory_assistant",
                content=agent_response[1]),
        )

        # Get token counts
        try:
            max_token_count = get_max_token_limit(self.openai_service.model)
            if isinstance(agent_response, str):
                token_count = count_token(agent_response, self.openai_service.model)
            else:
                token_count = count_token(agent_response[0], self.openai_service.model)
            logger.debug(f"Token count: {token_count}/{max_token_count}")
        except Exception as e:
            logger.error(f"Error getting token count: {e}")
            max_token_count = 0
            token_count = 0

        return ChatResponse(
            thread_id=chat_request.thread_id,
            message_id=agent_message_id,
            agent_response=agent_response[0] or "Sorry we were unable to generate a response. Please try again.",
            token_count=token_count,
            max_token_count=max_token_count,
            memory_summary=agent_response[1],
        )

