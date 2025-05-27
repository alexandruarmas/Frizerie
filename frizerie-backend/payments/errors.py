from fastapi import HTTPException, status
from typing import Optional

class PaymentError(Exception):
    """Base class for payment-related errors."""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class PaymentValidationError(PaymentError):
    """Raised when payment validation fails."""
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)

class PaymentProcessingError(PaymentError):
    """Raised when payment processing fails."""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.original_error = original_error
        super().__init__(message, status.HTTP_400_BAD_REQUEST)

class PaymentMethodError(PaymentError):
    """Raised when payment method operations fail."""
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)

class PaymentNotFoundError(PaymentError):
    """Raised when payment is not found."""
    def __init__(self, payment_id: int):
        super().__init__(f"Payment {payment_id} not found", status.HTTP_404_NOT_FOUND)

class PaymentMethodNotFoundError(PaymentError):
    """Raised when payment method is not found."""
    def __init__(self, payment_method_id: int):
        super().__init__(f"Payment method {payment_method_id} not found", status.HTTP_404_NOT_FOUND)

class PaymentAuthorizationError(PaymentError):
    """Raised when user is not authorized to perform payment operation."""
    def __init__(self, message: str = "Not authorized to perform this payment operation"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)

def handle_payment_error(error: Exception) -> HTTPException:
    """Convert payment errors to HTTP exceptions."""
    if isinstance(error, PaymentError):
        return HTTPException(
            status_code=error.status_code,
            detail=error.message
        )
    elif isinstance(error, stripe.error.StripeError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the payment"
        ) 