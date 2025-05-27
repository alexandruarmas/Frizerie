"""
Recurring booking services for handling series of recurring appointments.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import uuid
from dateutil.rrule import rrule, WEEKLY, MONTHLY
from dateutil.relativedelta import relativedelta

from booking.models import (
    Booking, BookingStatus, StylistAvailability,
    RecurringBooking, RecurringBookingStatus
)
from validation.schemas import (
    RecurringBookingCreate, RecurringBookingUpdate,
    RecurringBookingResponse, BookingResponse
)
from users.models import User
from services.models import Service
from notifications import services as notification_services
from booking import optimized_services as booking_services

def create_recurring_bookings(
    db: Session,
    booking_data: RecurringBookingCreate,
    user_id: int
) -> Tuple[Booking, List[Booking]]:
    """Create a series of recurring bookings."""
    # Validate service exists
    service = db.query(Service).filter(Service.id == booking_data.service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Validate stylist if specified
    if booking_data.stylist_id:
        stylist = db.query(User).filter(
            and_(
                User.id == booking_data.stylist_id,
                User.is_stylist == True
            )
        ).first()
        if not stylist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stylist not found"
            )
    
    # Calculate all booking dates
    if booking_data.recurrence_type == "WEEKLY":
        dates = list(rrule(
            WEEKLY,
            dtstart=booking_data.start_date,
            until=booking_data.end_date,
            interval=booking_data.recurrence_interval
        ))
    elif booking_data.recurrence_type == "MONTHLY":
        dates = list(rrule(
            MONTHLY,
            dtstart=booking_data.start_date,
            until=booking_data.end_date,
            interval=booking_data.recurrence_interval
        ))
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid recurrence type"
        )
    
    if not dates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid dates found for the recurrence pattern"
        )
    
    # Create parent booking
    parent_booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user_id,
        stylist_id=booking_data.stylist_id,
        service_id=booking_data.service_id,
        start_time=booking_data.start_date,
        end_time=booking_data.start_date + timedelta(minutes=service.duration_minutes),
        status=BookingStatus.CONFIRMED,
        notes=booking_data.notes,
        is_recurring=True
    )
    
    # Create recurring booking record
    recurring_booking = RecurringBooking(
        id=str(uuid.uuid4()),
        parent_booking_id=parent_booking.id,
        recurrence_type=booking_data.recurrence_type,
        recurrence_interval=booking_data.recurrence_interval,
        start_date=booking_data.start_date,
        end_date=booking_data.end_date,
        status=RecurringBookingStatus.ACTIVE
    )
    
    # Create child bookings
    child_bookings = []
    for date in dates[1:]:  # Skip first date as it's the parent booking
        # Calculate booking time
        booking_time = datetime.combine(
            date.date(),
            booking_data.start_date.time()
        )
        
        # Validate booking time
        conflicts = booking_services.validate_booking_time(
            db,
            booking_data.stylist_id,
            booking_time,
            booking_time + timedelta(minutes=service.duration_minutes)
        )
        
        if conflicts:
            # Skip this date if there's a conflict
            continue
        
        # Create child booking
        child_booking = Booking(
            id=str(uuid.uuid4()),
            user_id=user_id,
            stylist_id=booking_data.stylist_id,
            service_id=booking_data.service_id,
            start_time=booking_time,
            end_time=booking_time + timedelta(minutes=service.duration_minutes),
            status=BookingStatus.CONFIRMED,
            notes=booking_data.notes,
            is_recurring=True,
            parent_booking_id=parent_booking.id
        )
        child_bookings.append(child_booking)
    
    try:
        # Save all bookings
        db.add(parent_booking)
        db.add(recurring_booking)
        for booking in child_bookings:
            db.add(booking)
        
        db.commit()
        db.refresh(parent_booking)
        for booking in child_bookings:
            db.refresh(booking)
        
        # Create notification for the recurring booking series
        notification_services.create_notification(
            db=db,
            user_id=user_id,
            type="RECURRING_BOOKING_CREATED",
            title="Recurring Bookings Created",
            message=f"Your recurring bookings for {service.name} have been created",
            data={
                "parent_booking_id": parent_booking.id,
                "recurring_booking_id": recurring_booking.id,
                "total_bookings": len(child_bookings) + 1
            }
        )
        
        return parent_booking, child_bookings
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create recurring bookings"
        )

def update_recurring_bookings(
    db: Session,
    recurring_booking_id: str,
    booking_data: RecurringBookingUpdate,
    user_id: int
) -> Tuple[Booking, List[Booking]]:
    """Update a series of recurring bookings."""
    # Get recurring booking record
    recurring_booking = db.query(RecurringBooking).filter(
        RecurringBooking.id == recurring_booking_id
    ).first()
    
    if not recurring_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring booking not found"
        )
    
    # Get parent booking
    parent_booking = db.query(Booking).filter(
        Booking.id == recurring_booking.parent_booking_id
    ).first()
    
    if not parent_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent booking not found"
        )
    
    # Check if user has permission to update the bookings
    if parent_booking.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update these bookings"
        )
    
    # Get all child bookings
    child_bookings = db.query(Booking).filter(
        and_(
            Booking.parent_booking_id == parent_booking.id,
            Booking.id != parent_booking.id
        )
    ).all()
    
    # Cancel all future bookings
    current_time = datetime.utcnow()
    for booking in [parent_booking] + child_bookings:
        if booking.start_time > current_time:
            booking.status = BookingStatus.CANCELLED
    
    # Create new recurring booking series
    new_parent, new_children = create_recurring_bookings(
        db,
        RecurringBookingCreate(
            service_id=parent_booking.service_id,
            stylist_id=parent_booking.stylist_id,
            start_date=booking_data.start_date or parent_booking.start_time,
            end_date=booking_data.end_date or recurring_booking.end_date,
            recurrence_type=booking_data.recurrence_type or recurring_booking.recurrence_type,
            recurrence_interval=booking_data.recurrence_interval or recurring_booking.recurrence_interval,
            notes=booking_data.notes or parent_booking.notes
        ),
        user_id
    )
    
    # Update recurring booking record
    recurring_booking.status = RecurringBookingStatus.UPDATED
    recurring_booking.updated_at = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(new_parent)
        for booking in new_children:
            db.refresh(booking)
        
        return new_parent, new_children
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update recurring bookings"
        )

def cancel_recurring_bookings(
    db: Session,
    recurring_booking_id: str,
    user_id: int,
    cancel_future_only: bool = True
) -> Tuple[Booking, List[Booking]]:
    """Cancel a series of recurring bookings."""
    # Get recurring booking record
    recurring_booking = db.query(RecurringBooking).filter(
        RecurringBooking.id == recurring_booking_id
    ).first()
    
    if not recurring_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring booking not found"
        )
    
    # Get parent booking
    parent_booking = db.query(Booking).filter(
        Booking.id == recurring_booking.parent_booking_id
    ).first()
    
    if not parent_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent booking not found"
        )
    
    # Check if user has permission to cancel the bookings
    if parent_booking.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel these bookings"
        )
    
    # Get all child bookings
    child_bookings = db.query(Booking).filter(
        and_(
            Booking.parent_booking_id == parent_booking.id,
            Booking.id != parent_booking.id
        )
    ).all()
    
    # Cancel bookings
    current_time = datetime.utcnow()
    cancelled_bookings = []
    
    for booking in [parent_booking] + child_bookings:
        if not cancel_future_only or booking.start_time > current_time:
            booking.status = BookingStatus.CANCELLED
            cancelled_bookings.append(booking)
    
    # Update recurring booking record
    recurring_booking.status = RecurringBookingStatus.CANCELLED
    recurring_booking.updated_at = datetime.utcnow()
    
    try:
        db.commit()
        for booking in cancelled_bookings:
            db.refresh(booking)
        
        # Create notification for the cancellation
        notification_services.create_notification(
            db=db,
            user_id=user_id,
            type="RECURRING_BOOKING_CANCELLED",
            title="Recurring Bookings Cancelled",
            message="Your recurring bookings have been cancelled",
            data={
                "parent_booking_id": parent_booking.id,
                "recurring_booking_id": recurring_booking.id,
                "cancelled_count": len(cancelled_bookings)
            }
        )
        
        return parent_booking, child_bookings
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel recurring bookings"
        )

def get_recurring_bookings(
    db: Session,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[RecurringBooking]:
    """Get recurring bookings with optional filtering."""
    query = db.query(RecurringBooking).join(
        Booking,
        Booking.id == RecurringBooking.parent_booking_id
    )
    
    if user_id:
        query = query.filter(Booking.user_id == user_id)
    
    if status:
        query = query.filter(RecurringBooking.status == status)
    
    return query.order_by(
        RecurringBooking.created_at.desc()
    ).offset(skip).limit(limit).all()

def get_recurring_booking_details(
    db: Session,
    recurring_booking_id: str,
    user_id: int
) -> Tuple[RecurringBooking, Booking, List[Booking]]:
    """Get detailed information about a recurring booking series."""
    # Get recurring booking record
    recurring_booking = db.query(RecurringBooking).filter(
        RecurringBooking.id == recurring_booking_id
    ).first()
    
    if not recurring_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring booking not found"
        )
    
    # Get parent booking
    parent_booking = db.query(Booking).filter(
        Booking.id == recurring_booking.parent_booking_id
    ).first()
    
    if not parent_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent booking not found"
        )
    
    # Check if user has permission to view the bookings
    if parent_booking.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these bookings"
        )
    
    # Get all child bookings
    child_bookings = db.query(Booking).filter(
        and_(
            Booking.parent_booking_id == parent_booking.id,
            Booking.id != parent_booking.id
        )
    ).order_by(Booking.start_time).all()
    
    return recurring_booking, parent_booking, child_bookings 