from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Request model for chat operations."""

    thread_id: Optional[str] = None
    user_prompt: str
    event_type: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    topic: Optional[str] = None
    memory_record: Optional[bool] = True
    conversation_flow: str
    thread_chat_history: Optional[dict[str, str]] = {}
    thread_memory: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat operations."""

    thread_id: Optional[str] = None
    message_id: Optional[str] = None
    agent_response: Optional[str] = None
    followup_questions: Optional[dict[str, str]] = {}
    token_count: Optional[int] = None
    max_token_count: Optional[int] = None
    topic: Optional[str] = None
    memory_summary: Optional[str] = None
    event_type: Optional[str] = None


class MessageFeedbackRequest(BaseModel):
    """Request model for message feedback."""

    thread_id: Optional[str] = None
    message_id: Optional[str] = None
    user_id: Optional[str] = None
    positive_feedback: Optional[bool] = None
    feedback_type: str  # This should be required
    feedback_text: Optional[str] = None


class MessageFeedbackResponse(BaseModel):
    """Response model for message feedback."""

    message: Optional[str] = None
    message_id: Optional[str] = None
    feedback_type: Optional[str] = None
    success: Optional[bool] = None
    status: Optional[str] = None
    timestamp: Optional[str] = None
    feedback_id: Optional[str] = None
