"""
Routes for error logging and monitoring system.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from config.database import get_db
from auth.dependencies import get_current_admin
from . import schemas, services

router = APIRouter(
    prefix="/error-logging",
    tags=["error-logging"],
    dependencies=[Depends(get_current_admin)]
)

# Error Log Routes
@router.post("/error-logs", response_model=schemas.ErrorLog)
def create_error_log(
    error_log: schemas.ErrorLogCreate,
    db: Session = Depends(get_db)
):
    """Create a new error log entry."""
    return services.ErrorLoggingService.create_error_log(db, error_log)

@router.get("/error-logs/{error_log_id}", response_model=schemas.ErrorLog)
def get_error_log(
    error_log_id: int,
    db: Session = Depends(get_db)
):
    """Get an error log by ID."""
    return services.ErrorLoggingService.get_error_log(db, error_log_id)

@router.get("/error-logs", response_model=List[schemas.ErrorLog])
def get_error_logs(
    error_type: Optional[str] = None,
    severity: Optional[str] = None,
    source: Optional[str] = None,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    resolved: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get error logs with filtering."""
    filter_params = schemas.ErrorLogFilter(
        error_type=error_type,
        severity=severity,
        source=source,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        resolved=resolved
    )
    return services.ErrorLoggingService.get_error_logs(db, filter_params, skip, limit)

@router.patch("/error-logs/{error_log_id}", response_model=schemas.ErrorLog)
def update_error_log(
    error_log_id: int,
    error_log_update: schemas.ErrorLogUpdate,
    db: Session = Depends(get_db)
):
    """Update an error log."""
    return services.ErrorLoggingService.update_error_log(db, error_log_id, error_log_update)

# System Log Routes
@router.post("/system-logs", response_model=schemas.SystemLog)
def create_system_log(
    system_log: schemas.SystemLogCreate,
    db: Session = Depends(get_db)
):
    """Create a new system log entry."""
    return services.SystemLoggingService.create_system_log(db, system_log)

@router.get("/system-logs", response_model=List[schemas.SystemLog])
def get_system_logs(
    log_level: Optional[str] = None,
    source: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get system logs with filtering."""
    filter_params = schemas.SystemLogFilter(
        log_level=log_level,
        source=source,
        start_date=start_date,
        end_date=end_date
    )
    return services.SystemLoggingService.get_system_logs(db, filter_params, skip, limit)

# Monitoring Routes
@router.post("/metrics", response_model=schemas.MonitoringMetric)
def create_metric(
    metric: schemas.MonitoringMetricCreate,
    db: Session = Depends(get_db)
):
    """Create a new monitoring metric."""
    return services.MonitoringService.create_metric(db, metric)

@router.get("/metrics/{metric_name}", response_model=List[schemas.MonitoringMetric])
def get_metrics(
    metric_name: str,
    start_time: datetime,
    end_time: datetime,
    db: Session = Depends(get_db)
):
    """Get metrics for a specific metric name within a time range."""
    return services.MonitoringService.get_metrics(db, metric_name, start_time, end_time)

@router.get("/metrics/{metric_name}/latest", response_model=schemas.MonitoringMetric)
def get_latest_metric(
    metric_name: str,
    db: Session = Depends(get_db)
):
    """Get the latest metric for a specific metric name."""
    metric = services.MonitoringService.get_latest_metric(db, metric_name)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No metrics found for {metric_name}"
        )
    return metric

# Alert Routes
@router.post("/alert-rules", response_model=schemas.AlertRule)
def create_alert_rule(
    alert_rule: schemas.AlertRuleCreate,
    db: Session = Depends(get_db)
):
    """Create a new alert rule."""
    return services.AlertService.create_alert_rule(db, alert_rule)

@router.get("/alert-rules/{alert_rule_id}", response_model=schemas.AlertRule)
def get_alert_rule(
    alert_rule_id: int,
    db: Session = Depends(get_db)
):
    """Get an alert rule by ID."""
    return services.AlertService.get_alert_rule(db, alert_rule_id)

@router.patch("/alert-rules/{alert_rule_id}", response_model=schemas.AlertRule)
def update_alert_rule(
    alert_rule_id: int,
    alert_rule_update: schemas.AlertRuleUpdate,
    db: Session = Depends(get_db)
):
    """Update an alert rule."""
    return services.AlertService.update_alert_rule(db, alert_rule_id, alert_rule_update)

@router.post("/alerts", response_model=schemas.Alert)
def create_alert(
    alert: schemas.AlertCreate,
    db: Session = Depends(get_db)
):
    """Create a new alert."""
    return services.AlertService.create_alert(db, alert)

@router.get("/alerts", response_model=List[schemas.Alert])
def get_alerts(
    rule_id: Optional[int] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get alerts with filtering."""
    filter_params = schemas.AlertFilter(
        rule_id=rule_id,
        severity=severity,
        status=status,
        start_date=start_date,
        end_date=end_date
    )
    return services.AlertService.get_alerts(db, filter_params, skip, limit)

@router.patch("/alerts/{alert_id}", response_model=schemas.Alert)
def update_alert(
    alert_id: int,
    alert_update: schemas.AlertUpdate,
    db: Session = Depends(get_db)
):
    """Update an alert."""
    return services.AlertService.update_alert(db, alert_id, alert_update)

@router.post("/check-alerts", response_model=List[schemas.Alert])
def check_alert_rules(
    db: Session = Depends(get_db)
):
    """Check all active alert rules and create alerts if conditions are met."""
    return services.AlertService.check_alert_rules(db) 