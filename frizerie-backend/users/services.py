from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request
from typing import Optional, List, Dict, Any, Union
import json
from . import models
from auth.services import get_password_hash
from validation.schemas import UserCreate, UserUpdate, RoleCreate, RoleUpdate, PermissionCreate, PermissionUpdate, UserRoleUpdate
from notifications.services import create_notification # Import create_notification
from notifications.models import NotificationType # Import NotificationType enum
from .models import UserSetting, User, Role, Permission, RolePermission, UserRole, AuditLog
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from datetime import datetime

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get a user by email."""
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """Get a user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user_data: UserCreate) -> models.User:
    """Create a new user."""
    try:
        # Check if user already exists
        existing_user = get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if not user_data.terms_accepted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trebuie să accepți Termenii și Politica de Confidențialitate."
            )
        
        # Hash the password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user
        user = models.User(
            email=user_data.email,
            password_hash=hashed_password,
            name=user_data.name,
            vip_level="BRONZE",
            loyalty_points=0,
            terms_accepted=True,
            terms_accepted_at=datetime.utcnow()
        )
        
        # Add to database
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    except Exception as e:
        print("ERROR IN CREATE_USER SERVICE:", str(e))
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def calculate_vip_tier(loyalty_points: int) -> str:
    """Calculate VIP tier based on loyalty points."""
    if loyalty_points >= 1000:
        return "DIAMOND"
    elif loyalty_points >= 500:
        return "GOLD"
    elif loyalty_points >= 200:
        return "SILVER"
    else:
        return "BRONZE"

def update_user_loyalty(db: Session, user_id: int, points_to_add: int) -> models.User:
    """Update user loyalty points and tier."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    old_vip_level = user.vip_level
    old_loyalty_points = user.loyalty_points
    
    # Update points
    user.loyalty_points += points_to_add
    
    # Update VIP level
    new_vip_level = calculate_vip_tier(user.loyalty_points)
    user.vip_level = new_vip_level
    
    # Save changes
    db.commit()
    db.refresh(user)
    
    # --- Notification Triggering ---
    user_settings = user.settings
    if user_settings:
        # Notify about loyalty points update
        if points_to_add != 0:
            notification_title = "Loyalty Points Updated"
            notification_message = f"You have received {points_to_add} loyalty points. Your new balance is {user.loyalty_points} points."
            if user_settings.enable_local_notifications:
                create_notification(
                    db=db,
                    user_id=user_id,
                    notification_type=NotificationType.LOYALTY_POINTS,
                    title=notification_title,
                    message=notification_message,
                    method="local"
                )
            if user_settings.enable_email_notifications:
                create_notification(
                    db=db,
                    user_id=user_id,
                    notification_type=NotificationType.LOYALTY_POINTS,
                    title=notification_title,
                    message=notification_message,
                    method="email"
                )
            if user_settings.enable_sms_notifications:
                create_notification(
                    db=db,
                    user_id=user_id,
                    notification_type=NotificationType.LOYALTY_POINTS,
                    title=notification_title,
                    message=notification_message,
                    method="sms"
                )

        # Notify about VIP tier change
        if new_vip_level != old_vip_level:
            new_tier_info = get_vip_tier_info(db, new_vip_level)
            perks = json.loads(new_tier_info.perks) if new_tier_info and new_tier_info.perks else "None listed."
            notification_title = "VIP Tier Upgrade"
            notification_message = f"Congratulations! You've been upgraded to the {new_vip_level} tier! Perks: {perks}"
            if user_settings.enable_local_notifications:
                create_notification(
                    db=db,
                    user_id=user_id,
                    notification_type=NotificationType.VIP_UPGRADE,
                    title=notification_title,
                    message=notification_message,
                    method="local"
                )
            if user_settings.enable_email_notifications:
                create_notification(
                    db=db,
                    user_id=user_id,
                    notification_type=NotificationType.VIP_UPGRADE,
                    title=notification_title,
                    message=notification_message,
                    method="email"
                )
            if user_settings.enable_sms_notifications:
                create_notification(
                    db=db,
                    user_id=user_id,
                    notification_type=NotificationType.VIP_UPGRADE,
                    title=notification_title,
                    message=notification_message,
                    method="sms"
                )
    # --- End Notification Triggering ---
    
    return user

def get_loyalty_status(db: Session, user_id: int) -> Dict[str, Any]:
    """Get detailed loyalty status for a user."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get VIP tier information
    tier = user.vip_level
    points = user.loyalty_points
    
    # Calculate next tier and points needed
    next_tier = None
    points_to_next_tier = 0
    
    if tier == "BRONZE":
        next_tier = {
            "name": "SILVER",
            "points_needed": 200 - points,
            "bookings_needed": max(0, 5 - (points // 40))  # Assuming 40 points per booking
        }
    elif tier == "SILVER":
        next_tier = {
            "name": "GOLD",
            "points_needed": 500 - points,
            "bookings_needed": max(0, 8 - (points // 40))
        }
    elif tier == "GOLD":
        next_tier = {
            "name": "DIAMOND",
            "points_needed": 1000 - points,
            "bookings_needed": max(0, 15 - (points // 40))
        }
    
    # Get perks based on tier
    perks = []
    if tier in ["SILVER", "GOLD", "DIAMOND"]:
        perks.append("Priority booking (24h advance)")
    if tier in ["GOLD", "DIAMOND"]:
        perks.append("10% discount on all services")
        perks.append("Free styling products")
    if tier == "DIAMOND":
        perks.append("Exclusive event access")
        perks.append("Personal stylist consultation")
        perks.append("Birthday month special treatment")
    
    # Get recent points history
    points_history = get_points_history(db, user_id, limit=5)
    
    # Get available rewards
    available_rewards = get_available_rewards(db, user_id)
    
    # Get recent redemptions
    recent_redemptions = db.query(models.LoyaltyRedemption).filter(
        models.LoyaltyRedemption.user_id == user_id
    ).order_by(
        models.LoyaltyRedemption.redeemed_at.desc()
    ).limit(5).all()
    
    # Get bookings count
    bookings_count = db.query(models.Booking).filter(
        models.Booking.user_id == user_id,
        models.Booking.status == "COMPLETED"
    ).count()
    
    return {
        "tier": tier,
        "points": points,
        "bookings_count": bookings_count,
        "next_tier": next_tier,
        "perks": perks,
        "points_history": points_history,
        "available_rewards": available_rewards,
        "recent_redemptions": recent_redemptions
    }

def get_available_rewards(db: Session, user_id: int) -> List[models.LoyaltyReward]:
    """Get available rewards for a user based on their tier and points."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get rewards that are active and available for user's tier
    rewards = db.query(models.LoyaltyReward).filter(
        models.LoyaltyReward.is_active == True,
        models.LoyaltyReward.points_cost <= user.loyalty_points,
        or_(
            models.LoyaltyReward.min_tier_required == None,
            models.LoyaltyReward.min_tier_required == user.vip_level
        ),
        or_(
            models.LoyaltyReward.valid_until == None,
            models.LoyaltyReward.valid_until > datetime.utcnow()
        )
    ).all()
    
    return rewards

def redeem_reward(
    db: Session,
    user_id: int,
    reward_id: int,
    booking_id: Optional[int] = None
) -> models.LoyaltyRedemption:
    """Redeem a loyalty reward for points."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    reward = db.query(models.LoyaltyReward).filter(
        models.LoyaltyReward.id == reward_id,
        models.LoyaltyReward.is_active == True
    ).first()
    
    if not reward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reward not found or inactive"
        )
    
    # Validate user can redeem this reward
    if reward.points_cost > user.loyalty_points:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough points to redeem this reward"
        )
    
    if reward.min_tier_required and reward.min_tier_required != user.vip_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This reward requires {reward.min_tier_required} tier"
        )
    
    if reward.valid_until and reward.valid_until < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This reward has expired"
        )
    
    # Create redemption record
    redemption = models.LoyaltyRedemption(
        user_id=user_id,
        reward_id=reward_id,
        points_spent=reward.points_cost,
        booking_id=booking_id,
        status="PENDING"
    )
    
    # Deduct points and create history record
    user.loyalty_points -= reward.points_cost
    points_history = models.LoyaltyPointsHistory(
        user_id=user_id,
        points_change=-reward.points_cost,
        reason="REWARD_REDEMPTION",
        reference_id=redemption.id,
        reference_type="REDEMPTION"
    )
    
    db.add(redemption)
    db.add(points_history)
    db.commit()
    db.refresh(redemption)
    
    # Send notification
    user_settings = user.settings
    if user_settings:
        notification_title = "Reward Redeemed"
        notification_message = f"You have successfully redeemed {reward.name} for {reward.points_cost} points."
        if user_settings.enable_local_notifications:
            create_notification(
                db=db,
                user_id=user_id,
                notification_type=NotificationType.LOYALTY_REWARD,
                title=notification_title,
                message=notification_message,
                method="local"
            )
        if user_settings.enable_email_notifications:
            create_notification(
                db=db,
                user_id=user_id,
                notification_type=NotificationType.LOYALTY_REWARD,
                title=notification_title,
                message=notification_message,
                method="email"
            )
    
    return redemption

def get_points_history(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 10
) -> List[models.LoyaltyPointsHistory]:
    """Get user's points history."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    history = db.query(models.LoyaltyPointsHistory).filter(
        models.LoyaltyPointsHistory.user_id == user_id
    ).order_by(
        models.LoyaltyPointsHistory.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return history

def create_referral(
    db: Session,
    referrer_id: int,
    referred_email: str
) -> models.ReferralProgram:
    """Create a new referral."""
    referrer = get_user_by_id(db, referrer_id)
    if not referrer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referrer not found"
        )
    
    # Check if referred email exists
    referred = get_user_by_email(db, referred_email)
    if not referred:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referred user not found"
        )
    
    # Check if referral already exists
    existing_referral = db.query(models.ReferralProgram).filter(
        models.ReferralProgram.referrer_id == referrer_id,
        models.ReferralProgram.referred_id == referred.id
    ).first()
    
    if existing_referral:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Referral already exists"
        )
    
    # Create referral
    referral = models.ReferralProgram(
        referrer_id=referrer_id,
        referred_id=referred.id,
        points_awarded=50,  # Default points for referral
        status="PENDING"
    )
    
    db.add(referral)
    db.commit()
    db.refresh(referral)
    
    # Send notifications
    for user_id, is_referrer in [(referrer_id, True), (referred.id, False)]:
        user = get_user_by_id(db, user_id)
        if user and user.settings:
            notification_title = "New Referral" if is_referrer else "You've Been Referred"
            notification_message = (
                f"You have referred {referred.name} to our salon!" if is_referrer
                else f"{referrer.name} has referred you to our salon!"
            )
            
            if user.settings.enable_local_notifications:
                create_notification(
                    db=db,
                    user_id=user_id,
                    notification_type=NotificationType.REFERRAL,
                    title=notification_title,
                    message=notification_message,
                    method="local"
                )
            if user.settings.enable_email_notifications:
                create_notification(
                    db=db,
                    user_id=user_id,
                    notification_type=NotificationType.REFERRAL,
                    title=notification_title,
                    message=notification_message,
                    method="email"
                )
    
    return referral

def complete_referral(
    db: Session,
    referral_id: int
) -> models.ReferralProgram:
    """Complete a referral and award points."""
    referral = db.query(models.ReferralProgram).filter(
        models.ReferralProgram.id == referral_id
    ).first()
    
    if not referral:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral not found"
        )
    
    if referral.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Referral is not pending"
        )
    
    # Update referral status
    referral.status = "COMPLETED"
    referral.completed_at = datetime.utcnow()
    
    # Award points to referrer
    referrer = get_user_by_id(db, referral.referrer_id)
    if referrer:
        referrer.loyalty_points += referral.points_awarded
        
        # Create points history record
        points_history = models.LoyaltyPointsHistory(
            user_id=referrer.id,
            points_change=referral.points_awarded,
            reason="REFERRAL_COMPLETED",
            reference_id=referral.id,
            reference_type="REFERRAL"
        )
        db.add(points_history)
        
        # Send notification
        if referrer.settings:
            notification_title = "Referral Completed"
            notification_message = f"You have earned {referral.points_awarded} points for your referral!"
            if referrer.settings.enable_local_notifications:
                create_notification(
                    db=db,
                    user_id=referrer.id,
                    notification_type=NotificationType.REFERRAL,
                    title=notification_title,
                    message=notification_message,
                    method="local"
                )
            if referrer.settings.enable_email_notifications:
                create_notification(
                    db=db,
                    user_id=referrer.id,
                    notification_type=NotificationType.REFERRAL,
                    title=notification_title,
                    message=notification_message,
                    method="email"
                )
    
    db.commit()
    db.refresh(referral)
    return referral

def get_vip_tiers(db: Session) -> List[models.VIPTier]:
    """Get all VIP tiers."""
    return db.query(models.VIPTier).order_by(models.VIPTier.min_points).all()

def update_user(db: Session, user_id: int, user_data: Dict[str, Any]) -> models.User:
    """Update user information."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    for key, value in user_data.items():
        if hasattr(user, key) and key != "id" and key != "password_hash":
            setattr(user, key, value)
    
    # Save changes
    db.commit()
    db.refresh(user)
    
    return user

def add_loyalty_points(db: Session, user_id: int, points: int) -> models.User:
    """Add loyalty points to a user and update VIP level if needed."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    old_vip_level = user.vip_level
    
    # Add points
    user.loyalty_points += points
    
    # Check and update VIP level
    vip_tier = db.query(models.VIPTier).filter(
        models.VIPTier.min_points <= user.loyalty_points
    ).order_by(models.VIPTier.min_points.desc()).first()
    
    new_vip_level = user.vip_level # Default to current level
    if vip_tier and vip_tier.name != user.vip_level:
        user.vip_level = vip_tier.name
        new_vip_level = user.vip_level # Update if tier changed
    
    db.commit()
    db.refresh(user)
    
    # --- Notification Triggering ---
    user_settings = user.settings
    if user_settings:
        # Notify about loyalty points added
        if points > 0:
            notification_title = "Loyalty Points Added"
            notification_message = f"You have received {points} loyalty points. Your new balance is {user.loyalty_points} points."
            if user_settings.enable_local_notifications:
                create_notification(
                    db=db,
                    user_id=user_id,
                    notification_type=NotificationType.LOYALTY_POINTS,
                    title=notification_title,
                    message=notification_message,
                    method="local"
                )
            if user_settings.enable_email_notifications:
                create_notification(
                    db=db,
                    user_id=user_id,
                    notification_type=NotificationType.LOYALTY_POINTS,
                    title=notification_title,
                    message=notification_message,
                    method="email"
                )
            if user_settings.enable_sms_notifications:
                create_notification(
                    db=db,
                    user_id=user_id,
                    notification_type=NotificationType.LOYALTY_POINTS,
                    title=notification_title,
                    message=notification_message,
                    method="sms"
                )

        # Notify about VIP tier change
        if new_vip_level != old_vip_level:
            new_tier_info = get_vip_tier_info(db, new_vip_level)
            perks = json.loads(new_tier_info.perks) if new_tier_info and new_tier_info.perks else "None listed."
            notification_title = "VIP Tier Upgrade"
            notification_message = f"Congratulations! You've been upgraded to the {new_vip_level} tier! Perks: {perks}"
            if user_settings.enable_local_notifications:
                create_notification(
                    db=db,
                    user_id=user_id,
                    notification_type=NotificationType.VIP_UPGRADE,
                    title=notification_title,
                    message=notification_message,
                    method="local"
                )
            if user_settings.enable_email_notifications:
                create_notification(
                    db=db,
                    user_id=user_id,
                    notification_type=NotificationType.VIP_UPGRADE,
                    title=notification_title,
                    message=notification_message,
                    method="email"
                )
            if user_settings.enable_sms_notifications:
                create_notification(
                    db=db,
                    user_id=user_id,
                    notification_type=NotificationType.VIP_UPGRADE,
                    title=notification_title,
                    message=notification_message,
                    method="sms"
                )
    # --- End Notification Triggering ---
    
    return user

def get_vip_tier_info(db: Session, tier_name: str) -> Optional[models.VIPTier]:
    """Get information about a specific VIP tier."""
    return db.query(models.VIPTier).filter(models.VIPTier.name == tier_name).first()

def get_all_vip_tiers(db: Session) -> List[models.VIPTier]:
    """Get all VIP tiers ordered by minimum points."""
    return db.query(models.VIPTier).order_by(models.VIPTier.min_points).all()

def create_vip_tier(
    db: Session,
    name: str,
    min_points: int,
    perks: str
) -> models.VIPTier:
    """Create a new VIP tier."""
    # Check if tier already exists
    existing_tier = get_vip_tier_info(db, name)
    if existing_tier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="VIP tier already exists"
        )
    
    # Create tier
    tier = models.VIPTier(
        name=name,
        min_points=min_points,
        perks=perks
    )
    
    db.add(tier)
    db.commit()
    db.refresh(tier)
    return tier

def update_vip_tier(
    db: Session,
    tier_name: str,
    tier_data: Dict[str, Any]
) -> models.VIPTier:
    """Update a VIP tier."""
    tier = get_vip_tier_info(db, tier_name)
    if not tier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VIP tier not found"
        )
    
    # Update tier fields
    for key, value in tier_data.items():
        if hasattr(tier, key) and key != "id":
            setattr(tier, key, value)
    
    db.commit()
    db.refresh(tier)
    return tier

def get_user_settings(db: Session, user_id: int) -> models.UserSetting:
    """Get user settings, create default if none exist."""
    settings = db.query(models.UserSetting).filter(models.UserSetting.user_id == user_id).first()
    if not settings:
        # Create default settings if they don't exist
        settings = models.UserSetting(user_id=user_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

def update_user_settings(
    db: Session,
    user_id: int,
    settings_data: Dict[str, Any]
) -> models.UserSetting:
    """Update user settings."""
    settings = get_user_settings(db, user_id)

    for key, value in settings_data.items():
        if hasattr(settings, key) and key != "id" and key != "user_id":
            setattr(settings, key, value)

    db.commit()
    db.refresh(settings)
    return settings

# New admin service functions for user management
def get_all_users(
    db: Session,
    skip: int = 0,
    limit: int = 10
) -> List[models.User]:
    """Get a list of all users."""
    return db.query(models.User).offset(skip).limit(limit).all()

def admin_create_user(
    db: Session,
    user_data: UserCreate,
    is_admin: bool = False
) -> models.User:
    """Admin function to create a new user with optional admin status."""
    # Check if user already exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password
    hashed_password = get_password_hash(user_data.password)

    # Create user
    user = models.User(
        email=user_data.email,
        password_hash=hashed_password,
        name=user_data.name,
        vip_level="BRONZE", # Default VIP level
        loyalty_points=0,
        is_admin=is_admin
    )

    # Add to database
    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def admin_update_user(
    db: Session,
    user_id: int,
    user_data: UserUpdate
) -> models.User:
    """Admin function to update user information."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update user fields
    update_data = user_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(user, key) and key != "id" and key != "password_hash":
            setattr(user, key, value)

    # Save changes
    db.commit()
    db.refresh(user)

    return user

def admin_delete_user(
    db: Session,
    user_id: int
) -> Dict[str, bool]:
    """Admin function to delete a user."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {"success": True} 

def create_permission(
    db: Session,
    permission_data: PermissionCreate
) -> Permission:
    """Create a new permission."""
    try:
        permission = Permission(**permission_data.dict())
        db.add(permission)
        db.commit()
        db.refresh(permission)
        return permission
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission already exists"
        )

def get_permission(db: Session, permission_id: int) -> Optional[Permission]:
    """Get a permission by ID."""
    return db.query(Permission).filter(Permission.id == permission_id).first()

def get_permission_by_name(db: Session, name: str) -> Optional[Permission]:
    """Get a permission by name."""
    return db.query(Permission).filter(Permission.name == name).first()

def get_all_permissions(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Permission]:
    """Get all permissions."""
    return db.query(Permission).offset(skip).limit(limit).all()

def update_permission(
    db: Session,
    permission_id: int,
    permission_data: PermissionUpdate
) -> Permission:
    """Update a permission."""
    permission = get_permission(db, permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    update_data = permission_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(permission, key, value)
    
    try:
        db.commit()
        db.refresh(permission)
        return permission
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission name already exists"
        )

def delete_permission(db: Session, permission_id: int) -> bool:
    """Delete a permission."""
    permission = get_permission(db, permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    db.delete(permission)
    db.commit()
    return True

def create_role(
    db: Session,
    role_data: RoleCreate
) -> Role:
    """Create a new role with permissions."""
    try:
        # Create role
        role = Role(
            name=role_data.name,
            description=role_data.description
        )
        db.add(role)
        db.flush()  # Get role ID without committing
        
        # Add permissions
        for permission_id in role_data.permissions:
            permission = get_permission(db, permission_id)
            if not permission:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Permission {permission_id} not found"
                )
            role.permissions.append(permission)
        
        db.commit()
        db.refresh(role)
        return role
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role name already exists"
        )

def get_role(db: Session, role_id: int) -> Optional[Role]:
    """Get a role by ID."""
    return db.query(Role).filter(Role.id == role_id).first()

def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    """Get a role by name."""
    return db.query(Role).filter(Role.name == name).first()

def get_all_roles(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Role]:
    """Get all roles."""
    return db.query(Role).offset(skip).limit(limit).all()

def update_role(
    db: Session,
    role_id: int,
    role_data: RoleUpdate
) -> Role:
    """Update a role and its permissions."""
    role = get_role(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    update_data = role_data.dict(exclude_unset=True)
    
    # Update basic role information
    if "name" in update_data:
        role.name = update_data["name"]
    if "description" in update_data:
        role.description = update_data["description"]
    
    # Update permissions if provided
    if "permissions" in update_data:
        role.permissions = []
        for permission_id in update_data["permissions"]:
            permission = get_permission(db, permission_id)
            if not permission:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Permission {permission_id} not found"
                )
            role.permissions.append(permission)
    
    try:
        db.commit()
        db.refresh(role)
        return role
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role name already exists"
        )

def delete_role(db: Session, role_id: int) -> bool:
    """Delete a role."""
    role = get_role(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    db.delete(role)
    db.commit()
    return True

def update_user_roles(
    db: Session,
    user_id: int,
    role_data: UserRoleUpdate
) -> User:
    """Update a user's roles."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Clear existing roles
    user.roles = []
    
    # Add new roles
    for role_id in role_data.roles:
        role = get_role(db, role_id)
        if not role:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role {role_id} not found"
            )
        user.roles.append(role)
    
    db.commit()
    db.refresh(user)
    return user

def log_admin_action(
    db: Session,
    user_id: int,
    action: str,
    resource_type: str,
    resource_id: Union[int, str],
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None
) -> AuditLog:
    """Log an admin action for audit purposes."""
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id),
        details=details
    )
    
    if request:
        audit_log.ip_address = request.client.host
        audit_log.user_agent = request.headers.get("user-agent")
    
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log

def get_audit_logs(
    db: Session,
    user_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
) -> List[AuditLog]:
    """Get audit logs with optional filtering."""
    query = db.query(AuditLog)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    if resource_id:
        query = query.filter(AuditLog.resource_id == resource_id)
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
    
    return query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all() 