"""
Analytics and reporting services for tracking and analyzing business metrics.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, or_, text
from datetime import datetime, timedelta
import pandas as pd
import json
import os
from pathlib import Path
import uuid
import numpy as np
from fastapi import HTTPException, status

from analytics.models import AnalyticsEvent, EventType, Dashboard, DashboardWidget, WidgetDataCache, DailyAnalytics, MonthlyAnalytics
from analytics.schemas import AnalyticsEventCreate, TimeRange, DashboardCreate, DashboardUpdate, Dashboard as DashboardSchema, DashboardWidget as DashboardWidgetSchema, VisualizationData, WidgetData, ChartConfig, VisualizationType, CustomReportRequest, ExportRequest, ExportFormat
from users.models import User
from booking.models import Booking
from services.models import Service
from payments.models import Payment, PaymentStatus
from sqlalchemy.exc import IntegrityError
from validation.schemas import (
    AnalyticsResponse, BookingStatistics,
    StylistPerformance, ServicePopularity,
    CustomerAnalytics, DateRangeFilter
)

# Cache for real-time metrics
_realtime_cache = {}
_last_cache_update = datetime.min
CACHE_TTL = 60  # seconds

def track_event(
    db: Session,
    event_type: str,
    properties: Dict[str, Any],
    user_id: Optional[int] = None,
    stylist_id: Optional[int] = None,
    service_id: Optional[int] = None,
    booking_id: Optional[str] = None
) -> AnalyticsEvent:
    """Track an analytics event."""
    try:
        event = AnalyticsEvent(
            event_type=event_type,
            properties=properties,
            user_id=user_id,
            stylist_id=stylist_id,
            service_id=service_id,
            booking_id=booking_id
        )
        
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
    except Exception as e:
        db.rollback()
        print(f"Error tracking analytics event: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track analytics event: {str(e)}"
        )

def get_events(
    db: Session,
    event_type: Optional[EventType] = None,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0
) -> List[AnalyticsEvent]:
    """
    Get analytics events with optional filtering.
    """
    query = db.query(AnalyticsEvent)
    
    if event_type:
        query = query.filter(AnalyticsEvent.event_type == event_type)
    if user_id:
        query = query.filter(AnalyticsEvent.user_id == user_id)
    if start_date:
        query = query.filter(AnalyticsEvent.created_at >= start_date)
    if end_date:
        query = query.filter(AnalyticsEvent.created_at <= end_date)
    
    return query.order_by(desc(AnalyticsEvent.created_at)).offset(offset).limit(limit).all()

def get_summary(
    db: Session,
    time_range: TimeRange
) -> Dict[str, Any]:
    """
    Get overall analytics summary.
    """
    # Get total users
    total_users = db.query(func.count(User.id)).scalar()
    
    # Get total bookings
    total_bookings = db.query(func.count(Booking.id)).scalar()
    
    # Get total revenue
    total_revenue = db.query(func.sum(Payment.amount))\
        .filter(Payment.status == PaymentStatus.COMPLETED)\
        .scalar() or 0.0
    
    # Calculate average booking value
    avg_booking_value = total_revenue / total_bookings if total_bookings > 0 else 0.0
    
    # Calculate booking completion rate
    completed_bookings = db.query(func.count(Booking.id))\
        .filter(Booking.status == "completed")\
        .scalar()
    booking_completion_rate = (completed_bookings / total_bookings * 100) if total_bookings > 0 else 0.0
    
    # Get popular services
    popular_services = db.query(
        Service.name,
        func.count(Booking.id).label('booking_count')
    ).join(Booking)\
     .group_by(Service.name)\
     .order_by(desc('booking_count'))\
     .limit(5)\
     .all()
    
    # Get revenue by period
    revenue_by_period = db.query(
        func.date_trunc('day', Payment.created_at).label('date'),
        func.sum(Payment.amount).label('revenue')
    ).filter(
        Payment.status == PaymentStatus.COMPLETED,
        Payment.created_at.between(time_range.start_date, time_range.end_date)
    ).group_by('date')\
     .order_by('date')\
     .all()
    
    # Get bookings by period
    bookings_by_period = db.query(
        func.date_trunc('day', Booking.date).label('date'),
        func.count(Booking.id).label('count')
    ).filter(
        Booking.date.between(time_range.start_date, time_range.end_date)
    ).group_by('date')\
     .order_by('date')\
     .all()
    
    # Get user growth
    user_growth = db.query(
        func.date_trunc('day', User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter(
        User.created_at.between(time_range.start_date, time_range.end_date)
    ).group_by('date')\
     .order_by('date')\
     .all()
    
    return {
        "total_users": total_users,
        "total_bookings": total_bookings,
        "total_revenue": total_revenue,
        "average_booking_value": avg_booking_value,
        "booking_completion_rate": booking_completion_rate,
        "popular_services": [
            {"name": name, "count": count}
            for name, count in popular_services
        ],
        "revenue_by_period": [
            {"date": date.isoformat(), "revenue": revenue}
            for date, revenue in revenue_by_period
        ],
        "bookings_by_period": [
            {"date": date.isoformat(), "count": count}
            for date, count in bookings_by_period
        ],
        "user_growth": [
            {"date": date.isoformat(), "count": count}
            for date, count in user_growth
        ]
    }

def get_revenue_analytics(
    db: Session,
    time_range: TimeRange
) -> Dict[str, Any]:
    """
    Get revenue analytics.
    """
    # Get total revenue
    total_revenue = db.query(func.sum(Payment.amount))\
        .filter(
            Payment.status == PaymentStatus.COMPLETED,
            Payment.created_at.between(time_range.start_date, time_range.end_date)
        ).scalar() or 0.0
    
    # Get revenue by period
    revenue_by_period = db.query(
        func.date_trunc('day', Payment.created_at).label('date'),
        func.sum(Payment.amount).label('revenue')
    ).filter(
        Payment.status == PaymentStatus.COMPLETED,
        Payment.created_at.between(time_range.start_date, time_range.end_date)
    ).group_by('date')\
     .order_by('date')\
     .all()
    
    # Get revenue by service
    revenue_by_service = db.query(
        Service.name,
        func.sum(Payment.amount).label('revenue')
    ).join(Booking)\
     .join(Payment)\
     .filter(
        Payment.status == PaymentStatus.COMPLETED,
        Payment.created_at.between(time_range.start_date, time_range.end_date)
    ).group_by(Service.name)\
     .order_by(desc('revenue'))\
     .all()
    
    # Calculate average order value
    total_orders = db.query(func.count(Payment.id))\
        .filter(
            Payment.status == PaymentStatus.COMPLETED,
            Payment.created_at.between(time_range.start_date, time_range.end_date)
        ).scalar() or 1
    avg_order_value = total_revenue / total_orders
    
    # Calculate refund rate
    total_refunds = db.query(func.count(Payment.id))\
        .filter(
            Payment.status == PaymentStatus.REFUNDED,
            Payment.created_at.between(time_range.start_date, time_range.end_date)
        ).scalar()
    refund_rate = (total_refunds / total_orders * 100) if total_orders > 0 else 0.0
    
    return {
        "total_revenue": total_revenue,
        "revenue_by_period": [
            {"date": date.isoformat(), "revenue": revenue}
            for date, revenue in revenue_by_period
        ],
        "revenue_by_service": [
            {"service": name, "revenue": revenue}
            for name, revenue in revenue_by_service
        ],
        "average_order_value": avg_order_value,
        "refund_rate": refund_rate
    }

def get_booking_analytics(
    db: Session,
    time_range: TimeRange
) -> Dict[str, Any]:
    """
    Get booking analytics.
    """
    # Get total bookings
    total_bookings = db.query(func.count(Booking.id))\
        .filter(Booking.date.between(time_range.start_date, time_range.end_date))\
        .scalar()
    
    # Get bookings by period
    bookings_by_period = db.query(
        func.date_trunc('day', Booking.date).label('date'),
        func.count(Booking.id).label('count')
    ).filter(Booking.date.between(time_range.start_date, time_range.end_date))\
     .group_by('date')\
     .order_by('date')\
     .all()
    
    # Get bookings by service
    bookings_by_service = db.query(
        Service.name,
        func.count(Booking.id).label('count')
    ).join(Booking)\
     .filter(Booking.date.between(time_range.start_date, time_range.end_date))\
     .group_by(Service.name)\
     .order_by(desc('count'))\
     .all()
    
    # Calculate completion and cancellation rates
    completed_bookings = db.query(func.count(Booking.id))\
        .filter(
            Booking.status == "completed",
            Booking.date.between(time_range.start_date, time_range.end_date)
        ).scalar()
    cancelled_bookings = db.query(func.count(Booking.id))\
        .filter(
            Booking.status == "cancelled",
            Booking.date.between(time_range.start_date, time_range.end_date)
        ).scalar()
    
    completion_rate = (completed_bookings / total_bookings * 100) if total_bookings > 0 else 0.0
    cancellation_rate = (cancelled_bookings / total_bookings * 100) if total_bookings > 0 else 0.0
    
    return {
        "total_bookings": total_bookings,
        "bookings_by_period": [
            {"date": date.isoformat(), "count": count}
            for date, count in bookings_by_period
        ],
        "bookings_by_service": [
            {"service": name, "count": count}
            for name, count in bookings_by_service
        ],
        "completion_rate": completion_rate,
        "cancellation_rate": cancellation_rate
    }

def get_user_analytics(
    db: Session,
    time_range: TimeRange
) -> Dict[str, Any]:
    """
    Get user analytics.
    """
    # Get total users
    total_users = db.query(func.count(User.id)).scalar()
    
    # Get new users by period
    new_users_by_period = db.query(
        func.date_trunc('day', User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter(User.created_at.between(time_range.start_date, time_range.end_date))\
     .group_by('date')\
     .order_by('date')\
     .all()
    
    # Get active users (users with bookings)
    active_users = db.query(func.count(func.distinct(Booking.user_id)))\
        .filter(Booking.date.between(time_range.start_date, time_range.end_date))\
        .scalar()
    
    # Get user retention rate
    total_active_users = db.query(func.count(func.distinct(Booking.user_id))).scalar()
    retention_rate = (active_users / total_users * 100) if total_users > 0 else 0.0
    
    # Get user booking frequency
    booking_frequency = db.query(
        Booking.user_id,
        func.count(Booking.id).label('booking_count')
    ).filter(Booking.date.between(time_range.start_date, time_range.end_date))\
     .group_by(Booking.user_id)\
     .all()
    
    avg_booking_frequency = sum(count for _, count in booking_frequency) / len(booking_frequency) if booking_frequency else 0.0
    
    return {
        "total_users": total_users,
        "new_users_by_period": [
            {"date": date.isoformat(), "count": count}
            for date, count in new_users_by_period
        ],
        "active_users": active_users,
        "retention_rate": retention_rate,
        "average_booking_frequency": avg_booking_frequency
    }

async def get_realtime_metrics(db: Session) -> Dict[str, Any]:
    """Get real-time analytics metrics."""
    global _last_cache_update
    
    # Check if cache is still valid
    if (datetime.utcnow() - _last_cache_update).total_seconds() < CACHE_TTL:
        return _realtime_cache
    
    # Get active users (users with activity in last 15 minutes)
    active_users = db.query(func.count(func.distinct(AnalyticsEvent.user_id)))\
        .filter(
            AnalyticsEvent.created_at >= datetime.utcnow() - timedelta(minutes=15)
        ).scalar()
    
    # Get current bookings (bookings happening now)
    current_time = datetime.utcnow().time()
    current_bookings = db.query(func.count(Booking.id))\
        .filter(
            func.time(Booking.start_time) <= current_time,
            func.time(Booking.end_time) >= current_time,
            Booking.status == "confirmed"
        ).scalar()
    
    # Get pending payments
    pending_payments = db.query(func.count(Payment.id))\
        .filter(Payment.status == PaymentStatus.PENDING)\
        .scalar()
    
    # Get today's revenue
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    revenue_today = db.query(func.sum(Payment.amount))\
        .filter(
            Payment.status == PaymentStatus.COMPLETED,
            Payment.created_at >= today_start
        ).scalar() or 0.0
    
    # Get today's bookings
    bookings_today = db.query(func.count(Booking.id))\
        .filter(Booking.date >= today_start)\
        .scalar()
    
    # Get popular services right now
    popular_services = db.query(
        Service.name,
        func.count(Booking.id).label('count')
    ).join(Booking)\
     .filter(
        func.time(Booking.start_time) <= current_time,
        func.time(Booking.end_time) >= current_time,
        Booking.status == "confirmed"
    ).group_by(Service.name)\
     .order_by(desc('count'))\
     .limit(5)\
     .all()
    
    # Get recent events
    recent_events = db.query(AnalyticsEvent)\
        .order_by(desc(AnalyticsEvent.created_at))\
        .limit(10)\
        .all()
    
    # Update cache
    _realtime_cache = {
        "active_users": active_users,
        "current_bookings": current_bookings,
        "pending_payments": pending_payments,
        "revenue_today": revenue_today,
        "bookings_today": bookings_today,
        "popular_services_now": [
            {"name": name, "count": count}
            for name, count in popular_services
        ],
        "recent_events": [
            {
                "id": event.id,
                "type": event.event_type,
                "user_id": event.user_id,
                "properties": event.properties,
                "created_at": event.created_at.isoformat()
            }
            for event in recent_events
        ]
    }
    _last_cache_update = datetime.utcnow()
    
    return _realtime_cache

async def generate_custom_report(
    db: Session,
    request: CustomReportRequest
) -> Dict[str, Any]:
    """Generate a custom analytics report."""
    start_time = datetime.utcnow()
    
    # Build base query based on metrics and dimensions
    query = build_analytics_query(db, request.metrics, request.dimensions)
    
    # Apply filters
    if request.filters:
        query = apply_filters(query, request.filters)
    
    # Apply time range
    query = query.filter(
        AnalyticsEvent.created_at.between(
            request.time_range.start_date,
            request.time_range.end_date
        )
    )
    
    # Apply grouping
    if request.group_by:
        query = apply_grouping(query, request.group_by)
    
    # Apply sorting
    if request.sort_by:
        query = apply_sorting(query, request.sort_by)
    
    # Apply limit
    if request.limit:
        query = query.limit(request.limit)
    
    # Execute query
    results = query.all()
    
    # Calculate execution time
    execution_time = (datetime.utcnow() - start_time).total_seconds()
    
    return {
        "data": [dict(row) for row in results],
        "metadata": {
            "metrics": request.metrics,
            "dimensions": request.dimensions,
            "filters": request.filters,
            "group_by": request.group_by,
            "sort_by": request.sort_by,
            "time_range": {
                "start": request.time_range.start_date.isoformat(),
                "end": request.time_range.end_date.isoformat()
            }
        },
        "total_rows": len(results),
        "execution_time": execution_time
    }

async def export_report(
    db: Session,
    request: ExportRequest
) -> Dict[str, Any]:
    """Export analytics data in the specified format."""
    # Generate report data
    if request.report_type == "custom":
        report_data = await generate_custom_report(db, request)
        data = report_data["data"]
    else:
        # Handle predefined report types
        report_data = await get_predefined_report(db, request.report_type, request.time_range)
        data = report_data["data"]
    
    # Create export directory if it doesn't exist
    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)
    
    # Generate unique filename
    filename = f"{request.report_type}_{uuid.uuid4()}"
    
    # Export based on format
    if request.format == ExportFormat.CSV:
        filepath = export_dir / f"{filename}.csv"
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
    elif request.format == ExportFormat.JSON:
        filepath = export_dir / f"{filename}.json"
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    elif request.format == ExportFormat.EXCEL:
        filepath = export_dir / f"{filename}.xlsx"
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False)
    
    # Generate download URL (this would be handled by your static file server)
    download_url = f"/exports/{filepath.name}"
    
    # Set expiration (24 hours from now)
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    return {
        "download_url": download_url,
        "expires_at": expires_at.isoformat(),
        "file_size": filepath.stat().st_size,
        "format": request.format
    }

def build_analytics_query(
    db: Session,
    metrics: List[str],
    dimensions: List[str]
) -> Any:
    """Build base query for analytics based on metrics and dimensions."""
    # This is a simplified version - you would need to implement
    # proper metric and dimension mapping based on your schema
    query = db.query(AnalyticsEvent)
    
    # Add metrics
    for metric in metrics:
        if metric == "count":
            query = query.with_entities(func.count(AnalyticsEvent.id))
        elif metric == "unique_users":
            query = query.with_entities(func.count(func.distinct(AnalyticsEvent.user_id)))
        # Add more metrics as needed
    
    # Add dimensions
    for dimension in dimensions:
        if dimension == "event_type":
            query = query.add_columns(AnalyticsEvent.event_type)
        elif dimension == "user_id":
            query = query.add_columns(AnalyticsEvent.user_id)
        # Add more dimensions as needed
    
    return query

def apply_filters(query: Any, filters: Dict[str, Any]) -> Any:
    """Apply filters to the query."""
    for key, value in filters.items():
        if key == "event_type":
            query = query.filter(AnalyticsEvent.event_type == value)
        elif key == "user_id":
            query = query.filter(AnalyticsEvent.user_id == value)
        # Add more filters as needed
    return query

def apply_grouping(query: Any, group_by: List[str]) -> Any:
    """Apply grouping to the query."""
    for field in group_by:
        if field == "event_type":
            query = query.group_by(AnalyticsEvent.event_type)
        elif field == "user_id":
            query = query.group_by(AnalyticsEvent.user_id)
        # Add more grouping fields as needed
    return query

def apply_sorting(query: Any, sort_by: List[str]) -> Any:
    """Apply sorting to the query."""
    for field in sort_by:
        if field.startswith("-"):
            field = field[1:]
            if field == "created_at":
                query = query.order_by(desc(AnalyticsEvent.created_at))
        else:
            if field == "created_at":
                query = query.order_by(AnalyticsEvent.created_at)
        # Add more sorting fields as needed
    return query

async def get_predefined_report(
    db: Session,
    report_type: str,
    time_range: TimeRange
) -> Dict[str, Any]:
    """Get a predefined report."""
    if report_type == "revenue":
        return await get_revenue_analytics(db, time_range)
    elif report_type == "bookings":
        return await get_booking_analytics(db, time_range)
    elif report_type == "users":
        return await get_user_analytics(db, time_range)
    else:
        raise ValueError(f"Unknown report type: {report_type}")

async def create_dashboard(
    db: Session,
    dashboard_data: DashboardCreate,
    owner_id: int
) -> Dashboard:
    """Create a new dashboard."""
    dashboard = Dashboard(
        name=dashboard_data.name,
        description=dashboard_data.description,
        owner_id=owner_id,
        is_public=dashboard_data.is_public,
        layout=dashboard_data.layout,
        refresh_interval=dashboard_data.refresh_interval,
        time_range_start=dashboard_data.time_range.start_date,
        time_range_end=dashboard_data.time_range.end_date
    )
    
    db.add(dashboard)
    db.commit()
    db.refresh(dashboard)
    
    # Create widgets
    for widget_data in dashboard_data.widgets:
        widget = DashboardWidget(
            dashboard_id=dashboard.id,
            type=widget_data.type,
            title=widget_data.title,
            config=widget_data.config.dict(),
            data_source=widget_data.data_source,
            refresh_interval=widget_data.refresh_interval,
            position=widget_data.position,
            filters=widget_data.filters
        )
        db.add(widget)
    
    db.commit()
    return dashboard

async def update_dashboard(
    db: Session,
    dashboard_id: str,
    dashboard_data: DashboardUpdate,
    owner_id: int
) -> Dashboard:
    """Update an existing dashboard."""
    dashboard = db.query(Dashboard).filter(
        Dashboard.id == dashboard_id,
        Dashboard.owner_id == owner_id
    ).first()
    
    if not dashboard:
        raise ValueError("Dashboard not found")
    
    # Update dashboard fields
    if dashboard_data.name is not None:
        dashboard.name = dashboard_data.name
    if dashboard_data.description is not None:
        dashboard.description = dashboard_data.description
    if dashboard_data.is_public is not None:
        dashboard.is_public = dashboard_data.is_public
    if dashboard_data.layout is not None:
        dashboard.layout = dashboard_data.layout
    if dashboard_data.refresh_interval is not None:
        dashboard.refresh_interval = dashboard_data.refresh_interval
    if dashboard_data.time_range is not None:
        dashboard.time_range_start = dashboard_data.time_range.start_date
        dashboard.time_range_end = dashboard_data.time_range.end_date
    
    # Update widgets if provided
    if dashboard_data.widgets is not None:
        # Delete existing widgets
        db.query(DashboardWidget).filter(
            DashboardWidget.dashboard_id == dashboard_id
        ).delete()
        
        # Create new widgets
        for widget_data in dashboard_data.widgets:
            widget = DashboardWidget(
                dashboard_id=dashboard.id,
                type=widget_data.type,
                title=widget_data.title,
                config=widget_data.config.dict(),
                data_source=widget_data.data_source,
                refresh_interval=widget_data.refresh_interval,
                position=widget_data.position,
                filters=widget_data.filters
            )
            db.add(widget)
    
    db.commit()
    db.refresh(dashboard)
    return dashboard

async def get_dashboard(
    db: Session,
    dashboard_id: str,
    user_id: int
) -> Dashboard:
    """Get a dashboard by ID."""
    dashboard = db.query(Dashboard).filter(
        Dashboard.id == dashboard_id,
        (Dashboard.owner_id == user_id) | (Dashboard.is_public == True)
    ).first()
    
    if not dashboard:
        raise ValueError("Dashboard not found")
    
    return dashboard

async def list_dashboards(
    db: Session,
    user_id: int,
    include_public: bool = True
) -> List[Dashboard]:
    """List dashboards accessible to the user."""
    query = db.query(Dashboard).filter(
        (Dashboard.owner_id == user_id) | (Dashboard.is_public == True)
    )
    
    if not include_public:
        query = query.filter(Dashboard.owner_id == user_id)
    
    return query.all()

async def delete_dashboard(
    db: Session,
    dashboard_id: str,
    owner_id: int
) -> None:
    """Delete a dashboard."""
    dashboard = db.query(Dashboard).filter(
        Dashboard.id == dashboard_id,
        Dashboard.owner_id == owner_id
    ).first()
    
    if not dashboard:
        raise ValueError("Dashboard not found")
    
    db.delete(dashboard)
    db.commit()

async def get_widget_data(
    db: Session,
    widget_id: str,
    force_refresh: bool = False
) -> WidgetData:
    """Get widget data, using cache if available and not expired."""
    widget = db.query(DashboardWidget).filter(
        DashboardWidget.id == widget_id
    ).first()
    
    if not widget:
        raise ValueError("Widget not found")
    
    # Check cache
    cache = db.query(WidgetDataCache).filter(
        WidgetDataCache.widget_id == widget_id,
        WidgetDataCache.expires_at > datetime.utcnow()
    ).first()
    
    if cache and not force_refresh:
        return WidgetData(
            widget_id=widget_id,
            data=cache.data,
            last_updated=cache.last_updated,
            next_update=cache.next_update
        )
    
    # Generate new data
    data = await generate_widget_data(db, widget)
    
    # Update cache
    next_update = datetime.utcnow() + timedelta(seconds=widget.refresh_interval)
    expires_at = next_update + timedelta(minutes=5)  # Cache expires 5 minutes after next update
    
    if cache:
        cache.data = data
        cache.last_updated = datetime.utcnow()
        cache.next_update = next_update
        cache.expires_at = expires_at
    else:
        cache = WidgetDataCache(
            widget_id=widget_id,
            data=data,
            next_update=next_update,
            expires_at=expires_at
        )
        db.add(cache)
    
    db.commit()
    
    return WidgetData(
        widget_id=widget_id,
        data=data,
        last_updated=cache.last_updated,
        next_update=cache.next_update
    )

async def generate_widget_data(
    db: Session,
    widget: DashboardWidget
) -> VisualizationData:
    """Generate visualization data for a widget."""
    # Get raw data based on widget type and data source
    raw_data = await get_widget_raw_data(db, widget)
    
    # Transform data based on visualization type
    config = ChartConfig(**widget.config)
    return transform_data_for_visualization(raw_data, config)

async def get_widget_raw_data(
    db: Session,
    widget: DashboardWidget
) -> pd.DataFrame:
    """Get raw data for a widget based on its data source."""
    if widget.data_source == "revenue":
        return await get_revenue_data(db, widget.filters)
    elif widget.data_source == "bookings":
        return await get_booking_data(db, widget.filters)
    elif widget.data_source == "users":
        return await get_user_data(db, widget.filters)
    elif widget.data_source == "services":
        return await get_service_data(db, widget.filters)
    else:
        raise ValueError(f"Unknown data source: {widget.data_source}")

def transform_data_for_visualization(
    data: pd.DataFrame,
    config: ChartConfig
) -> VisualizationData:
    """Transform raw data into visualization-ready format."""
    if config.type == VisualizationType.LINE_CHART:
        return transform_for_line_chart(data, config)
    elif config.type == VisualizationType.BAR_CHART:
        return transform_for_bar_chart(data, config)
    elif config.type == VisualizationType.PIE_CHART:
        return transform_for_pie_chart(data, config)
    elif config.type == VisualizationType.AREA_CHART:
        return transform_for_area_chart(data, config)
    elif config.type == VisualizationType.TABLE:
        return transform_for_table(data, config)
    elif config.type == VisualizationType.GAUGE:
        return transform_for_gauge(data, config)
    elif config.type == VisualizationType.HEATMAP:
        return transform_for_heatmap(data, config)
    elif config.type == VisualizationType.SCATTER_PLOT:
        return transform_for_scatter_plot(data, config)
    else:
        raise ValueError(f"Unsupported visualization type: {config.type}")

def transform_for_line_chart(
    data: pd.DataFrame,
    config: ChartConfig
) -> VisualizationData:
    """Transform data for line chart visualization."""
    if config.x_axis and config.y_axis:
        x_data = data[config.x_axis].tolist()
        y_data = data[config.y_axis].tolist()
        
        if config.color_by:
            grouped_data = data.groupby(config.color_by)
            datasets = [
                {
                    "label": group,
                    "data": group_data[config.y_axis].tolist(),
                    "borderColor": f"hsl({i * 360 / len(grouped_data)}, 70%, 50%)"
                }
                for i, (group, group_data) in enumerate(grouped_data)
            ]
        else:
            datasets = [{
                "label": config.y_axis,
                "data": y_data,
                "borderColor": "hsl(0, 70%, 50%)"
            }]
        
        return VisualizationData(
            labels=x_data,
            datasets=datasets,
            metadata={
                "type": "line",
                "showLegend": config.show_legend,
                "showGrid": config.show_grid,
                "showTooltips": config.show_tooltips,
                "animation": config.animation
            }
        )
    else:
        raise ValueError("Line chart requires both x_axis and y_axis")

# Similar transformation functions for other chart types...
# (transform_for_bar_chart, transform_for_pie_chart, etc.)

# (Insert a stub (or alias) for get_analytics_summary (for example, as an alias of get_summary) so that "analytics/routes.py" can import it.)
get_analytics_summary = get_summary 

def get_booking_statistics(
    db: Session,
    date_range: DateRangeFilter
) -> List[BookingStatistics]:
    """Get booking statistics for a date range."""
    query = text("""
        SELECT 
            booking_date,
            total_bookings,
            completed_bookings,
            cancelled_bookings,
            total_revenue,
            average_duration,
            unique_customers,
            active_stylists
        FROM vw_booking_statistics
        WHERE booking_date BETWEEN :start_date AND :end_date
        ORDER BY booking_date
    """)
    
    try:
        result = db.execute(
            query,
            {
                "start_date": date_range.start_date,
                "end_date": date_range.end_date
            }
        )
        
        return [
            BookingStatistics(
                date=row.booking_date,
                total_bookings=row.total_bookings,
                completed_bookings=row.completed_bookings,
                cancelled_bookings=row.cancelled_bookings,
                total_revenue=row.total_revenue,
                average_duration=row.average_duration,
                unique_customers=row.unique_customers,
                active_stylists=row.active_stylists
            )
            for row in result
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get booking statistics"
        )

def get_stylist_performance(
    db: Session,
    date_range: Optional[DateRangeFilter] = None
) -> List[StylistPerformance]:
    """Get stylist performance metrics."""
    query = text("""
        SELECT 
            stylist_id,
            stylist_name,
            total_bookings,
            completed_bookings,
            cancelled_bookings,
            total_revenue,
            average_duration,
            unique_customers
        FROM vw_stylist_performance
        WHERE (:start_date IS NULL OR booking_date BETWEEN :start_date AND :end_date)
        ORDER BY total_revenue DESC
    """)
    
    try:
        result = db.execute(
            query,
            {
                "start_date": date_range.start_date if date_range else None,
                "end_date": date_range.end_date if date_range else None
            }
        )
        
        return [
            StylistPerformance(
                stylist_id=row.stylist_id,
                stylist_name=row.stylist_name,
                total_bookings=row.total_bookings,
                completed_bookings=row.completed_bookings,
                cancelled_bookings=row.cancelled_bookings,
                total_revenue=row.total_revenue,
                average_duration=row.average_duration,
                unique_customers=row.unique_customers
            )
            for row in result
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get stylist performance"
        )

def get_service_popularity(
    db: Session,
    date_range: Optional[DateRangeFilter] = None
) -> List[ServicePopularity]:
    """Get service popularity metrics."""
    query = text("""
        SELECT 
            service_id,
            service_name,
            total_bookings,
            completed_bookings,
            total_revenue,
            average_duration,
            unique_customers
        FROM vw_service_popularity
        WHERE (:start_date IS NULL OR booking_date BETWEEN :start_date AND :end_date)
        ORDER BY total_bookings DESC
    """)
    
    try:
        result = db.execute(
            query,
            {
                "start_date": date_range.start_date if date_range else None,
                "end_date": date_range.end_date if date_range else None
            }
        )
        
        return [
            ServicePopularity(
                service_id=row.service_id,
                service_name=row.service_name,
                total_bookings=row.total_bookings,
                completed_bookings=row.completed_bookings,
                total_revenue=row.total_revenue,
                average_duration=row.average_duration,
                unique_customers=row.unique_customers
            )
            for row in result
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get service popularity"
        )

def get_customer_analytics(
    db: Session,
    date_range: Optional[DateRangeFilter] = None
) -> List[CustomerAnalytics]:
    """Get customer analytics metrics."""
    query = text("""
        SELECT 
            user_id,
            customer_name,
            total_bookings,
            completed_bookings,
            cancelled_bookings,
            total_spent,
            average_booking_duration,
            stylists_visited,
            services_used,
            last_booking_date,
            first_booking_date
        FROM vw_customer_analytics
        WHERE (:start_date IS NULL OR booking_date BETWEEN :start_date AND :end_date)
        ORDER BY total_spent DESC
    """)
    
    try:
        result = db.execute(
            query,
            {
                "start_date": date_range.start_date if date_range else None,
                "end_date": date_range.end_date if date_range else None
            }
        )
        
        return [
            CustomerAnalytics(
                user_id=row.user_id,
                customer_name=row.customer_name,
                total_bookings=row.total_bookings,
                completed_bookings=row.completed_bookings,
                cancelled_bookings=row.cancelled_bookings,
                total_spent=row.total_spent,
                average_booking_duration=row.average_booking_duration,
                stylists_visited=row.stylists_visited,
                services_used=row.services_used,
                last_booking_date=row.last_booking_date,
                first_booking_date=row.first_booking_date
            )
            for row in result
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get customer analytics"
        )

def get_daily_analytics(
    db: Session,
    date: datetime
) -> Optional[DailyAnalytics]:
    """Get daily analytics for a specific date."""
    return db.query(DailyAnalytics).filter(
        DailyAnalytics.date == date.date()
    ).first()

def get_monthly_analytics(
    db: Session,
    year: int,
    month: int
) -> Optional[MonthlyAnalytics]:
    """Get monthly analytics for a specific year and month."""
    return db.query(MonthlyAnalytics).filter(
        and_(
            MonthlyAnalytics.year == year,
            MonthlyAnalytics.month == month
        )
    ).first()

def calculate_customer_retention(
    db: Session,
    year: int,
    month: int
) -> float:
    """Calculate customer retention rate for a specific month."""
    # Get the first day of the month
    month_start = datetime(year, month, 1)
    # Get the first day of the previous month
    prev_month_start = (month_start - timedelta(days=1)).replace(day=1)
    
    # Get customers who booked in the previous month
    prev_month_customers = db.query(func.count(func.distinct(Booking.user_id))).filter(
        and_(
            Booking.start_time >= prev_month_start,
            Booking.start_time < month_start,
            Booking.status == "COMPLETED"
        )
    ).scalar()
    
    if not prev_month_customers:
        return 0.0
    
    # Get customers who booked in both months
    returning_customers = db.query(func.count(func.distinct(Booking.user_id))).filter(
        and_(
            Booking.start_time >= month_start,
            Booking.start_time < (month_start + timedelta(days=32)).replace(day=1),
            Booking.status == "COMPLETED",
            Booking.user_id.in_(
                db.query(Booking.user_id).filter(
                    and_(
                        Booking.start_time >= prev_month_start,
                        Booking.start_time < month_start,
                        Booking.status == "COMPLETED"
                    )
                )
            )
        )
    ).scalar()
    
    return (returning_customers / prev_month_customers) * 100 if prev_month_customers > 0 else 0.0

def update_monthly_analytics(
    db: Session,
    year: int,
    month: int
) -> MonthlyAnalytics:
    """Update monthly analytics for a specific year and month."""
    # Get or create monthly analytics record
    analytics = get_monthly_analytics(db, year, month)
    if not analytics:
        analytics = MonthlyAnalytics(
            year=year,
            month=month
        )
        db.add(analytics)
    
    # Calculate customer retention rate
    retention_rate = calculate_customer_retention(db, year, month)
    analytics.customer_retention_rate = retention_rate
    
    try:
        db.commit()
        db.refresh(analytics)
        return analytics
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update monthly analytics"
        )

def generate_analytics_report(
    db: Session,
    date_range: DateRangeFilter
) -> AnalyticsResponse:
    """Generate a comprehensive analytics report for a date range."""
    try:
        # Get booking statistics
        booking_stats = get_booking_statistics(db, date_range)
        
        # Get stylist performance
        stylist_perf = get_stylist_performance(db, date_range)
        
        # Get service popularity
        service_pop = get_service_popularity(db, date_range)
        
        # Get customer analytics
        customer_analytics = get_customer_analytics(db, date_range)
        
        # Calculate summary metrics
        total_revenue = sum(stat.total_revenue for stat in booking_stats)
        total_bookings = sum(stat.total_bookings for stat in booking_stats)
        completed_bookings = sum(stat.completed_bookings for stat in booking_stats)
        cancelled_bookings = sum(stat.cancelled_bookings for stat in booking_stats)
        unique_customers = len(set(cust.user_id for cust in customer_analytics))
        
        return AnalyticsResponse(
            date_range=date_range,
            total_revenue=total_revenue,
            total_bookings=total_bookings,
            completed_bookings=completed_bookings,
            cancelled_bookings=cancelled_bookings,
            unique_customers=unique_customers,
            booking_statistics=booking_stats,
            stylist_performance=stylist_perf,
            service_popularity=service_pop,
            customer_analytics=customer_analytics
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate analytics report"
        ) 