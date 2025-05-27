from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from config.database import get_db
from auth.dependencies import get_current_admin
from users.models import User
from analytics.schemas import (
    AnalyticsEventCreate,
    AnalyticsEventResponse,
    TimeRange,
    AnalyticsSummary,
    RevenueAnalytics,
    BookingAnalytics,
    UserAnalytics,
    RealTimeMetrics,
    CustomReportRequest,
    CustomReportResponse,
    ExportRequest,
    ExportResponse,
    ExportFormat,
    DashboardConfig,
    WidgetConfig,
    DashboardCreate,
    DashboardUpdate,
    Dashboard as DashboardSchema,
    DashboardWidget as DashboardWidgetSchema,
    VisualizationData,
    WidgetData
)
from analytics import services as analytics_services
from analytics.services import (
    get_analytics_summary,
    get_revenue_analytics,
    get_booking_analytics,
    get_user_analytics,
    get_realtime_metrics,
    generate_custom_report,
    export_report,
    create_dashboard,
    update_dashboard,
    get_dashboard,
    list_dashboards,
    delete_dashboard,
    get_widget_data
)
from validation.schemas import (
    DateRangeFilter, AnalyticsResponse,
    BookingStatistics, StylistPerformance,
    ServicePopularity, CustomerAnalytics
)

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    dependencies=[Depends(get_current_admin)]
)

@router.post("/events", response_model=AnalyticsEventResponse)
def track_analytics_event(
    event_data: AnalyticsEventCreate,
    db: Session = Depends(get_db)
):
    """
    Track an analytics event.
    """
    return services.track_event(db, event_data)

@router.get("/events", response_model=List[AnalyticsEventResponse])
def get_analytics_events(
    event_type: Optional[str] = None,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Get analytics events with optional filtering.
    Only accessible by admin users.
    """
    return services.get_events(
        db,
        event_type=event_type,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )

@router.get("/summary", response_model=AnalyticsSummary)
def get_analytics_summary(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Get overall analytics summary for the specified time period.
    Only accessible by admin users.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    time_range = TimeRange(start_date=start_date, end_date=end_date)
    return services.get_summary(db, time_range)

@router.get("/revenue", response_model=RevenueAnalytics)
def get_revenue_analytics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Get revenue analytics for the specified time period.
    Only accessible by admin users.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    time_range = TimeRange(start_date=start_date, end_date=end_date)
    return services.get_revenue_analytics(db, time_range)

@router.get("/bookings", response_model=BookingAnalytics)
def get_booking_analytics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Get booking analytics for the specified time period.
    Only accessible by admin users.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    time_range = TimeRange(start_date=start_date, end_date=end_date)
    return services.get_booking_analytics(db, time_range)

@router.get("/users", response_model=UserAnalytics)
def get_user_analytics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Get user analytics for the specified time period.
    Only accessible by admin users.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    time_range = TimeRange(start_date=start_date, end_date=end_date)
    return services.get_user_analytics(db, time_range)

@router.get("/realtime", response_model=RealTimeMetrics)
async def get_realtime_analytics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """Get real-time analytics metrics."""
    return await get_realtime_metrics(db)

@router.post("/reports/custom", response_model=CustomReportResponse)
async def create_custom_report(
    request: CustomReportRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """Generate a custom analytics report."""
    try:
        return await generate_custom_report(db, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate report")

@router.post("/reports/export", response_model=ExportResponse)
async def export_analytics_report(
    request: ExportRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """Export analytics data in the specified format."""
    try:
        return await export_report(db, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to export report")

@router.get("/dashboard/config", response_model=DashboardConfig)
async def get_dashboard_config(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """Get the current dashboard configuration."""
    # This would typically come from a database
    # For now, return a default configuration
    return DashboardConfig(
        layout=[
            {"widget_id": "revenue", "x": 0, "y": 0, "w": 6, "h": 4},
            {"widget_id": "bookings", "x": 6, "y": 0, "w": 6, "h": 4},
            {"widget_id": "users", "x": 0, "y": 4, "w": 6, "h": 4},
            {"widget_id": "services", "x": 6, "y": 4, "w": 6, "h": 4}
        ],
        refresh_interval=60,
        time_range={
            "start": (datetime.utcnow() - timedelta(days=30)).isoformat(),
            "end": datetime.utcnow().isoformat()
        }
    )

@router.put("/dashboard/config", response_model=DashboardConfig)
async def update_dashboard_config(
    config: DashboardConfig,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """Update the dashboard configuration."""
    # This would typically save to a database
    # For now, just return the updated config
    return config

@router.get("/widgets", response_model=List[WidgetConfig])
async def get_available_widgets(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """Get available widget configurations."""
    # This would typically come from a database
    # For now, return a list of predefined widgets
    return [
        WidgetConfig(
            type="revenue",
            title="Revenue Overview",
            metrics=["total_revenue", "average_order_value"],
            dimensions=["date"],
            visualization="line_chart",
            refresh_interval=300
        ),
        WidgetConfig(
            type="bookings",
            title="Booking Analytics",
            metrics=["total_bookings", "booking_rate"],
            dimensions=["date", "service"],
            visualization="bar_chart",
            refresh_interval=300
        ),
        WidgetConfig(
            type="users",
            title="User Activity",
            metrics=["active_users", "new_users"],
            dimensions=["date"],
            visualization="area_chart",
            refresh_interval=300
        ),
        WidgetConfig(
            type="services",
            title="Popular Services",
            metrics=["booking_count"],
            dimensions=["service"],
            visualization="pie_chart",
            refresh_interval=300
        )
    ]

@router.post("/dashboards", response_model=DashboardSchema)
async def create_new_dashboard(
    dashboard_data: DashboardCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """Create a new analytics dashboard."""
    try:
        return await create_dashboard(db, dashboard_data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create dashboard")

@router.get("/dashboards", response_model=List[DashboardSchema])
async def get_user_dashboards(
    include_public: bool = True,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """List dashboards accessible to the current user."""
    try:
        return await list_dashboards(db, current_user.id, include_public)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to list dashboards")

@router.get("/dashboards/{dashboard_id}", response_model=DashboardSchema)
async def get_dashboard_by_id(
    dashboard_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """Get a specific dashboard by ID."""
    try:
        return await get_dashboard(db, dashboard_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get dashboard")

@router.put("/dashboards/{dashboard_id}", response_model=DashboardSchema)
async def update_existing_dashboard(
    dashboard_id: str,
    dashboard_data: DashboardUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """Update an existing dashboard."""
    try:
        return await update_dashboard(db, dashboard_id, dashboard_data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update dashboard")

@router.delete("/dashboards/{dashboard_id}")
async def delete_existing_dashboard(
    dashboard_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """Delete a dashboard."""
    try:
        await delete_dashboard(db, dashboard_id, current_user.id)
        return {"message": "Dashboard deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete dashboard")

@router.get("/widgets/{widget_id}/data", response_model=WidgetData)
async def get_widget_visualization_data(
    widget_id: str,
    force_refresh: bool = False,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """Get visualization data for a widget."""
    try:
        return await get_widget_data(db, widget_id, force_refresh)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get widget data")

@router.get("/booking-statistics", response_model=List[BookingStatistics])
async def get_booking_statistics(
    date_range: DateRangeFilter,
    db: Session = Depends(get_db)
):
    """Get booking statistics for a date range."""
    return analytics_services.get_booking_statistics(db, date_range)

@router.get("/stylist-performance", response_model=List[StylistPerformance])
async def get_stylist_performance(
    date_range: Optional[DateRangeFilter] = None,
    db: Session = Depends(get_db)
):
    """Get stylist performance metrics."""
    return analytics_services.get_stylist_performance(db, date_range)

@router.get("/service-popularity", response_model=List[ServicePopularity])
async def get_service_popularity(
    date_range: Optional[DateRangeFilter] = None,
    db: Session = Depends(get_db)
):
    """Get service popularity metrics."""
    return analytics_services.get_service_popularity(db, date_range)

@router.get("/customer-analytics", response_model=List[CustomerAnalytics])
async def get_customer_analytics(
    date_range: Optional[DateRangeFilter] = None,
    db: Session = Depends(get_db)
):
    """Get customer analytics metrics."""
    return analytics_services.get_customer_analytics(db, date_range)

@router.get("/daily-analytics/{date}")
async def get_daily_analytics(
    date: datetime,
    db: Session = Depends(get_db)
):
    """Get daily analytics for a specific date."""
    analytics = analytics_services.get_daily_analytics(db, date)
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Daily analytics not found for the specified date"
        )
    return analytics

@router.get("/monthly-analytics/{year}/{month}")
async def get_monthly_analytics(
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    """Get monthly analytics for a specific year and month."""
    analytics = analytics_services.get_monthly_analytics(db, year, month)
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monthly analytics not found for the specified period"
        )
    return analytics

@router.post("/monthly-analytics/{year}/{month}/update")
async def update_monthly_analytics(
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    """Update monthly analytics for a specific year and month."""
    return analytics_services.update_monthly_analytics(db, year, month)

@router.post("/report", response_model=AnalyticsResponse)
async def generate_analytics_report(
    date_range: DateRangeFilter,
    db: Session = Depends(get_db)
):
    """Generate a comprehensive analytics report for a date range."""
    return analytics_services.generate_analytics_report(db, date_range)

@router.post("/track-event")
async def track_analytics_event(
    event_type: str,
    event_data: dict,
    user_id: Optional[int] = None,
    stylist_id: Optional[int] = None,
    service_id: Optional[int] = None,
    booking_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Track an analytics event."""
    return analytics_services.track_event(
        db=db,
        event_type=event_type,
        event_data=event_data,
        user_id=user_id,
        stylist_id=stylist_id,
        service_id=service_id,
        booking_id=booking_id
    ) 