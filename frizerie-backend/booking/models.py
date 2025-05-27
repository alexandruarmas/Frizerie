from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Float, Enum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
import enum

class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
    WAITLISTED = "waitlisted"

class RecurrenceType(str, enum.Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stylist_id = Column(Integer, ForeignKey("stylists.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    notes = Column(String(500))
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # New fields for enhanced booking
    recurrence_type = Column(Enum(RecurrenceType), default=RecurrenceType.NONE, nullable=False)
    recurrence_end_date = Column(DateTime, nullable=True)
    recurrence_pattern = Column(JSON, nullable=True)  # For custom recurrence patterns
    parent_booking_id = Column(String(36), ForeignKey("bookings.id"), nullable=True)  # For recurring bookings
    calendar_event_id = Column(String(100), nullable=True)  # For external calendar integration
    reminder_sent = Column(Boolean, default=False, nullable=False)
    cancellation_reason = Column(String(500), nullable=True)
    cancellation_time = Column(DateTime, nullable=True)
    no_show_count = Column(Integer, default=0, nullable=False)
    last_modified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="bookings")
    stylist = relationship("Stylist", back_populates="bookings")
    service = relationship("Service", back_populates="bookings")
    parent_booking = relationship("Booking", remote_side=[id], backref="recurring_bookings")
    last_modified_user = relationship("User", foreign_keys=[last_modified_by])
    waitlist_entries = relationship("WaitlistEntry", back_populates="booking", cascade="all, delete-orphan")
    conflicts = relationship("BookingConflict", back_populates="booking", cascade="all, delete-orphan")
    redemption = relationship("LoyaltyRedemption", back_populates="booking", uselist=False)
    payment = relationship("Payment", back_populates="booking", uselist=False)

class WaitlistEntry(Base):
    __tablename__ = "waitlist_entries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_id = Column(String(36), ForeignKey("bookings.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    preferred_stylist_id = Column(Integer, ForeignKey("stylists.id"), nullable=True)
    preferred_date_range = Column(JSON, nullable=True)  # Store date range preferences
    status = Column(Enum(BookingStatus), default=BookingStatus.WAITLISTED, nullable=False)
    priority = Column(Integer, default=0, nullable=False)  # Higher number = higher priority
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    notification_sent = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    booking = relationship("Booking", back_populates="waitlist_entries")
    user = relationship("User", back_populates="waitlist_entries")
    service = relationship("Service")
    preferred_stylist = relationship("Stylist")

class BookingConflict(Base):
    __tablename__ = "booking_conflicts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_id = Column(String(36), ForeignKey("bookings.id"), nullable=False)
    conflict_type = Column(String(50), nullable=False)  # e.g., "double_booking", "stylist_unavailable"
    conflict_details = Column(JSON, nullable=True)
    resolved = Column(Boolean, default=False, nullable=False)
    resolution_notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    booking = relationship("Booking", back_populates="conflicts")

class StylistAvailability(Base):
    __tablename__ = "stylist_availability"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    stylist_id = Column(Integer, ForeignKey("stylists.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0-6 for Monday-Sunday
    start_time = Column(String(5), nullable=False)  # Format: "HH:MM"
    end_time = Column(String(5), nullable=False)  # Format: "HH:MM"
    is_available = Column(Boolean, default=True, nullable=False)
    break_start = Column(String(5), nullable=True)  # Format: "HH:MM"
    break_end = Column(String(5), nullable=True)  # Format: "HH:MM"
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    stylist = relationship("Stylist", back_populates="availability")

class StylistTimeOff(Base):
    __tablename__ = "stylist_time_off"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    stylist_id = Column(Integer, ForeignKey("stylists.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    reason = Column(String(500), nullable=True)
    is_approved = Column(Boolean, default=False, nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    stylist = relationship("Stylist", back_populates="time_off")
    approver = relationship("User", foreign_keys=[approved_by])

# Update existing relationships in User and Stylist models
from users.models import User
from stylists.models import Stylist

User.bookings = relationship("Booking", foreign_keys=[Booking.user_id], back_populates="user")
User.waitlist_entries = relationship("WaitlistEntry", back_populates="user")

Stylist.bookings = relationship("Booking", back_populates="stylist")
Stylist.availability = relationship("StylistAvailability", back_populates="stylist", cascade="all, delete-orphan")
Stylist.time_off = relationship("StylistTimeOff", back_populates="stylist", cascade="all, delete-orphan") 