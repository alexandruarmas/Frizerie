import sys
import os
import logging
import sentry_sdk
from secure import Secure
import traceback

from dotenv import load_dotenv
if os.path.exists('.env'):
    load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path to allow absolute imports
# This is a workaround if Python is not automatically recognizing the package structure
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Verify the path was added (optional debugging)
# print("sys.path after adding parent_dir:", sys.path)

import uvicorn

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from starlette.config import Config

# Add fastapi-limiter imports
# from fastapi_limiter import FastAPILimiter
# from fastapi_limiter.depends import RateLimiter
# from fastapi_limiter import get_remote_address

try:
    # Change imports to use the correct package name
    from config.database import engine, Base
    from auth.routes import router as auth_router
    from users.routes import router as users_router
    from bookings.routes import router as bookings_router
    from notifications.routes import router as notifications_router
    from services.routes import router as services_router
    from payments.routes import router as payments_router
    from analytics.routes import router as analytics_router
    from admin.routes import router as admin_router
    from config.settings import get_settings
    from validation import validate_request_middleware
    from errors import register_exception_handlers
    from app_logging import LoggingMiddleware
    from analytics.middleware import AnalyticsMiddleware
    from error_logging.middleware import (
        ErrorLoggingMiddleware,
        RequestLoggingMiddleware,
        PerformanceMonitoringMiddleware
    )
    from error_logging.routes import router as error_logging_router
except Exception as e:
    print("IMPORT ERROR:", e)
    traceback.print_exc()
    raise

# Get application settings
settings = get_settings()

# Create database tables
Base.metadata.create_all(bind=engine)

# Test database connection after creating tables
try:
    with engine.connect() as conn:
        logger.info("DB CONNECTION SUCCESSFUL")
except Exception as e:
    logger.error("DB CONNECTION FAILED:", e)

try:
    # Create FastAPI app
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        debug=False
    )

    # Register exception handlers
    register_exception_handlers(app)

    # Comment out all routers and middleware for debugging
    app.add_middleware(LoggingMiddleware)
    app.middleware("http")(validate_request_middleware)
    app.add_middleware(AnalyticsMiddleware)
    app.add_middleware(ErrorLoggingMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(PerformanceMonitoringMiddleware)

    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(bookings_router)
    app.include_router(notifications_router)
    app.include_router(services_router)
    app.include_router(payments_router)
    app.include_router(analytics_router)
    app.include_router(admin_router, prefix="/admin", tags=["Admin"])
    app.include_router(error_logging_router)

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://frizerie-git-master-alexandruarmas02-gmailcoms-projects.vercel.app",
            "http://localhost:5173",
            "http://localhost:5174"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Favicon route
    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        return FileResponse(os.path.join("static", "favicon.ico"))

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        import traceback
        tb = traceback.format_exc()
        logger.error(f"GLOBAL EXCEPTION: {exc}\n{tb}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": f"{exc}",
                "traceback": tb
            }
        )

    # --- Sentry Error Monitoring ---
    SENTRY_DSN = os.getenv("SENTRY_DSN")
    print(f"Sentry DSN in use: {SENTRY_DSN}")
    if SENTRY_DSN:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            traces_sample_rate=1.0,
            send_default_pii=True,
        )

    # --- Security Headers ---
    secure = Secure()

    @app.middleware("http")
    async def set_secure_headers(request, call_next):
        try:
            response = await call_next(request)
            if response is None:
                # For HEAD requests or when no response is returned, create an empty response
                response = JSONResponse(status_code=200, content={})
            for header, value in secure.headers().items():
                response.headers[header] = value
            return response
        except Exception as e:
            logger.error(f"Error in set_secure_headers middleware: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )

    # Sentry debug route for verification
    @app.get("/sentry-debug")
    async def trigger_error():
        division_by_zero = 1 / 0

except Exception as e:
    logger.error(f"APP STARTUP ERROR: {e}")
    traceback.print_exc()
    raise

# Root endpoint for API health check
@app.get("/")
@app.head("/")
async def root():
    try:
        return JSONResponse(
            content={"status": "healthy", "version": settings.APP_VERSION},
            status_code=200
        )
    except Exception as e:
        logger.error("ROOT ENDPOINT ERROR:", e)
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )

@app.get("/health")
@app.head("/health")
async def health_check():
    return JSONResponse(
        content={"status": "healthy", "database": settings.DATABASE_URL},
        status_code=200
    )

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="API for Frizerie - A Barbershop Booking System",
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

    
