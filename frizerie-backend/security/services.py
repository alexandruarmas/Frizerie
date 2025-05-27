"""
Security services for API key management, rate limiting, and request logging.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta
import json
from typing import Optional, Dict, Any, List

from security.models import APIKey, RateLimit, RequestLog, SecurityEvent
from security.schemas import APIKeyCreate, APIKeyUpdate
from users.models import User
from users.services import get_user_by_id

def create_api_key(
    db: Session,
    user_id: int,
    name: str,
    rate_limit: int = 100,
    expires_at: Optional[datetime] = None
) -> APIKey:
    """Create a new API key for a user."""
    # Generate a random API key
    import secrets
    api_key = secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    # Create API key record
    db_api_key = APIKey(
        key_hash=key_hash,
        user_id=user_id,
        name=name,
        rate_limit=rate_limit,
        expires_at=expires_at
    )
    
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    
    # Return both the API key and the database record
    return {
        "api_key": api_key,
        "db_record": db_api_key
    }

def validate_api_key(db: Session, key_hash: str) -> Optional[APIKey]:
    """Validate an API key and return the associated record if valid."""
    api_key = db.query(APIKey).filter(
        and_(
            APIKey.key_hash == key_hash,
            APIKey.is_active == True,
            or_(
                APIKey.expires_at == None,
                APIKey.expires_at > datetime.utcnow()
            )
        )
    ).first()
    
    if api_key:
        api_key.last_used_at = datetime.utcnow()
        db.commit()
    
    return api_key

def update_api_key(
    db: Session,
    key_hash: str,
    update_data: APIKeyUpdate
) -> Optional[APIKey]:
    """Update an API key's properties."""
    api_key = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()
    if not api_key:
        return None
    
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(api_key, field, value)
    
    db.commit()
    db.refresh(api_key)
    return api_key

def deactivate_api_key(db: Session, key_hash: str) -> bool:
    """Deactivate an API key."""
    api_key = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()
    if not api_key:
        return False
    
    api_key.is_active = False
    api_key.deactivated_at = datetime.utcnow()
    db.commit()
    return True

def get_user_api_keys(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[APIKey]:
    """Get all API keys for a user."""
    return db.query(APIKey).filter(
        APIKey.user_id == user_id
    ).offset(skip).limit(limit).all()

def check_rate_limit(
    db: Session,
    key_hash: str,
    endpoint: str,
    window_seconds: int,
    max_requests: int
) -> bool:
    """Check if a request is within rate limits."""
    window_start = datetime.utcnow() - timedelta(seconds=window_seconds)
    
    # Get the API key's custom rate limit
    api_key = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()
    if not api_key:
        return False
    
    max_requests = min(max_requests, api_key.rate_limit)
    
    # Count requests in the current window
    request_count = db.query(func.count(RateLimit.id)).filter(
        and_(
            RateLimit.key_hash == key_hash,
            RateLimit.endpoint == endpoint,
            RateLimit.created_at >= window_start
        )
    ).scalar()
    
    if request_count >= max_requests:
        return False
    
    # Log the request
    rate_limit = RateLimit(
        key_hash=key_hash,
        endpoint=endpoint
    )
    db.add(rate_limit)
    db.commit()
    
    return True

def log_request(
    db: Session,
    key_hash: str,
    endpoint: str,
    method: str,
    status_code: int,
    ip_address: str,
    user_agent: Optional[str] = None,
    request_data: Optional[Dict[str, Any]] = None,
    response_time: Optional[int] = None
) -> RequestLog:
    """Log an API request."""
    request_log = RequestLog(
        key_hash=key_hash,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        ip_address=ip_address,
        user_agent=user_agent,
        request_data=json.dumps(request_data) if request_data else None,
        response_time=response_time
    )
    
    db.add(request_log)
    db.commit()
    db.refresh(request_log)
    return request_log

def log_security_event(
    db: Session,
    event_type: str,
    severity: str,
    description: str,
    ip_address: Optional[str] = None,
    key_hash: Optional[str] = None,
    user_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> SecurityEvent:
    """Log a security-related event."""
    security_event = SecurityEvent(
        event_type=event_type,
        severity=severity,
        description=description,
        ip_address=ip_address,
        key_hash=key_hash,
        user_id=user_id,
        metadata=json.dumps(metadata) if metadata else None
    )
    
    db.add(security_event)
    db.commit()
    db.refresh(security_event)
    return security_event

def get_security_events(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[SecurityEvent]:
    """Get security events with optional filtering."""
    query = db.query(SecurityEvent)
    
    if event_type:
        query = query.filter(SecurityEvent.event_type == event_type)
    if severity:
        query = query.filter(SecurityEvent.severity == severity)
    if start_date:
        query = query.filter(SecurityEvent.created_at >= start_date)
    if end_date:
        query = query.filter(SecurityEvent.created_at <= end_date)
    
    return query.order_by(
        SecurityEvent.created_at.desc()
    ).offset(skip).limit(limit).all()

def get_request_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    key_hash: Optional[str] = None,
    endpoint: Optional[str] = None,
    status_code: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[RequestLog]:
    """Get request logs with optional filtering."""
    query = db.query(RequestLog)
    
    if key_hash:
        query = query.filter(RequestLog.key_hash == key_hash)
    if endpoint:
        query = query.filter(RequestLog.endpoint == endpoint)
    if status_code:
        query = query.filter(RequestLog.status_code == status_code)
    if start_date:
        query = query.filter(RequestLog.created_at >= start_date)
    if end_date:
        query = query.filter(RequestLog.created_at <= end_date)
    
    return query.order_by(
        RequestLog.created_at.desc()
    ).offset(skip).limit(limit).all() 