from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel

class SearchResultType(str, Enum):
    USER = "user"
    BOOKING = "booking"
    SERVICE = "service"
    PAYMENT = "payment"

class SearchResult(BaseModel):
    type: SearchResultType
    id: int
    title: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = {}
    score: float = 0.0
    
    class Config:
        from_attributes = True 