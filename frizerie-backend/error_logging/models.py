"""
SQLAlchemy models for error logging and monitoring system.
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from config.database import Base

class ErrorLog(Base):
    """Model for error logs."""
    __tablename__ = "error_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    error_type = Column(String(50), nullable=False, index=True)
    error_code = Column(String(50))
    message = Column(Text, nullable=False)
    stack_trace = Column(Text)
    severity = Column(String(20), nullable=False, index=True)
    source = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    request_id = Column(String(50))
    endpoint = Column(String(255))
    method = Column(String(10))
    status_code = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at = Column(DateTime(timezone=True))
    resolution_notes = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="error_logs")

class SystemLog(Base):
    """Model for system logs."""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    log_level = Column(String(20), nullable=False, index=True)
    message = Column(Text, nullable=False)
    source = Column(String(255), nullable=False, index=True)
    context = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class MonitoringMetric(Base):
    """Model for monitoring metrics."""
    __tablename__ = "monitoring_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_type = Column(String(50), nullable=False)
    labels = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

class AlertRule(Base):
    """Model for alert rules."""
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    metric_name = Column(String(100), nullable=False)
    condition = Column(String(50), nullable=False)
    threshold = Column(Float, nullable=False)
    severity = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    alerts = relationship("Alert", back_populates="rule")

class Alert(Base):
    """Model for alerts."""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("alert_rules.id"))
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    severity = Column(String(20), nullable=False, index=True)
    message = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    resolved_at = Column(DateTime(timezone=True))
    resolved_by = Column(Integer, ForeignKey("users.id"))
    resolution_notes = Column(Text)
    
    # Relationships
    rule = relationship("AlertRule", back_populates="alerts")
    resolver = relationship("User", back_populates="resolved_alerts") 