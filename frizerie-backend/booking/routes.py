"""
Booking routes using the optimized booking services.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from config.database import get_db
from auth.dependencies import get_current_user, get_current_stylist, get_current_admin_user
from users.models import User
from stylists.models import Stylist
from booking import optimized_services as booking_services
from validation.schemas import (
    BookingCreate, BookingUpdate, BookingResponse,
    WaitlistEntryCreate, WaitlistEntryUpdate, WaitlistEntryResponse,
    StylistAvailabilityCreate, StylistAvailabilityResponse,
    StylistTimeOffCreate, StylistTimeOffResponse,
    RecurringBookingCreate, RecurringBookingResponse,
    BookingSearchParams, BookingAvailabilityParams,
    TimeSlotResponse
)

router = APIRouter(prefix="/bookings", tags=["Bookings"])

# Basic Booking Routes
@router.post("", response_model=BookingResponse)
async def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new booking."""
    return booking_services.create_booking(db, booking_data, current_user.id)

@router.post("/recurring", response_model=RecurringBookingResponse)
async def create_recurring_bookings(
    booking_data: RecurringBookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a series of recurring bookings."""
    bookings = booking_services.create_recurring_bookings(db, booking_data, current_user.id)
    return RecurringBookingResponse(
        parent_booking=bookings[0],
        recurring_bookings=bookings[1:]
    )

@router.get("", response_model=List[BookingResponse])
async def search_bookings(
    params: BookingSearchParams,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search bookings with various filters."""
    return booking_services.search_bookings(db, params, skip, limit)

@router.get("/available-slots", response_model=List[TimeSlotResponse])
async def get_available_slots(
    params: BookingAvailabilityParams,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available time slots for a service and optional stylist."""
    return booking_services.get_available_slots(db, params)

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific booking."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check if user has permission to view the booking
    if booking.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this booking"
        )
    
    return booking

@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: str,
    booking_data: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing booking."""
    return booking_services.update_booking(db, booking_id, booking_data, current_user.id)

@router.delete("/{booking_id}", response_model=BookingResponse)
async def cancel_booking(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a booking."""
    return booking_services.cancel_booking(db, booking_id, current_user.id)

# Waitlist Routes
@router.post("/waitlist", response_model=WaitlistEntryResponse)
async def create_waitlist_entry(
    waitlist_data: WaitlistEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new waitlist entry."""
    if waitlist_data.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create waitlist entry for another user"
        )
    return booking_services.create_waitlist_entry(db, waitlist_data)

@router.get("/waitlist", response_model=List[WaitlistEntryResponse])
async def get_waitlist_entries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get waitlist entries for the current user."""
    if current_user.is_admin:
        # Admin can see all waitlist entries
        entries = db.query(WaitlistEntry).offset(skip).limit(limit).all()
    else:
        # Regular users can only see their own entries
        entries = db.query(WaitlistEntry).filter(
            WaitlistEntry.user_id == current_user.id
        ).offset(skip).limit(limit).all()
    
    return entries

@router.put("/waitlist/{entry_id}", response_model=WaitlistEntryResponse)
async def update_waitlist_entry(
    entry_id: str,
    entry_data: WaitlistEntryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a waitlist entry."""
    entry = db.query(WaitlistEntry).filter(WaitlistEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waitlist entry not found"
        )
    
    if entry.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this waitlist entry"
        )
    
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

# Stylist Availability Routes
@router.put("/stylist/availability", response_model=List[StylistAvailabilityResponse])
async def update_stylist_availability(
    availability_data: List[StylistAvailabilityCreate],
    db: Session = Depends(get_db),
    current_stylist: Stylist = Depends(get_current_stylist)
):
    """Update a stylist's availability schedule."""
    return booking_services.update_stylist_availability(
        db,
        current_stylist.id,
        availability_data
    )

@router.post("/stylist/time-off", response_model=StylistTimeOffResponse)
async def request_time_off(
    time_off_data: StylistTimeOffCreate,
    db: Session = Depends(get_db),
    current_stylist: Stylist = Depends(get_current_stylist)
):
    """Request time off."""
    return booking_services.create_time_off_request(
        db,
        current_stylist.id,
        time_off_data
    )

@router.get("/stylist/me", response_model=List[BookingResponse])
async def get_my_stylist_bookings(
    include_past: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_stylist: Stylist = Depends(get_current_stylist)
):
    """Get all bookings for the current stylist."""
    return booking_services.get_stylist_bookings(
        db,
        current_stylist.id,
        include_past,
        skip,
        limit
    )

# User-specific Routes
@router.get("/user/me", response_model=List[BookingResponse])
async def get_my_bookings(
    include_past: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all bookings for the current user."""
    return booking_services.get_user_bookings(
        db,
        current_user.id,
        include_past,
        skip,
        limit
    )

# Admin Routes
@router.get("/admin/all", response_model=List[BookingResponse])
async def get_all_bookings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all bookings (admin only)."""
    return booking_services.get_all_bookings(db, skip, limit)

@router.get("/admin/waitlist", response_model=List[WaitlistEntryResponse])
async def get_all_waitlist_entries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all waitlist entries (admin only)."""
    return db.query(WaitlistEntry).order_by(
        WaitlistEntry.created_at.desc()
    ).offset(skip).limit(limit).all()

@router.get("/admin/time-off", response_model=List[StylistTimeOffResponse])
async def get_all_time_off_requests(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all time off requests (admin only)."""
    return db.query(StylistTimeOff).order_by(
        StylistTimeOff.created_at.desc()
    ).offset(skip).limit(limit).all()

@router.put("/admin/{booking_id}/status", response_model=BookingResponse)
async def update_booking_status(
    booking_id: str,
    status: BookingStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update a booking's status (admin only)."""
    return booking_services.update_booking_status(db, booking_id, status)

@router.put("/admin/stylist/{stylist_id}/time-off/{time_off_id}", response_model=StylistTimeOffResponse)
async def approve_time_off(
    stylist_id: int,
    time_off_id: str,
    approved: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Approve or reject a time off request (admin only)."""
    return booking_services.update_time_off_status(
        db,
        stylist_id,
        time_off_id,
        approved
    ) 