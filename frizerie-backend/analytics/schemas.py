from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from .models import EventType
from enum import Enum

class TimeRange(BaseModel):
    start_date: datetime
    end_date: datetime

class AnalyticsEventBase(BaseModel):
    event_type: EventType
    properties: Dict[str, Any] = Field(default_factory=dict)

class AnalyticsEventCreate(AnalyticsEventBase):
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class AnalyticsEventResponse(AnalyticsEventBase):
    id: int
    user_id: Optional[int]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class AnalyticsSummary(BaseModel):
    total_users: int
    total_bookings: int
    total_revenue: float
    average_booking_value: float
    booking_completion_rate: float
    popular_services: List[Dict[str, Any]]
    revenue_by_period: List[Dict[str, Any]]
    bookings_by_period: List[Dict[str, Any]]
    user_growth: List[Dict[str, Any]]

class RevenueAnalytics(BaseModel):
    total_revenue: float
    revenue_by_period: List[Dict[str, Any]]
    revenue_by_service: List[Dict[str, Any]]
    average_order_value: float
    refund_rate: float

class BookingAnalytics(BaseModel):
    total_bookings: int
    bookings_by_period: List[Dict[str, Any]]
    bookings_by_service: List[Dict[str, Any]]
    completion_rate: float
    cancellation_rate: float
    average_booking_duration: float

class UserAnalytics(BaseModel):
    total_users: int
    active_users: int
    new_users_by_period: List[Dict[str, Any]]
    user_retention_rate: float
    average_session_duration: float
    popular_pages: List[Dict[str, Any]]

class RealTimeMetrics(BaseModel):
    active_users: int
    current_bookings: int
    pending_payments: int
    revenue_today: float
    bookings_today: int
    popular_services_now: List[Dict[str, Any]]
    recent_events: List[Dict[str, Any]]

class CustomReportRequest(BaseModel):
    metrics: List[str]
    dimensions: List[str]
    filters: Dict[str, Any] = Field(default_factory=dict)
    time_range: TimeRange
    group_by: Optional[List[str]] = None
    sort_by: Optional[List[str]] = None
    limit: Optional[int] = None

class CustomReportResponse(BaseModel):
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    total_rows: int
    execution_time: float

class ExportFormat(str, Enum):
    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"

class ExportRequest(BaseModel):
    report_type: str
    time_range: TimeRange
    format: ExportFormat
    filters: Dict[str, Any] = Field(default_factory=dict)
    include_metadata: bool = True

class ExportResponse(BaseModel):
    download_url: str
    expires_at: datetime
    file_size: int
    format: ExportFormat

class DashboardConfig(BaseModel):
    widgets: List[Dict[str, Any]]
    layout: Dict[str, Any]
    refresh_interval: int = 300  # seconds
    time_range: TimeRange

class WidgetConfig(BaseModel):
    type: str
    title: str
    metrics: List[str]
    dimensions: Optional[List[str]] = None
    filters: Dict[str, Any] = Field(default_factory=dict)
    visualization: Dict[str, Any]

class VisualizationType(str, Enum):
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    AREA_CHART = "area_chart"
    TABLE = "table"
    GAUGE = "gauge"
    HEATMAP = "heatmap"
    SCATTER_PLOT = "scatter_plot"

class ChartConfig(BaseModel):
    type: VisualizationType
    title: str
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    color_by: Optional[str] = None
    aggregation: Optional[str] = None
    show_legend: bool = True
    show_grid: bool = True
    show_tooltips: bool = True
    animation: bool = True
    height: int = 400
    width: Optional[int] = None

class DashboardWidget(BaseModel):
    id: str
    type: str
    title: str
    config: ChartConfig
    data_source: str
    refresh_interval: int = 300
    position: Dict[str, int]  # x, y, w, h
    filters: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

class Dashboard(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    widgets: List[DashboardWidget]
    layout: List[Dict[str, Any]]
    owner_id: int
    is_public: bool = False
    created_at: datetime
    updated_at: datetime
    refresh_interval: int = 300
    time_range: TimeRange

class DashboardCreate(BaseModel):
    name: str
    description: Optional[str] = None
    widgets: List[DashboardWidget]
    layout: List[Dict[str, Any]]
    is_public: bool = False
    refresh_interval: int = 300
    time_range: TimeRange

class DashboardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    widgets: Optional[List[DashboardWidget]] = None
    layout: Optional[List[Dict[str, Any]]] = None
    is_public: Optional[bool] = None
    refresh_interval: Optional[int] = None
    time_range: Optional[TimeRange] = None

class VisualizationData(BaseModel):
    labels: List[str]
    datasets: List[Dict[str, Any]]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WidgetData(BaseModel):
    widget_id: str
    data: VisualizationData
    last_updated: datetime
    next_update: datetime 