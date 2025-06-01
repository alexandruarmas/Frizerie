"""
Security middleware for handling rate limiting, request validation, and API key management.
"""
from fastapi import Request, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import time
import hashlib
import json
from typing import Optional, Callable, Dict, Any
import re

from database import get_db
from security.models import APIKey, RateLimit, RequestLog, SecurityEvent
from security.services import (
    validate_api_key,
    check_rate_limit,
    log_request,
    log_security_event
)

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        # rate_limit_window: int = 60,  # 1 minute window
        # max_requests_per_window: int = 100,  # 100 requests per minute
        excluded_paths: set = None,
        require_api_key: bool = True
    ):
        super().__init__(app)
        # self.rate_limit_window = rate_limit_window
        # self.max_requests_per_window = max_requests_per_window
        self.excluded_paths = excluded_paths or {
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/auth/login",
            "/auth/register"
        }
        self.require_api_key = require_api_key
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> JSONResponse:
        # Skip security checks for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)
        
        start_time = time.time()
        db = next(get_db())
        
        try:
            # Get API key from header
            api_key = request.headers.get("X-API-Key")
            
            # Validate API key if required
            if self.require_api_key:
                if not api_key:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="API key is required"
                    )
                
                key_hash = hashlib.sha256(api_key.encode()).hexdigest()
                api_key_obj = validate_api_key(db, key_hash)
                if not api_key_obj:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid API key"
                    )
                
                # Check rate limit
                # if not check_rate_limit(
                #     db,
                #     key_hash,
                #     request.url.path,
                #     self.rate_limit_window,
                #     self.max_requests_per_window
                # ):
                #     raise HTTPException(
                #         status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                #         detail="Rate limit exceeded"
                #     )
            
            # Validate request
            await self.validate_request(request)
            
            # Process request
            response = await call_next(request)
            
            # Calculate response time
            response_time = int((time.time() - start_time) * 1000)
            
            # Log request
            if api_key:
                log_request(
                    db,
                    key_hash=key_hash,
                    endpoint=request.url.path,
                    method=request.method,
                    status_code=response.status_code,
                    ip_address=request.client.host,
                    user_agent=request.headers.get("user-agent"),
                    request_data=await self.get_request_data(request),
                    response_time=response_time
                )
            
            return response
            
        except HTTPException as e:
            # Log security event for unauthorized/forbidden requests
            if e.status_code in (401, 403, 429):
                log_security_event(
                    db,
                    event_type="unauthorized_access",
                    severity="warning",
                    description=f"Unauthorized access attempt: {e.detail}",
                    ip_address=request.client.host,
                    key_hash=key_hash if api_key else None,
                    metadata={
                        "path": request.url.path,
                        "method": request.method,
                        "status_code": e.status_code
                    }
                )
            raise
            
        except Exception as e:
            # Log security event for unexpected errors
            log_security_event(
                db,
                event_type="error",
                severity="error",
                description=f"Unexpected error: {str(e)}",
                ip_address=request.client.host,
                key_hash=key_hash if api_key else None,
                metadata={
                    "path": request.url.path,
                    "method": request.method,
                    "error": str(e)
                }
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def validate_request(self, request: Request) -> None:
        """Validate request headers and content."""
        # Check content type for POST/PUT requests
        if request.method in ("POST", "PUT"):
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith("application/json"):
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail="Content-Type must be application/json"
                )
        
        # Validate request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 1024 * 1024:  # 1MB limit
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Request body too large"
            )
        
        # Check for potentially malicious headers
        for header in request.headers:
            if re.search(r'(?i)(script|exec|eval|system)', header):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid header detected"
                )
    
    async def get_request_data(self, request: Request) -> Dict[str, Any]:
        """Get request data for logging."""
        try:
            if request.method in ("POST", "PUT"):
                body = await request.body()
                if body:
                    return json.loads(body)
            return {}
        except:
            return {} 