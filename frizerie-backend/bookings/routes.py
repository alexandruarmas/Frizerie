from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

from config.database import get_db
from config.dependencies import get_current_user
from . import services
from . import models
from users.models import User

router = APIRouter(prefix="/bookings", tags=["Bookings"])

class BookingCreate(BaseModel):
    stylist_id: int
    service_type: str
    start_time: datetime

class BookingResponse(BaseModel):
    id: int
    stylist_id: int
    service_type: str
    start_time: datetime
    end_time: datetime
    status: str
    
    class Config:
        from_attributes = True

@router.get("/stylists", response_model=List[Dict[str, Any]])
async def get_stylists(db: Session = Depends(get_db)):
    """Get all available stylists."""
    stylists = services.get_stylists(db)
    return [
        {
            "id": stylist.id,
            "name": stylist.name,
            "specialization": stylist.specialization
        } for stylist in stylists
    ]

@router.get("/available-slots/{stylist_id}/{date}", response_model=List[Dict[str, Any]])
async def get_available_slots(
    stylist_id: int, 
    date: str,
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
    
    return services.get_available_slots(db, stylist_id, date_obj, current_user.vip_level)

@router.post("/", response_model=Dict[str, Any])
async def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new booking."""
    booking = services.create_booking(
        db,
        current_user.id,
        booking_data.stylist_id,
        booking_data.service_type,
        booking_data.start_time
    )
    
    stylist = services.get_stylist(db, booking.stylist_id)
    
    return {
        "id": booking.id,
        "stylist": {
            "id": stylist.id,
            "name": stylist.name
        },
        "service_type": booking.service_type,
        "start_time": booking.start_time.isoformat(),
        "end_time": booking.end_time.isoformat(),
        "status": booking.status
    }

@router.get("/my-bookings", response_model=List[Dict[str, Any]])
async def get_user_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all bookings for the current user."""
    bookings = services.get_user_bookings(db, current_user.id)
    result = []
    
    for booking in bookings:
        stylist = services.get_stylist(db, booking.stylist_id)
        result.append({
            "id": booking.id,
            "stylist": {
                "id": stylist.id,
                "name": stylist.name
            },
            "service_type": booking.service_type,
            "start_time": booking.start_time.isoformat(),
            "end_time": booking.end_time.isoformat(),
            "status": booking.status
        })
    
    return result

@router.delete("/{booking_id}", response_model=Dict[str, Any])
async def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a booking."""
    booking = services.cancel_booking(db, booking_id, current_user.id)
    stylist = services.get_stylist(db, booking.stylist_id)
    
    return {
        "id": booking.id,
        "stylist": {
            "id": stylist.id,
            "name": stylist.name
        },
        "service_type": booking.service_type,
        "start_time": booking.start_time.isoformat(),
        "end_time": booking.end_time.isoformat(),
        "status": booking.status
    }

@router.post("/setup-test-data", status_code=status.HTTP_201_CREATED)
async def setup_test_data(db: Session = Depends(get_db)):
    """Set up test data for the application."""
    services.setup_test_data(db)
    return {"message": "Test data created successfully"} 