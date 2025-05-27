"""
Pydantic schemas for error logging and monitoring system.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class ErrorLogBase(BaseModel):
    """Base schema for error logs."""
    error_type: str = Field(..., description="Type of error (e.g., 'ValidationError', 'DatabaseError')")
    error_code: Optional[str] = Field(None, description="Error code if applicable")
    message: str = Field(..., description="Error message")
    stack_trace: Optional[str] = Field(None, description="Stack trace if available")
    severity: str = Field(..., description="Error severity (e.g., 'ERROR', 'WARNING', 'INFO')")
    source: str = Field(..., description="Source of the error (e.g., 'API', 'Database', 'Service')")
    user_id: Optional[int] = Field(None, description="ID of the user who encountered the error")
    request_id: Optional[str] = Field(None, description="Request ID if applicable")
    endpoint: Optional[str] = Field(None, description="API endpoint where the error occurred")
    method: Optional[str] = Field(None, description="HTTP method of the request")
    status_code: Optional[int] = Field(None, description="HTTP status code")

class ErrorLogCreate(ErrorLogBase):
    """Schema for creating error logs."""
    pass

class ErrorLogUpdate(BaseModel):
    """Schema for updating error logs."""
    resolved_at: Optional[datetime] = Field(None, description="When the error was resolved")
    resolution_notes: Optional[str] = Field(None, description="Notes about how the error was resolved")

class ErrorLog(ErrorLogBase):
    """Schema for error log responses."""
    id: int
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

    class Config:
        from_attributes = True

class SystemLogBase(BaseModel):
    """Base schema for system logs."""
    log_level: str = Field(..., description="Log level (e.g., 'INFO', 'WARNING', 'ERROR')")
    message: str = Field(..., description="Log message")
    source: str = Field(..., description="Source of the log")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context data")

class SystemLogCreate(SystemLogBase):
    """Schema for creating system logs."""
    pass

class SystemLog(SystemLogBase):
    """Schema for system log responses."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class MonitoringMetricBase(BaseModel):
    """Base schema for monitoring metrics."""
    metric_name: str = Field(..., description="Name of the metric")
    metric_value: float = Field(..., description="Value of the metric")
    metric_type: str = Field(..., description="Type of metric (e.g., 'counter', 'gauge', 'histogram')")
    labels: Optional[Dict[str, str]] = Field(None, description="Labels for the metric")

class MonitoringMetricCreate(MonitoringMetricBase):
    """Schema for creating monitoring metrics."""
    pass

class MonitoringMetric(MonitoringMetricBase):
    """Schema for monitoring metric responses."""
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class AlertRuleBase(BaseModel):
    """Base schema for alert rules."""
    name: str = Field(..., description="Name of the alert rule")
    description: Optional[str] = Field(None, description="Description of the alert rule")
    metric_name: str = Field(..., description="Name of the metric to monitor")
    condition: str = Field(..., description="Condition for the alert (e.g., '>', '<', '==')")
    threshold: float = Field(..., description="Threshold value for the alert")
    severity: str = Field(..., description="Severity of the alert (e.g., 'critical', 'warning', 'info')")
    is_active: bool = Field(True, description="Whether the alert rule is active")

class AlertRuleCreate(AlertRuleBase):
    """Schema for creating alert rules."""
    pass

class AlertRuleUpdate(BaseModel):
    """Schema for updating alert rules."""
    description: Optional[str] = None
    condition: Optional[str] = None
    threshold: Optional[float] = None
    severity: Optional[str] = None
    is_active: Optional[bool] = None

class AlertRule(AlertRuleBase):
    """Schema for alert rule responses."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AlertBase(BaseModel):
    """Base schema for alerts."""
    rule_id: int = Field(..., description="ID of the alert rule that triggered this alert")
    metric_name: str = Field(..., description="Name of the metric that triggered the alert")
    metric_value: float = Field(..., description="Value of the metric that triggered the alert")
    threshold: float = Field(..., description="Threshold value that was exceeded")
    severity: str = Field(..., description="Severity of the alert")
    message: str = Field(..., description="Alert message")
    status: str = Field(..., description="Status of the alert (e.g., 'active', 'resolved')")

class AlertCreate(AlertBase):
    """Schema for creating alerts."""
    pass

class AlertUpdate(BaseModel):
    """Schema for updating alerts."""
    status: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    resolution_notes: Optional[str] = None

class Alert(AlertBase):
    """Schema for alert responses."""
    id: int
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    resolution_notes: Optional[str] = None

    class Config:
        from_attributes = True

class ErrorLogFilter(BaseModel):
    """Schema for filtering error logs."""
    error_type: Optional[str] = None
    severity: Optional[str] = None
    source: Optional[str] = None
    user_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    resolved: Optional[bool] = None

class SystemLogFilter(BaseModel):
    """Schema for filtering system logs."""
    log_level: Optional[str] = None
    source: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class AlertFilter(BaseModel):
    """Schema for filtering alerts."""
    rule_id: Optional[int] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None 