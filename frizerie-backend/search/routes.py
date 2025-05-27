from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..auth.dependencies import get_current_user
from .schemas import SearchQuery, SearchResponse
from .services import (
    search_users,
    search_bookings,
    search_services,
    search_payments
)
from .models import SearchResultType

router = APIRouter(prefix="/search", tags=["search"])

@router.get("", response_model=SearchResponse)
async def search(
    query: str = Query(..., min_length=1, max_length=100),
    types: List[SearchResultType] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    filters: dict = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Search across all entities or specific types.
    """
    results = []
    total = 0
    
    # If no types specified, search all types
    if not types:
        types = list(SearchResultType)
    
    # Search each type
    for search_type in types:
        if search_type == SearchResultType.USER:
            type_results = await search_users(db, query, limit, offset, filters)
        elif search_type == SearchResultType.BOOKING:
            type_results = await search_bookings(db, query, limit, offset, filters)
        elif search_type == SearchResultType.SERVICE:
            type_results = await search_services(db, query, limit, offset, filters)
        elif search_type == SearchResultType.PAYMENT:
            type_results = await search_payments(db, query, limit, offset, filters)
        
        results.extend(type_results)
        total += len(type_results)
    
    # Sort results by score (if implemented) and limit to requested limit
    results = sorted(results, key=lambda x: x.score, reverse=True)[:limit]
    
    return SearchResponse(
        results=results,
        total=total,
        offset=offset,
        limit=limit,
        query=query
    )

@router.post("/", response_model=SearchResponse)
def search(search_request: SearchRequest, db: Session = Depends(get_db)):
    """Perform a search across different entities."""
    return perform_search(db, search_request) 