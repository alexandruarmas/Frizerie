from typing import List, Dict, Any
from datetime import datetime, time, timedelta
import json
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from . import models
from users.models import User

# In a real app, these would interact with the database
# These are just placeholders

async def get_bookings_by_user_id(user_id: int) -> List[Dict[str, Any]]:
    """
    Get all bookings for a specific user.
    In a real app, this would query the database.
    """
    # Mock data for testing
    if user_id == 1:
        return [
            {
                "id": 1,
                "stylist_id": 2,
                "stylist_name": "Jane Smith",
                "service": "Haircut",
                "date": "2023-09-15",
                "time": "14:30",
                "status": "confirmed"
            },
            {
                "id": 2,
                "stylist_id": 1,
                "stylist_name": "John Doe",
                "service": "Beard Trim",
                "date": "2023-09-20",
                "time": "10:00",
                "status": "pending"
            }
        ]
    return []

async def create_booking(user_id: int, stylist_id: int, service: str, date_str: str, time_str: str) -> Dict[str, Any]:
    """
    Create a new booking.
    In a real app, this would save to the database.
    """
    # Mock implementation
    # In a real app, you'd create a new record and return it
    return {
        "id": 3,
        "user_id": user_id,
        "stylist_id": stylist_id,
        "service": service,
        "date": date_str,
        "time": time_str,
        "status": "pending"
    }

async def get_stylist_by_id(stylist_id: int) -> Dict[str, Any]:
    """
    Get a stylist by ID.
    In a real app, this would query the database.
    """
    # Mock data
    stylists = {
        1: {
            "id": 1,
            "name": "John Doe",
            "available_hours": json.dumps({
                "monday": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "13:00", "13:30", "14:00"],
                "tuesday": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "13:00", "13:30", "14:00"],
                "wednesday": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "13:00", "13:30", "14:00"],
                "thursday": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "13:00", "13:30", "14:00"],
                "friday": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "13:00", "13:30", "14:00"],
                "saturday": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30"],
                "sunday": []
            })
        },
        2: {
            "id": 2,
            "name": "Jane Smith",
            "available_hours": json.dumps({
                "monday": ["13:00", "13:30", "14:00", "14:30", "15:00", "15:30"],
                "tuesday": ["13:00", "13:30", "14:00", "14:30", "15:00", "15:30"],
                "wednesday": ["13:00", "13:30", "14:00", "14:30", "15:00", "15:30"],
                "thursday": ["13:00", "13:30", "14:00", "14:30", "15:00", "15:30"],
                "friday": ["13:00", "13:30", "14:00", "14:30", "15:00", "15:30"],
                "saturday": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30"],
                "sunday": []
            })
        }
    }
    
    return stylists.get(stylist_id)

async def get_available_slots(stylist_id: int, date_str: str) -> List[str]:
    """
    Get available time slots for a stylist on a specific date.
    In a real app, this would check the database for available slots.
    """
    # Parse the date
    date = datetime.strptime(date_str, "%Y-%m-%d")
    day_of_week = date.strftime("%A").lower()
    
    # Get stylist's schedule
    stylist = await get_stylist_by_id(stylist_id)
    if not stylist:
        return []
    
    available_hours = json.loads(stylist["available_hours"])
    
    # Get all slots for the day
    all_slots = available_hours.get(day_of_week, [])
    
    # In a real app, you'd check existing bookings and remove booked slots
    # For now, just return all available slots
    return all_slots 

def get_stylists(db: Session) -> List[models.Stylist]:
    """Get all stylists."""
    return db.query(models.Stylist).all()

def get_stylist(db: Session, stylist_id: int) -> models.Stylist:
    """Get stylist by ID."""
    stylist = db.query(models.Stylist).filter(models.Stylist.id == stylist_id).first()
    if not stylist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stylist not found")
    return stylist

def get_stylist_availability(db: Session, stylist_id: int, date: datetime) -> List[models.StylistAvailability]:
    """Get stylist availability for a specific date."""
    # Get the start and end of the day
    start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1)
    
    stylist = get_stylist(db, stylist_id)
    availability = db.query(models.StylistAvailability).filter(
        models.StylistAvailability.stylist_id == stylist_id,
        models.StylistAvailability.start_time >= start_date,
        models.StylistAvailability.start_time < end_date
    ).all()
    
    return availability

def get_bookings_for_date(db: Session, date: datetime) -> List[models.Booking]:
    """Get all bookings for a specific date."""
    # Get the start and end of the day
    start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1)
    
    return db.query(models.Booking).filter(
        models.Booking.start_time >= start_date,
        models.Booking.start_time < end_date
    ).all()

def get_available_slots(db: Session, stylist_id: int, date: datetime, user_vip_level: int = 0) -> List[Dict[str, Any]]:
    """Get all available booking slots for a specific stylist and date."""
    availability = get_stylist_availability(db, stylist_id, date)
    bookings = db.query(models.Booking).filter(
        models.Booking.stylist_id == stylist_id,
        models.Booking.start_time >= date.replace(hour=0, minute=0, second=0, microsecond=0),
        models.Booking.start_time < (date.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1))
    ).all()
    
    # Get the booked time slots
    booked_slots = []
    for booking in bookings:
        booked_slots.append((booking.start_time, booking.end_time))
    
    # Calculate available slots
    available_slots = []
    for avail in availability:
        # Create 30-minute slots within the availability period
        current_time = avail.start_time
        while current_time + timedelta(minutes=30) <= avail.end_time:
            slot_end_time = current_time + timedelta(minutes=30)
            
            # Check if the slot is already booked
            is_booked = False
            for booked_start, booked_end in booked_slots:
                if (current_time >= booked_start and current_time < booked_end) or \
                   (slot_end_time > booked_start and slot_end_time <= booked_end) or \
                   (current_time <= booked_start and slot_end_time >= booked_end):
                    is_booked = True
                    break
            
            # Check VIP restrictions (vip_restricted flag)
            is_vip_restricted = avail.vip_restricted
            is_vip_accessible = not is_vip_restricted or (is_vip_restricted and user_vip_level >= 1)
            
            if not is_booked and is_vip_accessible:
                available_slots.append({
                    "start_time": current_time.isoformat(),
                    "end_time": slot_end_time.isoformat(),
                    "is_vip_only": is_vip_restricted
                })
            
            current_time = slot_end_time
    
    return available_slots

def create_booking(
    db: Session, 
    user_id: int, 
    stylist_id: int, 
    service_type: str, 
    start_time: datetime
) -> models.Booking:
    """Create a new booking."""
    # Check if the stylist exists
    stylist = get_stylist(db, stylist_id)
    
    # Calculate end time (assuming 30 minutes per booking)
    end_time = start_time + timedelta(minutes=30)
    
    # Check if the slot is available
    slot_available = False
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    available_slots = get_available_slots(db, stylist_id, start_time, user.vip_level)
    for slot in available_slots:
        slot_start = datetime.fromisoformat(slot["start_time"])
        if slot_start == start_time:
            # If this is a VIP-only slot, ensure the user has VIP status
            if slot["is_vip_only"] and user.vip_level < 1:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail="This slot is available to VIP members only"
                )
            slot_available = True
            break
    
    if not slot_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="The selected time slot is not available"
        )
    
    # Create booking
    booking = models.Booking(
        user_id=user_id,
        stylist_id=stylist_id,
        service_type=service_type,
        start_time=start_time,
        end_time=end_time,
        status="SCHEDULED"
    )
    
    # Add and commit to DB
    db.add(booking)
    db.commit()
    db.refresh(booking)
    
    # Update user loyalty points (as a reward for booking)
    user.loyalty_points += 10  # Add 10 points per booking
    db.commit()
    
    return booking

def get_user_bookings(db: Session, user_id: int) -> List[models.Booking]:
    """Get all bookings for a specific user."""
    return db.query(models.Booking).filter(models.Booking.user_id == user_id).all()

def cancel_booking(db: Session, booking_id: int, user_id: int) -> models.Booking:
    """Cancel a booking."""
    booking = db.query(models.Booking).filter(
        models.Booking.id == booking_id,
        models.Booking.user_id == user_id
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Booking not found or does not belong to the current user"
        )
    
    # Check if the booking is already cancelled
    if booking.status == "CANCELLED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Booking is already cancelled"
        )
    
    # Check if the booking is in the past
    if booking.start_time < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Cannot cancel bookings in the past"
        )
    
    # Update booking status
    booking.status = "CANCELLED"
    db.commit()
    db.refresh(booking)
    
    return booking

def setup_test_data(db: Session):
    """Set up test data for the application."""
    # Create some stylists if none exist
    if db.query(models.Stylist).count() == 0:
        stylists = [
            models.Stylist(name="Ana Maria", specialization="Color Specialist"),
            models.Stylist(name="Ion", specialization="Haircuts"),
            models.Stylist(name="Elena", specialization="Styling")
        ]
        db.add_all(stylists)
        db.commit()
        
        # Create availability for stylists
        now = datetime.now()
        start_date = now.replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Create availability for the next 7 days
        for i in range(7):
            day = start_date + timedelta(days=i)
            
            # Morning shift (9 AM - 1 PM)
            for stylist in stylists:
                morning_start = day.replace(hour=9, minute=0)
                morning_end = day.replace(hour=13, minute=0)
                
                # Make some morning slots VIP-only (e.g., 10-11 AM on weekends)
                vip_restricted = False
                if day.weekday() >= 5:  # Weekend
                    vip_restricted = True
                
                db.add(models.StylistAvailability(
                    stylist_id=stylist.id,
                    start_time=morning_start,
                    end_time=morning_end,
                    vip_restricted=vip_restricted
                ))
            
            # Afternoon shift (2 PM - 6 PM)
            for stylist in stylists:
                afternoon_start = day.replace(hour=14, minute=0)
                afternoon_end = day.replace(hour=18, minute=0)
                
                # Make some afternoon slots VIP-only (e.g., 4-5 PM)
                vip_restricted = False
                if 15 <= afternoon_start.hour < 17:  # 3 PM to 5 PM
                    vip_restricted = True
                
                db.add(models.StylistAvailability(
                    stylist_id=stylist.id,
                    start_time=afternoon_start,
                    end_time=afternoon_end,
                    vip_restricted=vip_restricted
                ))
        
        db.commit() 