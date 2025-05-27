import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # Start timer
        start_time = time.time()

        # Get request details
        request_id = request.headers.get("X-Request-ID", "")
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            logger.error(
                f"Request failed",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "error": str(e),
                    "client_ip": client_ip,
                    "user_agent": user_agent
                }
            )
            raise

        # Calculate processing time
        process_time = time.time() - start_time

        # Log request details
        logger.info(
            f"Request processed",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "status_code": status_code,
                "process_time": f"{process_time:.3f}s",
                "client_ip": client_ip,
                "user_agent": user_agent
            }
        )

        return response

def logging_middleware(app: ASGIApp) -> LoggingMiddleware:
    """
    Create and return a logging middleware instance.
    """
    return LoggingMiddleware(app) 