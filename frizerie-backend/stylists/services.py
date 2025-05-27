from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import func

from . import models
from users.models import User
from validation.schemas import StylistCreate, StylistBase # Import schemas for type hinting
from notifications.services import create_notification # Import create_notification
from notifications.models import NotificationType # Import NotificationType enum

def get_stylists(db: Session) -> List[models.Stylist]:
    """Get all active stylists."""
    return db.query(models.Stylist).filter(models.Stylist.is_active == True).all()

def get_stylist_by_id(db: Session, stylist_id: int) -> Optional[models.Stylist]:
    """Get a stylist by ID."""
    return db.query(models.Stylist).filter(models.Stylist.id == stylist_id).first()

# New service functions for stylist reviews
def create_stylist_review(
    db: Session,
    user_id: int,
    stylist_id: int,
    rating: float,
    review_text: Optional[str] = None
) -> models.StylistReview:
    """Create a new stylist review."""
    # Check if stylist exists
    stylist = get_stylist_by_id(db, stylist_id)
    if not stylist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stylist not found")

    # Check if user has already reviewed this stylist
    existing_review = db.query(models.StylistReview).filter(
        models.StylistReview.user_id == user_id,
        models.StylistReview.stylist_id == stylist_id
    ).first()
    if existing_review:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already reviewed this stylist.")

    # Validate rating
    if not 1.0 <= rating <= 5.0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rating must be between 1.0 and 5.0.")

    review = models.StylistReview(
        user_id=user_id,
        stylist_id=stylist_id,
        rating=rating,
        review_text=review_text
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    # Update stylist's average rating
    update_stylist_average_rating(db, stylist_id)

    # --- Notification Triggering ---
    # Notify the stylist about the new review
    if stylist and stylist.user_id: # Ensure stylist has an associated user ID for notifications
        notification_title = "New Stylist Review"
        notification_message = f"You have received a new review with a rating of {rating:.1f}."
        if review_text:
            notification_message += f" Review: \"{review_text}\"."
        
        # Retrieve stylist's user settings (assuming Stylist model has a user relationship or can access it)
        # If Stylist model doesn't directly link to UserSetting, we might need to fetch the User first.
        stylist_user = db.query(User).filter(User.id == stylist.user_id).first()
        if stylist_user and stylist_user.settings:
            user_settings = stylist_user.settings
            
            if user_settings.enable_local_notifications:
                create_notification(
                    db=db,
                    user_id=stylist.user_id,
                    notification_type=NotificationType.NEW_REVIEW,
                    title=notification_title,
                    message=notification_message,
                    method="local"
                )
            if user_settings.enable_email_notifications:
                create_notification(
                    db=db,
                    user_id=stylist.user_id,
                    notification_type=NotificationType.NEW_REVIEW,
                    title=notification_title,
                    message=notification_message,
                    method="email"
                )
            if user_settings.enable_sms_notifications:
                create_notification(
                    db=db,
                    user_id=stylist.user_id,
                    notification_type=NotificationType.NEW_REVIEW,
                    title=notification_title,
                    message=notification_message,
                    method="sms"
                )
    # --- End Notification Triggering ---

    return review

def get_reviews_for_stylist(
    db: Session,
    stylist_id: int,
    skip: int = 0,
    limit: int = 10
) -> List[models.StylistReview]:
    """Get reviews for a specific stylist."""
    reviews = db.query(models.StylistReview).filter(
        models.StylistReview.stylist_id == stylist_id
    ).offset(skip).limit(limit).all()
    return reviews

def update_stylist_average_rating(db: Session, stylist_id: int):
    """Calculate and update the average rating for a stylist."""
    average_rating = db.query(func.avg(models.StylistReview.rating)).filter(
        models.StylistReview.stylist_id == stylist_id
    ).scalar()

    stylist = get_stylist_by_id(db, stylist_id)
    if stylist:
        stylist.average_rating = round(average_rating, 2) if average_rating else 0.0
        db.commit()
        db.refresh(stylist)

# New admin service functions for stylist management
def admin_create_stylist(
    db: Session,
    stylist_data: StylistCreate
) -> models.Stylist:
    """Admin function to create a new stylist."""
    # Check if stylist name already exists (optional, depending on requirement)
    existing_stylist = db.query(models.Stylist).filter(models.Stylist.name == stylist_data.name).first()
    if existing_stylist:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stylist with this name already exists")

    stylist = models.Stylist(
        name=stylist_data.name,
        specialization=stylist_data.specialization,
        bio=stylist_data.bio,
        avatar_url=stylist_data.avatar_url,
        is_active=True # New stylists are active by default
    )
    db.add(stylist)
    db.commit()
    db.refresh(stylist)
    return stylist

def admin_get_stylist_by_id(db: Session, stylist_id: int) -> Optional[models.Stylist]:
    """Admin function to get a stylist by ID (including inactive)."""
    return db.query(models.Stylist).filter(models.Stylist.id == stylist_id).first()

def admin_get_all_stylists(
    db: Session,
    skip: int = 0,
    limit: int = 10
) -> List[models.Stylist]:
    """Admin function to get a list of all stylists (including inactive)."""
    return db.query(models.Stylist).offset(skip).limit(limit).all()

def admin_update_stylist(
    db: Session,
    stylist_id: int,
    stylist_data: Dict[str, Any]
) -> models.Stylist:
    """Admin function to update stylist information."""
    stylist = admin_get_stylist_by_id(db, stylist_id)
    if not stylist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stylist not found")

    # Check for duplicate name if name is being updated
    if "name" in stylist_data and db.query(models.Stylist).filter(models.Stylist.name == stylist_data["name"]).first() and db.query(models.Stylist).filter(models.Stylist.name == stylist_data["name"]).first().id != stylist_id:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stylist with this name already exists")

    for key, value in stylist_data.items():
        if hasattr(stylist, key) and key != "id":
            setattr(stylist, key, value)

    db.commit()
    db.refresh(stylist)
    return stylist

def admin_delete_stylist(db: Session, stylist_id: int) -> Dict[str, bool]:
    """Admin function to delete a stylist (hard delete)."""
    # Consider soft delete instead if preserving historical data is important
    stylist = admin_get_stylist_by_id(db, stylist_id)
    if not stylist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stylist not found")

    db.delete(stylist)
    db.commit()
    return {"success": True}

def admin_deactivate_stylist(db: Session, stylist_id: int) -> models.Stylist:
    """Admin function to deactivate a stylist (soft delete)."""
    stylist = admin_get_stylist_by_id(db, stylist_id)
    if not stylist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stylist not found")

    stylist.is_active = False
    db.commit()
    db.refresh(stylist)
    return stylist 