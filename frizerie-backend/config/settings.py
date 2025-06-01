from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os
import secrets
from typing import Optional, List
from pydantic import EmailStr

class Settings(BaseSettings):
    """
    Application settings.
    
    Values are loaded from environment variables, with defaults provided.
    In production, load these from a .env file or environment variables.
    """
    # App config
    APP_NAME: str = "Frizerie API"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Sentry config
    SENTRY_DSN: Optional[str] = None
    
    # Auth config
    SECRET_KEY: str = secrets.token_hex(32)  # Generate a random secret key
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database config
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./frizerie.db")
    
    # CORS config
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Local development
        "http://localhost:5174",  # Local development alternative port
        "https://frizerie-git-master-alexandruarmas02-gmailcoms-projects.vercel.app",  # Your Vercel deployment
        "https://*.vercel.app"  # All Vercel subdomains
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Email settings
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str = APP_NAME
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    
    # SMS settings (Twilio)
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str
    
    # Firebase settings
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    
    # Celery settings
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Stripe settings
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_RETURN_URL: str
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings.
    
    Uses lru_cache to avoid loading settings multiple times.
    """
    return Settings() 