from typing import Optional

from pydantic import BaseModel


class MessageFeedbackRequest(BaseModel):
    thread_id: str
    message_id: str
    user_id: Optional[str] = None
    positive_feedback: Optional[bool] = None


class MessageFeedbackResponse(BaseModel):
    message: str
