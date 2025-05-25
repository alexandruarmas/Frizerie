from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import datetime

from . import models
from users.models import User

def create_notification(
    db: Session,
    user_id: int,
    message: str,
    method: str = "SMS"
) -> models.Notification:
    """Create a new notification."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    notification = models.Notification(
        user_id=user_id,
        message=message,
        method=method,
        sent_at=datetime.now(),
        status="PENDING"
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    return notification

def send_notification(db: Session, notification_id: int) -> models.Notification:
    """Mark a notification as sent."""
    notification = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    
    # In a real application, this would actually send the notification via SMS or email
    # For now, we'll just mark it as sent
    notification.status = "SENT"
    db.commit()
    db.refresh(notification)
    
    return notification

def get_user_notifications(db: Session, user_id: int) -> List[models.Notification]:
    """Get all notifications for a user."""
    return db.query(models.Notification).filter(models.Notification.user_id == user_id).all()

def create_booking_notification(
    db: Session,
    user_id: int,
    booking_id: int,
    stylist_name: str,
    service_type: str,
    start_time: datetime
) -> models.Notification:
    """Create a notification for a booking."""
    # Format the date and time for the message
    formatted_date = start_time.strftime("%A, %B %d, %Y")
    formatted_time = start_time.strftime("%I:%M %p")
    
    message = f"Booking confirmed with {stylist_name} for a {service_type} on {formatted_date} at {formatted_time}."
    
    return create_notification(db, user_id, message)

def create_reminder_notification(
    db: Session,
    user_id: int,
    booking_id: int,
    stylist_name: str,
    service_type: str,
    start_time: datetime
) -> models.Notification:
    """Create a reminder notification for a booking."""
    # Format the date and time for the message
    formatted_date = start_time.strftime("%A, %B %d, %Y")
    formatted_time = start_time.strftime("%I:%M %p")
    
    message = f"Reminder: You have an appointment with {stylist_name} for a {service_type} tomorrow at {formatted_time}."
    
    return create_notification(db, user_id, message)

def create_vip_notification(db: Session, user_id: int, tier_name: str) -> models.Notification:
    """Create a notification for VIP tier upgrade."""
    message = f"Congratulations! You've been upgraded to {tier_name} VIP status. Enjoy your new perks!"
    
    return create_notification(db, user_id, message)

async def send_local_notification(recipient_id: int, message: str) -> Dict[str, Any]:
    """
    Send a local notification to a user.
    In a real app, this would save to the database and possibly trigger a WebSocket event.
    """
    # Mock implementation
    notification = {
        "id": 1,
        "recipient_id": recipient_id,
        "message": message,
        "method": "local",
        "sent_at": datetime.utcnow().isoformat(),
        "status": "sent"
    }
    
    # In a real app, you might trigger a WebSocket event here
    
    return notification

async def send_sms_notification(recipient_id: int, message: str) -> Dict[str, Any]:
    """
    Send an SMS notification to a user.
    In a real app, this would use an SMS API like Twilio.
    """
    # Mock implementation
    # In a real app, you would:
    # 1. Get the user's phone number from the database
    # 2. Use Twilio or another SMS API to send the message
    # 3. Save the notification to the database
    
    # For now, just return a mock response
    notification = {
        "id": 2,
        "recipient_id": recipient_id,
        "message": message,
        "method": "sms",
        "sent_at": datetime.utcnow().isoformat(),
        "status": "sent"
    }
    
    return notification

async def get_notifications_for_user(user_id: int, limit: int = 10) -> list:
    """
    Get recent notifications for a user.
    In a real app, this would query the database.
    """
    # Mock data
    if user_id == 1:
        return [
            {
                "id": 1,
                "message": "Your appointment has been confirmed",
                "method": "local",
                "sent_at": "2023-09-14T10:30:00",
                "status": "sent"
            },
            {
                "id": 2,
                "message": "Reminder: You have an appointment tomorrow",
                "method": "sms",
                "sent_at": "2023-09-14T15:00:00",
                "status": "sent"
            }
        ]
    return [] 