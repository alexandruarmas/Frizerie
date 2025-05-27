"""
API routes for security features including API key management, rate limiting, and request logging.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from security import schemas, services
from security.middleware import SecurityMiddleware
from users.dependencies import get_current_admin_user, get_current_user
from users.models import User

router = APIRouter(
    prefix="/security",
    tags=["security"],
    dependencies=[Depends(get_current_admin_user)]  # All security routes require admin access
)

@router.post("/api-keys", response_model=schemas.APIKeyWithToken)
def create_api_key(
    api_key_data: schemas.APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new API key for the current user."""
    result = services.create_api_key(
        db=db,
        user_id=current_user.id,
        name=api_key_data.name,
        rate_limit=api_key_data.rate_limit,
        expires_at=api_key_data.expires_at
    )
    return result

@router.get("/api-keys", response_model=List[schemas.APIKeyResponse])
def get_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get all API keys for the current user."""
    return services.get_user_api_keys(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )

@router.put("/api-keys/{key_hash}", response_model=schemas.APIKeyResponse)
def update_api_key(
    key_hash: str,
    api_key_data: schemas.APIKeyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an API key's properties."""
    api_key = services.update_api_key(db, key_hash, api_key_data)
    if not api_key or api_key.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    return api_key

@router.delete("/api-keys/{key_hash}")
def deactivate_api_key(
    key_hash: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate an API key."""
    api_key = services.validate_api_key(db, key_hash)
    if not api_key or api_key.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    if services.deactivate_api_key(db, key_hash):
        return {"message": "API key deactivated successfully"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Failed to deactivate API key"
    )

@router.get("/request-logs", response_model=List[schemas.RequestLogResponse])
def get_request_logs(
    filter_data: schemas.RequestLogFilter = Depends(),
    db: Session = Depends(get_db)
):
    """Get request logs with optional filtering."""
    return services.get_request_logs(
        db=db,
        skip=filter_data.skip,
        limit=filter_data.limit,
        key_hash=filter_data.key_hash,
        endpoint=filter_data.endpoint,
        status_code=filter_data.status_code,
        start_date=filter_data.start_date,
        end_date=filter_data.end_date
    )

@router.get("/security-events", response_model=List[schemas.SecurityEventResponse])
def get_security_events(
    filter_data: schemas.SecurityEventFilter = Depends(),
    db: Session = Depends(get_db)
):
    """Get security events with optional filtering."""
    return services.get_security_events(
        db=db,
        skip=filter_data.skip,
        limit=filter_data.limit,
        event_type=filter_data.event_type,
        severity=filter_data.severity,
        start_date=filter_data.start_date,
        end_date=filter_data.end_date
    )

@router.post("/security-events", response_model=schemas.SecurityEventResponse)
def create_security_event(
    event_data: schemas.SecurityEventCreate,
    db: Session = Depends(get_db)
):
    """Create a new security event."""
    return services.log_security_event(
        db=db,
        event_type=event_data.event_type,
        severity=event_data.severity,
        description=event_data.description,
        ip_address=event_data.ip_address,
        key_hash=event_data.key_hash,
        user_id=event_data.user_id,
        metadata=event_data.metadata
    )

@router.get("/stats", response_model=schemas.SecurityStats)
def get_security_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get security statistics for a given period."""
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=7)
    if not end_date:
        end_date = datetime.utcnow()
    
    # Get total requests and failed requests
    total_requests = db.query(func.count(RequestLog.id)).filter(
        RequestLog.created_at.between(start_date, end_date)
    ).scalar()
    
    failed_requests = db.query(func.count(RequestLog.id)).filter(
        and_(
            RequestLog.created_at.between(start_date, end_date),
            RequestLog.status_code >= 400
        )
    ).scalar()
    
    # Get average response time
    avg_response_time = db.query(func.avg(RequestLog.response_time)).filter(
        and_(
            RequestLog.created_at.between(start_date, end_date),
            RequestLog.response_time.isnot(None)
        )
    ).scalar() or 0.0
    
    # Get security events by type and severity
    events_by_type = dict(db.query(
        SecurityEvent.event_type,
        func.count(SecurityEvent.id)
    ).filter(
        SecurityEvent.created_at.between(start_date, end_date)
    ).group_by(SecurityEvent.event_type).all())
    
    events_by_severity = dict(db.query(
        SecurityEvent.severity,
        func.count(SecurityEvent.id)
    ).filter(
        SecurityEvent.created_at.between(start_date, end_date)
    ).group_by(SecurityEvent.severity).all())
    
    # Get top endpoints
    top_endpoints = db.query(
        RequestLog.endpoint,
        func.count(RequestLog.id).label("count"),
        func.avg(RequestLog.response_time).label("avg_response_time")
    ).filter(
        RequestLog.created_at.between(start_date, end_date)
    ).group_by(RequestLog.endpoint).order_by(
        func.count(RequestLog.id).desc()
    ).limit(10).all()
    
    # Get top IP addresses
    top_ip_addresses = db.query(
        RequestLog.ip_address,
        func.count(RequestLog.id).label("count"),
        func.count(case([(RequestLog.status_code >= 400, 1)])).label("failed_requests")
    ).filter(
        RequestLog.created_at.between(start_date, end_date)
    ).group_by(RequestLog.ip_address).order_by(
        func.count(RequestLog.id).desc()
    ).limit(10).all()
    
    return {
        "total_requests": total_requests,
        "failed_requests": failed_requests,
        "average_response_time": float(avg_response_time),
        "security_events_by_type": events_by_type,
        "security_events_by_severity": events_by_severity,
        "top_endpoints": [
            {
                "endpoint": endpoint,
                "count": count,
                "avg_response_time": float(avg_response_time or 0)
            }
            for endpoint, count, avg_response_time in top_endpoints
        ],
        "top_ip_addresses": [
            {
                "ip_address": ip,
                "count": count,
                "failed_requests": failed
            }
            for ip, count, failed in top_ip_addresses
        ],
        "period_start": start_date,
        "period_end": end_date
    } 