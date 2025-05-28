from typing import TYPE_CHECKING

from ingenious.domain.model.chat.message_feedback import (
    MessageFeedbackRequest,
    MessageFeedbackResponse,
)

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from ingenious.application.repository.chat_history_repository import (
        ChatHistoryRepository,
    )


class MessageFeedbackService:
    def __init__(self, chat_history_repository: "ChatHistoryRepository"):
        self.chat_history_repository = chat_history_repository

    async def update_message_feedback(
        self, message_id: str, message_feedback_request: MessageFeedbackRequest
    ) -> MessageFeedbackResponse:
        # Validate message ID
        if message_id != message_feedback_request.message_id:
            raise ValueError("Message ID does not match message feedback request.")

        # Get message from DB
        message = await self.chat_history_repository.get_message(
            message_id, message_feedback_request.thread_id
        )
        if not message:
            raise ValueError(f"Message {message_id} not found.")

        # Validate user ID
        if (message.user_id or "") != (message_feedback_request.user_id or ""):
            raise ValueError("User ID does not match message feedback request.")

        # Update feedback
        await self.chat_history_repository.update_message_feedback(
            message_id,
            message_feedback_request.thread_id,
            message_feedback_request.positive_feedback,
        )

        return MessageFeedbackResponse(
            message=f"Feedback submitted for message {message_id}."
        )
