from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, func, Boolean, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from config.database import Base
from stylists.models import StylistReview
from datetime import datetime
from error_logging.models import ErrorLog

# Remove this line as it redefines Base
# Base = declarative_base()

class User(Base):
    """User model representing customers and stylists."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True, unique=True)
    vip_level = Column(String(20), default="BRONZE")
    loyalty_points = Column(Integer, default=0)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    terms_accepted = Column(Boolean, default=False)
    terms_accepted_at = Column(DateTime, nullable=True)
    
    # Relationships
    bookings = relationship("Booking", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    notification_preferences = relationship("NotificationPreference", back_populates="user", uselist=False)
    notification_digests = relationship("NotificationDigest", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    analytics_events = relationship("AnalyticsEvent", back_populates="user", foreign_keys="[AnalyticsEvent.user_id]")
    settings = relationship("UserSetting", back_populates="user")
    stylist_reviews = relationship("StylistReview", back_populates="user")
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    redemptions = relationship("LoyaltyRedemption", back_populates="user")
    points_history = relationship("LoyaltyPointsHistory", back_populates="user")
    referrals_given = relationship("ReferralProgram", 
                                 foreign_keys="ReferralProgram.referrer_id",
                                 back_populates="referrer")
    referrals_received = relationship("ReferralProgram",
                                    foreign_keys="ReferralProgram.referred_id",
                                    back_populates="referred")
    dashboards = relationship("Dashboard", back_populates="owner")
    error_logs = relationship("ErrorLog", back_populates="user")
    resolved_alerts = relationship("Alert", back_populates="resolver", foreign_keys="[Alert.resolved_by]")
    stylist_analytics_events = relationship("AnalyticsEvent", back_populates="stylist", foreign_keys="[AnalyticsEvent.stylist_id]")
    
    def __repr__(self):
        return f"<User {self.email}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone_number": self.phone_number,
            "vip_level": self.vip_level,
            "loyalty_points": self.loyalty_points,
            "is_admin": self.is_admin
        }

    def has_permission(self, resource: str, action: str) -> bool:
        """Check if user has a specific permission."""
        for role in self.roles:
            for permission in role.permissions:
                if permission.resource == resource and permission.action == action:
                    return True
        return False
    
    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        return any(role.name == role_name for role in self.roles)


class VIPTier(Base):
    """VIP Tier model for defining loyalty tiers and perks."""
    __tablename__ = "vip_tiers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True, nullable=False)  # BRONZE, SILVER, GOLD, DIAMOND
    min_points = Column(Integer, nullable=False)
    perks = Column(Text, nullable=True)  # JSON string or description
    
    def __repr__(self):
        return f"<VIPTier {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "min_points": self.min_points,
            "perks": self.perks
        }


class UserSetting(Base):
    """Model for user specific settings and preferences."""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    # Notification settings
    enable_notifications = Column(Boolean, default=True)
    enable_email_notifications = Column(Boolean, default=True)
    enable_sms_notifications = Column(Boolean, default=False)
    enable_booking_reminders = Column(Boolean, default=True)
    enable_promotional_messages = Column(Boolean, default=False)
    enable_vip_updates = Column(Boolean, default=True)
    enable_last_minute_alerts = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="settings")
    
    def __repr__(self):
        return f"<UserSetting for user {self.user_id}>"


class Role(Base):
    """Role model for role-based access control."""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")
    users = relationship("User", secondary="user_roles", back_populates="roles")
    
    def __repr__(self):
        return f"<Role {self.name}>"


class Permission(Base):
    """Permission model for granular access control."""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(200), nullable=True)
    resource = Column(String(50), nullable=False)  # e.g., 'users', 'bookings', 'services'
    action = Column(String(50), nullable=False)    # e.g., 'create', 'read', 'update', 'delete'
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")
    
    def __repr__(self):
        return f"<Permission {self.resource}:{self.action}>"


# Association tables for many-to-many relationships
class RolePermission(Base):
    """Association table for role-permission relationships."""
    __tablename__ = "role_permissions"
    
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime, default=func.now())


class UserRole(Base):
    """Association table for user-role relationships."""
    __tablename__ = "user_roles"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime, default=func.now())


class AuditLog(Base):
    """Audit log model for tracking admin actions."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # e.g., 'create', 'update', 'delete'
    resource_type = Column(String(50), nullable=False)  # e.g., 'user', 'role', 'permission'
    resource_id = Column(String(50), nullable=False)  # ID of the affected resource
    details = Column(JSON, nullable=True)  # Additional details about the action
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", backref="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog {self.action} {self.resource_type}:{self.resource_id}>"


class LoyaltyReward(Base):
    """Model for loyalty rewards that can be redeemed with points."""
    __tablename__ = "loyalty_rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    points_cost = Column(Integer, nullable=False)
    reward_type = Column(String(50), nullable=False)  # SERVICE, PRODUCT, DISCOUNT, etc.
    reward_value = Column(Float, nullable=False)  # Value of the reward (e.g., discount percentage)
    is_active = Column(Boolean, default=True)
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    min_tier_required = Column(String(20), ForeignKey("vip_tiers.name"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<LoyaltyReward {self.name}>"


class LoyaltyRedemption(Base):
    """Model for tracking loyalty point redemptions."""
    __tablename__ = "loyalty_redemptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reward_id = Column(Integer, ForeignKey("loyalty_rewards.id"), nullable=False)
    points_spent = Column(Integer, nullable=False)
    redeemed_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="PENDING")  # PENDING, COMPLETED, CANCELLED
    booking_id = Column(String(36), ForeignKey("bookings.id"), nullable=True)  # If redeemed for a service
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="redemptions")
    reward = relationship("LoyaltyReward")
    booking = relationship("Booking", back_populates="redemption")

    def __repr__(self):
        return f"<LoyaltyRedemption {self.id} - {self.user_id}>"


class LoyaltyPointsHistory(Base):
    """Model for tracking loyalty points history."""
    __tablename__ = "loyalty_points_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    points_change = Column(Integer, nullable=False)  # Can be positive or negative
    reason = Column(String(100), nullable=False)  # BOOKING, REDEMPTION, REFERRAL, etc.
    reference_id = Column(Integer, nullable=True)  # ID of related entity (booking, redemption, etc.)
    reference_type = Column(String(50), nullable=True)  # Type of reference (BOOKING, REDEMPTION, etc.)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="points_history")

    def __repr__(self):
        return f"<LoyaltyPointsHistory {self.id} - {self.user_id}>"


class ReferralProgram(Base):
    """Model for tracking referral program."""
    __tablename__ = "referral_program"
    
    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    referred_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    points_awarded = Column(Integer, nullable=False)
    status = Column(String(20), default="PENDING")  # PENDING, COMPLETED, EXPIRED
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    referrer = relationship("User", foreign_keys=[referrer_id], back_populates="referrals_given")
    referred = relationship("User", foreign_keys=[referred_id], back_populates="referrals_received")

    def __repr__(self):
        return f"<ReferralProgram {self.id} - {self.referrer_id}>"

# Add late-binding relationships
from files.models import File
User.files = relationship("File", back_populates="user") 