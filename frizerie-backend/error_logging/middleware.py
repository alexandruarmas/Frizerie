"""
Middleware for automatic error and system event logging.
"""
import time
import traceback
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from config.database import SessionLocal
from . import schemas, services

class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic error logging."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        db = SessionLocal()
        
        try:
            # Get response from next middleware/route handler
            response = await call_next(request)
            
            # If no response was returned, create a default one
            if response is None:
                response = JSONResponse(
                    status_code=200,
                    content={"status": "ok"}
                )
            
            process_time = time.time() - start_time
            
            # Log successful request
            if response.status_code >= 200 and response.status_code < 400:
                services.SystemLoggingService.create_system_log(
                    db,
                    schemas.SystemLogCreate(
                        log_level="INFO",
                        message=f"Request completed: {request.method} {request.url.path}",
                        source="api",
                        context={
                            "method": request.method,
                            "path": request.url.path,
                            "status_code": response.status_code,
                            "process_time": process_time
                        }
                    )
                )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            # Log error
            error_log = schemas.ErrorLogCreate(
                error_type=type(e).__name__,
                message=str(e),
                stack_trace=traceback.format_exc(),
                severity="ERROR",
                source="api",
                endpoint=str(request.url.path),
                method=request.method,
                status_code=500
            )
            
            # Try to get user ID from request if available
            try:
                if hasattr(request.state, "user"):
                    error_log.user_id = request.state.user.id
            except:
                pass
            
            services.ErrorLoggingService.create_error_log(db, error_log)
            
            # Log system event
            services.SystemLoggingService.create_system_log(
                db,
                schemas.SystemLogCreate(
                    log_level="ERROR",
                    message=f"Request failed: {request.method} {request.url.path}",
                    source="api",
                    context={
                        "method": request.method,
                        "path": request.url.path,
                        "error": str(e),
                        "process_time": process_time
                    }
                )
            )
            
            # ADD THESE LINES FOR DEBUGGING
            print("UNHANDLED EXCEPTION:", e)
            traceback.print_exc()
            
            # Return error response
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
            
        finally:
            db.close()

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all requests."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        db = SessionLocal()
        
        try:
            # Log request start
            services.SystemLoggingService.create_system_log(
                db,
                schemas.SystemLogCreate(
                    log_level="INFO",
                    message=f"Request started: {request.method} {request.url.path}",
                    source="api",
                    context={
                        "method": request.method,
                        "path": request.url.path,
                        "client_host": request.client.host if request.client else None
                    }
                )
            )
            
            # Get response from next middleware/route handler
            response = await call_next(request)
            
            # If no response was returned, create a default one
            if response is None:
                response = JSONResponse(
                    status_code=200,
                    content={"status": "ok"}
                )
            
            process_time = time.time() - start_time
            
            # Log request completion
            services.SystemLoggingService.create_system_log(
                db,
                schemas.SystemLogCreate(
                    log_level="INFO",
                    message=f"Request completed: {request.method} {request.url.path}",
                    source="api",
                    context={
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                        "process_time": process_time
                    }
                )
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            # Log error
            services.SystemLoggingService.create_system_log(
                db,
                schemas.SystemLogCreate(
                    log_level="ERROR",
                    message=f"Request failed: {request.method} {request.url.path}",
                    source="api",
                    context={
                        "method": request.method,
                        "path": request.url.path,
                        "error": str(e),
                        "process_time": process_time
                    }
                )
            )
            
            # Return error response
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
            
        finally:
            db.close()

class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring request performance."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        db = SessionLocal()
        
        try:
            # Get response from next middleware/route handler
            response = await call_next(request)
            
            # If no response was returned, create a default one
            if response is None:
                response = JSONResponse(
                    status_code=200,
                    content={"status": "ok"}
                )
            
            process_time = time.time() - start_time
            
            # Record performance metric
            services.MonitoringService.create_metric(
                db,
                schemas.MonitoringMetricCreate(
                    metric_name="request_duration_seconds",
                    metric_value=process_time,
                    metric_type="histogram",
                    labels={
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": str(response.status_code)
                    }
                )
            )
            
            # Record request count
            services.MonitoringService.create_metric(
                db,
                schemas.MonitoringMetricCreate(
                    metric_name="request_count_total",
                    metric_value=1,
                    metric_type="counter",
                    labels={
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": str(response.status_code)
                    }
                )
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            # Log error
            services.MonitoringService.create_metric(
                db,
                schemas.MonitoringMetricCreate(
                    metric_name="request_errors_total",
                    metric_value=1,
                    metric_type="counter",
                    labels={
                        "method": request.method,
                        "path": request.url.path,
                        "error": type(e).__name__
                    }
                )
            )
            
            # Return error response
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
            
        finally:
            db.close() 