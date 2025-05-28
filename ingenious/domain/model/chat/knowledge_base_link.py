from typing import Any, Dict, Optional

from pydantic import BaseModel


class KnowledgeBaseLink(BaseModel):
    """
    Represents a link to a knowledge base item.
    """

    id: str
    title: str
    url: Optional[str] = None
    content: Optional[str] = None
    score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
