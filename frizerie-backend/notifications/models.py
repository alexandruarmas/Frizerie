from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, func, Enum, Boolean, JSON, Table
from sqlalchemy.orm import relationship
from config.database import Base
import enum
from datetime import datetime

class NotificationType(str, enum.Enum):
    # Booking related
    BOOKING_CONFIRMATION = "booking_confirmation"
    BOOKING_CANCELLATION = "booking_cancellation"
    BOOKING_REMINDER = "booking_reminder"
    BOOKING_MODIFICATION = "booking_modification"
    BOOKING_WAITLIST = "booking_waitlist"
    BOOKING_FEEDBACK_REQUEST = "booking_feedback_request"
    
    # Payment related
    PAYMENT_CONFIRMATION = "payment_confirmation"
    PAYMENT_FAILED = "payment_failed"
    PAYMENT_REFUND = "payment_refund"
    PAYMENT_DISPUTE = "payment_dispute"
    INVOICE_AVAILABLE = "invoice_available"
    
    # Loyalty related
    LOYALTY_POINT_UPDATE = "loyalty_point_update"
    LOYALTY_TIER_UPGRADE = "loyalty_tier_upgrade"
    LOYALTY_REWARD_AVAILABLE = "loyalty_reward_available"
    LOYALTY_POINT_EXPIRING = "loyalty_point_expiring"
    
    # Stylist related
    STYLIST_REVIEW = "stylist_review"
    STYLIST_AVAILABILITY = "stylist_availability"
    STYLIST_TIME_OFF = "stylist_time_off"
    STYLIST_CANCELLATION = "stylist_cancellation"
    
    # System related
    SYSTEM_UPDATE = "system_update"
    SECURITY_ALERT = "security_alert"
    ACCOUNT_UPDATE = "account_update"
    PASSWORD_CHANGE = "password_change"
    EMAIL_VERIFICATION = "email_verification"
    PHONE_VERIFICATION = "phone_verification"
    
    # Marketing related
    PROMOTIONAL_OFFER = "promotional_offer"
    SPECIAL_EVENT = "special_event"
    NEW_SERVICE = "new_service"
    PRICE_UPDATE = "price_update"
    HOLIDAY_HOURS = "holiday_hours"
    
    # Urgent notifications
    URGENT_ALERT = "urgent_alert"
    EMERGENCY_CLOSURE = "emergency_closure"
    LAST_MINUTE_AVAILABILITY = "last_minute_availability"

class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEB_PUSH = "web_push"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"

class NotificationPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NotificationTemplate(Base):
    """Template for notification messages."""
    __tablename__ = "notification_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    language = Column(String(10), default="en")
    subject = Column(String(255))
    body = Column(Text, nullable=False)
    variables = Column(JSON)  # List of required variables for template
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Notification(Base):
    """Enhanced notification model for user notifications."""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIUM)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    template_id = Column(Integer, ForeignKey("notification_templates.id"), nullable=True)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    notification_metadata = Column(JSON)  # Additional data specific to the notification
    error_details = Column(JSON)  # Error information if sending failed
    scheduled_for = Column(DateTime, nullable=True)  # For scheduled notifications
    expires_at = Column(DateTime, nullable=True)  # For time-sensitive notifications
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    template = relationship("NotificationTemplate")
    analytics = relationship("NotificationAnalytics", back_populates="notification", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Notification {self.id} for user {self.user_id}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type,
            "channel": self.channel,
            "priority": self.priority,
            "title": self.title,
            "message": self.message,
            "template_id": self.template_id,
            "status": self.status,
            "notification_metadata": self.notification_metadata,
            "error_details": self.error_details,
            "scheduled_for": self.scheduled_for.isoformat() if self.scheduled_for else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class NotificationPreference(Base):
    """User preferences for notifications."""
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Channel preferences
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=True)
    push_enabled = Column(Boolean, default=True)
    in_app_enabled = Column(Boolean, default=True)
    web_push_enabled = Column(Boolean, default=True)
    whatsapp_enabled = Column(Boolean, default=False)
    telegram_enabled = Column(Boolean, default=False)
    
    # Type preferences
    booking_notifications = Column(Boolean, default=True)
    payment_notifications = Column(Boolean, default=True)
    loyalty_notifications = Column(Boolean, default=True)
    stylist_notifications = Column(Boolean, default=True)
    system_notifications = Column(Boolean, default=True)
    marketing_notifications = Column(Boolean, default=False)
    urgent_notifications = Column(Boolean, default=True)
    
    # Advanced preferences
    quiet_hours_start = Column(String(5), nullable=True)  # Format: "HH:MM"
    quiet_hours_end = Column(String(5), nullable=True)  # Format: "HH:MM"
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="en")
    digest_frequency = Column(String(20), nullable=True)  # daily, weekly, none
    last_digest_sent = Column(DateTime, nullable=True)
    
    # Channel-specific settings
    email_frequency = Column(String(20), default="immediate")  # immediate, daily, weekly
    sms_frequency = Column(String(20), default="urgent_only")  # all, urgent_only, none
    push_frequency = Column(String(20), default="immediate")  # immediate, daily, none
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notification_preferences")
    
    def __repr__(self):
        return f"<NotificationPreference for user {self.user_id}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "email_enabled": self.email_enabled,
            "sms_enabled": self.sms_enabled,
            "push_enabled": self.push_enabled,
            "in_app_enabled": self.in_app_enabled,
            "web_push_enabled": self.web_push_enabled,
            "whatsapp_enabled": self.whatsapp_enabled,
            "telegram_enabled": self.telegram_enabled,
            "booking_notifications": self.booking_notifications,
            "payment_notifications": self.payment_notifications,
            "loyalty_notifications": self.loyalty_notifications,
            "stylist_notifications": self.stylist_notifications,
            "system_notifications": self.system_notifications,
            "marketing_notifications": self.marketing_notifications,
            "urgent_notifications": self.urgent_notifications,
            "quiet_hours_start": self.quiet_hours_start,
            "quiet_hours_end": self.quiet_hours_end,
            "timezone": self.timezone,
            "language": self.language,
            "digest_frequency": self.digest_frequency,
            "last_digest_sent": self.last_digest_sent.isoformat() if self.last_digest_sent else None,
            "email_frequency": self.email_frequency,
            "sms_frequency": self.sms_frequency,
            "push_frequency": self.push_frequency,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class NotificationDigest(Base):
    """Model for notification digests."""
    __tablename__ = "notification_digests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    frequency = Column(String(20), nullable=False)  # daily, weekly
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notification_digests")
    notifications = relationship("Notification", secondary="digest_notifications")
    
    def __repr__(self):
        return f"<NotificationDigest {self.id} for user {self.user_id}>"

# Association table for digest notifications
digest_notifications = Table(
    "digest_notifications",
    Base.metadata,
    Column("digest_id", Integer, ForeignKey("notification_digests.id"), primary_key=True),
    Column("notification_id", Integer, ForeignKey("notifications.id"), primary_key=True)
)

class NotificationAnalytics(Base):
    """Model for notification analytics."""
    __tablename__ = "notification_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    event_type = Column(String(50), nullable=False)  # sent, delivered, opened, clicked, etc.
    event_time = Column(DateTime, nullable=False)
    notification_metadata = Column(JSON)  # Additional analytics data
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    notification = relationship("Notification", back_populates="analytics")
    
    def __repr__(self):
        return f"<NotificationAnalytics {self.id} for notification {self.notification_id}>" 