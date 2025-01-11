from typing import Optional
from pydantic import BaseModel



class ChatRequest(BaseModel):
    thread_id: Optional[str] = None
    user_prompt: str
    event_type: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    topic: Optional[str] = None
    memory_record: Optional[bool] = True
    conversation_flow: str


class ChatResponse(BaseModel):
    thread_id: str
    message_id: str
    agent_response: str
    followup_questions: Optional[dict[str, str]] = {}
    token_count: int
    max_token_count: int
    topic: Optional[str] = None
    memory_summary: Optional[str]  = None
    event_type: Optional[str] = None
