from typing import Optional
from pydantic import BaseModel


class IChatRequest(BaseModel):
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


class IChatResponse(BaseModel):
    thread_id: str
    message_id: str
    agent_response: str
    followup_questions: Optional[dict[str, str]] = {}
    token_count: int
    max_token_count: int
    topic: Optional[str] = None
    memory_summary: Optional[str]  = None
    event_type: Optional[str] = None


class ChatRequest(IChatRequest):
    pass


class ChatResponse(IChatResponse):
    pass

