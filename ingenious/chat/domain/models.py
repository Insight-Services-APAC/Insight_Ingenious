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

    thread_id: Optional[str]
    message_id: Optional[str]
    agent_response: Optional[str]
    followup_questions: Optional[dict[str, str]] = {}
    token_count: Optional[int]
    max_token_count: Optional[int]
    topic: Optional[str] = None
    memory_summary: Optional[str] = None
    event_type: Optional[str] = None


class MessageFeedbackRequest(BaseModel):
    """Request model for message feedback."""

    thread_id: str
    message_id: str
    user_id: Optional[str]
    positive_feedback: Optional[bool]


class MessageFeedbackResponse(BaseModel):
    """Response model for message feedback."""

    message: str
