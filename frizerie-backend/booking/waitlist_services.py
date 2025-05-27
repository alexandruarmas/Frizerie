"""
Waitlist management services for handling waitlist entries and notifications.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import uuid

from booking.models import (
    WaitlistEntry, WaitlistNotification, Booking,
    BookingStatus, StylistAvailability
)
from validation.schemas import (
    WaitlistEntryCreate, WaitlistEntryUpdate,
    WaitlistEntryResponse, TimeSlotResponse
)
from users.models import User
from services.models import Service
from notifications import services as notification_services

def create_waitlist_entry(
    db: Session,
    entry_data: WaitlistEntryCreate,
    user_id: int
) -> WaitlistEntry:
    """Create a new waitlist entry."""
    # Validate service exists
    service = db.query(Service).filter(Service.id == entry_data.service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Validate stylist if specified
    if entry_data.stylist_id:
        stylist = db.query(User).filter(
            and_(
                User.id == entry_data.stylist_id,
                User.is_stylist == True
            )
        ).first()
        if not stylist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stylist not found"
            )
    
    # Set expiration (default 7 days from now)
    expires_at = datetime.utcnow() + timedelta(days=7)
    if entry_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=entry_data.expires_in_days)
    
    # Create waitlist entry
    entry = WaitlistEntry(
        id=str(uuid.uuid4()),
        user_id=user_id,
        service_id=entry_data.service_id,
        stylist_id=entry_data.stylist_id,
        preferred_date_start=entry_data.preferred_date_start,
        preferred_date_end=entry_data.preferred_date_end,
        preferred_time_start=entry_data.preferred_time_start,
        preferred_time_end=entry_data.preferred_time_end,
        status="PENDING",
        notes=entry_data.notes,
        expires_at=expires_at
    )
    
    try:
        db.add(entry)
        db.commit()
        db.refresh(entry)
        
        # Create notification for the waitlist entry
        notification_services.create_notification(
            db=db,
            user_id=user_id,
            type="WAITLIST_ENTRY_CREATED",
            title="Waitlist Entry Created",
            message=f"Your waitlist entry for {service.name} has been created",
            data={"waitlist_entry_id": entry.id}
        )
        
        return entry
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create waitlist entry"
        )

def update_waitlist_entry(
    db: Session,
    entry_id: str,
    entry_data: WaitlistEntryUpdate,
    user_id: int
) -> WaitlistEntry:
    """Update an existing waitlist entry."""
    entry = db.query(WaitlistEntry).filter(WaitlistEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waitlist entry not found"
        )
    
    # Check if user has permission to update the entry
    if entry.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this waitlist entry"
        )
    
    # Check if entry can be updated
    if entry.status not in ["PENDING", "NOTIFIED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update waitlist entry with status {entry.status}"
        )
    
    # Update fields
    update_data = entry_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)
    
    try:
        db.commit()
        db.refresh(entry)
        return entry
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update waitlist entry"
        )

def cancel_waitlist_entry(
    db: Session,
    entry_id: str,
    user_id: int
) -> WaitlistEntry:
    """Cancel a waitlist entry."""
    entry = db.query(WaitlistEntry).filter(WaitlistEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waitlist entry not found"
        )
    
    # Check if user has permission to cancel the entry
    if entry.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this waitlist entry"
        )
    
    # Check if entry can be cancelled
    if entry.status not in ["PENDING", "NOTIFIED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel waitlist entry with status {entry.status}"
        )
    
    entry.status = "CANCELLED"
    
    try:
        db.commit()
        db.refresh(entry)
        
        # Create notification for the cancellation
        notification_services.create_notification(
            db=db,
            user_id=user_id,
            type="WAITLIST_ENTRY_CANCELLED",
            title="Waitlist Entry Cancelled",
            message="Your waitlist entry has been cancelled",
            data={"waitlist_entry_id": entry.id}
        )
        
        return entry
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel waitlist entry"
        )

def check_waitlist_availability(
    db: Session,
    entry: WaitlistEntry
) -> Optional[TimeSlotResponse]:
    """Check if a slot becomes available for a waitlist entry."""
    # Get service duration
    service = db.query(Service).filter(Service.id == entry.service_id).first()
    if not service:
        return None
    
    # Get stylists to check
    if entry.stylist_id:
        stylists = [db.query(User).filter(User.id == entry.stylist_id).first()]
    else:
        stylists = db.query(User).filter(User.is_stylist == True).all()
    
    current_time = entry.preferred_date_start
    while current_time < entry.preferred_date_end:
        for stylist in stylists:
            # Skip if stylist is not available for this day
            availability = db.query(StylistAvailability).filter(
                and_(
                    StylistAvailability.stylist_id == stylist.id,
                    StylistAvailability.day_of_week == current_time.weekday(),
                    StylistAvailability.is_available == True
                )
            ).first()
            
            if not availability:
                continue
            
            # Convert availability times to datetime
            avail_start = datetime.strptime(
                f"{current_time.strftime('%Y-%m-%d')} {availability.start_time}",
                "%Y-%m-%d %H:%M"
            )
            avail_end = datetime.strptime(
                f"{current_time.strftime('%Y-%m-%d')} {availability.end_time}",
                "%Y-%m-%d %H:%M"
            )
            
            # Check if time is within preferred time range
            if entry.preferred_time_start and entry.preferred_time_end:
                preferred_start = datetime.strptime(
                    f"{current_time.strftime('%Y-%m-%d')} {entry.preferred_time_start}",
                    "%Y-%m-%d %H:%M"
                )
                preferred_end = datetime.strptime(
                    f"{current_time.strftime('%Y-%m-%d')} {entry.preferred_time_end}",
                    "%Y-%m-%d %H:%M"
                )
                
                if current_time < preferred_start or current_time + timedelta(minutes=service.duration_minutes) > preferred_end:
                    continue
            
            # Check for breaks
            if availability.break_start and availability.break_end:
                break_start = datetime.strptime(
                    f"{current_time.strftime('%Y-%m-%d')} {availability.break_start}",
                    "%Y-%m-%d %H:%M"
                )
                break_end = datetime.strptime(
                    f"{current_time.strftime('%Y-%m-%d')} {availability.break_end}",
                    "%Y-%m-%d %H:%M"
                )
                
                if (current_time < break_end and current_time + timedelta(minutes=service.duration_minutes) > break_start):
                    continue
            
            # Check for existing bookings
            existing_booking = db.query(Booking).filter(
                and_(
                    Booking.stylist_id == stylist.id,
                    Booking.status != BookingStatus.CANCELLED,
                    or_(
                        and_(
                            Booking.start_time >= current_time,
                            Booking.start_time < current_time + timedelta(minutes=service.duration_minutes)
                        ),
                        and_(
                            Booking.end_time > current_time,
                            Booking.end_time <= current_time + timedelta(minutes=service.duration_minutes)
                        ),
                        and_(
                            Booking.start_time <= current_time,
                            Booking.end_time >= current_time + timedelta(minutes=service.duration_minutes)
                        )
                    )
                )
            ).first()
            
            if not existing_booking:
                return TimeSlotResponse(
                    start_time=current_time,
                    end_time=current_time + timedelta(minutes=service.duration_minutes),
                    stylist_id=stylist.id,
                    is_available=True
                )
        
        # Move to next time slot (30-minute intervals)
        current_time += timedelta(minutes=30)
    
    return None

def process_waitlist_entries(db: Session) -> None:
    """Process all pending waitlist entries to check for availability."""
    # Get all pending entries that haven't expired
    entries = db.query(WaitlistEntry).filter(
        and_(
            WaitlistEntry.status == "PENDING",
            WaitlistEntry.expires_at > datetime.utcnow()
        )
    ).all()
    
    for entry in entries:
        # Check if a slot is available
        slot = check_waitlist_availability(db, entry)
        if slot:
            # Update entry status
            entry.status = "NOTIFIED"
            entry.notified_at = datetime.utcnow()
            
            # Create notification
            notification_services.create_notification(
                db=db,
                user_id=entry.user_id,
                type="WAITLIST_SLOT_AVAILABLE",
                title="Slot Available",
                message=f"A slot is available for your waitlist entry at {slot.start_time.strftime('%Y-%m-%d %H:%M')}",
                data={
                    "waitlist_entry_id": entry.id,
                    "slot": slot.dict()
                }
            )
            
            # Create waitlist notification record
            waitlist_notification = WaitlistNotification(
                id=str(uuid.uuid4()),
                waitlist_entry_id=entry.id,
                notification_type="SLOT_AVAILABLE",
                status="SENT"
            )
            db.add(waitlist_notification)
    
    # Update expired entries
    expired_entries = db.query(WaitlistEntry).filter(
        and_(
            WaitlistEntry.status == "PENDING",
            WaitlistEntry.expires_at <= datetime.utcnow()
        )
    ).all()
    
    for entry in expired_entries:
        entry.status = "EXPIRED"
        
        # Create notification
        notification_services.create_notification(
            db=db,
            user_id=entry.user_id,
            type="WAITLIST_ENTRY_EXPIRED",
            title="Waitlist Entry Expired",
            message="Your waitlist entry has expired",
            data={"waitlist_entry_id": entry.id}
        )
        
        # Create waitlist notification record
        waitlist_notification = WaitlistNotification(
            id=str(uuid.uuid4()),
            waitlist_entry_id=entry.id,
            notification_type="EXPIRED",
            status="SENT"
        )
        db.add(waitlist_notification)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process waitlist entries"
        )

def get_waitlist_entries(
    db: Session,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[WaitlistEntry]:
    """Get waitlist entries with optional filtering."""
    query = db.query(WaitlistEntry)
    
    if user_id:
        query = query.filter(WaitlistEntry.user_id == user_id)
    
    if status:
        query = query.filter(WaitlistEntry.status == status)
    
    return query.order_by(
        WaitlistEntry.created_at.desc()
    ).offset(skip).limit(limit).all() 