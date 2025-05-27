from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import stripe

from config.database import get_db
from auth.dependencies import get_current_user, get_current_active_user
from payments.schemas import PaymentCreate, PaymentUpdate, PaymentResponse, PaymentIntentCreate, PaymentIntentResponse, PaymentMethodAttach, SavedPaymentMethodResponse, RefundCreate, RefundResponse, DisputeCreate, DisputeResponse, InvoiceCreate, InvoiceResponse, PaymentMethodResponse, CardPaymentMethodCreate, BankPaymentMethodCreate, PaymentSearchParams, PaymentAnalyticsParams
from payments.services import (
    create_payment,
    process_payment,
    get_payment,
    get_user_payments,
    refund_payment,
    validate_payment,
    PaymentService
)
from notifications.services import create_notification
from notifications.schemas import NotificationType
from payments.analytics import get_payment_analytics, get_user_payment_analytics, track_payment_event
from analytics.models import EventType
from core.security import check_permissions
from payments.models import Payment, PaymentStatus, PaymentMethod, PaymentGateway
from users.models import User, UserRole

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/", response_model=PaymentResponse)
async def create_payment_endpoint(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create a new payment."""
    payment_service = PaymentService(db)
    payment = payment_service.create_payment(payment_data, current_user.id)
    await track_payment_event(
        db=db,
        event_type=EventType.PAYMENT_CREATED,
        payment=payment
    )
    return payment

@router.post("/intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    intent_data: PaymentIntentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a payment intent."""
    payment_service = PaymentService(db)
    return payment_service._create_payment_intent(intent_data, current_user.id)

@router.post("/{payment_id}/process", response_model=PaymentResponse)
async def process_payment_endpoint(
    payment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Process a payment."""
    payment_service = PaymentService(db)
    payment = await get_payment(db, payment_id)
    if payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to process this payment"
        )
    
    result = payment_service.process_payment(payment_id, current_user.id, request)
    await track_payment_event(
        db=db,
        event_type=EventType.PAYMENT_PROCESSED,
        payment=payment,
        properties={"payment_method_id": request.headers.get("payment-method-id")}
    )
    return result

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment_endpoint(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get a payment by ID."""
    payment_service = PaymentService(db)
    payment = await payment_service._get_payment(payment_id, current_user.id)
    if payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this payment"
        )
    return payment

@router.get("/user/me", response_model=List[PaymentResponse])
async def get_my_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    status: Optional[PaymentStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get all payments for the current user."""
    payment_service = PaymentService(db)
    params = PaymentSearchParams(
        status=status,
        start_date=start_date,
        end_date=end_date
    )
    payments, _ = payment_service.search_payments(params, current_user.id)
    return payments

@router.post("/{payment_id}/refund", response_model=RefundResponse)
async def create_refund(
    payment_id: int,
    refund_data: RefundCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a refund for a payment."""
    payment_service = PaymentService(db)
    return payment_service.create_refund(refund_data, current_user.id)

@router.post("/{payment_id}/dispute", response_model=DisputeResponse)
async def create_dispute(
    payment_id: int,
    dispute_data: DisputeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a dispute for a payment."""
    payment_service = PaymentService(db)
    return payment_service.create_dispute(dispute_data, current_user.id)

@router.post("/{payment_id}/invoice", response_model=InvoiceResponse)
async def create_invoice(
    payment_id: int,
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create an invoice for a payment."""
    payment_service = PaymentService(db)
    return payment_service.create_invoice(invoice_data)

@router.get("/methods", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all saved payment methods for the current user."""
    payment_service = PaymentService(db)
    return payment_service.get_payment_methods(current_user.id)

@router.post("/methods/card", response_model=PaymentMethodResponse)
async def add_card_payment_method(
    method_data: CardPaymentMethodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a new card payment method."""
    payment_service = PaymentService(db)
    return payment_service.add_payment_method(method_data.dict(), current_user.id)

@router.post("/methods/bank", response_model=PaymentMethodResponse)
async def add_bank_payment_method(
    method_data: BankPaymentMethodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a new bank payment method."""
    payment_service = PaymentService(db)
    return payment_service.add_payment_method(method_data.dict(), current_user.id)

@router.get("/search", response_model=List[PaymentResponse])
async def search_payments(
    params: PaymentSearchParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Search payments with various filters."""
    payment_service = PaymentService(db)
    payments, _ = payment_service.search_payments(params, current_user.id)
    return payments

@router.get("/analytics")
async def get_payment_analytics(
    params: PaymentAnalyticsParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment analytics data."""
    # Check if user has admin role
    if not any(role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized to access analytics")
    
    payment_service = PaymentService(db)
    return payment_service.get_payment_analytics(params)

@router.get("/admin/all", response_model=List[PaymentResponse])
async def get_all_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: Optional[PaymentStatus] = None,
    method: Optional[PaymentMethod] = None,
    gateway: Optional[PaymentGateway] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get all payments (admin only)."""
    # Check if user has admin role
    if not any(role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized to access all payments")
    
    payment_service = PaymentService(db)
    params = PaymentSearchParams(
        status=status,
        method=method,
        gateway=gateway,
        start_date=start_date,
        end_date=end_date
    )
    payments, _ = payment_service.search_payments(params)
    return payments

@router.get("/admin/analytics/dashboard")
async def get_payment_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365)
):
    """Get payment dashboard data (admin only)."""
    # Check if user has admin role
    if not any(role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Not authorized to access dashboard")
    
    payment_service = PaymentService(db)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    params = PaymentAnalyticsParams(
        start_date=start_date,
        end_date=end_date,
        group_by="day"
    )
    
    analytics = payment_service.get_payment_analytics(params)
    
    # Add additional dashboard metrics
    dashboard_data = {
        **analytics,
        "daily_revenue": [],  # List of daily revenue
        "payment_method_distribution": {},  # Distribution of payment methods
        "gateway_distribution": {},  # Distribution of payment gateways
        "refund_rate": 0,  # Refund rate
        "dispute_rate": 0,  # Dispute rate
        "average_transaction_value": 0,  # Average transaction value
        "top_services": [],  # Top services by revenue
        "customer_retention": 0,  # Customer retention rate
        "payment_success_rate": 0  # Payment success rate
    }
    
    # Calculate additional metrics
    if analytics["total_payments"] > 0:
        dashboard_data["refund_rate"] = (analytics["refunded_payments"] / analytics["total_payments"]) * 100
        dashboard_data["dispute_rate"] = (analytics["disputed_payments"] / analytics["total_payments"]) * 100
        dashboard_data["payment_success_rate"] = (analytics["successful_payments"] / analytics["total_payments"]) * 100
    
    return dashboard_data

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event.type == "payment_intent.succeeded":
        payment_intent = event.data.object
        await handle_payment_success(db, payment_intent)
    elif event.type == "payment_intent.payment_failed":
        payment_intent = event.data.object
        await handle_payment_failure(db, payment_intent)
    elif event.type == "charge.refunded":
        charge = event.data.object
        await handle_refund(db, charge)

    return {"status": "success"}

async def handle_payment_success(db: Session, payment_intent: dict):
    """Handle successful payment."""
    payment = db.query(Payment).filter(
        Payment.payment_intent_id == payment_intent.id
    ).first()
    
    if payment:
        payment.status = PaymentStatus.COMPLETED
        payment.transaction_id = payment_intent.latest_charge
        payment.updated_at = datetime.utcnow()
        
        # Update booking status
        if payment.booking:
            payment.booking.status = "confirmed"
        
        db.commit()
        
        # Create notification
        await create_notification(
            db=db,
            user_id=payment.user_id,
            notification_type=NotificationType.PAYMENT_CONFIRMATION,
            title="Payment Successful",
            message=f"Your payment of {payment.amount} {payment.currency} has been processed successfully.",
            method="all"
        )

async def handle_payment_failure(db: Session, payment_intent: dict):
    """Handle failed payment."""
    payment = db.query(Payment).filter(
        Payment.payment_intent_id == payment_intent.id
    ).first()
    
    if payment:
        payment.status = PaymentStatus.FAILED
        payment.updated_at = datetime.utcnow()
        db.commit()
        
        # Create notification
        await create_notification(
            db=db,
            user_id=payment.user_id,
            notification_type=NotificationType.PAYMENT_FAILED,
            title="Payment Failed",
            message=f"Your payment of {payment.amount} {payment.currency} has failed. Please try again.",
            method="all"
        )

async def handle_refund(db: Session, charge: dict):
    """Handle refund."""
    payment = db.query(Payment).filter(
        Payment.transaction_id == charge.id
    ).first()
    
    if payment:
        payment.status = PaymentStatus.REFUNDED
        payment.refund_id = charge.refunds.data[0].id
        payment.updated_at = datetime.utcnow()
        db.commit()
        
        # Create notification
        await create_notification(
            db=db,
            user_id=payment.user_id,
            notification_type=NotificationType.PAYMENT_REFUNDED,
            title="Payment Refunded",
            message=f"Your payment of {payment.amount} {payment.currency} has been refunded.",
            method="all"
        )

@router.post("/payment-methods", response_model=SavedPaymentMethodResponse)
async def attach_payment_method(
    payment_data: PaymentMethodAttach,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Attach a new payment method to the user."""
    try:
        # Retrieve payment method from Stripe
        payment_method = stripe.PaymentMethod.retrieve(payment_data.payment_method_id)
        
        # Verify the payment method belongs to the user
        if payment_method.customer != current_user.stripe_customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Payment method does not belong to user"
            )
        
        # If this is set as default, unset any existing default
        if payment_data.is_default:
            db.query(SavedPaymentMethod).filter(
                SavedPaymentMethod.user_id == current_user.id,
                SavedPaymentMethod.is_default == True
            ).update({"is_default": False})
        
        # Create saved payment method
        saved_method = SavedPaymentMethod(
            user_id=current_user.id,
            stripe_payment_method_id=payment_method.id,
            card_last4=payment_method.card.last4,
            card_brand=payment_method.card.brand,
            card_exp_month=payment_method.card.exp_month,
            card_exp_year=payment_method.card.exp_year,
            is_default=payment_data.is_default
        )
        
        db.add(saved_method)
        db.commit()
        db.refresh(saved_method)
        
        return saved_method
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/payment-methods", response_model=List[SavedPaymentMethodResponse])
async def list_payment_methods(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all payment methods for the current user."""
    return db.query(SavedPaymentMethod).filter(
        SavedPaymentMethod.user_id == current_user.id
    ).all()

@router.delete("/payment-methods/{payment_method_id}")
async def detach_payment_method(
    payment_method_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Detach a payment method from the user."""
    saved_method = db.query(SavedPaymentMethod).filter(
        SavedPaymentMethod.id == payment_method_id,
        SavedPaymentMethod.user_id == current_user.id
    ).first()
    
    if not saved_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    
    try:
        # Detach from Stripe
        stripe.PaymentMethod.detach(saved_method.stripe_payment_method_id)
        
        # Delete from database
        db.delete(saved_method)
        db.commit()
        
        return {"status": "success"}
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.patch("/payment-methods/{payment_method_id}/default")
async def set_default_payment_method(
    payment_method_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Set a payment method as default."""
    saved_method = db.query(SavedPaymentMethod).filter(
        SavedPaymentMethod.id == payment_method_id,
        SavedPaymentMethod.user_id == current_user.id
    ).first()
    
    if not saved_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    
    # Unset any existing default
    db.query(SavedPaymentMethod).filter(
        SavedPaymentMethod.user_id == current_user.id,
        SavedPaymentMethod.is_default == True
    ).update({"is_default": False})
    
    # Set new default
    saved_method.is_default = True
    db.commit()
    
    return {"status": "success"}

@router.get("/analytics", response_model=Dict[str, Any])
async def get_payment_analytics_endpoint(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get payment analytics for the specified time period."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    return await get_payment_analytics(db, start_date, end_date)

@router.get("/analytics/user/me", response_model=Dict[str, Any])
async def get_my_payment_analytics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get payment analytics for the current user."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    return await get_user_payment_analytics(db, current_user.id, start_date, end_date) 