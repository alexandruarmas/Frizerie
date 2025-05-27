from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Callable
import time
from datetime import datetime

async def validate_request_middleware(request: Request, call_next: Callable):
    """Middleware to validate incoming requests."""
    # Start timer for request processing
    start_time = time.time()
    
    try:
        # Validate request headers
        if not request.headers.get("user-agent"):
            raise HTTPException(
                status_code=400,
                detail="User-Agent header is required"
            )
        
        # Process the request
        response = await call_next(request)
        
        # Add processing time to response headers
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

def validate_date_range(start_date: datetime, end_date: datetime) -> None:
    """Validate date range for bookings and availability."""
    if start_date >= end_date:
        raise HTTPException(
            status_code=400,
            detail="Start date must be before end date"
        )
    
    # Check if date range is not too far in the future (e.g., 3 months)
    max_future_date = datetime.now().replace(month=datetime.now().month + 3)
    if end_date > max_future_date:
        raise HTTPException(
            status_code=400,
            detail="Cannot book appointments more than 3 months in advance"
        )

def validate_booking_duration(start_time: datetime, end_time: datetime) -> None:
    """Validate booking duration."""
    duration = end_time - start_time
    max_duration = 180  # 3 hours in minutes
    
    if duration.total_seconds() / 60 > max_duration:
        raise HTTPException(
            status_code=400,
            detail=f"Booking duration cannot exceed {max_duration} minutes"
        ) 