import logging
import uuid as uuid_module
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from jinja2 import Environment
from openai.types.chat import ChatCompletionMessageParam

import ingenious.config.config as ig_config

if TYPE_CHECKING:
    from ingenious.models.config import Config
from ingenious.core.structured_logging import get_logger
from ingenious.db.chat_history_repository import ChatHistoryRepository
from ingenious.errors.content_filter_error import ContentFilterError
from ingenious.files.files_repository import FileStorage
from ingenious.models.chat import IChatRequest, IChatResponse
from ingenious.utils.namespace_utils import (
    import_class_with_fallback,
    normalize_workflow_name,
)

logger = get_logger(__name__)


class multi_agent_chat_service:
    config: "Config"
    chat_history_repository: ChatHistoryRepository
    conversation_flow: str
    openai_service: Optional[ChatCompletionMessageParam]

    def __init__(
        self,
        config: "Config",
        chat_history_repository: ChatHistoryRepository,
        conversation_flow: str,
    ):
        self.config = config
        self.chat_history_repository = chat_history_repository
        self.conversation_flow = conversation_flow
        # Get openai_service from config if available
        if hasattr(config, "openai_service_instance"):
            self.openai_service = config.openai_service_instance  # type: ignore
        else:
            # OpenAI service should be injected via config
            raise RuntimeError(
                "OpenAI service not properly configured. Please ensure the service is initialized with proper dependencies."
            )

    async def get_chat_response(self, chat_request: IChatRequest) -> IChatResponse:
        if not chat_request.conversation_flow:
            raise ValueError(f"conversation_flow not set {chat_request}")

        if isinstance(chat_request.topic, str):
            chat_request.topic = [
                topic.strip() for topic in chat_request.topic.split(",")
            ]  # type: ignore

        # Initialize additional response fields - to be populated later
        chat_request.thread_chat_history = [{"role": "user", "content": ""}]  # type: ignore
        # thread_memory = ""

        # Check if thread exists
        if not chat_request.thread_id:
            chat_request.thread_id = str(uuid_module.uuid4())

        # Get thread messages & add to messages list
        thread_messages = await self.chat_history_repository.get_thread_messages(
            chat_request.thread_id
        )
        # Build thread memory from messages
        if thread_messages:
            memory_parts = []
            for msg in thread_messages[-10:]:  # Use last 10 messages
                memory_parts.append(f"{msg.role}: {msg.content[:200]}...")
            chat_request.thread_memory = "\n".join(memory_parts)
        else:
            chat_request.thread_memory = "no existing context."

        logger.info(
            "Current memory state",
            thread_id=chat_request.thread_id,
            memory_length=len(chat_request.thread_memory or ""),
        )
        logger.debug(
            "Thread messages and memory processed",
            message_count=len(thread_messages or []),
            operation="process_thread_context",
        )

        for thread_message in thread_messages or []:
            # Validate user_id
            # if thread_message.user_id != chat_request.user_id:
            #     raise ValueError("User ID does not match thread messages.")

            # Validate content_filter_results not present
            if thread_message.content_filter_results:
                raise ContentFilterError(
                    content_filter_results=thread_message.content_filter_results
                )

            if (
                hasattr(chat_request, "thread_chat_history")
                and chat_request.thread_chat_history
            ):
                chat_request.thread_chat_history.append(  # type: ignore
                    {"role": thread_message.role, "content": thread_message.content}
                )

        try:
            # call specific agent flow here and get final response
            logger.info(
                "Starting conversation flow execution",
                conversation_flow=self.conversation_flow,
                operation="conversation_flow_start",
            )
            if not self.conversation_flow:
                self.conversation_flow = chat_request.conversation_flow
            if not self.conversation_flow:
                raise ValueError(f"conversation_flow4 not set {chat_request}")

            # Normalize workflow name to support both hyphenated and underscored formats
            normalized_flow = normalize_workflow_name(self.conversation_flow)
            module_name = f"services.chat_services.multi_agent.conversation_flows.{normalized_flow}.{normalized_flow}"
            class_name = "ConversationFlow"
            logger.debug(
                "Loading conversation flow module",
                module_name=module_name,
                class_name=class_name,
                original_workflow=self.conversation_flow,
                normalized_workflow=normalized_flow,
                operation="module_loading",
            )

            conversation_flow_service_class = import_class_with_fallback(
                module_name, class_name
            )
            logger.info(
                "Successfully loaded conversation flow class",
                class_type=str(type(conversation_flow_service_class)),
                conversation_flow=self.conversation_flow,
                operation="class_loading_success",
            )

            # Try to instantiate with new pattern first (IConversationFlow)
            try:
                # Check if it's the new pattern by trying to instantiate with parent service
                conversation_flow_service_class_instance = (
                    conversation_flow_service_class(
                        parent_multi_agent_chat_service=self
                    )
                )

                response_task = (
                    conversation_flow_service_class_instance.get_conversation_response(
                        chat_request=chat_request
                    )
                )

                agent_response = await response_task

            except TypeError as te:
                # Fall back to old pattern (static methods)
                logger.info(
                    "Using static method pattern for conversation flow",
                    conversation_flow=self.conversation_flow,
                    type_error=str(te),
                    operation="fallback_static_method",
                )

                # Try different static method signatures
                import inspect

                sig = inspect.signature(
                    conversation_flow_service_class.get_conversation_response
                )
                params = list(sig.parameters.keys())
                logger.debug(
                    "Analyzing method signature",
                    parameters=params,
                    param_count=len(params),
                    operation="method_signature_analysis",
                )

                if len(params) == 1 and params[0] not in ["self", "cls"]:
                    # Single parameter - likely ChatRequest
                    logger.debug(
                        "Using single ChatRequest parameter",
                        operation="single_param_call",
                    )
                    response_task = (
                        conversation_flow_service_class.get_conversation_response(
                            chat_request
                        )
                    )
                else:
                    # Multiple parameters - individual arguments
                    logger.debug(
                        "Using individual parameters", operation="multi_param_call"
                    )
                    response_task = (
                        conversation_flow_service_class.get_conversation_response(
                            message=chat_request.user_prompt,
                            topics=chat_request.topic
                            if isinstance(chat_request.topic, list)
                            else ([chat_request.topic] if chat_request.topic else []),
                            thread_memory=getattr(chat_request, "thread_memory", ""),
                            memory_record_switch=getattr(
                                chat_request, "memory_record", True
                            ),
                            thread_chat_history=getattr(
                                chat_request, "thread_chat_history", []
                            ),
                        )
                    )

                logger.debug(
                    "Awaiting conversation flow response", operation="response_await"
                )
                agent_response_tuple = await response_task
                logger.debug(
                    "Received conversation flow response",
                    response_type=str(type(agent_response_tuple)),
                    operation="response_received",
                )

                # Convert old response format to new format
                from ingenious.models.chat import ChatResponse

                logger.debug(
                    "Creating ChatResponse object",
                    uuid_module_available=uuid_module is not None,
                    operation="chat_response_creation",
                )

                # Handle different response types
                if isinstance(agent_response_tuple, ChatResponse):
                    # Already a ChatResponse object
                    logger.debug(
                        "Response is already ChatResponse format",
                        operation="response_format_check",
                    )
                    agent_response = agent_response_tuple
                elif (
                    isinstance(agent_response_tuple, tuple)
                    and len(agent_response_tuple) == 2
                ):
                    # Tuple response (response_text, memory_summary)
                    logger.debug(
                        "Converting tuple response to ChatResponse",
                        operation="tuple_conversion",
                    )
                    response_text, memory_summary = agent_response_tuple
                    agent_response = ChatResponse(
                        thread_id=chat_request.thread_id,
                        message_id=str(uuid_module.uuid4()),
                        agent_response=response_text,
                        token_count=0,
                        max_token_count=0,
                        memory_summary=memory_summary,
                    )
                else:
                    # Handle single response case
                    logger.debug(
                        "Converting single response to ChatResponse",
                        operation="single_response_conversion",
                    )
                    agent_response = ChatResponse(
                        thread_id=chat_request.thread_id,
                        message_id=str(uuid_module.uuid4()),
                        agent_response=str(agent_response_tuple),
                        token_count=0,
                        max_token_count=0,
                        memory_summary="",
                    )

        except Exception as e:
            logger.error(
                "Error occurred while processing conversation flow",
                conversation_flow=self.conversation_flow,
                error=str(e),
                exc_info=True,
            )
            raise e

        # Save chat history if memory_record is enabled
        if getattr(chat_request, "memory_record", True):
            try:
                # Save user message
                if chat_request.user_id and chat_request.thread_id:
                    from ingenious.models.message import Message

                    user_message_id = await self.chat_history_repository.add_message(
                        Message(
                            user_id=chat_request.user_id,
                            thread_id=chat_request.thread_id,
                            role="user",
                            content=chat_request.user_prompt,
                        )
                    )
                    logger.info(
                        "Saved user message",
                        message_id=user_message_id,
                        thread_id=chat_request.thread_id,
                    )

                    # Save agent response
                    agent_message_id = await self.chat_history_repository.add_message(
                        Message(
                            user_id=chat_request.user_id,
                            thread_id=chat_request.thread_id,
                            role="assistant",
                            content=agent_response.agent_response,
                        )
                    )
                    logger.info(
                        "Saved agent message",
                        message_id=agent_message_id,
                        thread_id=chat_request.thread_id,
                    )

                    # Save memory summary if available
                    if (
                        hasattr(agent_response, "memory_summary")
                        and agent_response.memory_summary
                    ):
                        memory_id = await self.chat_history_repository.add_memory(
                            Message(
                                user_id=chat_request.user_id,
                                thread_id=chat_request.thread_id,
                                role="memory_assistant",
                                content=agent_response.memory_summary,
                            )
                        )
                        logger.info(
                            "Saved memory",
                            memory_id=memory_id,
                            thread_id=chat_request.thread_id,
                        )

            except Exception as e:
                logger.error(
                    "Failed to save chat history",
                    thread_id=chat_request.thread_id,
                    user_id=chat_request.user_id,
                    error=str(e),
                    exc_info=True,
                )
                # Continue execution even if database save fails
                # This ensures the chat response is still returned to the user

        return agent_response  # type: ignore


class IConversationPattern(ABC):
    _config: "Config"
    _memory_path: str
    _memory_file_path: str
    _memory_manager: Any

    def __init__(self) -> None:
        super().__init__()
        self._config = ig_config.get_config()
        self._memory_path = self.GetConfig().chat_history.memory_path
        self._memory_file_path = f"{self._memory_path}/context.md"

        # Initialize memory manager for cloud storage support
        from ingenious.services.memory_manager import get_memory_manager

        self._memory_manager = get_memory_manager(self._config, self._memory_path)

    def GetConfig(self) -> "Config":
        return self._config

    def Get_Models(self) -> Dict[str, Any]:
        return self._config.models.__dict__

    def Get_Memory_Path(self) -> str:
        return self._memory_path

    def Get_Memory_File(self) -> str:
        return self._memory_file_path

    def Maintain_Memory(self, new_content: str, max_words: int = 150) -> Any:
        """
        Maintain memory using the MemoryManager for cloud storage support.
        """
        from ingenious.services.memory_manager import run_async_memory_operation

        return run_async_memory_operation(  # type: ignore
            self._memory_manager.maintain_memory(new_content, max_words)
        )

    async def write_llm_responses_to_file(
        self, response_array: List[Dict[str, Any]], event_type: str, output_path: str
    ) -> None:
        fs = FileStorage(self._config)
        for res in response_array:
            make_llm_calls = True
            if make_llm_calls:
                this_response = res["chat_response"]
            else:
                this_response = "Insight not yet generated"

            await fs.write_file(
                this_response,
                f"agent_response_{event_type}_{res['chat_title']}.md",
                output_path,
            )

    @abstractmethod
    async def get_conversation_response(
        self, message: str, thread_memory: str
    ) -> IChatResponse:
        pass


class IConversationFlow(ABC):
    _config: "Config"
    _memory_path: str
    _memory_file_path: str
    _logger: logging.Logger
    _chat_service: multi_agent_chat_service
    _memory_manager: Any

    def __init__(
        self, parent_multi_agent_chat_service: multi_agent_chat_service
    ) -> None:
        super().__init__()
        # Use configuration from parent service instead of loading separately
        self._config = parent_multi_agent_chat_service.config
        self._memory_path = self.GetConfig().chat_history.memory_path
        self._memory_file_path = f"{self._memory_path}/context.md"
        self._logger = get_logger(__name__)  # type: ignore
        self._chat_service = parent_multi_agent_chat_service

        # Initialize memory manager for cloud storage support
        from ingenious.services.memory_manager import get_memory_manager

        self._memory_manager = get_memory_manager(self._config, self._memory_path)

    def GetConfig(self) -> "Config":
        return self._config

    async def Get_Template(
        self, revision_id: Optional[str] = None, file_name: str = "user_prompt.md"
    ) -> str:
        fs = FileStorage(self._config)
        template_path = await fs.get_prompt_template_path(revision_id or "")
        content = await fs.read_file(file_name=file_name, file_path=template_path)
        if content is None:
            logger.warning(
                "Prompt template file not found",
                file_name=file_name,
                template_path=template_path,
                operation="template_file_lookup",
            )
            return ""
        env = Environment()
        template = env.from_string(content)
        return template.render()  # type: ignore

    def Get_Models(self) -> Any:
        return self._config.models

    def Get_Memory_Path(self) -> str:
        return self._memory_path

    def Get_Memory_File(self) -> str:
        return self._memory_file_path

    def Maintain_Memory(self, new_content: str, max_words: int = 150) -> Any:
        """
        Maintain memory using the MemoryManager for cloud storage support.
        """
        from ingenious.services.memory_manager import run_async_memory_operation

        return run_async_memory_operation(  # type: ignore
            self._memory_manager.maintain_memory(new_content, max_words)
        )

    @abstractmethod
    async def get_conversation_response(
        self, chat_request: IChatRequest
    ) -> IChatResponse:
        pass


# Save agent response
# agent_message_id = await self.chat_history_repository.add_message(
#     Message(
#         user_id=chat_request.user_id,
#         thread_id=chat_request.thread_id,
#         role="assistant",
#         content=agent_response[0])
# )

# logger.debug("Agent response received", response_preview=str(agent_response)[:100])
# _ = await self.chat_history_repository.add_memory(
#     Message(
#         user_id=chat_request.user_id,
#         thread_id=chat_request.thread_id,
#         role="memory_assistant",
#         content=agent_response[1]),
# )
