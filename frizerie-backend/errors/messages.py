from typing import Dict

# Authentication Errors
AUTH_ERRORS: Dict[str, str] = {
    "INVALID_CREDENTIALS": "Invalid email or password",
    "TOKEN_EXPIRED": "Authentication token has expired",
    "INVALID_TOKEN": "Invalid authentication token",
    "MISSING_TOKEN": "Authentication token is missing",
    "INVALID_REFRESH_TOKEN": "Invalid refresh token",
    "REFRESH_TOKEN_EXPIRED": "Refresh token has expired"
}

# Authorization Errors
AUTHZ_ERRORS: Dict[str, str] = {
    "INSUFFICIENT_PERMISSIONS": "You don't have permission to perform this action",
    "VIP_REQUIRED": "This action requires VIP membership",
    "ADMIN_REQUIRED": "This action requires administrator privileges"
}

# Validation Errors
VALIDATION_ERRORS: Dict[str, str] = {
    "INVALID_EMAIL": "Invalid email format",
    "INVALID_PASSWORD": "Password must be at least 8 characters long and contain uppercase, lowercase, and numbers",
    "INVALID_NAME": "Name must be between 2 and 50 characters",
    "INVALID_DATE": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)",
    "INVALID_TIME": "Invalid time format",
    "INVALID_SERVICE": "Invalid service type",
    "INVALID_NOTIFICATION_METHOD": "Invalid notification method"
}

# Business Logic Errors
BUSINESS_ERRORS: Dict[str, str] = {
    "BOOKING_TIME_UNAVAILABLE": "The selected time slot is not available",
    "BOOKING_IN_PAST": "Cannot book appointments in the past",
    "BOOKING_TOO_FAR": "Cannot book appointments more than 3 months in advance",
    "BOOKING_DURATION_EXCEEDED": "Booking duration cannot exceed 3 hours",
    "BOOKING_ALREADY_CANCELLED": "Booking is already cancelled",
    "BOOKING_ALREADY_COMPLETED": "Booking is already completed",
    "VIP_SLOT_UNAVAILABLE": "This VIP slot is not available for your membership level"
}

# Not Found Errors
NOT_FOUND_ERRORS: Dict[str, str] = {
    "USER_NOT_FOUND": "User not found",
    "BOOKING_NOT_FOUND": "Booking not found",
    "STYLIST_NOT_FOUND": "Stylist not found",
    "NOTIFICATION_NOT_FOUND": "Notification not found"
}

# Conflict Errors
CONFLICT_ERRORS: Dict[str, str] = {
    "EMAIL_EXISTS": "Email already registered",
    "BOOKING_CONFLICT": "There is already a booking at this time",
    "USERNAME_EXISTS": "Username already taken"
}

# Database Errors
DATABASE_ERRORS: Dict[str, str] = {
    "CONNECTION_ERROR": "Database connection error",
    "QUERY_ERROR": "Database query error",
    "TRANSACTION_ERROR": "Database transaction error"
}

# General Errors
GENERAL_ERRORS: Dict[str, str] = {
    "INTERNAL_ERROR": "An internal server error occurred",
    "SERVICE_UNAVAILABLE": "Service temporarily unavailable",
    "RATE_LIMIT_EXCEEDED": "Rate limit exceeded"
} 