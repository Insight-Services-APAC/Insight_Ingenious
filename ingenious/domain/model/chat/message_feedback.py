from typing import Optional

from pydantic import BaseModel


class MessageFeedbackRequest(BaseModel):
    thread_id: str
    message_id: str
    user_id: Optional[str]
    positive_feedback: Optional[bool]


class MessageFeedbackResponse(BaseModel):
    message: str


class MessageFeedback(BaseModel):
    thread_id: str
    message_id: str
    user_id: str = "test_user"  # Provide a default for user_id to allow None in tests
    positive_feedback: Optional[bool]

    @classmethod
    def from_request(cls, request: MessageFeedbackRequest) -> "MessageFeedback":
        """
        Create a MessageFeedback from a MessageFeedbackRequest.

        Args:
            request: The request to create the feedback from

        Returns:
            MessageFeedback: The created feedback
        """
        return cls(
            thread_id=request.thread_id,
            message_id=request.message_id,
            user_id=request.user_id,
            positive_feedback=request.positive_feedback,
        )
