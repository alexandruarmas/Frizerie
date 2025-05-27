from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from config.database import get_db
from auth.dependencies import get_current_user, get_current_admin
from .models import Notification, NotificationType, NotificationStatus, NotificationChannel
from .schemas import (
    NotificationCreate, NotificationResponse, NotificationUpdate,
    NotificationTemplateCreate, NotificationTemplateResponse, NotificationTemplateUpdate,
    NotificationPreferenceCreate, NotificationPreferenceResponse, NotificationPreferenceUpdate,
    NotificationDigestCreate, NotificationDigestResponse,
    NotificationSearchParams, NotificationAnalyticsParams
)
from .services import NotificationService, notify_breach_all_users

router = APIRouter(prefix="/notifications", tags=["notifications"])

# Notification endpoints
@router.post("/", response_model=NotificationResponse)
async def create_notification(
    notification: NotificationCreate,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new notification."""
    service = NotificationService(db)
    return await service.create_notification(notification, background_tasks)

@router.get("/search", response_model=List[NotificationResponse])
async def search_notifications(
    params: NotificationSearchParams = Depends(),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search notifications with various filters."""
    service = NotificationService(db)
    notifications, total = await service.search_notifications(params)
    return notifications

@router.get("/me", response_model=List[NotificationResponse])
async def get_my_notifications(
    include_read: bool = False,
    include_expired: bool = False,
    limit: int = 50,
    offset: int = 0,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notifications for the current user."""
    service = NotificationService(db)
    params = NotificationSearchParams(
        user_id=current_user.id,
        include_read=include_read,
        include_expired=include_expired,
        limit=limit,
        offset=offset
    )
    notifications, _ = await service.search_notifications(params)
    return notifications

@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific notification."""
    notification = db.query(Notification).get(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view this notification")
    return notification

@router.patch("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: int,
    notification_update: NotificationUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a notification (e.g., mark as read)."""
    notification = db.query(Notification).get(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this notification")
    
    for field, value in notification_update.dict(exclude_unset=True).items():
        setattr(notification, field, value)
    
    db.commit()
    db.refresh(notification)
    return notification

# Template endpoints
@router.post("/templates", response_model=NotificationTemplateResponse)
async def create_template(
    template: NotificationTemplateCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new notification template (admin only)."""
    service = NotificationService(db)
    return await service.create_notification_template(template)

@router.get("/templates", response_model=List[NotificationTemplateResponse])
async def get_templates(
    type: Optional[NotificationType] = None,
    channel: Optional[NotificationChannel] = None,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get notification templates (admin only)."""
    query = db.query(NotificationTemplate)
    if type:
        query = query.filter(NotificationTemplate.type == type)
    if channel:
        query = query.filter(NotificationTemplate.channel == channel)
    return query.all()

@router.patch("/templates/{template_id}", response_model=NotificationTemplateResponse)
async def update_template(
    template_id: int,
    template_update: NotificationTemplateUpdate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update a notification template (admin only)."""
    service = NotificationService(db)
    return await service.update_notification_template(template_id, template_update)

# Preference endpoints
@router.post("/preferences", response_model=NotificationPreferenceResponse)
async def create_preferences(
    preference: NotificationPreferenceCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create notification preferences for a user."""
    service = NotificationService(db)
    return await service.create_notification_preference(preference)

@router.get("/preferences/me", response_model=NotificationPreferenceResponse)
async def get_my_preferences(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notification preferences for the current user."""
    preferences = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).first()
    if not preferences:
        raise HTTPException(status_code=404, detail="Notification preferences not found")
    return preferences

@router.patch("/preferences/me", response_model=NotificationPreferenceResponse)
async def update_my_preferences(
    preference_update: NotificationPreferenceUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update notification preferences for the current user."""
    service = NotificationService(db)
    return await service.update_notification_preference(current_user.id, preference_update)

# Digest endpoints
@router.post("/digests", response_model=NotificationDigestResponse)
async def create_digest(
    digest: NotificationDigestCreate,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new notification digest."""
    service = NotificationService(db)
    return await service.create_notification_digest(digest, background_tasks)

@router.get("/digests/me", response_model=List[NotificationDigestResponse])
async def get_my_digests(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notification digests for the current user."""
    query = db.query(NotificationDigest).filter(
        NotificationDigest.user_id == current_user.id
    )
    if start_date:
        query = query.filter(NotificationDigest.start_date >= start_date)
    if end_date:
        query = query.filter(NotificationDigest.end_date <= end_date)
    return query.order_by(NotificationDigest.created_at.desc()).all()

# Analytics endpoints (admin only)
@router.get("/analytics")
async def get_analytics(
    params: NotificationAnalyticsParams = Depends(),
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get notification analytics data (admin only)."""
    service = NotificationService(db)
    return await service.get_notification_analytics(params)

@router.get("/analytics/dashboard")
async def get_analytics_dashboard(
    days: int = Query(30, ge=1, le=365),
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get notification analytics dashboard data (admin only)."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    service = NotificationService(db)
    params = NotificationAnalyticsParams(
        start_date=start_date,
        end_date=end_date,
        group_by="day"
    )
    
    analytics = await service.get_notification_analytics(params)
    
    # Add additional dashboard metrics
    total_notifications = analytics["total_sent"]
    total_users = db.query(Notification.user_id.distinct()).count()
    
    # Calculate engagement metrics
    engagement_rate = (
        analytics["total_read"] / total_notifications
        if total_notifications > 0 else 0
    )
    
    # Get top notification types
    top_types = sorted(
        analytics["type_stats"].items(),
        key=lambda x: x[1]["total_sent"],
        reverse=True
    )[:5]
    
    # Get channel performance
    channel_performance = {
        channel: stats["delivery_rate"]
        for channel, stats in analytics["channel_stats"].items()
        if stats["total_sent"] > 0
    }
    
    return {
        **analytics,
        "total_users": total_users,
        "engagement_rate": engagement_rate,
        "top_notification_types": top_types,
        "channel_performance": channel_performance,
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days
        }
    }

@router.post("/admin/breach-notification", response_model=dict)
async def send_breach_notification(
    message: str,
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin)
):
    """Admin: Send a security breach notification to all users."""
    notify_breach_all_users(db, message)
    return {"detail": "Notificare de breach trimisă la toți userii."} 