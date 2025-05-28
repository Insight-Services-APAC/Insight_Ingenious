"""Event handling service for processing prompt tuning events."""

import json
import logging
from typing import Any, Dict, Optional

from ingenious.models.chat import ChatRequest
from ingenious_prompt_tuner.services import FileService

logger = logging.getLogger(__name__)


class EventService:
    """Handles event data processing and chat request preparation."""

    def __init__(self, file_service: FileService):
        """Initialize with file service."""
        self.file_service = file_service

    async def load_event_data(self, file_name: str, file_path: str) -> Dict[str, Any]:
        """
        Load event data from a file.

        Args:
            file_name: The name of the file
            file_path: The path to the file

        Returns:
            The loaded JSON data as a dictionary
        """
        try:
            file_contents = await self.file_service.fs_data.read_file(
                file_name=file_name, file_path=file_path
            )
            return json.loads(file_contents)
        except Exception as e:
            logger.error(f"Error loading event data from {file_path}/{file_name}: {e}")
            return {}

    def prepare_chat_request(
        self,
        json_object: Dict[str, Any],
        identifier: str,
        prompt_template_name: str,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> ChatRequest:
        """
        Prepare a chat request from event data.

        Args:
            json_object: The event data
            identifier: The identifier for the chat
            prompt_template_name: The name of the prompt template
            additional_context: Additional context for the chat

        Returns:
            A prepared ChatRequest object
        """
        # Create a base chat request
        chat_request = ChatRequest()
        chat_request.identifier = identifier
        chat_request.prompt_template_name = prompt_template_name
        chat_request.prompt_template_input = json_object

        # Add additional context if provided
        if additional_context:
            for key, value in additional_context.items():
                chat_request.prompt_template_input[key] = value

        return chat_request
