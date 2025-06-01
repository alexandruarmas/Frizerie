"""
Database models for security features including API keys, rate limiting, and request logging.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base

class APIKey(Base):
    """Model for API keys."""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key_hash = Column(String(64), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    # rate_limit = Column(Integer, default=100, nullable=False)  # Commented for development
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    deactivated_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    # rate_limits = relationship("RateLimit", back_populates="api_key")  # Commented for development
    request_logs = relationship("RequestLog", back_populates="api_key")
    security_events = relationship("SecurityEvent", back_populates="api_key")

# class RateLimit(Base):  # Commented for development
#     """Model for tracking rate limits."""
#     __tablename__ = "rate_limits"
    
#     id = Column(Integer, primary_key=True, index=True)
#     key_hash = Column(String(64), ForeignKey("api_keys.key_hash"), nullable=False)
#     endpoint = Column(String(255), nullable=False)
#     created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
#     # Relationships
#     api_key = relationship("APIKey", back_populates="rate_limits")

class RequestLog(Base):
    """Model for logging API requests."""
    __tablename__ = "request_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    key_hash = Column(String(64), ForeignKey("api_keys.key_hash"), nullable=False)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    ip_address = Column(String(45), nullable=False)  # IPv6 compatible
    user_agent = Column(String(255), nullable=True)
    request_data = Column(JSON, nullable=True)
    response_time = Column(Integer, nullable=True)  # in milliseconds
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    api_key = relationship("APIKey", back_populates="request_logs")

class SecurityEvent(Base):
    """Model for logging security-related events."""
    __tablename__ = "security_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)  # info, warning, error, critical
    description = Column(Text, nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    key_hash = Column(String(64), ForeignKey("api_keys.key_hash"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    api_key = relationship("APIKey", back_populates="security_events")
    user = relationship("User", back_populates="security_events") 