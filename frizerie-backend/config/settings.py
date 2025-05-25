from pydantic import BaseModel
from functools import lru_cache
import os
import secrets

class Settings(BaseModel):
    """
    Application settings.
    
    Values are loaded from environment variables, with defaults provided.
    In production, load these from a .env file or environment variables.
    """
    # App config
    APP_NAME: str = "Frizerie API"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    # Auth config
    SECRET_KEY: str = secrets.token_hex(32)  # Generate a random secret key
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database config
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./frizerie.db")  # Use environment variable or fallback to SQLite
    
    # CORS config
    CORS_ORIGINS: list = [
        "http://localhost:5173", 
        "http://localhost:5174",
        "https://frizerie.vercel.app",
        "https://frizerie-git-master-alexandruarmas.vercel.app",
        "https://frizerie-frontend.vercel.app",
        "https://frizerie-git-master-alexandruarmas02-gmailcoms-projects.vercel.app",
        # Add wildcard for all subdomains to be safe
        "https://*.vercel.app",
        "*"  # Temporarily allow all origins for debugging
    ]  # Frontend URLs
    
    # Set CORS to allow credentials
    CORS_ALLOW_CREDENTIALS: bool = True

    # Note: In Pydantic v2, BaseSettings was moved to pydantic-settings
    # For simplicity, we're using BaseModel instead
    # In a production app, consider installing pydantic-settings

@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings.
    
    Uses lru_cache to avoid loading settings multiple times.
    """
    return Settings() 