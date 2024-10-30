import importlib
import logging
from abc import ABC, abstractmethod

from openai.types.chat import ChatCompletionMessageParam

from ingenious.db.chat_history_repository import ChatHistoryRepository
from ingenious.errors.content_filter_error import ContentFilterError
from ingenious.external_services.openai_service import OpenAIService
from ingenious.models.chat import Action, ChatRequest, ChatResponse, Product
from ingenious.models.message import Message
from ingenious.utils.conversation_builder import (build_message, build_system_prompt, build_user_message)
from ingenious.utils.namespace_utils import import_module_safely
from autogen.token_count_utils import count_token, get_max_token_limit
from ingenious.dependencies import get_openai_service

logger = logging.getLogger(__name__)


class IConversationPattern(ABC):
    @abstractmethod
    async def get_conversation_response(self, message: str, thread_memory: str) -> ChatResponse:
        pass


class multi_agent_chat_service:
    def __init__(
            self,
            chat_history_repository: ChatHistoryRepository,
            openai_service: OpenAIService,
            conversation_flow: str):
        self.chat_history_repository = chat_history_repository
        self.openai_service = openai_service
        self.conversation_flow = conversation_flow
        self.openai_service = get_openai_service()

    async def get_chat_response(self, chat_request: ChatRequest) -> ChatResponse:


        if not chat_request.conversation_flow:
            raise ValueError(f"conversation_flow not set {chat_request}")

        if isinstance(chat_request.topic, str):
            chat_request.topic = [topic.strip() for topic in chat_request.topic.split(',')]
        messages: list[ChatCompletionMessageParam] = []

        # Initialize additional response fields - to be populated later
        follow_up_questions: dict[str, str] = {}
        actions: list[Action] = []
        products: list[Product] = []
        thread_chat_history = [{"role": "user", "content": ""}]
        thread_memory = ''
        # await self.chat_history_repository.update_sql_memory()

        # Check if thread exists
        if not chat_request.thread_id:
            chat_request.thread_id = await self.chat_history_repository.create_thread()
        else:
            # Get thread messages & add to messages list
            thread_messages = await self.chat_history_repository.get_thread_messages(chat_request.thread_id)
            thread_memory_list = await self.chat_history_repository.get_thread_memory(chat_request.thread_id)
            thread_memory = 'New conversation'

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
                if thread_message.user_id != chat_request.user_id:
                    raise ValueError("User ID does not match thread messages.")

                # Validate content_filter_results not present
                if thread_message.content_filter_results:
                    raise ContentFilterError(content_filter_results=thread_message.content_filter_results)

                # Add thread message to messages list
                message = build_message(
                    role=thread_message.role,
                    content=thread_message.content,
                    user_name=chat_request.user_name,
                    tool_calls=thread_message.tool_calls,
                    tool_call_id=thread_message.tool_call_id,
                    tool_call_function=thread_message.tool_call_function)
                messages.append(message)

                thread_chat_history.append({"role": thread_message.role, "content": thread_message.content})


        # If system prompt is not first message add it in the beginning
        if not messages or messages[0]["role"] != "system":
            # Add system prompt
            system_prompt_message = build_system_prompt(user_name=chat_request.user_name)
            messages.insert(0, system_prompt_message)

            # Save system prompt message
            await self.chat_history_repository.add_message(
                Message(
                    user_id=chat_request.user_id,
                    thread_id=chat_request.thread_id,
                    role=system_prompt_message["role"],
                    content=system_prompt_message["content"])
            )

        # Add latest user message
        user_message = build_user_message(chat_request.user_prompt, chat_request.user_name)
        messages.append(user_message)

        # Save user message
        user_message_id = await self.chat_history_repository.add_message(
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
            module_name = f"ingenious.services.chat_services.multi_agent.conversation_flows.{self.conversation_flow.lower()}.{self.conversation_flow.lower()}"
            class_name = "ConversationFlow"

             
            conversation_flow_service_class = import_module_safely(module_name, class_name)                        

            response_task = conversation_flow_service_class.get_conversation_response(
                message=chat_request.user_prompt,
                memory_record_switch = chat_request.memory_record,
                thread_memory = thread_memory,
                topics = chat_request.topic,
                thread_chat_history = thread_chat_history
            )
            response = await response_task

        # except ContentFilterError as cfe:
        #     # Update user message with content filter results
        #     await self.chat_history_repository.update_message_content_filter_results(
        #         user_message_id, chat_request.thread_id, cfe.content_filter_results)
        #     raise

        except Exception as e:
            logger.error(f"Error occurred while processing conversation flow: {e}")
            raise e

        agent_response = response

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
            followup_questions=follow_up_questions,
            actions=actions,
            products=products,
            token_count=token_count,
            max_token_count=max_token_count,
            memory_summary = agent_response[1]
        )
