from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Product(BaseModel):
    """
    Represents a product that can be recommended in a chat.
    """

    id: str
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    images: Optional[List[str]] = None
    url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
