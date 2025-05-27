"""
Optimized booking services that use the real availability system.
This replaces the mock implementation with proper database queries and validation.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import uuid
from dateutil.parser import parse

from booking.models import (
    Booking, BookingStatus, StylistAvailability, StylistTimeOff,
    WaitlistEntry, BookingConflict
)
from validation.schemas import (
    BookingCreate, BookingUpdate, BookingResponse,
    WaitlistEntryCreate, WaitlistEntryUpdate,
    StylistAvailabilityCreate, StylistTimeOffCreate,
    BookingSearchParams, BookingAvailabilityParams,
    TimeSlotResponse
)
from users.models import User
from stylists.models import Stylist
from services.models import Service
from notifications import services as notification_services

def get_stylist_availability(
    db: Session,
    stylist_id: int,
    date: datetime
) -> Optional[StylistAvailability]:
    """Get stylist's availability for a specific date."""
    day_of_week = date.weekday()
    return db.query(StylistAvailability).filter(
        and_(
            StylistAvailability.stylist_id == stylist_id,
            StylistAvailability.day_of_week == day_of_week,
            StylistAvailability.is_available == True
        )
    ).first()

def check_stylist_time_off(
    db: Session,
    stylist_id: int,
    start_time: datetime,
    end_time: datetime
) -> Optional[StylistTimeOff]:
    """Check if stylist has approved time off during the given period."""
    return db.query(StylistTimeOff).filter(
        and_(
            StylistTimeOff.stylist_id == stylist_id,
            StylistTimeOff.is_approved == True,
            or_(
                and_(
                    StylistTimeOff.start_date <= start_time,
                    StylistTimeOff.end_date >= start_time
                ),
                and_(
                    StylistTimeOff.start_date <= end_time,
                    StylistTimeOff.end_date >= end_time
                )
            )
        )
    ).first()

def get_existing_bookings(
    db: Session,
    stylist_id: int,
    start_time: datetime,
    end_time: datetime,
    exclude_booking_id: Optional[str] = None
) -> List[Booking]:
    """Get all existing bookings that overlap with the given time period."""
    query = db.query(Booking).filter(
        and_(
            Booking.stylist_id == stylist_id,
            Booking.status != BookingStatus.CANCELLED,
            or_(
                and_(Booking.start_time >= start_time, Booking.start_time < end_time),
                and_(Booking.end_time > start_time, Booking.end_time <= end_time),
                and_(Booking.start_time <= start_time, Booking.end_time >= end_time)
            )
        )
    )
    
    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)
    
    return query.all()

def validate_booking_time(
    db: Session,
    stylist_id: int,
    start_time: datetime,
    end_time: datetime,
    exclude_booking_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Validate if a booking can be made at the given time."""
    conflicts = []
    
    # Check stylist availability
    availability = get_stylist_availability(db, stylist_id, start_time)
    if not availability:
        conflicts.append({
            "type": "stylist_unavailable",
            "details": "Stylist is not available on this day"
        })
        return conflicts
    
    # Convert availability times to datetime for comparison
    avail_start = parse(f"{start_time.strftime('%Y-%m-%d')} {availability.start_time}")
    avail_end = parse(f"{start_time.strftime('%Y-%m-%d')} {availability.end_time}")
    
    # Check if booking is within stylist's available hours
    if start_time < avail_start or end_time > avail_end:
        conflicts.append({
            "type": "outside_availability",
            "details": f"Booking must be between {availability.start_time} and {availability.end_time}"
        })
        return conflicts
    
    # Check for breaks
    if availability.break_start and availability.break_end:
        break_start = parse(f"{start_time.strftime('%Y-%m-%d')} {availability.break_start}")
        break_end = parse(f"{start_time.strftime('%Y-%m-%d')} {availability.break_end}")
        
        if (start_time < break_end and end_time > break_start):
            conflicts.append({
                "type": "break_time",
                "details": f"Booking overlaps with stylist's break time ({availability.break_start}-{availability.break_end})"
            })
            return conflicts
    
    # Check for time off
    time_off = check_stylist_time_off(db, stylist_id, start_time, end_time)
    if time_off:
        conflicts.append({
            "type": "time_off",
            "details": f"Stylist is on time off from {time_off.start_date} to {time_off.end_date}"
        })
        return conflicts
    
    # Check for existing bookings
    existing_bookings = get_existing_bookings(db, stylist_id, start_time, end_time, exclude_booking_id)
    if existing_bookings:
        conflicts.append({
            "type": "double_booking",
            "details": {
                "booking_id": existing_bookings[0].id,
                "message": "Time slot is already booked"
            }
        })
    
    return conflicts

def get_available_slots(
    db: Session,
    params: BookingAvailabilityParams
) -> List[TimeSlotResponse]:
    """Get available time slots for a service and optional stylist."""
    # Get service duration
    service = db.query(Service).filter(Service.id == params.service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    duration = params.duration_minutes or service.duration_minutes
    
    # Get stylists to check
    if params.stylist_id:
        stylists = [db.query(Stylist).filter(Stylist.id == params.stylist_id).first()]
        if not stylists[0]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stylist not found"
            )
    else:
        stylists = db.query(Stylist).all()
    
    available_slots = []
    current_time = params.start_date
    
    while current_time < params.end_date:
        for stylist in stylists:
            # Skip if stylist is not available for this day
            availability = get_stylist_availability(db, stylist.id, current_time)
            if not availability:
                continue
            
            # Convert availability times to datetime
            avail_start = parse(f"{current_time.strftime('%Y-%m-%d')} {availability.start_time}")
            avail_end = parse(f"{current_time.strftime('%Y-%m-%d')} {availability.end_time}")
            
            # Skip if current time is outside availability
            if current_time < avail_start or current_time + timedelta(minutes=duration) > avail_end:
                continue
            
            # Check for breaks
            if availability.break_start and availability.break_end:
                break_start = parse(f"{current_time.strftime('%Y-%m-%d')} {availability.break_start}")
                break_end = parse(f"{current_time.strftime('%Y-%m-%d')} {availability.break_end}")
                
                if (current_time < break_end and current_time + timedelta(minutes=duration) > break_start):
                    continue
            
            # Check for time off
            if check_stylist_time_off(db, stylist.id, current_time, current_time + timedelta(minutes=duration)):
                continue
            
            # Check for existing bookings
            conflicts = validate_booking_time(
                db,
                stylist.id,
                current_time,
                current_time + timedelta(minutes=duration)
            )
            
            slot = TimeSlotResponse(
                start_time=current_time,
                end_time=current_time + timedelta(minutes=duration),
                stylist_id=stylist.id,
                is_available=len(conflicts) == 0,
                conflicting_bookings=[
                    BookingResponse.from_orm(booking)
                    for conflict in conflicts
                    if conflict["type"] == "double_booking"
                    for booking in [db.query(Booking).filter(
                        Booking.id == conflict["details"]["booking_id"]
                    ).first()]
                    if booking
                ] if conflicts else None
            )
            
            available_slots.append(slot)
        
        # Move to next time slot (30-minute intervals)
        current_time += timedelta(minutes=30)
    
    return available_slots

def create_booking(
    db: Session,
    booking_data: BookingCreate,
    user_id: int
) -> Booking:
    """Create a new booking with proper validation."""
    # Get service and calculate end time
    service = db.query(Service).filter(Service.id == booking_data.service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    end_time = booking_data.start_time + timedelta(minutes=service.duration_minutes)
    
    # Validate booking time
    conflicts = validate_booking_time(
        db,
        booking_data.stylist_id,
        booking_data.start_time,
        end_time
    )
    
    if conflicts:
        conflict = conflicts[0]
        if conflict["type"] == "double_booking":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The selected time slot is already booked"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=conflict["details"]
            )
    
    # Create the booking
    booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user_id,
        stylist_id=booking_data.stylist_id,
        service_id=booking_data.service_id,
        start_time=booking_data.start_time,
        end_time=end_time,
        status=BookingStatus.CONFIRMED,
        notes=booking_data.notes
    )
    
    try:
        db.add(booking)
        db.commit()
        db.refresh(booking)
        
        # Create notification for the booking
        notification_services.create_notification(
            db=db,
            user_id=user_id,
            type="BOOKING_CONFIRMED",
            title="Booking Confirmed",
            message=f"Your booking for {service.name} has been confirmed for {booking_data.start_time.strftime('%Y-%m-%d %H:%M')}",
            data={"booking_id": booking.id}
        )
        
        return booking
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create booking"
        )

def update_booking(
    db: Session,
    booking_id: str,
    booking_data: BookingUpdate,
    user_id: int
) -> Booking:
    """Update an existing booking with proper validation."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check if user has permission to update the booking
    if booking.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this booking"
        )
    
    # If updating time, validate the new time slot
    if booking_data.start_time:
        service = db.query(Service).filter(Service.id == booking.service_id).first()
        end_time = booking_data.start_time + timedelta(minutes=service.duration_minutes)
        
        conflicts = validate_booking_time(
            db,
            booking.stylist_id,
            booking_data.start_time,
            end_time,
            exclude_booking_id=booking.id
        )
        
        if conflicts:
            conflict = conflicts[0]
            if conflict["type"] == "double_booking":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="The selected time slot is already booked"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=conflict["details"]
                )
        
        booking.start_time = booking_data.start_time
        booking.end_time = end_time
    
    # Update other fields
    if booking_data.notes is not None:
        booking.notes = booking_data.notes
    
    try:
        db.commit()
        db.refresh(booking)
        
        # Create notification for the update
        notification_services.create_notification(
            db=db,
            user_id=user_id,
            type="BOOKING_UPDATED",
            title="Booking Updated",
            message=f"Your booking has been updated to {booking.start_time.strftime('%Y-%m-%d %H:%M')}",
            data={"booking_id": booking.id}
        )
        
        return booking
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update booking"
        )

def cancel_booking(
    db: Session,
    booking_id: str,
    user_id: int
) -> Booking:
    """Cancel a booking with proper validation."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check if user has permission to cancel the booking
    if booking.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this booking"
        )
    
    # Check if booking can be cancelled (e.g., not in the past)
    if booking.start_time < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel a booking that has already started"
        )
    
    booking.status = BookingStatus.CANCELLED
    
    try:
        db.commit()
        db.refresh(booking)
        
        # Create notification for the cancellation
        notification_services.create_notification(
            db=db,
            user_id=user_id,
            type="BOOKING_CANCELLED",
            title="Booking Cancelled",
            message="Your booking has been cancelled",
            data={"booking_id": booking.id}
        )
        
        return booking
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel booking"
        ) 