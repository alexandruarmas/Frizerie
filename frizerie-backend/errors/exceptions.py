from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class BaseAPIException(HTTPException):
    """Base exception for all API errors."""
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str,
        extra: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.extra = extra or {}

class ValidationError(BaseAPIException):
    """Exception for validation errors."""
    def __init__(
        self,
        detail: str,
        error_code: str = "VALIDATION_ERROR",
        extra: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code,
            extra=extra
        )

class AuthenticationError(BaseAPIException):
    """Exception for authentication errors."""
    def __init__(
        self,
        detail: str,
        error_code: str = "AUTHENTICATION_ERROR",
        extra: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code,
            extra=extra
        )

class AuthorizationError(BaseAPIException):
    """Exception for authorization errors."""
    def __init__(
        self,
        detail: str,
        error_code: str = "AUTHORIZATION_ERROR",
        extra: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code,
            extra=extra
        )

class NotFoundError(BaseAPIException):
    """Exception for resource not found errors."""
    def __init__(
        self,
        detail: str,
        error_code: str = "NOT_FOUND",
        extra: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code,
            extra=extra
        )

class ConflictError(BaseAPIException):
    """Exception for resource conflict errors."""
    def __init__(
        self,
        detail: str,
        error_code: str = "CONFLICT",
        extra: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=error_code,
            extra=extra
        )

class BusinessLogicError(BaseAPIException):
    """Exception for business logic errors."""
    def __init__(
        self,
        detail: str,
        error_code: str = "BUSINESS_LOGIC_ERROR",
        extra: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code=error_code,
            extra=extra
        )

class DatabaseError(BaseAPIException):
    """Exception for database errors."""
    def __init__(
        self,
        detail: str,
        error_code: str = "DATABASE_ERROR",
        extra: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code=error_code,
            extra=extra
        ) 