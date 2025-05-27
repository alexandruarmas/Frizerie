from stylists.models import Stylist
from booking.models import StylistAvailability, StylistTimeOff, Booking
from typing import List, Dict, Any, Optional
from datetime import datetime, time, timedelta
import json
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status
import logging # Import logging 

from . import models
from users.models import User, UserSetting # Import User and UserSetting models
from services.models import Service # Import Service model
from notifications.services import create_notification # Import create_notification
from notifications.models import NotificationType # Import NotificationType enum

# In a real app, these would interact with the database
# These are just placeholders

# Set up logging
logger = logging.getLogger(__name__)

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

# This async function seems to be a leftover from mock data, keeping it for now but might need refactoring
async def create_booking_mock(user_id: int, stylist_id: int, service: str, date_str: str, time_str: str) -> Dict[str, Any]:
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

# This async function seems to be a leftover from mock data, keeping it for now but might need refactoring
async def get_stylist_by_id_mock(stylist_id: int) -> Dict[str, Any]:
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

# This async function seems to be a leftover from mock data, keeping it for now but might need refactoring
async def get_available_slots_mock(stylist_id: int, date_str: str) -> List[str]:
    """
    Get available time slots for a stylist on a specific date.
    In a real app, this would check the database for available slots.
    """
    # Parse the date
    date = datetime.strptime(date_str, "%Y-%m-%d")
    day_of_week = date.strftime("%A").lower()
    
    # Get stylist's schedule
    stylist = await get_stylist_by_id_mock(stylist_id)
    if not stylist:
        return []
    
    available_hours = json.loads(stylist["available_hours"])
    
    # Get all slots for the day
    all_slots = available_hours.get(day_of_week, [])
    
    # In a real app, you'd check existing bookings and remove booked slots
    # For now, just return all available slots
    return all_slots

def get_stylists(db: Session) -> List[Stylist]:
    """Get all stylists."""
    return db.query(Stylist).all()

def get_stylist(db: Session, stylist_id: int) -> Stylist:
    """Get stylist by ID."""
    stylist = db.query(Stylist).filter(Stylist.id == stylist_id).first()
    if not stylist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stylist not found")
    return stylist

def get_stylist_availability(db: Session, stylist_id: int, date: datetime) -> List[StylistAvailability]:
    """Get stylist availability for a specific date."""
    # Get the start and end of the day
    start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1)
    
    stylist = get_stylist(db, stylist_id)
    availability = db.query(StylistAvailability).filter(
        StylistAvailability.stylist_id == stylist_id,
        StylistAvailability.start_time >= start_date,
        StylistAvailability.start_time < end_date
    ).all()
    
    return availability

def get_bookings_for_time_range(
    db: Session,
    stylist_id: int,
    start_time: datetime,
    end_time: datetime
) -> List[Booking]:
    """Get all bookings for a stylist within a specific time range."""
    return db.query(Booking).filter(
        Booking.stylist_id == stylist_id,
        Booking.status != "CANCELLED", # Exclude cancelled bookings
        or_(
            and_(Booking.start_time >= start_time, Booking.start_time < end_time),
            and_(Booking.end_time > start_time, Booking.end_time <= end_time),
            and_(Booking.start_time <= start_time, Booking.end_time >= end_time)
        )
    ).all()

def get_available_slots(
    db: Session,
    stylist_id: int,
    date: datetime,
    service_id: int,
    user_vip_level: int = 0
) -> List[Dict[str, Any]]:
    """Get all available booking slots for a specific stylist, date, and service."""
    
    # Get service duration
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
        
    service_duration = timedelta(minutes=service.duration)
    
    availability = get_stylist_availability(db, stylist_id, date)
    
    # Get existing bookings for the stylist on the given date
    start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    existing_bookings = get_bookings_for_time_range(db, stylist_id, start_of_day, end_of_day)
    
    available_slots = []
    for avail in availability:
        # Generate potential slots based on service duration within availability
        current_time = avail.start_time
        while current_time + service_duration <= avail.end_time:
            slot_end_time = current_time + service_duration
            
            # Check for overlaps with existing bookings
            is_booked = False
            for booking in existing_bookings:
                 if (current_time < booking.end_time and slot_end_time > booking.start_time):
                    is_booked = True
                    break
            
            # Check VIP restrictions
            is_vip_restricted = avail.vip_restricted
            is_vip_accessible = not is_vip_restricted or (is_vip_restricted and user_vip_level >= 1)
            
            # Check if the slot is in the past
            is_in_past = current_time < datetime.now()
            
            if not is_booked and is_vip_accessible and not is_in_past:
                available_slots.append({
                    "start_time": current_time.isoformat(),
                    "end_time": slot_end_time.isoformat(),
                    "is_vip_only": is_vip_restricted
                })
            
            current_time += timedelta(minutes=15) # Move to the next potential start time (e.g., every 15 mins)
            
    # Sort available slots by start time
    available_slots.sort(key=lambda x: x['start_time'])

    return available_slots

def create_booking(
    db: Session, 
    user_id: int, 
    stylist_id: int, 
    service_id: int,
    start_time: datetime
) -> Booking:
    """Create a new booking."""
    # Check if the stylist and service exist
    stylist = get_stylist(db, stylist_id)
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    # Calculate end time based on service duration
    end_time = start_time + timedelta(minutes=service.duration)
    
    # Check for overlapping bookings for the stylist in the requested time range
    overlapping_bookings = get_bookings_for_time_range(db, stylist_id, start_time, end_time)
    if overlapping_bookings:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The selected time slot is not available"
        )

    # Create the booking
    booking = Booking(
        user_id=user_id,
        stylist_id=stylist_id,
        service_id=service_id,
        start_time=start_time,
        end_time=end_time,
        status="CONFIRMED"
    )
    
    db.add(booking)
    db.commit()
    db.refresh(booking)

    # --- Notification Triggering ---
    # Get user settings
    user_settings = db.query(UserSetting).filter(UserSetting.user_id == user_id).first()
    
    # Prepare notification content
    notification_title = "Booking Confirmation"
    notification_message = (
        f"Your booking has been confirmed!\n"
        f"Service: {service.name}\n"
        f"Date: {start_time.strftime('%Y-%m-%d')}\n"
        f"Time: {start_time.strftime('%H:%M')}\n"
        f"Stylist: {stylist.name}"
    )
    
    if user_settings:
        # Send local notification
        if user_settings.enable_notifications:
            create_notification(
                db=db,
                user_id=user_id,
                notification_type=NotificationType.BOOKING_CONFIRMATION,
                title=notification_title,
                message=notification_message,
                method="local"
            )
        
        # Send email notification
        if user_settings.enable_email_notifications:
            create_notification(
                db=db,
                user_id=user_id,
                notification_type=NotificationType.BOOKING_CONFIRMATION,
                title=notification_title,
                message=notification_message,
                method="email"
            )
        
        # Send SMS notification
        if user_settings.enable_sms_notifications:
            create_notification(
                db=db,
                user_id=user_id,
                notification_type=NotificationType.BOOKING_CONFIRMATION,
                title=notification_title,
                message=notification_message,
                method="sms"
            )
    
    return booking

def get_user_bookings(db: Session, user_id: int) -> List[Booking]:
    """Get all bookings for a user."""
    return db.query(Booking).filter(Booking.user_id == user_id).all()

def cancel_booking(db: Session, booking_id: int, user_id: int) -> Booking:
    """Cancel a booking."""
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == user_id
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking.status == "CANCELLED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is already cancelled"
        )
    
    # Get service and stylist details for notification
    service = db.query(Service).filter(Service.id == booking.service_id).first()
    stylist = get_stylist(db, booking.stylist_id)
    
    # Update booking status
    booking.status = "CANCELLED"
    db.commit()
    db.refresh(booking)
    
    # --- Notification Triggering ---
    # Get user settings
    user_settings = db.query(UserSetting).filter(UserSetting.user_id == user_id).first()
    
    # Prepare notification content
    notification_title = "Booking Cancellation"
    notification_message = (
        f"Your booking has been cancelled.\n"
        f"Service: {service.name}\n"
        f"Date: {booking.start_time.strftime('%Y-%m-%d')}\n"
        f"Time: {booking.start_time.strftime('%H:%M')}\n"
        f"Stylist: {stylist.name}"
    )
    
    if user_settings:
        # Send local notification
        if user_settings.enable_notifications:
            create_notification(
                db=db,
                user_id=user_id,
                notification_type=NotificationType.BOOKING_CANCELLATION,
                title=notification_title,
                message=notification_message,
                method="local"
            )
        
        # Send email notification
        if user_settings.enable_email_notifications:
            create_notification(
                db=db,
                user_id=user_id,
                notification_type=NotificationType.BOOKING_CANCELLATION,
                title=notification_title,
                message=notification_message,
                method="email"
            )
        
        # Send SMS notification
        if user_settings.enable_sms_notifications:
            create_notification(
                db=db,
                user_id=user_id,
                notification_type=NotificationType.BOOKING_CANCELLATION,
                title=notification_title,
                message=notification_message,
                method="sms"
            )
            
    # --- Trigger Last-Minute Availability Notification ---
    # Prepare booking details to pass to the notification function
    booking_details = {
        "service_name": service.name,
        "stylist_name": stylist.name,
        "date": booking.start_time.strftime('%Y-%m-%d'),
        "time": booking.start_time.strftime('%H:%M'),
        "start_time": booking.start_time, # Pass datetime object for potential future use
        "end_time": booking.end_time # Pass datetime object for potential future use
    }
    send_last_minute_availability_notifications(db, booking_details)

    return booking

def setup_test_data(db: Session):
    """Helper function to set up test data."""
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

    # Create some services if none exist
    if db.query(Service).count() == 0:
        # Assuming Service Categories exist with IDs 1, 2, 3 for Haircuts, Color, Styling
        services = [
            Service(name="Men's Haircut", description="Classic or modern men's haircut.", price=25.0, duration=30, category_id=1, is_active=True),
            Service(name="Women's Haircut", description="Stylish women's haircut.", price=40.0, duration=60, category_id=1, is_active=True),
            Service(name="Hair Coloring (Full)", description="Full hair color application.", price=80.0, duration=120, category_id=2, is_active=True),
            Service(name="Highlights", description="Partial or full highlights.", price=100.0, duration=150, category_id=2, is_active=True),
            Service(name="Styling & Blowout", description="Wash, blow-dry, and styling.", price=30.0, duration=45, category_id=3, is_active=True),
            Service(name="Beard Trim", description="Trimming and shaping of beard.", price=20.0, duration=20, category_id=1, is_active=True),
        ]
        db.add_all(services)
        db.commit()


# New functions for booking history and upcoming bookings
def get_user_booking_history(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 10
) -> List[Booking]:
    """Get past bookings for a user."""
    return db.query(Booking).filter(
        and_(
            Booking.user_id == user_id,
            Booking.end_time < datetime.now()
        )
    ).order_by(Booking.start_time.desc()).offset(skip).limit(limit).all()

def get_user_upcoming_bookings(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 10
) -> List[Booking]:
    """Get upcoming bookings for a user."""
    return db.query(Booking).filter(
        and_(
            Booking.user_id == user_id,
            Booking.end_time >= datetime.now()
        )
    ).order_by(Booking.start_time.asc()).offset(skip).limit(limit).all()

def send_booking_reminder(db: Session, booking_id: int) -> bool:
    """
    Send a reminder notification for an upcoming booking.
    This function should be called by a scheduled task (e.g., Celery) 24 hours before the booking.
    """
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.status == "CONFIRMED"
    ).first()
    
    if not booking:
        logger.warning(f"Booking {booking_id} not found or not confirmed")
        return False
    
    # Get service and stylist details
    service = db.query(Service).filter(Service.id == booking.service_id).first()
    stylist = get_stylist(db, booking.stylist_id)
    
    # Get user settings
    user_settings = db.query(UserSetting).filter(UserSetting.user_id == booking.user_id).first()
    
    if not user_settings or not user_settings.enable_booking_reminders:
        logger.info(f"User {booking.user_id} has disabled booking reminders")
        return False
    
    # Prepare notification content
    notification_title = "Booking Reminder"
    notification_message = (
        f"Reminder: You have a booking tomorrow!\n"
        f"Service: {service.name}\n"
        f"Date: {booking.start_time.strftime('%Y-%m-%d')}\n"
        f"Time: {booking.start_time.strftime('%H:%M')}\n"
        f"Stylist: {stylist.name}"
    )
    
    # Send notifications based on user preferences
    notifications_sent = False
    
    if user_settings.enable_notifications:
        create_notification(
            db=db,
            user_id=booking.user_id,
            notification_type=NotificationType.BOOKING_REMINDER,
            title=notification_title,
            message=notification_message,
            method="local"
        )
        notifications_sent = True
    
    if user_settings.enable_email_notifications:
        create_notification(
            db=db,
            user_id=booking.user_id,
            notification_type=NotificationType.BOOKING_REMINDER,
            title=notification_title,
            message=notification_message,
            method="email"
        )
        notifications_sent = True
    
    if user_settings.enable_sms_notifications:
        create_notification(
            db=db,
            user_id=booking.user_id,
            notification_type=NotificationType.BOOKING_REMINDER,
            title=notification_title,
            message=notification_message,
            method="sms"
        )
        notifications_sent = True
    
    return notifications_sent

def send_booking_feedback_request(db: Session, booking_id: int) -> bool:
    """
    Send a feedback request notification after a completed booking.
    This function should be called by a scheduled task after the booking end time.
    """
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.status == "CONFIRMED"
    ).first()
    
    if not booking:
        logger.warning(f"Booking {booking_id} not found or not confirmed")
        return False
    
    # Get service and stylist details
    service = db.query(Service).filter(Service.id == booking.service_id).first()
    stylist = get_stylist(db, booking.stylist_id)
    
    # Get user settings
    user_settings = db.query(UserSetting).filter(UserSetting.user_id == booking.user_id).first()
    
    if not user_settings:
        logger.info(f"No user settings found for user {booking.user_id}")
        return False
    
    # Prepare notification content
    notification_title = "How was your experience?"
    notification_message = (
        f"We hope you enjoyed your {service.name} with {stylist.name}!\n"
        f"Please take a moment to rate your experience and provide feedback."
    )
    
    # Send notifications based on user preferences
    notifications_sent = False
    
    if user_settings.enable_notifications:
        create_notification(
            db=db,
            user_id=booking.user_id,
            notification_type=NotificationType.FEEDBACK_REQUEST,
            title=notification_title,
            message=notification_message,
            method="local"
        )
        notifications_sent = True
    
    if user_settings.enable_email_notifications:
        create_notification(
            db=db,
            user_id=booking.user_id,
            notification_type=NotificationType.FEEDBACK_REQUEST,
            title=notification_title,
            message=notification_message,
            method="email"
        )
        notifications_sent = True
    
    if user_settings.enable_sms_notifications:
        create_notification(
            db=db,
            user_id=booking.user_id,
            notification_type=NotificationType.FEEDBACK_REQUEST,
            title=notification_title,
            message=notification_message,
            method="sms"
        )
        notifications_sent = True
    
    return notifications_sent