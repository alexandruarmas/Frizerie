from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from .database import get_db
from .settings import get_settings
from users.models import User

# Get application settings
settings = get_settings()

# OAuth2 scheme for token extraction from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Validate the access token and return the current user.
    
    This is a dependency that can be reused across routes.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Extract user info from token
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if email is None or user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise credentials_exception
        
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    Check if the current user is active.
    
    This is a dependency that can be used when an active user is required.
    """
    # In a real app, you might have an 'is_active' field in your user model
    # For now we'll assume all users are active
    return current_user

async def get_admin_user(current_user: User = Depends(get_current_user)):
    """
    Check if the current user is an admin.
    
    This is a dependency that can be used when admin privileges are required.
    """
    # In a real app, you would check a role or is_admin field
    # For now, we'll just raise an exception
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough permissions"
    ) 