from typing import List, Optional, Any
from pydantic import BaseModel, Field
from .models import SearchResult, SearchResultType

class SearchQuery(BaseModel):
    query: str = Field(..., min_length=1, max_length=100)
    types: Optional[List[SearchResultType]] = None
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    filters: Optional[dict] = None

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    offset: int
    limit: int
    query: str
    
    class Config:
        from_attributes = True

class SearchRequest(BaseModel):
    query: str
    filters: dict = {}
    limit: int = 10
    skip: int = 0

class SearchResultItem(BaseModel):
    type: str # e.g., "user", "booking", "service", "stylist"
    id: Any
    score: float = 0.0
    data: dict # The actual data of the item

class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResultItem]
    limit: int
    skip: int 