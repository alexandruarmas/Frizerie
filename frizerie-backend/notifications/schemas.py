from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from .models import NotificationType, NotificationStatus, NotificationChannel, NotificationPriority

class NotificationTemplateBase(BaseModel):
    type: NotificationType
    channel: NotificationChannel
    language: str = "en"
    subject: Optional[str] = None
    body: str
    variables: Optional[List[str]] = None
    is_active: bool = True

class NotificationTemplateCreate(NotificationTemplateBase):
    pass

class NotificationTemplateUpdate(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None

class NotificationTemplateResponse(NotificationTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NotificationBase(BaseModel):
    user_id: int
    type: NotificationType
    channel: NotificationChannel
    priority: NotificationPriority = NotificationPriority.MEDIUM
    title: str
    message: str
    template_id: Optional[int] = None
    notification_metadata: Optional[Dict[str, Any]] = None
    scheduled_for: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    status: Optional[NotificationStatus] = None
    error_details: Optional[Dict[str, Any]] = None
    scheduled_for: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class NotificationResponse(NotificationBase):
    id: int
    status: NotificationStatus
    error_details: Optional[Dict[str, Any]] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NotificationPreferenceBase(BaseModel):
    # Channel preferences
    email_enabled: bool = True
    sms_enabled: bool = True
    push_enabled: bool = True
    in_app_enabled: bool = True
    web_push_enabled: bool = True
    whatsapp_enabled: bool = False
    telegram_enabled: bool = False
    
    # Type preferences
    booking_notifications: bool = True
    payment_notifications: bool = True
    loyalty_notifications: bool = True
    stylist_notifications: bool = True
    system_notifications: bool = True
    marketing_notifications: bool = False
    urgent_notifications: bool = True
    
    # Advanced preferences
    quiet_hours_start: Optional[str] = None  # Format: "HH:MM"
    quiet_hours_end: Optional[str] = None  # Format: "HH:MM"
    timezone: str = "UTC"
    language: str = "en"
    digest_frequency: Optional[str] = None  # daily, weekly, none
    
    # Channel-specific settings
    email_frequency: str = "immediate"  # immediate, daily, weekly
    sms_frequency: str = "urgent_only"  # all, urgent_only, none
    push_frequency: str = "immediate"  # immediate, daily, none

    @validator('quiet_hours_start', 'quiet_hours_end')
    def validate_time_format(cls, v):
        if v is not None:
            try:
                hours, minutes = map(int, v.split(':'))
                if not (0 <= hours <= 23 and 0 <= minutes <= 59):
                    raise ValueError
            except ValueError:
                raise ValueError('Time must be in HH:MM format')
        return v

    @validator('digest_frequency')
    def validate_digest_frequency(cls, v):
        if v is not None and v not in ['daily', 'weekly', 'none']:
            raise ValueError('Digest frequency must be daily, weekly, or none')
        return v

    @validator('email_frequency', 'push_frequency')
    def validate_frequency(cls, v):
        if v not in ['immediate', 'daily', 'weekly', 'none']:
            raise ValueError('Frequency must be immediate, daily, weekly, or none')
        return v

    @validator('sms_frequency')
    def validate_sms_frequency(cls, v):
        if v not in ['all', 'urgent_only', 'none']:
            raise ValueError('SMS frequency must be all, urgent_only, or none')
        return v

class NotificationPreferenceCreate(NotificationPreferenceBase):
    user_id: int

class NotificationPreferenceUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    web_push_enabled: Optional[bool] = None
    whatsapp_enabled: Optional[bool] = None
    telegram_enabled: Optional[bool] = None
    booking_notifications: Optional[bool] = None
    payment_notifications: Optional[bool] = None
    loyalty_notifications: Optional[bool] = None
    stylist_notifications: Optional[bool] = None
    system_notifications: Optional[bool] = None
    marketing_notifications: Optional[bool] = None
    urgent_notifications: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    digest_frequency: Optional[str] = None
    email_frequency: Optional[str] = None
    sms_frequency: Optional[str] = None
    push_frequency: Optional[str] = None

class NotificationPreferenceResponse(NotificationPreferenceBase):
    id: int
    user_id: int
    last_digest_sent: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NotificationDigestBase(BaseModel):
    user_id: int
    frequency: str  # daily, weekly
    start_date: datetime
    end_date: datetime

class NotificationDigestCreate(NotificationDigestBase):
    pass

class NotificationDigestResponse(NotificationDigestBase):
    id: int
    status: NotificationStatus
    sent_at: Optional[datetime] = None
    created_at: datetime
    notifications: List[NotificationResponse]

    class Config:
        from_attributes = True

class NotificationAnalyticsBase(BaseModel):
    notification_id: int
    channel: NotificationChannel
    event_type: str
    event_time: datetime
    notification_metadata: Optional[Dict[str, Any]] = None

class NotificationAnalyticsCreate(NotificationAnalyticsBase):
    pass

class NotificationAnalyticsResponse(NotificationAnalyticsBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationSearchParams(BaseModel):
    user_id: Optional[int] = None
    type: Optional[NotificationType] = None
    channel: Optional[NotificationChannel] = None
    status: Optional[NotificationStatus] = None
    priority: Optional[NotificationPriority] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_read: bool = True
    include_expired: bool = False
    limit: int = 50
    offset: int = 0

class NotificationAnalyticsParams(BaseModel):
    start_date: datetime
    end_date: datetime
    channel: Optional[NotificationChannel] = None
    type: Optional[NotificationType] = None
    group_by: str = "day"  # day, week, month

class NotificationAnalyticsResponse(BaseModel):
    total_sent: int
    total_delivered: int
    total_read: int
    total_failed: int
    delivery_rate: float
    read_rate: float
    average_delivery_time: float  # in seconds
    average_read_time: float  # in seconds
    channel_stats: Dict[NotificationChannel, Dict[str, Any]]
    type_stats: Dict[NotificationType, Dict[str, Any]]
    time_series: List[Dict[str, Any]] 