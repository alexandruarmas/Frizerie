"""
Pydantic schemas for security features including API keys, rate limiting, and request logging.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime

class APIKeyBase(BaseModel):
    """Base schema for API key operations."""
    name: str = Field(..., min_length=1, max_length=100)
    rate_limit: int = Field(default=100, ge=1, le=1000)
    expires_at: Optional[datetime] = None

class APIKeyCreate(APIKeyBase):
    """Schema for creating a new API key."""
    pass

class APIKeyUpdate(BaseModel):
    """Schema for updating an API key."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    rate_limit: Optional[int] = Field(None, ge=1, le=1000)
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None

class APIKeyResponse(APIKeyBase):
    """Schema for API key response."""
    id: int
    key_hash: str
    user_id: int
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None
    deactivated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class APIKeyWithToken(APIKeyResponse):
    """Schema for API key response including the actual key."""
    api_key: str

class RateLimitResponse(BaseModel):
    """Schema for rate limit response."""
    id: int
    key_hash: str
    endpoint: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class RequestLogResponse(BaseModel):
    """Schema for request log response."""
    id: int
    key_hash: str
    endpoint: str
    method: str
    status_code: int
    ip_address: str
    user_agent: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    response_time: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class SecurityEventResponse(BaseModel):
    """Schema for security event response."""
    id: int
    event_type: str
    severity: str
    description: str
    ip_address: Optional[str] = None
    key_hash: Optional[str] = None
    user_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class SecurityEventCreate(BaseModel):
    """Schema for creating a security event."""
    event_type: str = Field(..., min_length=1, max_length=50)
    severity: str = Field(..., regex="^(info|warning|error|critical)$")
    description: str = Field(..., min_length=1)
    ip_address: Optional[str] = None
    key_hash: Optional[str] = None
    user_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class SecurityEventFilter(BaseModel):
    """Schema for filtering security events."""
    event_type: Optional[str] = None
    severity: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)

class RequestLogFilter(BaseModel):
    """Schema for filtering request logs."""
    key_hash: Optional[str] = None
    endpoint: Optional[str] = None
    status_code: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)

class SecurityStats(BaseModel):
    """Schema for security statistics."""
    total_requests: int
    failed_requests: int
    average_response_time: float
    security_events_by_type: Dict[str, int]
    security_events_by_severity: Dict[str, int]
    top_endpoints: List[Dict[str, Any]]
    top_ip_addresses: List[Dict[str, Any]]
    period_start: datetime
    period_end: datetime 