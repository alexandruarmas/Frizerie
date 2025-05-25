from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import timedelta

from config.database import get_db
from config.dependencies import get_current_user
from config.settings import get_settings
from auth.services import create_access_token, create_refresh_token
from . import services
from . import models

router = APIRouter(prefix="/users", tags=["Users"])
settings = get_settings()

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserUpdate(BaseModel):
    name: str = None
    email: EmailStr = None

@router.post("/register", response_model=Dict[str, Any])
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    user = services.create_user(db, user_data.email, user_data.password, user_data.name)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token = create_refresh_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "vip_level": user.vip_level,
        "loyalty_points": user.loyalty_points,
        "token": access_token,
        "refresh_token": refresh_token
    }

@router.get("/me", response_model=Dict[str, Any])
async def get_user_profile(current_user: models.User = Depends(get_current_user)):
    """Get the current user's profile."""
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "vip_level": current_user.vip_level,
        "loyalty_points": current_user.loyalty_points
    }

@router.put("/me", response_model=Dict[str, Any])
async def update_user_profile(
    user_data: UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the current user's profile."""
    # Create a dictionary with only the fields that are not None
    update_data = user_data.dict(exclude_unset=True, exclude_none=True)
    
    if not update_data:
        return {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "vip_level": current_user.vip_level,
            "loyalty_points": current_user.loyalty_points
        }
    
    # Update user
    updated_user = services.update_user(db, current_user.id, update_data)
    
    return {
        "id": updated_user.id,
        "name": updated_user.name,
        "email": updated_user.email,
        "vip_level": updated_user.vip_level,
        "loyalty_points": updated_user.loyalty_points
    }

@router.get("/loyalty-status", response_model=Dict[str, Any])
async def get_loyalty_status(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current user's loyalty status and VIP perks."""
    return services.get_loyalty_status(db, current_user.id) 