from typing import Any, Dict, Optional

from pydantic import BaseModel


class Action(BaseModel):
    """
    Represents an action that can be taken in response to a chat message.
    """

    id: str
    name: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
