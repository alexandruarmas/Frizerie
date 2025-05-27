from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List, Dict, Any
from datetime import datetime
from booking.models import BookingStatus, RecurrenceType

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: constr(min_length=2, max_length=50)

class UserCreate(UserBase):
    password: constr(min_length=8)
    terms_accepted: bool

class UserUpdate(BaseModel):
    name: Optional[constr(min_length=2, max_length=50)] = None
    email: Optional[EmailStr] = None



# User Setting Schemas
class UserSettingBase(BaseModel):
    enable_notifications: Optional[bool] = True
    enable_email_notifications: Optional[bool] = True
    enable_sms_notifications: Optional[bool] = False
    enable_booking_reminders: Optional[bool] = True
    enable_promotional_messages: Optional[bool] = False
    enable_vip_updates: Optional[bool] = True

class UserSettingCreate(UserSettingBase):
    pass

class UserSettingResponse(UserSettingBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Booking Schemas
class BookingBase(BaseModel):
    user_id: int
    stylist_id: int
    service_id: int
    start_time: datetime
    end_time: datetime
    notes: Optional[str] = None
    recurrence_type: RecurrenceType = RecurrenceType.NONE
    recurrence_end_date: Optional[datetime] = None
    recurrence_pattern: Optional[Dict[str, Any]] = None

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    stylist_id: Optional[int] = None
    service_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[BookingStatus] = None
    notes: Optional[str] = None
    recurrence_type: Optional[RecurrenceType] = None
    recurrence_end_date: Optional[datetime] = None
    recurrence_pattern: Optional[Dict[str, Any]] = None
    cancellation_reason: Optional[str] = None

class BookingResponse(BookingBase):
    id: str
    status: BookingStatus
    created_at: datetime
    updated_at: datetime
    calendar_event_id: Optional[str] = None
    reminder_sent: bool
    cancellation_reason: Optional[str] = None
    cancellation_time: Optional[datetime] = None
    no_show_count: int
    last_modified_by: Optional[int] = None
    
    class Config:
        from_attributes = True

# Waitlist Schemas
class WaitlistEntryBase(BaseModel):
    user_id: int
    service_id: int
    preferred_stylist_id: Optional[int] = None
    preferred_date_range: Optional[Dict[str, Any]] = None
    priority: int = 0

class WaitlistEntryCreate(WaitlistEntryBase):
    pass

class WaitlistEntryUpdate(BaseModel):
    preferred_stylist_id: Optional[int] = None
    preferred_date_range: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None
    status: Optional[BookingStatus] = None
    expires_at: Optional[datetime] = None

class WaitlistEntryResponse(WaitlistEntryBase):
    id: str
    booking_id: str
    status: BookingStatus
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    notification_sent: bool
    
    class Config:
        from_attributes = True

# Stylist Schemas
class StylistBase(BaseModel):
    name: constr(min_length=2, max_length=50)
    specialization: str
    bio: Optional[str] = None

class StylistCreate(StylistBase):
    pass

class StylistResponse(StylistBase):
    id: int
    is_active: bool
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True

# Stylist Review Schemas
class StylistReviewBase(BaseModel):
    stylist_id: int
    rating: float
    review_text: Optional[str] = None

class StylistReviewCreate(StylistReviewBase):
    pass

class StylistReviewResponse(StylistReviewBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Service Category Schemas
class ServiceCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class ServiceCategoryCreate(ServiceCategoryBase):
    pass

class ServiceCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ServiceCategoryResponse(ServiceCategoryBase):
    id: int

    class Config:
        from_attributes = True

# Notification Schemas
class NotificationBase(BaseModel):
    message: str
    method: str

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    sent_at: datetime
    status: str
    
    class Config:
        from_attributes = True

# Service Schemas
class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    duration: int # duration in minutes
    category_id: int # ForeignKey to ServiceCategory
    is_active: Optional[bool] = True

class ServiceCreate(ServiceBase):
    pass

class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None
    resource: str
    action: str

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None

class PermissionResponse(PermissionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    permissions: List[int]  # List of permission IDs

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[int]] = None  # List of permission IDs

class RoleResponse(RoleBase):
    id: int
    permissions: List[PermissionResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserRoleUpdate(BaseModel):
    roles: List[int]  # List of role IDs

class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    resource_type: str
    resource_id: str
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Stylist Availability Schemas
class StylistAvailabilityBase(BaseModel):
    stylist_id: int
    day_of_week: int
    start_time: str
    end_time: str
    is_available: bool = True
    break_start: Optional[str] = None
    break_end: Optional[str] = None

class StylistAvailabilityCreate(StylistAvailabilityBase):
    pass

class StylistAvailabilityUpdate(BaseModel):
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    is_available: Optional[bool] = None
    break_start: Optional[str] = None
    break_end: Optional[str] = None

class StylistAvailabilityResponse(StylistAvailabilityBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Stylist Time Off Schemas
class StylistTimeOffBase(BaseModel):
    stylist_id: int
    start_date: datetime
    end_date: datetime
    reason: Optional[str] = None

class StylistTimeOffCreate(StylistTimeOffBase):
    pass

class StylistTimeOffUpdate(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    reason: Optional[str] = None
    is_approved: Optional[bool] = None

class StylistTimeOffResponse(StylistTimeOffBase):
    id: str
    is_approved: bool
    approved_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Booking Conflict Schemas
class BookingConflictBase(BaseModel):
    booking_id: str
    conflict_type: str
    conflict_details: Optional[Dict[str, Any]] = None

class BookingConflictCreate(BookingConflictBase):
    pass

class BookingConflictUpdate(BaseModel):
    resolved: Optional[bool] = None
    resolution_notes: Optional[str] = None

class BookingConflictResponse(BookingConflictBase):
    id: str
    resolved: bool
    resolution_notes: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Calendar Integration Schemas
class CalendarEventCreate(BaseModel):
    booking_id: str
    calendar_type: str  # e.g., "google", "outlook"
    event_details: Dict[str, Any]

class CalendarEventResponse(BaseModel):
    booking_id: str
    calendar_type: str
    event_id: str
    event_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Recurring Booking Schemas
class RecurringBookingCreate(BaseModel):
    base_booking: BookingCreate
    recurrence_type: RecurrenceType
    recurrence_end_date: datetime
    recurrence_pattern: Optional[Dict[str, Any]] = None

class RecurringBookingResponse(BaseModel):
    parent_booking: BookingResponse
    recurring_bookings: List[BookingResponse]
    
    class Config:
        from_attributes = True

# Booking Search and Filter Schemas
class BookingSearchParams(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    stylist_id: Optional[int] = None
    service_id: Optional[int] = None
    status: Optional[BookingStatus] = None
    user_id: Optional[int] = None
    include_recurring: bool = True

class BookingAvailabilityParams(BaseModel):
    service_id: int
    stylist_id: Optional[int] = None
    start_date: datetime
    end_date: datetime
    duration_minutes: Optional[int] = None

class TimeSlotResponse(BaseModel):
    start_time: datetime
    end_time: datetime
    stylist_id: int
    is_available: bool
    conflicting_bookings: Optional[List[BookingResponse]] = None

class LoyaltyRewardBase(BaseModel):
    name: str
    description: Optional[str] = None
    points_cost: int
    reward_type: str
    reward_value: float
    is_active: bool = True
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    min_tier_required: Optional[str] = None

class LoyaltyRewardCreate(LoyaltyRewardBase):
    pass

class LoyaltyRewardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    points_cost: Optional[int] = None
    reward_type: Optional[str] = None
    reward_value: Optional[float] = None
    is_active: Optional[bool] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    min_tier_required: Optional[str] = None

class LoyaltyRewardResponse(LoyaltyRewardBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LoyaltyRedemptionBase(BaseModel):
    reward_id: int
    points_spent: int
    notes: Optional[str] = None

class LoyaltyRedemptionCreate(LoyaltyRedemptionBase):
    pass

class LoyaltyRedemptionUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    booking_id: Optional[int] = None

class LoyaltyRedemptionResponse(LoyaltyRedemptionBase):
    id: int
    user_id: int
    redeemed_at: datetime
    status: str
    booking_id: Optional[int] = None

    class Config:
        from_attributes = True

class LoyaltyPointsHistoryBase(BaseModel):
    points_change: int
    reason: str
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None

class LoyaltyPointsHistoryCreate(LoyaltyPointsHistoryBase):
    pass

class LoyaltyPointsHistoryResponse(LoyaltyPointsHistoryBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ReferralProgramBase(BaseModel):
    referred_email: str  # Email of the person being referred

class ReferralProgramCreate(ReferralProgramBase):
    pass

class ReferralProgramUpdate(BaseModel):
    status: Optional[str] = None
    points_awarded: Optional[int] = None

class ReferralProgramResponse(BaseModel):
    id: int
    referrer_id: int
    referred_id: int
    points_awarded: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

class UserResponse(UserBase):
    id: int
    vip_level: str
    loyalty_points: int
    referrals_given: List[ReferralProgramResponse] = []
    referrals_received: List[ReferralProgramResponse] = []
    
    class Config:
        from_attributes = True    

    class Config:
        from_attributes = True

# Update LoyaltyStatus to include more detailed information
class LoyaltyStatus(BaseModel):
    tier: str
    points: int
    bookings_count: int
    next_tier: Optional[Dict[str, Any]] = None
    perks: List[str]
    points_history: List[LoyaltyPointsHistoryResponse] = []
    available_rewards: List[LoyaltyRewardResponse] = []
    recent_redemptions: List[LoyaltyRedemptionResponse] = []

    class Config:
        from_attributes = True

class AnalyticsResponse(BaseModel):
    date: datetime
    total_bookings: int
    total_revenue: float
    new_users: int
    cancellations: int

    class Config:
        from_attributes = True

class BookingStatistics(BaseModel):
    total_bookings: int
    completed_bookings: int
    cancelled_bookings: int
    no_show_bookings: int
    revenue: float
    average_booking_value: float
    period_start: datetime
    period_end: datetime

    class Config:
        from_attributes = True

class StylistPerformance(BaseModel):
    stylist_id: int
    stylist_name: str
    total_bookings: int
    completed_bookings: int
    cancelled_bookings: int
    revenue: float
    average_rating: float
    period_start: datetime
    period_end: datetime

    class Config:
        from_attributes = True

class ServicePopularity(BaseModel):
    service_id: int
    service_name: str
    total_bookings: int
    revenue: float
    average_rating: float
    period_start: datetime
    period_end: datetime

    class Config:
        from_attributes = True

class CustomerAnalytics(BaseModel):
    user_id: int
    name: str
    email: str
    total_bookings: int
    completed_bookings: int
    cancelled_bookings: int
    no_show_count: int
    total_spent: float
    average_booking_value: float
    loyalty_points: int
    last_booking_date: Optional[datetime] = None
    average_rating: Optional[float] = None

    class Config:
        from_attributes = True

class DateRangeFilter(BaseModel):
    start_date: datetime
    end_date: datetime 