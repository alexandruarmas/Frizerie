from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel

from config.database import get_db
from config.dependencies import get_current_user
from . import services
from . import models
from users.models import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])

class NotificationCreate(BaseModel):
    message: str
    method: str = "SMS"

class NotificationResponse(BaseModel):
    id: int
    message: str
    method: str
    sent_at: str
    status: str
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[Dict[str, Any]])
async def get_user_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all notifications for the current user."""
    notifications = services.get_user_notifications(db, current_user.id)
    
    return [
        {
            "id": notification.id,
            "message": notification.message,
            "method": notification.method,
            "sent_at": notification.sent_at.isoformat(),
            "status": notification.status
        } for notification in notifications
    ]

@router.post("/", response_model=Dict[str, Any])
async def create_notification(
    notification_data: NotificationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new notification for the current user."""
    notification = services.create_notification(
        db,
        current_user.id,
        notification_data.message,
        notification_data.method
    )
    
    # In a real app, we would send the notification here
    notification = services.send_notification(db, notification.id)
    
    return {
        "id": notification.id,
        "message": notification.message,
        "method": notification.method,
        "sent_at": notification.sent_at.isoformat(),
        "status": notification.status
    }

@router.get("/settings", response_model=Dict[str, Any])
async def get_notification_settings(current_user: User = Depends(get_current_user)):
    """Get notification settings for the current user."""
    # In a real app, this would be stored in the database
    # For now, return default settings
    return {
        "sms_enabled": True,
        "email_enabled": True,
        "booking_reminders": True,
        "promotional_messages": False,
        "vip_updates": True
    }

@router.put("/settings", response_model=Dict[str, Any])
async def update_notification_settings(
    settings: Dict[str, bool],
    current_user: User = Depends(get_current_user)
):
    """Update notification settings for the current user."""
    # In a real app, this would update the database
    # For now, just return the provided settings
    return settings 