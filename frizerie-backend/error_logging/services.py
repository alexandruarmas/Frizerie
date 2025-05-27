"""
Services for error logging and monitoring system.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from fastapi import HTTPException, status

from . import models, schemas

class ErrorLoggingService:
    """Service for handling error logging operations."""
    
    @staticmethod
    def create_error_log(db: Session, error_log: schemas.ErrorLogCreate) -> models.ErrorLog:
        """Create a new error log entry."""
        db_error_log = models.ErrorLog(**error_log.dict())
        db.add(db_error_log)
        db.commit()
        db.refresh(db_error_log)
        return db_error_log
    
    @staticmethod
    def get_error_log(db: Session, error_log_id: int) -> models.ErrorLog:
        """Get an error log by ID."""
        error_log = db.query(models.ErrorLog).filter(models.ErrorLog.id == error_log_id).first()
        if not error_log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Error log not found"
            )
        return error_log
    
    @staticmethod
    def get_error_logs(
        db: Session,
        filter_params: schemas.ErrorLogFilter,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.ErrorLog]:
        """Get error logs with filtering."""
        query = db.query(models.ErrorLog)
        
        if filter_params.error_type:
            query = query.filter(models.ErrorLog.error_type == filter_params.error_type)
        if filter_params.severity:
            query = query.filter(models.ErrorLog.severity == filter_params.severity)
        if filter_params.source:
            query = query.filter(models.ErrorLog.source == filter_params.source)
        if filter_params.user_id:
            query = query.filter(models.ErrorLog.user_id == filter_params.user_id)
        if filter_params.start_date:
            query = query.filter(models.ErrorLog.created_at >= filter_params.start_date)
        if filter_params.end_date:
            query = query.filter(models.ErrorLog.created_at <= filter_params.end_date)
        if filter_params.resolved is not None:
            if filter_params.resolved:
                query = query.filter(models.ErrorLog.resolved_at.isnot(None))
            else:
                query = query.filter(models.ErrorLog.resolved_at.is_(None))
        
        return query.order_by(desc(models.ErrorLog.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_error_log(
        db: Session,
        error_log_id: int,
        error_log_update: schemas.ErrorLogUpdate
    ) -> models.ErrorLog:
        """Update an error log."""
        error_log = ErrorLoggingService.get_error_log(db, error_log_id)
        
        for field, value in error_log_update.dict(exclude_unset=True).items():
            setattr(error_log, field, value)
        
        db.commit()
        db.refresh(error_log)
        return error_log

class SystemLoggingService:
    """Service for handling system logging operations."""
    
    @staticmethod
    def create_system_log(db: Session, system_log: schemas.SystemLogCreate) -> models.SystemLog:
        """Create a new system log entry."""
        db_system_log = models.SystemLog(**system_log.dict())
        db.add(db_system_log)
        db.commit()
        db.refresh(db_system_log)
        return db_system_log
    
    @staticmethod
    def get_system_logs(
        db: Session,
        filter_params: schemas.SystemLogFilter,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.SystemLog]:
        """Get system logs with filtering."""
        query = db.query(models.SystemLog)
        
        if filter_params.log_level:
            query = query.filter(models.SystemLog.log_level == filter_params.log_level)
        if filter_params.source:
            query = query.filter(models.SystemLog.source == filter_params.source)
        if filter_params.start_date:
            query = query.filter(models.SystemLog.created_at >= filter_params.start_date)
        if filter_params.end_date:
            query = query.filter(models.SystemLog.created_at <= filter_params.end_date)
        
        return query.order_by(desc(models.SystemLog.created_at)).offset(skip).limit(limit).all()

class MonitoringService:
    """Service for handling monitoring operations."""
    
    @staticmethod
    def create_metric(db: Session, metric: schemas.MonitoringMetricCreate) -> models.MonitoringMetric:
        """Create a new monitoring metric."""
        db_metric = models.MonitoringMetric(**metric.dict())
        db.add(db_metric)
        db.commit()
        db.refresh(db_metric)
        return db_metric
    
    @staticmethod
    def get_metrics(
        db: Session,
        metric_name: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[models.MonitoringMetric]:
        """Get metrics for a specific metric name within a time range."""
        return db.query(models.MonitoringMetric).filter(
            and_(
                models.MonitoringMetric.metric_name == metric_name,
                models.MonitoringMetric.timestamp >= start_time,
                models.MonitoringMetric.timestamp <= end_time
            )
        ).order_by(models.MonitoringMetric.timestamp).all()
    
    @staticmethod
    def get_latest_metric(db: Session, metric_name: str) -> Optional[models.MonitoringMetric]:
        """Get the latest metric for a specific metric name."""
        return db.query(models.MonitoringMetric).filter(
            models.MonitoringMetric.metric_name == metric_name
        ).order_by(desc(models.MonitoringMetric.timestamp)).first()

class AlertService:
    """Service for handling alert operations."""
    
    @staticmethod
    def create_alert_rule(db: Session, alert_rule: schemas.AlertRuleCreate) -> models.AlertRule:
        """Create a new alert rule."""
        db_alert_rule = models.AlertRule(**alert_rule.dict())
        db.add(db_alert_rule)
        db.commit()
        db.refresh(db_alert_rule)
        return db_alert_rule
    
    @staticmethod
    def get_alert_rule(db: Session, alert_rule_id: int) -> models.AlertRule:
        """Get an alert rule by ID."""
        alert_rule = db.query(models.AlertRule).filter(models.AlertRule.id == alert_rule_id).first()
        if not alert_rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert rule not found"
            )
        return alert_rule
    
    @staticmethod
    def update_alert_rule(
        db: Session,
        alert_rule_id: int,
        alert_rule_update: schemas.AlertRuleUpdate
    ) -> models.AlertRule:
        """Update an alert rule."""
        alert_rule = AlertService.get_alert_rule(db, alert_rule_id)
        
        for field, value in alert_rule_update.dict(exclude_unset=True).items():
            setattr(alert_rule, field, value)
        
        db.commit()
        db.refresh(alert_rule)
        return alert_rule
    
    @staticmethod
    def create_alert(db: Session, alert: schemas.AlertCreate) -> models.Alert:
        """Create a new alert."""
        db_alert = models.Alert(**alert.dict())
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        return db_alert
    
    @staticmethod
    def get_alerts(
        db: Session,
        filter_params: schemas.AlertFilter,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.Alert]:
        """Get alerts with filtering."""
        query = db.query(models.Alert)
        
        if filter_params.rule_id:
            query = query.filter(models.Alert.rule_id == filter_params.rule_id)
        if filter_params.severity:
            query = query.filter(models.Alert.severity == filter_params.severity)
        if filter_params.status:
            query = query.filter(models.Alert.status == filter_params.status)
        if filter_params.start_date:
            query = query.filter(models.Alert.created_at >= filter_params.start_date)
        if filter_params.end_date:
            query = query.filter(models.Alert.created_at <= filter_params.end_date)
        
        return query.order_by(desc(models.Alert.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_alert(
        db: Session,
        alert_id: int,
        alert_update: schemas.AlertUpdate
    ) -> models.Alert:
        """Update an alert."""
        alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        for field, value in alert_update.dict(exclude_unset=True).items():
            setattr(alert, field, value)
        
        db.commit()
        db.refresh(alert)
        return alert
    
    @staticmethod
    def check_alert_rules(db: Session) -> List[models.Alert]:
        """Check all active alert rules and create alerts if conditions are met."""
        alerts = []
        active_rules = db.query(models.AlertRule).filter(models.AlertRule.is_active == True).all()
        
        for rule in active_rules:
            latest_metric = MonitoringService.get_latest_metric(db, rule.metric_name)
            if not latest_metric:
                continue
            
            should_alert = False
            if rule.condition == ">":
                should_alert = latest_metric.metric_value > rule.threshold
            elif rule.condition == "<":
                should_alert = latest_metric.metric_value < rule.threshold
            elif rule.condition == "==":
                should_alert = latest_metric.metric_value == rule.threshold
            
            if should_alert:
                alert = schemas.AlertCreate(
                    rule_id=rule.id,
                    metric_name=rule.metric_name,
                    metric_value=latest_metric.metric_value,
                    threshold=rule.threshold,
                    severity=rule.severity,
                    message=f"Alert: {rule.metric_name} {rule.condition} {rule.threshold}",
                    status="active"
                )
                alerts.append(AlertService.create_alert(db, alert))
        
        return alerts 