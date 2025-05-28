from typing import Optional

from pydantic import BaseModel


class MessageFeedback(BaseModel):
    message_id: str
    thread_id: str
    user_id: str
    positive_feedback: bool
    negative_feedback: Optional[bool] = None
    feedback_text: Optional[str] = None
