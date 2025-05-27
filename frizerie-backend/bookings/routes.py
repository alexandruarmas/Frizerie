from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from config.database import get_db
from config.dependencies import get_current_user
from . import services
from . import models
from users.models import User
from services.models import Service
from validation import (
    BookingCreate,
    BookingResponse,
    validate_booking_time,
    validate_vip_booking
)

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.get("/stylists", response_model=List[Dict[str, Any]])
def get_stylists(db: Session = Depends(get_db)):
    """Get all available stylists."""
    stylists = services.get_stylists(db)
    return [
        {
            "id": stylist.id,
            "name": stylist.name,
            "specialization": stylist.specialization,
            "bio": stylist.bio,
            "avatar_url": stylist.avatar_url
        } for stylist in stylists
    ]

@router.get("/available-slots/{stylist_id}/{date}", response_model=List[Dict[str, Any]])
def get_available_slots(
    stylist_id: int, 
    date: str,
    service_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available slots for a stylist on a specific date."""
    try:
        date_obj = datetime.fromisoformat(date.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        )
    
    # Validate service exists
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    return services.get_available_slots(db, stylist_id, date_obj, service_id, current_user.vip_level)

@router.post("/", response_model=BookingResponse)
def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new booking."""
    # Validate booking time
    validate_booking_time(booking_data.start_time)
    
    # Create booking
    booking = services.create_booking(
        db,
        current_user.id,
        booking_data.stylist_id,
        booking_data.service_id,
        booking_data.start_time
    )
    
    return booking

@router.get("/my-bookings", response_model=List[BookingResponse])
def get_user_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all bookings for the current user."""
    return services.get_user_bookings(db, current_user.id)

@router.delete("/{booking_id}", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a booking."""
    return services.cancel_booking(db, booking_id, current_user.id)

@router.get("/my-bookings/history", response_model=List[BookingResponse])
def get_user_booking_history(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get booking history for the current user."""
    return services.get_user_booking_history(db, current_user.id, skip=skip, limit=limit)

@router.get("/my-bookings/upcoming", response_model=List[BookingResponse])
def get_user_upcoming_bookings(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get upcoming bookings for the current user."""
    return services.get_user_upcoming_bookings(db, current_user.id, skip=skip, limit=limit)

@router.post("/setup-test-data", status_code=status.HTTP_201_CREATED)
async def setup_test_data(db: Session = Depends(get_db)):
    """Set up test data for the application."""
    services.setup_test_data(db)
    return {"message": "Test data created successfully"} 