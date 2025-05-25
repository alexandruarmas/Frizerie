from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, List, Dict, Any
import json
from . import models
from auth.services import get_password_hash

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get a user by email."""
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """Get a user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, email: str, password: str, name: str) -> models.User:
    """Create a new user."""
    # Check if user already exists
    existing_user = get_user_by_email(db, email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = get_password_hash(password)
    
    # Create user
    user = models.User(
        email=email,
        password_hash=hashed_password,
        name=name,
        vip_level="BRONZE",
        loyalty_points=0
    )
    
    # Add to database
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

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
    
    # Update points
    user.loyalty_points += points_to_add
    
    # Update VIP level
    user.vip_level = calculate_vip_tier(user.loyalty_points)
    
    # Save changes
    db.commit()
    db.refresh(user)
    
    return user

def get_loyalty_status(db: Session, user_id: int) -> Dict[str, Any]:
    """Get loyalty status and perks for a user."""
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
        next_tier = "SILVER"
        points_to_next_tier = 200 - points
    elif tier == "SILVER":
        next_tier = "GOLD"
        points_to_next_tier = 500 - points
    elif tier == "GOLD":
        next_tier = "DIAMOND"
        points_to_next_tier = 1000 - points
    
    # Get perks based on tier
    perks = []
    if tier in ["SILVER", "GOLD", "DIAMOND"]:
        perks.append("Priority booking")
    if tier in ["GOLD", "DIAMOND"]:
        perks.append("10% discount")
    if tier == "DIAMOND":
        perks.append("Free styling products")
    
    return {
        "tier": tier,
        "points": points,
        "next_tier": next_tier,
        "points_to_next_tier": points_to_next_tier,
        "perks": perks
    }

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