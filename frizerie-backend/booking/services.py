from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import uuid
import json
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY
from dateutil.parser import parse

from booking.models import (
    Booking, BookingStatus, RecurrenceType,
    WaitlistEntry, BookingConflict,
    StylistAvailability, StylistTimeOff
)
from validation.schemas import (
    BookingCreate, BookingUpdate, BookingResponse,
    WaitlistEntryCreate, WaitlistEntryUpdate,
    StylistAvailabilityCreate, StylistTimeOffCreate,
    RecurringBookingCreate, BookingSearchParams,
    BookingAvailabilityParams, TimeSlotResponse
)
from users.models import User
from stylists.models import Stylist
from services.models import Service
from notifications import services as notification_services
from calendar_integration import services as calendar_services

# Booking Management
def create_booking(db: Session, booking_data: BookingCreate, user_id: int) -> Booking:
    """Create a new booking with validation and conflict checking."""
    # Validate service exists and get duration
    service = db.query(Service).filter(Service.id == booking_data.service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Validate stylist exists and is available
    stylist = db.query(Stylist).filter(Stylist.id == booking_data.stylist_id).first()
    if not stylist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stylist not found"
        )
    
    # Check for conflicts
    conflicts = check_booking_conflicts(
        db,
        booking_data.stylist_id,
        booking_data.start_time,
        booking_data.end_time
    )
    if conflicts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Booking conflicts with existing appointments",
            headers={"X-Conflict-Details": json.dumps(conflicts)}
        )
    
    # Create booking
    booking = Booking(
        id=str(uuid.uuid4()),
        user_id=user_id,
        stylist_id=booking_data.stylist_id,
        service_id=booking_data.service_id,
        start_time=booking_data.start_time,
        end_time=booking_data.end_time,
        notes=booking_data.notes,
        recurrence_type=booking_data.recurrence_type,
        recurrence_end_date=booking_data.recurrence_end_date,
        recurrence_pattern=booking_data.recurrence_pattern,
        last_modified_by=user_id
    )
    
    try:
        db.add(booking)
        db.commit()
        db.refresh(booking)
        
        # Create calendar event
        try:
            calendar_event = calendar_services.create_calendar_event(booking)
            booking.calendar_event_id = calendar_event.event_id
            db.commit()
        except Exception as e:
            # Log calendar integration error but don't fail the booking
            print(f"Calendar integration failed: {str(e)}")
        
        # Send notification
        notification_services.send_booking_confirmation(booking)
        
        return booking
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create booking"
        )

def create_recurring_bookings(
    db: Session,
    booking_data: RecurringBookingCreate,
    user_id: int
) -> List[Booking]:
    """Create a series of recurring bookings."""
    base_booking = booking_data.base_booking
    recurrence_type = booking_data.recurrence_type
    end_date = booking_data.recurrence_end_date
    
    # Calculate recurrence dates
    if recurrence_type == RecurrenceType.DAILY:
        freq = DAILY
    elif recurrence_type == RecurrenceType.WEEKLY:
        freq = WEEKLY
    elif recurrence_type == RecurrenceType.MONTHLY:
        freq = MONTHLY
    else:
        # Custom recurrence pattern
        pattern = booking_data.recurrence_pattern
        if not pattern:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Custom recurrence pattern required"
            )
        # Implement custom recurrence logic based on pattern
        # This is a simplified example
        freq = pattern.get("frequency", WEEKLY)
    
    # Generate dates
    dates = list(rrule(
        freq,
        dtstart=base_booking.start_time,
        until=end_date,
        **booking_data.recurrence_pattern or {}
    ))
    
    # Create parent booking
    parent_booking = create_booking(
        db,
        BookingCreate(
            **base_booking.dict(),
            recurrence_type=recurrence_type,
            recurrence_end_date=end_date,
            recurrence_pattern=booking_data.recurrence_pattern
        ),
        user_id
    )
    
    # Create recurring bookings
    recurring_bookings = []
    for date in dates[1:]:  # Skip first date as it's the parent booking
        duration = base_booking.end_time - base_booking.start_time
        start_time = date
        end_time = start_time + duration
        
        try:
            booking = create_booking(
                db,
                BookingCreate(
                    **base_booking.dict(),
                    start_time=start_time,
                    end_time=end_time,
                    recurrence_type=recurrence_type,
                    recurrence_end_date=end_date,
                    recurrence_pattern=booking_data.recurrence_pattern
                ),
                user_id
            )
            booking.parent_booking_id = parent_booking.id
            recurring_bookings.append(booking)
        except HTTPException as e:
            if e.status_code == status.HTTP_409_CONFLICT:
                # Handle conflict by creating waitlist entry
                create_waitlist_entry(
                    db,
                    WaitlistEntryCreate(
                        user_id=user_id,
                        service_id=base_booking.service_id,
                        preferred_stylist_id=base_booking.stylist_id,
                        preferred_date_range={
                            "start": start_time.isoformat(),
                            "end": end_time.isoformat()
                        }
                    )
                )
            else:
                raise e
    
    db.commit()
    return [parent_booking] + recurring_bookings

def update_booking(
    db: Session,
    booking_id: str,
    booking_data: BookingUpdate,
    user_id: int
) -> Booking:
    """Update a booking with validation and conflict checking."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check if booking can be modified
    if booking.status in [BookingStatus.COMPLETED, BookingStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify completed or cancelled booking"
        )
    
    # Update fields
    update_data = booking_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(booking, field, value)
    
    # If time is being changed, check for conflicts
    if any(field in update_data for field in ['start_time', 'end_time', 'stylist_id']):
        conflicts = check_booking_conflicts(
            db,
            booking.stylist_id,
            booking.start_time,
            booking.end_time,
            exclude_booking_id=booking_id
        )
        if conflicts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking conflicts with existing appointments",
                headers={"X-Conflict-Details": json.dumps(conflicts)}
            )
    
    booking.last_modified_by = user_id
    
    try:
        db.commit()
        db.refresh(booking)
        
        # Update calendar event
        if booking.calendar_event_id:
            try:
                calendar_services.update_calendar_event(booking)
            except Exception as e:
                print(f"Calendar update failed: {str(e)}")
        
        # Send notification
        notification_services.send_booking_update(booking)
        
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
    reason: str,
    user_id: int,
    cancel_recurring: bool = False
) -> Booking:
    """Cancel a booking and optionally its recurring instances."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is already cancelled"
        )
    
    if cancel_recurring and booking.recurrence_type != RecurrenceType.NONE:
        # Cancel all recurring bookings
        recurring_bookings = db.query(Booking).filter(
            or_(
                Booking.id == booking_id,
                Booking.parent_booking_id == booking_id
            )
        ).all()
        
        for recurring_booking in recurring_bookings:
            recurring_booking.status = BookingStatus.CANCELLED
            recurring_booking.cancellation_reason = reason
            recurring_booking.cancellation_time = datetime.utcnow()
            recurring_booking.last_modified_by = user_id
            
            # Cancel calendar event
            if recurring_booking.calendar_event_id:
                try:
                    calendar_services.delete_calendar_event(recurring_booking)
                except Exception as e:
                    print(f"Calendar deletion failed: {str(e)}")
            
            # Send cancellation notification
            notification_services.send_booking_cancellation(recurring_booking)
    else:
        # Cancel single booking
        booking.status = BookingStatus.CANCELLED
        booking.cancellation_reason = reason
        booking.cancellation_time = datetime.utcnow()
        booking.last_modified_by = user_id
        
        # Cancel calendar event
        if booking.calendar_event_id:
            try:
                calendar_services.delete_calendar_event(booking)
            except Exception as e:
                print(f"Calendar deletion failed: {str(e)}")
        
        # Send cancellation notification
        notification_services.send_booking_cancellation(booking)
    
    try:
        db.commit()
        db.refresh(booking)
        return booking
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel booking"
        )

# Waitlist Management
def create_waitlist_entry(
    db: Session,
    waitlist_data: WaitlistEntryCreate
) -> WaitlistEntry:
    """Create a new waitlist entry."""
    # Validate service exists
    service = db.query(Service).filter(Service.id == waitlist_data.service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Validate stylist if specified
    if waitlist_data.preferred_stylist_id:
        stylist = db.query(Stylist).filter(Stylist.id == waitlist_data.preferred_stylist_id).first()
        if not stylist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Preferred stylist not found"
            )
    
    # Create waitlist entry
    waitlist_entry = WaitlistEntry(
        id=str(uuid.uuid4()),
        user_id=waitlist_data.user_id,
        service_id=waitlist_data.service_id,
        preferred_stylist_id=waitlist_data.preferred_stylist_id,
        preferred_date_range=waitlist_data.preferred_date_range,
        priority=waitlist_data.priority,
        expires_at=datetime.utcnow() + timedelta(days=7)  # Default expiration
    )
    
    try:
        db.add(waitlist_entry)
        db.commit()
        db.refresh(waitlist_entry)
        
        # Send waitlist confirmation
        notification_services.send_waitlist_confirmation(waitlist_entry)
        
        return waitlist_entry
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create waitlist entry"
        )

def process_waitlist(
    db: Session,
    booking_id: str,
    stylist_id: int,
    start_time: datetime,
    end_time: datetime
) -> Optional[WaitlistEntry]:
    """Process waitlist entries when a slot becomes available."""
    # Find matching waitlist entries
    matching_entries = db.query(WaitlistEntry).filter(
        and_(
            WaitlistEntry.status == BookingStatus.WAITLISTED,
            WaitlistEntry.expires_at > datetime.utcnow(),
            or_(
                WaitlistEntry.preferred_stylist_id == stylist_id,
                WaitlistEntry.preferred_stylist_id.is_(None)
            )
        )
    ).order_by(WaitlistEntry.priority.desc(), WaitlistEntry.created_at.asc()).all()
    
    for entry in matching_entries:
        # Check if the time slot matches preferences
        if entry.preferred_date_range:
            preferred_start = parse(entry.preferred_date_range["start"])
            preferred_end = parse(entry.preferred_date_range["end"])
            if not (preferred_start <= start_time <= preferred_end and
                   preferred_start <= end_time <= preferred_end):
                continue
        
        # Create booking for the waitlist entry
        try:
            booking = create_booking(
                db,
                BookingCreate(
                    user_id=entry.user_id,
                    stylist_id=stylist_id,
                    service_id=entry.service_id,
                    start_time=start_time,
                    end_time=end_time
                ),
                entry.user_id
            )
            
            # Update waitlist entry
            entry.status = BookingStatus.CONFIRMED
            entry.booking_id = booking.id
            entry.notification_sent = True
            
            db.commit()
            
            # Send notification
            notification_services.send_waitlist_fulfilled(entry, booking)
            
            return entry
        except HTTPException as e:
            if e.status_code == status.HTTP_409_CONFLICT:
                continue
            raise e
    
    return None

# Availability Management
def check_booking_conflicts(
    db: Session,
    stylist_id: int,
    start_time: datetime,
    end_time: datetime,
    exclude_booking_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Check for booking conflicts."""
    conflicts = []
    
    # Check stylist availability
    day_of_week = start_time.weekday()
    availability = db.query(StylistAvailability).filter(
        and_(
            StylistAvailability.stylist_id == stylist_id,
            StylistAvailability.day_of_week == day_of_week,
            StylistAvailability.is_available == True
        )
    ).first()
    
    if not availability:
        conflicts.append({
            "type": "stylist_unavailable",
            "details": "Stylist is not available on this day"
        })
        return conflicts
    
    # Check time off
    time_off = db.query(StylistTimeOff).filter(
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
    
    if time_off:
        conflicts.append({
            "type": "stylist_time_off",
            "details": f"Stylist is on time off from {time_off.start_date} to {time_off.end_date}"
        })
        return conflicts
    
    # Check existing bookings
    query = db.query(Booking).filter(
        and_(
            Booking.stylist_id == stylist_id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
            or_(
                and_(
                    Booking.start_time <= start_time,
                    Booking.end_time > start_time
                ),
                and_(
                    Booking.start_time < end_time,
                    Booking.end_time >= end_time
                )
            )
        )
    )
    
    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)
    
    existing_bookings = query.all()
    
    for booking in existing_bookings:
        conflicts.append({
            "type": "double_booking",
            "details": {
                "booking_id": booking.id,
                "start_time": booking.start_time.isoformat(),
                "end_time": booking.end_time.isoformat(),
                "user_id": booking.user_id
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
            # Check stylist availability
            day_of_week = current_time.weekday()
            availability = db.query(StylistAvailability).filter(
                and_(
                    StylistAvailability.stylist_id == stylist.id,
                    StylistAvailability.day_of_week == day_of_week,
                    StylistAvailability.is_available == True
                )
            ).first()
            
            if not availability:
                continue
            
            # Check time off
            time_off = db.query(StylistTimeOff).filter(
                and_(
                    StylistTimeOff.stylist_id == stylist.id,
                    StylistTimeOff.is_approved == True,
                    or_(
                        and_(
                            StylistTimeOff.start_date <= current_time,
                            StylistTimeOff.end_date >= current_time
                        ),
                        and_(
                            StylistTimeOff.start_date <= current_time + timedelta(minutes=duration),
                            StylistTimeOff.end_date >= current_time + timedelta(minutes=duration)
                        )
                    )
                )
            ).first()
            
            if time_off:
                continue
            
            # Check existing bookings
            end_time = current_time + timedelta(minutes=duration)
            conflicts = check_booking_conflicts(
                db,
                stylist.id,
                current_time,
                end_time
            )
            
            slot = TimeSlotResponse(
                start_time=current_time,
                end_time=end_time,
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

# Stylist Availability Management
def update_stylist_availability(
    db: Session,
    stylist_id: int,
    availability_data: List[StylistAvailabilityCreate]
) -> List[StylistAvailability]:
    """Update a stylist's availability schedule."""
    # Delete existing availability
    db.query(StylistAvailability).filter(
        StylistAvailability.stylist_id == stylist_id
    ).delete()
    
    # Create new availability entries
    availability_entries = []
    for entry in availability_data:
        availability = StylistAvailability(
            id=str(uuid.uuid4()),
            stylist_id=stylist_id,
            day_of_week=entry.day_of_week,
            start_time=entry.start_time,
            end_time=entry.end_time,
            is_available=entry.is_available,
            break_start=entry.break_start,
            break_end=entry.break_end
        )
        availability_entries.append(availability)
    
    try:
        db.add_all(availability_entries)
        db.commit()
        
        for entry in availability_entries:
            db.refresh(entry)
        
        return availability_entries
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update stylist availability"
        )

def request_time_off(
    db: Session,
    time_off_data: StylistTimeOffCreate,
    stylist_id: int
) -> StylistTimeOff:
    """Request time off for a stylist."""
    # Validate dates
    if time_off_data.start_date >= time_off_data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date"
        )
    
    # Check for existing bookings
    existing_bookings = db.query(Booking).filter(
        and_(
            Booking.stylist_id == stylist_id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
            or_(
                and_(
                    Booking.start_time <= time_off_data.start_date,
                    Booking.end_time > time_off_data.start_date
                ),
                and_(
                    Booking.start_time < time_off_data.end_date,
                    Booking.end_time >= time_off_data.end_date
                )
            )
        )
    ).all()
    
    if existing_bookings:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Time off request conflicts with existing bookings",
            headers={"X-Conflict-Details": json.dumps([
                {
                    "booking_id": booking.id,
                    "start_time": booking.start_time.isoformat(),
                    "end_time": booking.end_time.isoformat()
                }
                for booking in existing_bookings
            ])}
        )
    
    # Create time off request
    time_off = StylistTimeOff(
        id=str(uuid.uuid4()),
        stylist_id=stylist_id,
        start_date=time_off_data.start_date,
        end_date=time_off_data.end_date,
        reason=time_off_data.reason
    )
    
    try:
        db.add(time_off)
        db.commit()
        db.refresh(time_off)
        
        # Notify admin
        notification_services.send_time_off_request(time_off)
        
        return time_off
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create time off request"
        )

def approve_time_off(
    db: Session,
    time_off_id: str,
    admin_id: int
) -> StylistTimeOff:
    """Approve a time off request."""
    time_off = db.query(StylistTimeOff).filter(StylistTimeOff.id == time_off_id).first()
    if not time_off:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time off request not found"
        )
    
    if time_off.is_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Time off request is already approved"
        )
    
    # Check for existing bookings
    existing_bookings = db.query(Booking).filter(
        and_(
            Booking.stylist_id == time_off.stylist_id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
            or_(
                and_(
                    Booking.start_time <= time_off.start_date,
                    Booking.end_time > time_off.start_date
                ),
                and_(
                    Booking.start_time < time_off.end_date,
                    Booking.end_time >= time_off.end_date
                )
            )
        )
    ).all()
    
    if existing_bookings:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot approve time off with existing bookings",
            headers={"X-Conflict-Details": json.dumps([
                {
                    "booking_id": booking.id,
                    "start_time": booking.start_time.isoformat(),
                    "end_time": booking.end_time.isoformat()
                }
                for booking in existing_bookings
            ])}
        )
    
    time_off.is_approved = True
    time_off.approved_by = admin_id
    
    try:
        db.commit()
        db.refresh(time_off)
        
        # Notify stylist
        notification_services.send_time_off_approval(time_off)
        
        return time_off
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve time off request"
        )

# Search and Filter
def search_bookings(
    db: Session,
    params: BookingSearchParams,
    skip: int = 0,
    limit: int = 100
) -> List[Booking]:
    """Search bookings with various filters."""
    query = db.query(Booking)
    
    if params.start_date:
        query = query.filter(Booking.start_time >= params.start_date)
    if params.end_date:
        query = query.filter(Booking.end_time <= params.end_date)
    if params.stylist_id:
        query = query.filter(Booking.stylist_id == params.stylist_id)
    if params.service_id:
        query = query.filter(Booking.service_id == params.service_id)
    if params.status:
        query = query.filter(Booking.status == params.status)
    if params.user_id:
        query = query.filter(Booking.user_id == params.user_id)
    
    if not params.include_recurring:
        query = query.filter(Booking.parent_booking_id.is_(None))
    
    return query.order_by(Booking.start_time.desc()).offset(skip).limit(limit).all()

def get_user_bookings(
    db: Session,
    user_id: int,
    include_past: bool = False,
    skip: int = 0,
    limit: int = 100
) -> List[Booking]:
    """Get all bookings for a user."""
    query = db.query(Booking).filter(Booking.user_id == user_id)
    
    if not include_past:
        query = query.filter(Booking.start_time >= datetime.utcnow())
    
    return query.order_by(Booking.start_time.desc()).offset(skip).limit(limit).all()

def get_stylist_bookings(
    db: Session,
    stylist_id: int,
    include_past: bool = False,
    skip: int = 0,
    limit: int = 100
) -> List[Booking]:
    """Get all bookings for a stylist."""
    query = db.query(Booking).filter(Booking.stylist_id == stylist_id)
    
    if not include_past:
        query = query.filter(Booking.start_time >= datetime.utcnow())
    
    return query.order_by(Booking.start_time.desc()).offset(skip).limit(limit).all() 