from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from config.database import Base
from users.models import User

class EventType(str, Enum):
    PAGE_VIEW = "page_view"
    BOOKING_CREATED = "booking_created"
    BOOKING_CANCELLED = "booking_cancelled"
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_FAILED = "payment_failed"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTERED = "user_registered"
    SERVICE_VIEWED = "service_viewed"
    ERROR = "error"

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    stylist_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)
    booking_id = Column(String, nullable=True)
    event_type = Column(SQLEnum(EventType), nullable=False)
    properties = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="analytics_events", foreign_keys=[user_id])
    stylist = relationship("User", back_populates="stylist_analytics_events", foreign_keys=[stylist_id])
    service = relationship("Service", back_populates="analytics_events")
    
    def __repr__(self):
        return f"<AnalyticsEvent {self.id}: {self.event_type}>"

class Dashboard(Base):
    __tablename__ = "dashboards"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False)
    layout = Column(JSON, nullable=False)
    refresh_interval = Column(Integer, default=300)
    time_range_start = Column(DateTime, nullable=False)
    time_range_end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="dashboards")
    widgets = relationship("DashboardWidget", back_populates="dashboard", cascade="all, delete-orphan")

class DashboardWidget(Base):
    __tablename__ = "dashboard_widgets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_id = Column(String, ForeignKey("dashboards.id"), nullable=False)
    type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    config = Column(JSON, nullable=False)
    data_source = Column(String, nullable=False)
    refresh_interval = Column(Integer, default=300)
    position = Column(JSON, nullable=False)  # {x, y, w, h}
    filters = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    dashboard = relationship("Dashboard", back_populates="widgets")
    data_cache = relationship("WidgetDataCache", back_populates="widget", cascade="all, delete-orphan")

class WidgetDataCache(Base):
    __tablename__ = "widget_data_cache"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    widget_id = Column(String, ForeignKey("dashboard_widgets.id"), nullable=False)
    data = Column(JSON, nullable=False)
    last_updated = Column(DateTime, server_default=func.now())
    next_update = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    widget = relationship("DashboardWidget", back_populates="data_cache")

# Add relationship to User model
User.dashboards = relationship("Dashboard", back_populates="owner")

class DailyAnalytics(Base):
    __tablename__ = "daily_analytics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, unique=True)
    total_bookings = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    new_users = Column(Integer, default=0)
    cancellations = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<DailyAnalytics {self.date}: bookings={self.total_bookings}, revenue={self.total_revenue}>"

class MonthlyAnalytics(Base):
    __tablename__ = "monthly_analytics"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    total_bookings = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    new_users = Column(Integer, default=0)
    cancellations = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<MonthlyAnalytics {self.year}-{self.month}: bookings={self.total_bookings}, revenue={self.total_revenue}>" 