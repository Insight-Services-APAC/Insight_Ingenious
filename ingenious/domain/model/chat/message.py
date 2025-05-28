from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"


class Message(BaseModel):
    id: str
    role: str
    content: Optional[str] = (
        ""  # Making content optional with default empty string for function calls
    )
    thread_id: str
    user_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Optional[dict[str, object]] = None
    feedback: Optional[dict[str, object]] = None
    content_filter_results: Optional[dict[str, object]] = None
    tool_calls: Optional[list[dict[str, object]]] = None
    tool_call_id: Optional[str] = None
    tool_call_function: Optional[dict[str, object]] = None
    function_call: Optional[dict[str, object]] = None  # Add function_call support

    def model_post_init(self, _context):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()
        if not self.id:
            self.id = str(uuid4())
