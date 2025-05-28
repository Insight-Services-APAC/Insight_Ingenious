from typing import Any, Dict, List, Optional

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
    thread_id: Optional[str]
    message_id: Optional[str]
    agent_response: Optional[str]
    followup_questions: Optional[dict[str, str]] = {}
    token_count: Optional[int]
    max_token_count: Optional[int]
    topic: Optional[str] = None
    memory_summary: Optional[str] = None
    event_type: Optional[str] = None


class ChatRequest(IChatRequest):
    messages: Optional[List[Dict[str, Any]]] = None
    model: Optional[str] = None
    functions: Optional[List[Dict[str, Any]]] = None
    function_call: Optional[Any] = None


class ChatResponse(IChatResponse):
    content: Optional[Any] = None
    model: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    job_id: Optional[str] = None
    tools: Optional[List[Any]] = None
    function_call: Optional[Any] = None
