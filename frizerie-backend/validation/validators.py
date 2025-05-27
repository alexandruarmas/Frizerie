from datetime import datetime, time
from typing import Optional
from fastapi import HTTPException

def validate_booking_time(start_time: datetime) -> None:
    """Validate if the booking time is valid."""
    # Check if booking is in the future
    if start_time < datetime.now():
        raise HTTPException(
            status_code=400,
            detail="Booking time must be in the future"
        )
    
    # Check if booking is within business hours (9 AM to 8 PM)
    booking_time = start_time.time()
    if not (time(9, 0) <= booking_time <= time(20, 0)):
        raise HTTPException(
            status_code=400,
            detail="Booking must be between 9 AM and 8 PM"
        )

def validate_password_strength(password: str) -> None:
    """Validate password strength."""
    if len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long"
        )
    
    if not any(c.isupper() for c in password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one uppercase letter"
        )
    
    if not any(c.islower() for c in password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one lowercase letter"
        )
    
    if not any(c.isdigit() for c in password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one number"
        )

def validate_vip_booking(user_vip_level: int, is_vip_slot: bool) -> None:
    """Validate if user can book VIP slots."""
    if is_vip_slot and user_vip_level < 1:
        raise HTTPException(
            status_code=403,
            detail="VIP slots are only available for Silver tier and above"
        )

def validate_service_type(service_type: str) -> None:
    """Validate if service type is valid."""
    valid_services = [
        "Haircut",
        "Hair Coloring",
        "Hair Styling",
        "Beard Trim",
        "Facial Treatment"
    ]
    
    if service_type not in valid_services:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid service type. Must be one of: {', '.join(valid_services)}"
        )

def validate_notification_method(method: str) -> None:
    """Validate if notification method is valid."""
    valid_methods = ["SMS", "EMAIL", "PUSH"]
    
    if method not in valid_methods:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid notification method. Must be one of: {', '.join(valid_methods)}"
        ) 