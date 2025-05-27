from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime

from .models import SearchResult, SearchResultType
from .schemas import SearchQuery, SearchRequest, SearchResultItem
from ..users.models import User
from ..bookings.models import Booking, Stylist
from ..services.models import Service
from ..payments.models import Payment

async def search_users(
    db: Session,
    query: str,
    limit: int = 10,
    offset: int = 0,
    filters: Optional[dict] = None
) -> List[SearchResult]:
    """
    Search users based on query string.
    """
    search_query = db.query(User).filter(
        or_(
            User.email.ilike(f"%{query}%"),
            User.first_name.ilike(f"%{query}%"),
            User.last_name.ilike(f"%{query}%")
        )
    )
    
    if filters:
        if filters.get("is_active") is not None:
            search_query = search_query.filter(User.is_active == filters["is_active"])
    
    users = search_query.offset(offset).limit(limit).all()
    
    return [
        SearchResult(
            type=SearchResultType.USER,
            id=user.id,
            title=f"{user.first_name} {user.last_name}",
            description=user.email,
            metadata={
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat()
            }
        )
        for user in users
    ]

async def search_bookings(
    db: Session,
    query: str,
    limit: int = 10,
    offset: int = 0,
    filters: Optional[dict] = None
) -> List[SearchResult]:
    """
    Search bookings based on query string.
    """
    search_query = db.query(Booking).join(User).filter(
        or_(
            User.email.ilike(f"%{query}%"),
            User.first_name.ilike(f"%{query}%"),
            User.last_name.ilike(f"%{query}%")
        )
    )
    
    if filters:
        if filters.get("status"):
            search_query = search_query.filter(Booking.status == filters["status"])
        if filters.get("date_from"):
            search_query = search_query.filter(Booking.date >= filters["date_from"])
        if filters.get("date_to"):
            search_query = search_query.filter(Booking.date <= filters["date_to"])
    
    bookings = search_query.offset(offset).limit(limit).all()
    
    return [
        SearchResult(
            type=SearchResultType.BOOKING,
            id=booking.id,
            title=f"Booking for {booking.user.first_name} {booking.user.last_name}",
            description=f"Date: {booking.date.strftime('%Y-%m-%d %H:%M')}",
            metadata={
                "status": booking.status,
                "service": booking.service.name,
                "user_email": booking.user.email
            }
        )
        for booking in bookings
    ]

async def search_services(
    db: Session,
    query: str,
    limit: int = 10,
    offset: int = 0,
    filters: Optional[dict] = None
) -> List[SearchResult]:
    """
    Search services based on query string.
    """
    search_query = db.query(Service).filter(
        or_(
            Service.name.ilike(f"%{query}%"),
            Service.description.ilike(f"%{query}%")
        )
    )
    
    if filters:
        if filters.get("category"):
            search_query = search_query.filter(Service.category == filters["category"])
        if filters.get("min_price"):
            search_query = search_query.filter(Service.price >= filters["min_price"])
        if filters.get("max_price"):
            search_query = search_query.filter(Service.price <= filters["max_price"])
    
    services = search_query.offset(offset).limit(limit).all()
    
    return [
        SearchResult(
            type=SearchResultType.SERVICE,
            id=service.id,
            title=service.name,
            description=service.description,
            metadata={
                "price": service.price,
                "duration": service.duration,
                "category": service.category
            }
        )
        for service in services
    ]

async def search_payments(
    db: Session,
    query: str,
    limit: int = 10,
    offset: int = 0,
    filters: Optional[dict] = None
) -> List[SearchResult]:
    """
    Search payments based on query string.
    """
    search_query = db.query(Payment).join(User).filter(
        or_(
            User.email.ilike(f"%{query}%"),
            User.first_name.ilike(f"%{query}%"),
            User.last_name.ilike(f"%{query}%")
        )
    )
    
    if filters:
        if filters.get("status"):
            search_query = search_query.filter(Payment.status == filters["status"])
        if filters.get("method"):
            search_query = search_query.filter(Payment.method == filters["method"])
        if filters.get("date_from"):
            search_query = search_query.filter(Payment.created_at >= filters["date_from"])
        if filters.get("date_to"):
            search_query = search_query.filter(Payment.created_at <= filters["date_to"])
    
    payments = search_query.offset(offset).limit(limit).all()
    
    return [
        SearchResult(
            type=SearchResultType.PAYMENT,
            id=payment.id,
            title=f"Payment for {payment.user.first_name} {payment.user.last_name}",
            description=f"Amount: {payment.amount} {payment.currency}",
            metadata={
                "status": payment.status,
                "method": payment.method,
                "created_at": payment.created_at.isoformat()
            }
        )
        for payment in payments
    ]

def search_stylists(db: Session, query: str, limit: int, skip: int) -> List[SearchResultItem]:
    # Basic stylist search by name or specialization
    search_results = db.query(Stylist).filter(
        (Stylist.name.ilike(f"%{query}%")) |
        (Stylist.specialization.ilike(f"%{query}%"))
    ).limit(limit).offset(skip).all()
    
    return [SearchResultItem(type="stylist", id=stylist.id, data={'id': stylist.id, 'name': stylist.name, 'specialization': stylist.specialization, 'bio': stylist.bio, 'is_active': stylist.is_active}) for stylist in search_results]

def perform_search(db: Session, search_request: SearchRequest) -> Dict[str, Any]:
    results = []
    total_results = 0

    # Example of searching across different types. You can add logic here
    # to determine which types to search based on filters in search_request.

    # Search Users
    user_results = search_users(db, search_request.query, search_request.limit, search_request.skip)
    results.extend(user_results)
    # Note: Total results count needs to be more accurate for combined searches
    total_results += len(user_results)

    # Search Stylists
    stylist_results = search_stylists(db, search_request.query, search_request.limit, search_request.skip)
    results.extend(stylist_results)
    total_results += len(stylist_results)
    
    # Search Services
    service_results = search_services(db, search_request.query, search_request.limit, search_request.skip)
    results.extend(service_results)
    total_results += len(service_results)

    # Search Bookings
    booking_results = search_bookings(db, search_request.query, search_request.limit, search_request.skip)
    results.extend(booking_results)
    total_results += len(booking_results)


    return {
        "query": search_request.query,
        "total_results": total_results, # This count will be inaccurate for pagination across types
        "results": results,
        "limit": search_request.limit,
        "skip": search_request.skip
    } 