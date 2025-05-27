from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import json
from datetime import datetime

from analytics.models import EventType
from analytics.schemas import AnalyticsEventCreate
from analytics import services
from config.database import SessionLocal

class AnalyticsMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: set = None
    ):
        super().__init__(app)
        self.exclude_paths = exclude_paths or {
            "/docs",
            "/redoc",
            "/openapi.json",
            "/analytics/events",
            "/static",
            "/favicon.ico"
        }

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # Skip analytics for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Get user ID from request if available
        user_id = None
        if hasattr(request.state, "user"):
            user_id = request.state.user.id

        # Track page view
        event_data = AnalyticsEventCreate(
            user_id=user_id,
            event_type=EventType.PAGE_VIEW,
            properties={
                "page": request.url.path,
                "method": request.method,
                "query_params": dict(request.query_params)
            },
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )

        # Create database session
        db = SessionLocal()
        try:
            # Track the event
            services.track_event(
                db=db,
                event_type=event_data.event_type,
                properties=event_data.properties,
                user_id=event_data.user_id
            )
        finally:
            db.close()

        # Process the request
        response = await call_next(request)

        # Track response status
        if response.status_code >= 400:
            error_event_data = AnalyticsEventCreate(
                user_id=user_id,
                event_type=EventType.ERROR,
                properties={
                    "page": request.url.path,
                    "method": request.method,
                    "status_code": response.status_code,
                    "error": response.status_code
                },
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent")
            )

            db = SessionLocal()
            try:
                services.track_event(
                    db=db,
                    event_type=error_event_data.event_type,
                    properties=error_event_data.properties,
                    user_id=error_event_data.user_id
                )
            finally:
                db.close()

        return response

def track_custom_event(
    event_type: EventType,
    properties: dict,
    user_id: int = None,
    request: Request = None
):
    """
    Helper function to track custom events from anywhere in the application.
    """
    event_data = AnalyticsEventCreate(
        user_id=user_id,
        event_type=event_type,
        properties=properties,
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None
    )

    db = SessionLocal()
    try:
        services.track_event(db, event_data)
    finally:
        db.close() 