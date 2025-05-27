from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging # Import logging
import pytz
from fastapi import BackgroundTasks
import json

from . import models
from users.models import User
from external_services.email import send_email # Import email sending utility
from external_services.sms import send_sms # Import SMS sending utility
from config.settings import get_settings
from tasks.email_tasks import send_email_notification
from tasks.sms_tasks import send_sms_notification
from tasks.push_tasks import send_push_notification
from users.models import UserSetting
from .schemas import (
    NotificationCreate, NotificationUpdate, NotificationPreferenceCreate,
    NotificationPreferenceUpdate, NotificationDigestCreate, NotificationAnalyticsCreate,
    NotificationSearchParams, NotificationAnalyticsParams, NotificationTemplateCreate, NotificationTemplateUpdate
)
from .models import NotificationTemplate, NotificationDigest
from utils.email import send_email
from utils.sms import send_sms
from utils.push import send_push_notification
from utils.webpush import send_web_push
from utils.whatsapp import send_whatsapp_message
from utils.telegram import send_telegram_message
from notifications.models import NotificationPreference
from .models import Notification
from .models import NotificationAnalytics
from notifications.models import NotificationType

# Set up logging
logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    async def create_notification(
        self,
        notification: NotificationCreate,
        background_tasks: BackgroundTasks
    ) -> models.Notification:
        """Create a new notification and queue it for delivery."""
        try:
            # Get user preferences
            preferences = self.db.query(NotificationPreference).filter(
                NotificationPreference.user_id == notification.user_id
            ).first()

            if not preferences:
                # Create default preferences if none exist
                preferences = NotificationPreference(
                    user_id=notification.user_id
                )
                self.db.add(preferences)
                self.db.commit()
                self.db.refresh(preferences)

            # Check if notification type is enabled
            if not self._is_notification_type_enabled(notification.type, preferences):
                raise HTTPException(
                    status_code=400,
                    detail=f"Notifications of type {notification.type} are disabled for this user"
                )

            # Create notification
            db_notification = models.Notification(**notification.dict())
            self.db.add(db_notification)
            self.db.commit()
            self.db.refresh(db_notification)

            # Queue notification for delivery
            background_tasks.add_task(
                self._process_notification_delivery,
                db_notification.id,
                preferences
            )

            return db_notification

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating notification: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error creating notification"
            )

    async def _process_notification_delivery(
        self,
        notification_id: int,
        preferences: NotificationPreference
    ):
        """Process notification delivery based on user preferences."""
        try:
            notification = self.db.query(models.Notification).get(notification_id)
            if not notification:
                return

            # Check if notification is expired
            if notification.expires_at and notification.expires_at < datetime.utcnow():
                notification.status = models.NotificationStatus.EXPIRED
                self.db.commit()
                return

            # Check quiet hours
            if self._is_in_quiet_hours(notification, preferences):
                # Schedule for after quiet hours
                next_available = self._get_next_available_time(notification, preferences)
                notification.scheduled_for = next_available
                notification.status = models.NotificationStatus.QUEUED
                self.db.commit()
                return

            # Determine delivery channels based on preferences and priority
            channels = self._get_delivery_channels(notification, preferences)

            # Process each channel
            for channel in channels:
                try:
                    await self._send_notification(notification, channel)
                    self._log_analytics(notification, channel, "sent")
                except Exception as e:
                    logger.error(f"Error sending notification via {channel}: {str(e)}")
                    self._log_analytics(
                        notification,
                        channel,
                        "failed",
                        {"error": str(e)}
                    )

            # Update notification status
            notification.status = models.NotificationStatus.SENT
            notification.sent_at = datetime.utcnow()
            self.db.commit()

        except Exception as e:
            logger.error(f"Error processing notification delivery: {str(e)}")
            notification.status = models.NotificationStatus.FAILED
            notification.error_details = {"error": str(e)}
            self.db.commit()

    def _is_notification_type_enabled(
        self,
        notification_type: models.NotificationType,
        preferences: NotificationPreference
    ) -> bool:
        """Check if a notification type is enabled in user preferences."""
        type_mapping = {
            models.NotificationType.BOOKING_CONFIRMATION: preferences.booking_notifications,
            models.NotificationType.BOOKING_CANCELLATION: preferences.booking_notifications,
            models.NotificationType.BOOKING_REMINDER: preferences.booking_notifications,
            models.NotificationType.BOOKING_MODIFICATION: preferences.booking_notifications,
            models.NotificationType.BOOKING_WAITLIST: preferences.booking_notifications,
            models.NotificationType.BOOKING_FEEDBACK_REQUEST: preferences.booking_notifications,
            models.NotificationType.PAYMENT_CONFIRMATION: preferences.payment_notifications,
            models.NotificationType.PAYMENT_FAILED: preferences.payment_notifications,
            models.NotificationType.PAYMENT_REFUND: preferences.payment_notifications,
            models.NotificationType.PAYMENT_DISPUTE: preferences.payment_notifications,
            models.NotificationType.INVOICE_AVAILABLE: preferences.payment_notifications,
            models.NotificationType.LOYALTY_POINT_UPDATE: preferences.loyalty_notifications,
            models.NotificationType.LOYALTY_TIER_UPGRADE: preferences.loyalty_notifications,
            models.NotificationType.LOYALTY_REWARD_AVAILABLE: preferences.loyalty_notifications,
            models.NotificationType.LOYALTY_POINT_EXPIRING: preferences.loyalty_notifications,
            models.NotificationType.STYLIST_REVIEW: preferences.stylist_notifications,
            models.NotificationType.STYLIST_AVAILABILITY: preferences.stylist_notifications,
            models.NotificationType.STYLIST_TIME_OFF: preferences.stylist_notifications,
            models.NotificationType.STYLIST_CANCELLATION: preferences.stylist_notifications,
            models.NotificationType.SYSTEM_UPDATE: preferences.system_notifications,
            models.NotificationType.SECURITY_ALERT: preferences.system_notifications,
            models.NotificationType.ACCOUNT_UPDATE: preferences.system_notifications,
            models.NotificationType.PASSWORD_CHANGE: preferences.system_notifications,
            models.NotificationType.EMAIL_VERIFICATION: preferences.system_notifications,
            models.NotificationType.PHONE_VERIFICATION: preferences.system_notifications,
            models.NotificationType.PROMOTIONAL_OFFER: preferences.marketing_notifications,
            models.NotificationType.SPECIAL_EVENT: preferences.marketing_notifications,
            models.NotificationType.NEW_SERVICE: preferences.marketing_notifications,
            models.NotificationType.PRICE_UPDATE: preferences.marketing_notifications,
            models.NotificationType.HOLIDAY_HOURS: preferences.marketing_notifications,
            models.NotificationType.URGENT_ALERT: preferences.urgent_notifications,
            models.NotificationType.EMERGENCY_CLOSURE: preferences.urgent_notifications,
            models.NotificationType.LAST_MINUTE_AVAILABILITY: preferences.urgent_notifications
        }
        return type_mapping.get(notification_type, True)

    def _is_in_quiet_hours(
        self,
        notification: models.Notification,
        preferences: NotificationPreference
    ) -> bool:
        """Check if current time is within user's quiet hours."""
        if not preferences.quiet_hours_start or not preferences.quiet_hours_end:
            return False

        if notification.priority == models.NotificationPriority.URGENT:
            return False

        user_tz = pytz.timezone(preferences.timezone)
        current_time = datetime.now(user_tz).time()
        start_time = datetime.strptime(preferences.quiet_hours_start, "%H:%M").time()
        end_time = datetime.strptime(preferences.quiet_hours_end, "%H:%M").time()

        if start_time <= end_time:
            return start_time <= current_time <= end_time
        else:  # Handles overnight quiet hours
            return current_time >= start_time or current_time <= end_time

    def _get_next_available_time(
        self,
        notification: models.Notification,
        preferences: NotificationPreference
    ) -> datetime:
        """Calculate the next available time after quiet hours."""
        user_tz = pytz.timezone(preferences.timezone)
        current_time = datetime.now(user_tz)
        end_time = datetime.strptime(preferences.quiet_hours_end, "%H:%M").time()
        next_available = datetime.combine(current_time.date(), end_time)
        
        if current_time.time() > end_time:
            next_available += timedelta(days=1)
        
        return next_available.astimezone(pytz.UTC)

    def _get_delivery_channels(
        self,
        notification: models.Notification,
        preferences: NotificationPreference
    ) -> List[models.NotificationChannel]:
        """Determine which channels to use for notification delivery."""
        channels = []
        
        # Always include in-app notifications
        if preferences.in_app_enabled:
            channels.append(models.NotificationChannel.IN_APP)
        
        # Add other channels based on preferences and priority
        if notification.priority == models.NotificationPriority.URGENT:
            if preferences.sms_enabled:
                channels.append(models.NotificationChannel.SMS)
            if preferences.push_enabled:
                channels.append(models.NotificationChannel.PUSH)
            if preferences.web_push_enabled:
                channels.append(models.NotificationChannel.WEB_PUSH)
        else:
            if preferences.email_enabled:
                channels.append(models.NotificationChannel.EMAIL)
            if preferences.whatsapp_enabled:
                channels.append(models.NotificationChannel.WHATSAPP)
            if preferences.telegram_enabled:
                channels.append(models.NotificationChannel.TELEGRAM)
        
        return channels

    async def _send_notification(
        self,
        notification: models.Notification,
        channel: models.NotificationChannel
    ):
        """Send notification through the specified channel."""
        user = notification.user
        
        if channel == models.NotificationChannel.EMAIL:
            await send_email(
                email_to=user.email,
                subject=notification.title,
                body=notification.message
            )
        elif channel == models.NotificationChannel.SMS:
            await send_sms(
                phone_number=user.phone_number,
                message=notification.message
            )
        elif channel == models.NotificationChannel.PUSH:
            await send_push_notification(
                user_id=user.id,
                title=notification.title,
                message=notification.message
            )
        elif channel == models.NotificationChannel.WEB_PUSH:
            await send_web_push(
                user_id=user.id,
                title=notification.title,
                message=notification.message
            )
        elif channel == models.NotificationChannel.WHATSAPP:
            await send_whatsapp_message(
                phone_number=user.phone_number,
                message=notification.message
            )
        elif channel == models.NotificationChannel.TELEGRAM:
            await send_telegram_message(
                chat_id=user.telegram_chat_id,
                message=notification.message
            )

    def _log_analytics(
        self,
        notification: models.Notification,
        channel: models.NotificationChannel,
        event_type: str,
        notification_metadata: Optional[Dict[str, Any]] = None
    ):
        """Log notification analytics event."""
        analytics = NotificationAnalytics(
            notification_id=notification.id,
            channel=channel,
            event_type=event_type,
            event_time=datetime.utcnow(),
            notification_metadata=notification_metadata
        )
        self.db.add(analytics)
        self.db.commit()

    async def create_notification_template(
        self,
        template: NotificationTemplateCreate
    ) -> NotificationTemplate:
        """Create a new notification template."""
        try:
            db_template = NotificationTemplate(**template.dict())
            self.db.add(db_template)
            self.db.commit()
            self.db.refresh(db_template)
            return db_template
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating notification template: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error creating notification template"
            )

    async def update_notification_template(
        self,
        template_id: int,
        template_update: NotificationTemplateUpdate
    ) -> NotificationTemplate:
        """Update an existing notification template."""
        template = self.db.query(NotificationTemplate).get(template_id)
        if not template:
            raise HTTPException(
                status_code=404,
                detail="Notification template not found"
            )

        try:
            for field, value in template_update.dict(exclude_unset=True).items():
                setattr(template, field, value)
            
            self.db.commit()
            self.db.refresh(template)
            return template
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating notification template: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error updating notification template"
            )

    async def create_notification_preference(
        self,
        preference: NotificationPreferenceCreate
    ) -> NotificationPreference:
        """Create notification preferences for a user."""
        try:
            # Check if preferences already exist
            existing = self.db.query(NotificationPreference).filter(
                NotificationPreference.user_id == preference.user_id
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="Notification preferences already exist for this user"
                )

            db_preference = NotificationPreference(**preference.dict())
            self.db.add(db_preference)
            self.db.commit()
            self.db.refresh(db_preference)
            return db_preference
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating notification preferences: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error creating notification preferences"
            )

    async def update_notification_preference(
        self,
        user_id: int,
        preference_update: NotificationPreferenceUpdate
    ) -> NotificationPreference:
        """Update notification preferences for a user."""
        preference = self.db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).first()
        
        if not preference:
            raise HTTPException(
                status_code=404,
                detail="Notification preferences not found"
            )

        try:
            for field, value in preference_update.dict(exclude_unset=True).items():
                setattr(preference, field, value)
            
            self.db.commit()
            self.db.refresh(preference)
            return preference
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating notification preferences: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error updating notification preferences"
            )

    async def create_notification_digest(
        self,
        digest: NotificationDigestCreate,
        background_tasks: BackgroundTasks
    ) -> NotificationDigest:
        """Create a new notification digest."""
        try:
            # Get user preferences
            preferences = self.db.query(NotificationPreference).filter(
                NotificationPreference.user_id == digest.user_id
            ).first()
            
            if not preferences or preferences.digest_frequency != digest.frequency:
                raise HTTPException(
                    status_code=400,
                    detail="Digest frequency not enabled for this user"
                )

            # Get notifications for the digest period
            notifications = self.db.query(Notification).filter(
                and_(
                    Notification.user_id == digest.user_id,
                    Notification.created_at >= digest.start_date,
                    Notification.created_at <= digest.end_date,
                    Notification.status != NotificationStatus.READ
                )
            ).all()

            if not notifications:
                raise HTTPException(
                    status_code=400,
                    detail="No notifications available for digest"
                )

            # Create digest
            db_digest = NotificationDigest(**digest.dict())
            db_digest.notifications = notifications
            self.db.add(db_digest)
            self.db.commit()
            self.db.refresh(db_digest)

            # Queue digest for delivery
            background_tasks.add_task(
                self._process_digest_delivery,
                db_digest.id,
                preferences
            )

            return db_digest
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating notification digest: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error creating notification digest"
            )

    async def _process_digest_delivery(
        self,
        digest_id: int,
        preferences: NotificationPreference
    ):
        """Process digest delivery."""
        try:
            digest = self.db.query(NotificationDigest).get(digest_id)
            if not digest:
                return

            # Prepare digest content
            content = self._prepare_digest_content(digest)

            # Send digest through preferred channels
            if preferences.email_enabled:
                await send_email(
                    email_to=digest.user.email,
                    subject=f"Your {digest.frequency} notification digest",
                    body=content
                )

            # Mark notifications as read
            for notification in digest.notifications:
                notification.status = NotificationStatus.READ
                notification.read_at = datetime.utcnow()

            # Update digest status
            digest.status = NotificationStatus.SENT
            digest.sent_at = datetime.utcnow()
            
            # Update last digest sent time
            preferences.last_digest_sent = datetime.utcnow()
            
            self.db.commit()

        except Exception as e:
            logger.error(f"Error processing digest delivery: {str(e)}")
            digest.status = NotificationStatus.FAILED
            self.db.commit()

    def _prepare_digest_content(self, digest: NotificationDigest) -> str:
        """Prepare digest content from notifications."""
        content = []
        
        # Group notifications by type
        grouped = {}
        for notification in digest.notifications:
            if notification.type not in grouped:
                grouped[notification.type] = []
            grouped[notification.type].append(notification)
        
        # Create sections for each type
        for type_, notifications in grouped.items():
            content.append(f"\n{type_.replace('_', ' ').title()}:")
            for notification in notifications:
                content.append(f"- {notification.title}")
                if notification.message:
                    content.append(f"  {notification.message}")
        
        return "\n".join(content)

    async def search_notifications(
        self,
        params: NotificationSearchParams
    ) -> Tuple[List[Notification], int]:
        """Search notifications with various filters."""
        query = self.db.query(Notification)

        # Apply filters
        if params.user_id:
            query = query.filter(Notification.user_id == params.user_id)
        if params.type:
            query = query.filter(Notification.type == params.type)
        if params.channel:
            query = query.filter(Notification.channel == params.channel)
        if params.status:
            query = query.filter(Notification.status == params.status)
        if params.priority:
            query = query.filter(Notification.priority == params.priority)
        if params.start_date:
            query = query.filter(Notification.created_at >= params.start_date)
        if params.end_date:
            query = query.filter(Notification.created_at <= params.end_date)
        if not params.include_read:
            query = query.filter(Notification.status != NotificationStatus.READ)
        if not params.include_expired:
            query = query.filter(
                or_(
                    Notification.expires_at.is_(None),
                    Notification.expires_at > datetime.utcnow()
                )
            )

        # Get total count
        total = query.count()

        # Apply pagination
        query = query.order_by(Notification.created_at.desc())
        query = query.offset(params.offset).limit(params.limit)

        return query.all(), total

    async def get_notification_analytics(
        self,
        params: NotificationAnalyticsParams
    ) -> Dict[str, Any]:
        """Get notification analytics data."""
        try:
            # Base query for analytics
            query = self.db.query(NotificationAnalytics).filter(
                NotificationAnalytics.event_time >= params.start_date,
                NotificationAnalytics.event_time <= params.end_date
            )

            if params.channel:
                query = query.filter(NotificationAnalytics.channel == params.channel)
            if params.type:
                query = query.join(Notification).filter(Notification.type == params.type)

            # Get all analytics events
            events = query.all()

            # Calculate basic metrics
            total_sent = sum(1 for e in events if e.event_type == "sent")
            total_delivered = sum(1 for e in events if e.event_type == "delivered")
            total_read = sum(1 for e in events if e.event_type == "read")
            total_failed = sum(1 for e in events if e.event_type == "failed")

            # Calculate rates
            delivery_rate = total_delivered / total_sent if total_sent > 0 else 0
            read_rate = total_read / total_delivered if total_delivered > 0 else 0

            # Calculate average times
            delivery_times = []
            read_times = []
            for event in events:
                if event.event_type == "delivered":
                    sent_event = next(
                        (e for e in events if e.notification_id == event.notification_id and e.event_type == "sent"),
                        None
                    )
                    if sent_event:
                        delivery_times.append(
                            (event.event_time - sent_event.event_time).total_seconds()
                        )
                elif event.event_type == "read":
                    delivered_event = next(
                        (e for e in events if e.notification_id == event.notification_id and e.event_type == "delivered"),
                        None
                    )
                    if delivered_event:
                        read_times.append(
                            (event.event_time - delivered_event.event_time).total_seconds()
                        )

            average_delivery_time = sum(delivery_times) / len(delivery_times) if delivery_times else 0
            average_read_time = sum(read_times) / len(read_times) if read_times else 0

            # Calculate channel stats
            channel_stats = {}
            for channel in models.NotificationChannel:
                channel_events = [e for e in events if e.channel == channel]
                channel_stats[channel] = {
                    "total_sent": sum(1 for e in channel_events if e.event_type == "sent"),
                    "total_delivered": sum(1 for e in channel_events if e.event_type == "delivered"),
                    "total_read": sum(1 for e in channel_events if e.event_type == "read"),
                    "total_failed": sum(1 for e in channel_events if e.event_type == "failed"),
                    "delivery_rate": sum(1 for e in channel_events if e.event_type == "delivered") /
                                   sum(1 for e in channel_events if e.event_type == "sent")
                    if sum(1 for e in channel_events if e.event_type == "sent") > 0 else 0
                }

            # Calculate type stats
            type_stats = {}
            for type_ in models.NotificationType:
                type_events = [e for e in events if e.notification.type == type_]
                type_stats[type_] = {
                    "total_sent": sum(1 for e in type_events if e.event_type == "sent"),
                    "total_delivered": sum(1 for e in type_events if e.event_type == "delivered"),
                    "total_read": sum(1 for e in type_events if e.event_type == "read"),
                    "total_failed": sum(1 for e in type_events if e.event_type == "failed"),
                    "delivery_rate": sum(1 for e in type_events if e.event_type == "delivered") /
                                   sum(1 for e in type_events if e.event_type == "sent")
                    if sum(1 for e in type_events if e.event_type == "sent") > 0 else 0
                }

            # Generate time series data
            time_series = self._generate_time_series_data(events, params.group_by)

            return {
                "total_sent": total_sent,
                "total_delivered": total_delivered,
                "total_read": total_read,
                "total_failed": total_failed,
                "delivery_rate": delivery_rate,
                "read_rate": read_rate,
                "average_delivery_time": average_delivery_time,
                "average_read_time": average_read_time,
                "channel_stats": channel_stats,
                "type_stats": type_stats,
                "time_series": time_series
            }

        except Exception as e:
            logger.error(f"Error getting notification analytics: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error getting notification analytics"
            )

    def _generate_time_series_data(
        self,
        events: List[NotificationAnalytics],
        group_by: str
    ) -> List[Dict[str, Any]]:
        """Generate time series data for analytics."""
        # Group events by time period
        grouped_events = {}
        for event in events:
            if group_by == "day":
                key = event.event_time.date()
            elif group_by == "week":
                key = event.event_time.isocalendar()[:2]  # (year, week)
            else:  # month
                key = (event.event_time.year, event.event_time.month)

            if key not in grouped_events:
                grouped_events[key] = []
            grouped_events[key].append(event)

        # Generate time series data
        time_series = []
        for key, period_events in sorted(grouped_events.items()):
            if group_by == "day":
                date_str = key.isoformat()
            elif group_by == "week":
                date_str = f"{key[0]}-W{key[1]:02d}"
            else:
                date_str = f"{key[0]}-{key[1]:02d}"

            time_series.append({
                "period": date_str,
                "total_sent": sum(1 for e in period_events if e.event_type == "sent"),
                "total_delivered": sum(1 for e in period_events if e.event_type == "delivered"),
                "total_read": sum(1 for e in period_events if e.event_type == "read"),
                "total_failed": sum(1 for e in period_events if e.event_type == "failed"),
                "delivery_rate": sum(1 for e in period_events if e.event_type == "delivered") /
                               sum(1 for e in period_events if e.event_type == "sent")
                if sum(1 for e in period_events if e.event_type == "sent") > 0 else 0
            })

        return time_series

def create_notification(
    db: Session,
    user_id: int,
    notification_type: models.NotificationType,
    title: str,
    message: str,
    method: str = "local", # 'local', 'email', 'sms', 'push'
    related_resource_type: str = None,
    related_resource_id: int = None
) -> models.Notification:
    """
    Creates a new notification record in the database and triggers sending
    via the specified method.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check user notification settings
    user_settings = user.settings # Assuming user.settings is a loaded relationship or lazy loaded
    if not user_settings or (method == "email" and not user_settings.enable_email_notifications) or (method == "sms" and not user_settings.enable_sms_notifications) or (method == "local" and not user_settings.enable_notifications):
        # Don't create notification if user has opted out for this method
        print(f"User {user_id} has opted out of {method} notifications.")
        return None # Or raise a specific exception/return a different status

    # Create notification record in DB
    notification = models.Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        related_resource_type=related_resource_type,
        related_resource_id=related_resource_id
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    # Trigger sending based on method
    if method == "email":
        send_email_notification.delay(user_id, title, message)
        logger.info(f"Email notification queued for user {user_id}: {title}")
    elif method == "sms":
        # Integrate with SMS service (e.g., Twilio)
        if not user.phone_number:
            logger.warning(f"User phone number not found for SMS notification {notification.id}")
            notification.status = models.NotificationStatus.FAILED
        else:
            # Check user setting again before sending SMS
            if user_settings and user_settings.enable_sms_notifications:
                send_sms_notification.delay(user.phone_number, message)
                logger.info(f"SMS notification queued for user {user_id}: {message}")
                notification.status = models.NotificationStatus.SENT
            else:
                logger.info(f"User {user.id} has opted out of SMS notifications for notification {notification.id}.")
                notification.status = models.NotificationStatus.CANCELED
    elif method == "push":
        # Implement push notification logic here
        send_push_notification.delay(user_id, title, message)
        logger.info(f"Push notification queued for user {user_id}: {title}")
    elif method == "local":
        # Handle local notification delivery (e.g., WebSocket, in-app display) - Placeholder
        logger.info(f"Sending local notification to user {user.id}: {notification.message}")
        notification.status = models.NotificationStatus.SENT # Or DELIVERED if confirmed
    else:
        logger.warning(f"Unknown notification method: {method} for notification {notification.id}")
        notification.status = models.NotificationStatus.FAILED

    # Only set sent_at if the notification was actually sent or attempted
    if notification.status in [models.NotificationStatus.SENT, models.NotificationStatus.FAILED]:
        notification.sent_at = datetime.now()

    db.commit()
    # db.refresh(notification) # No need to refresh after commit if object is still valid

    return notification

# Synchronous function to send a notification (can be called by background task)
def send_notification_sync(db: Session, notification_id: int):
    """Process and send a notification based on its method."""
    notification = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if not notification or notification.status != models.NotificationStatus.PENDING:
        # Notification not found or already processed
        return

    user = notification.user # Assuming user relationship is loaded
    if not user:
        logger.warning(f"User not found for notification {notification_id}")
        notification.status = models.NotificationStatus.FAILED
        db.commit()
        return

    try:
        if notification.method == "email":
            if not user.email:
                logger.warning(f"User email not found for email notification {notification_id}")
                notification.status = models.NotificationStatus.FAILED
            else:
                # Use the email utility
                send_email(
                    to_email=user.email,
                    subject=notification.title,
                    body=notification.message
                )
                notification.status = models.NotificationStatus.SENT
        elif notification.method == "sms":
            # Integrate with SMS service (e.g., Twilio)
            if not user.phone_number:
                 logger.warning(f"User phone number not found for SMS notification {notification_id}")
                 notification.status = models.NotificationStatus.FAILED
            else:
                # Check user setting again before sending SMS
                user_settings = user.settings
                if user_settings and user_settings.enable_sms_notifications:
                    success, error_msg = send_sms(
                        to_phone_number=user.phone_number,
                        body=notification.message
                    )
                    if success:
                        notification.status = models.NotificationStatus.SENT
                    else:
                        logger.error(f"Failed to send SMS notification {notification_id}: {error_msg}")
                        notification.status = models.NotificationStatus.FAILED
                else:
                    logger.info(f"User {user.id} has opted out of SMS notifications for notification {notification_id}.")
                    notification.status = models.NotificationStatus.CANCELED

        elif notification.method == "local":
            # Handle local notification delivery (e.g., WebSocket, in-app display) - Placeholder
            logger.info(f"Sending local notification to user {user.id}: {notification.message}")
            # send_local(user_id=user.id, message=notification.message)
            notification.status = models.NotificationStatus.SENT # Or DELIVERED if confirmed
        else:
            logger.warning(f"Unknown notification method: {notification.method} for notification {notification.id}")
            notification.status = models.NotificationStatus.FAILED

        # Only set sent_at if the notification was actually sent or attempted
        if notification.status in [models.NotificationStatus.SENT, models.NotificationStatus.FAILED]:
             notification.sent_at = datetime.now()

        db.commit()
        # db.refresh(notification) # No need to refresh after commit if object is still valid

    except Exception as e:
        logger.error(f"Error sending notification {notification.id}: {e}", exc_info=True)
        notification.status = models.NotificationStatus.FAILED
        # notification.sent_at = datetime.now() # Consider if sent_at should be set on failure
        db.commit()
        # db.refresh(notification)

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

def get_user_notifications(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    unread_only: bool = False
) -> List[models.Notification]:
    """Get notifications for a user."""
    query = db.query(models.Notification).filter(models.Notification.user_id == user_id)
    
    if unread_only:
        query = query.filter(models.Notification.read_at.is_(None))
    
    return query.order_by(models.Notification.created_at.desc()).offset(skip).limit(limit).all()

def mark_notification_as_read(
    db: Session,
    notification_id: int,
    user_id: int
) -> models.Notification:
    """Mark a notification as read."""
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.user_id == user_id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.read_at = datetime.now()
    db.commit()
    db.refresh(notification)
    
    return notification

def mark_all_notifications_as_read(
    db: Session,
    user_id: int
) -> int:
    """Mark all notifications as read for a user."""
    result = db.query(models.Notification).filter(
        models.Notification.user_id == user_id,
        models.Notification.read_at.is_(None)
    ).update({"read_at": datetime.now()})
    
    db.commit()
    return result

def delete_notification(
    db: Session,
    notification_id: int,
    user_id: int
) -> bool:
    """Delete a notification."""
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.user_id == user_id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    db.delete(notification)
    db.commit()
    return True

def create_booking_notification(
    db: Session,
    user_id: int,
    booking_id: int,
    notification_type: models.NotificationType,
    title: str,
    message: str
) -> Optional[models.Notification]: # Can return None if user opts out
    """Create a booking-related notification."""
    return create_notification(
        db=db,
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        message=message,
        method="email"  # Booking notifications are typically sent via email
    )

def create_vip_notification(
    db: Session,
    user_id: int,
    new_tier: str,
    perks: str
) -> Optional[models.Notification]: # Can return None if user opts out
    """Create a VIP upgrade notification."""
    return create_notification(
        db=db,
        user_id=user_id,
        notification_type=models.NotificationType.VIP_UPGRADE,
        title=f"VIP Upgrade to {new_tier}",
        message=f"Congratulations! You've been upgraded to {new_tier} tier. Your new perks include: {perks}",
        method="email"
    )

def create_loyalty_points_notification(
    db: Session,
    user_id: int,
    points: int,
    reason: str
) -> Optional[models.Notification]: # Can return None if user opts out
    """Create a loyalty points notification."""
    return create_notification(
        db=db,
        user_id=user_id,
        notification_type=models.NotificationType.LOYALTY_POINTS,
        title="Loyalty Points Update",
        message=f"You've earned {points} loyalty points for {reason}",
        method="local" # Loyalty points updates can be local notifications
    )

def send_last_minute_availability_notifications(
    db: Session,
    booking_details: dict
):
    """
    Sends notifications to users who have opted in for last-minute availability alerts.
    """
    logger.info(f"Attempting to send last-minute availability notifications for cancelled booking.")

    # Find users who have enabled last-minute availability alerts
    users_to_notify = db.query(User).join(UserSetting).filter(UserSetting.enable_last_minute_alerts == True).all()

    if not users_to_notify:
        logger.info("No users have enabled last-minute availability alerts.")
        return

    notification_title = "Last Minute Availability!"
    notification_message = (
        f"A slot has opened up for {booking_details['service_name']} "
        f"with {booking_details['stylist_name']} on "
        f"{booking_details['date']} at {booking_details['time']}. Book now!"
    )

    for user in users_to_notify:
        # Get user settings to determine preferred notification methods
        user_settings = user.settings
        if user_settings:
            if user_settings.enable_notifications:
                 create_notification(
                    db=db,
                    user_id=user.id,
                    notification_type=models.NotificationType.LAST_MINUTE_AVAILABILITY,
                    title=notification_title,
                    message=notification_message,
                    method="local"
                )
            if user_settings.enable_email_notifications:
                 create_notification(
                    db=db,
                    user_id=user.id,
                    notification_type=models.NotificationType.LAST_MINUTE_AVAILABILITY,
                    title=notification_title,
                    message=notification_message,
                    method="email"
                )
            if user_settings.enable_sms_notifications:
                 create_notification(
                    db=db,
                    user_id=user.id,
                    notification_type=models.NotificationType.LAST_MINUTE_AVAILABILITY,
                    title=notification_title,
                    message=notification_message,
                    method="sms"
                )
        else:
            logger.warning(f"User {user.id} has no settings. Cannot send notifications.")

    logger.info(f"Sent last-minute availability notifications to {len(users_to_notify)} users.")

def send_promotional_or_event_notification(
    db: Session,
    notification_type: models.NotificationType, # Should be PROMOTIONAL_OFFER or SPECIAL_EVENT
    title: str,
    message: str,
    # Optional filtering criteria could be added here later (e.g., target_user_ids: List[int] = None)
):
    """
    Sends promotional offer or special event notifications to users who have opted in.
    This function is intended to be called by an administrator interface or a marketing tool.
    """
    if notification_type not in [models.NotificationType.PROMOTIONAL_OFFER, models.NotificationType.SPECIAL_EVENT]:
        logger.warning(f"Attempted to send notification with invalid type: {notification_type}")
        return

    logger.info(f"Attempting to send {notification_type} notifications.")

    # Find users who have enabled promotional messages
    # In a real app, you might add more complex filtering here
    users_to_notify = db.query(User).join(UserSetting).filter(UserSetting.enable_promotional_messages == True).all()

    if not users_to_notify:
        logger.info(f"No users have enabled promotional messages. Skipping {notification_type} notifications.")
        return

    sent_count = 0
    for user in users_to_notify:
        # Get user settings to determine preferred notification methods
        user_settings = user.settings
        if user_settings:
            # Create notification for each enabled method
            if user_settings.enable_notifications:
                 create_notification(
                    db=db,
                    user_id=user.id,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    method="local"
                )
                 sent_count += 1
            if user_settings.enable_email_notifications:
                 create_notification(
                    db=db,
                    user_id=user.id,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    method="email"
                )
                 sent_count += 1
            if user_settings.enable_sms_notifications:
                 create_notification(
                    db=db,
                    user_id=user.id,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    method="sms"
                )
                 sent_count += 1
            # Add push notifications here if implemented
            # if user_settings.enable_push_notifications:
            #     create_notification(...

        else:
            logger.warning(f"User {user.id} has no settings. Cannot send promotional notifications.")

    logger.info(f"Attempted to send {notification_type} notifications to {len(users_to_notify)} users. Total notifications created: {sent_count}.")

def send_urgent_alert(
    db: Session,
    title: str,
    message: str,
    # Optional filtering criteria could be added later (e.g., target_user_ids: List[int] = None)
):
    """
    Sends urgent alerts to all active users, bypassing individual notification settings.
    This function is intended to be called by an administrator interface for critical announcements.
    """
    logger.info("Attempting to send urgent alerts to all active users.")

    # Find all active users
    # In a real app, you might consider if urgent alerts should go to inactive users too
    users_to_notify = db.query(User).filter(User.is_active == True).all() # Assuming User model has an is_active flag

    if not users_to_notify:
        logger.info("No active users found to send urgent alerts.")
        return

    sent_count = 0
    for user in users_to_notify:
        # For urgent alerts, we bypass individual notification settings
        # and attempt to send via all available methods.

        # Attempt to send local notification
        try:
            create_notification(
                db=db,
                user_id=user.id,
                notification_type=models.NotificationType.URGENT_ALERT,
                title=title,
                message=message,
                method="local"
            )
            sent_count += 1
        except Exception as e:
            logger.error(f"Failed to create local urgent alert for user {user.id}: {e}")

        # Attempt to send email notification (if user has email)
        if user.email:
            try:
                create_notification(
                    db=db,
                    user_id=user.id,
                    notification_type=models.NotificationType.URGENT_ALERT,
                    title=title,
                    message=message,
                    method="email"
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to create email urgent alert for user {user.id}: {e}")

        # Attempt to send SMS notification (if user has phone number)
        if user.phone_number:
            try:
                create_notification(
                    db=db,
                    user_id=user.id,
                    notification_type=models.NotificationType.URGENT_ALERT,
                    title=title,
                    message=message,
                    method="sms"
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to create SMS urgent alert for user {user.id}: {e}")

        # Add push notifications here if implemented
        # if user.push_token:
        #     try:
        #         create_notification(
        #             db=db,
        #             user_id=user.id,
        #             notification_type=models.NotificationType.URGENT_ALERT,
        #             title=title,
        #             message=message,
        #             method="push"
        #         )
        #         sent_count += 1
        #     except Exception as e:
        #         logger.error(f"Failed to create push urgent alert for user {user.id}: {e}")

    logger.info(f"Attempted to send urgent alerts to {len(users_to_notify)} users. Total notifications created: {sent_count}.")

def notify_breach_all_users(db, message: str):
    users = db.query(User).all()
    for user in users:
        create_notification(
            db=db,
            user_id=user.id,
            notification_type=NotificationType.SECURITY if hasattr(NotificationType, 'SECURITY') else 'SECURITY',
            title="Important: Incident de securitate",
            message=message,
            method="email"
        )
    db.commit()
    print(f"Notificare trimisă la {len(users)} useri.")

# Remove or update existing async send functions if they are not needed anymore
# async def send_local_notification(recipient_id: int, message: str) -> Dict[str, Any]:
#    ...
# async def send_sms_notification(recipient_id: int, message: str) -> Dict[str, Any]:
#    ...
# async def get_notifications_for_user(user_id: int, limit: int = 10) -> list:
#    ... 