from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Time, func, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from config.database import Base
from users.models import User

class Service(Base):
    """Service model for different types of services offered."""
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey("service_categories.id"), nullable=True) # New foreign key to category
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    bookings = relationship("Booking", back_populates="service")
    category = relationship("ServiceCategory", back_populates="services") # New relationship to category
    analytics_events = relationship("AnalyticsEvent", back_populates="service")

    def __repr__(self):
        return f"<Service {self.name}>"

class ServiceCategory(Base):
    """Model for service categories."""
    __tablename__ = "service_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    services = relationship("Service", back_populates="category")

    def __repr__(self):
        return f"<ServiceCategory {self.name}>" 