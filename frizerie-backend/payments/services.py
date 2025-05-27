from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Request
import stripe
import logging # Import logging

from payments.models import Payment, PaymentStatus, PaymentMethod, PaymentGateway, PaymentRefund, PaymentDispute, PaymentSecurityLog, PaymentAnalyticsEvent, PaymentInvoice, SavedPaymentMethod
from payments.schemas import PaymentCreate, PaymentUpdate, PaymentIntentCreate, RefundCreate, DisputeCreate, InvoiceCreate, PaymentAnalyticsEventCreate, PaymentSecurityLogCreate, PaymentSearchParams, PaymentAnalyticsParams
from payments.stripe_client import stripe_client
from errors.exceptions import BusinessLogicError, NotFoundError
from notifications.services import create_notification # Import create_notification
from notifications.models import NotificationType # Import NotificationType enum
from users.models import UserSetting # Import UserSetting
from booking.models import Booking
from users.models import User
from core.config import settings
from core.security import get_fraud_score, get_risk_level
from core.utils import generate_invoice_number, create_pdf_invoice

# Set up logging
logger = logging.getLogger(__name__)

# Initialize payment gateways
stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentGatewayError(Exception):
    pass

class PaymentService:
    def __init__(self, db: Session):
        self.db = db

    def create_payment(self, payment_data: PaymentCreate, user_id: int) -> Payment:
        """Create a new payment with fraud detection and security checks."""
        # Get booking and validate
        booking = self.db.query(Booking).filter(Booking.id == payment_data.booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        if booking.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to create payment for this booking")

        # Check if payment already exists
        existing_payment = self.db.query(Payment).filter(
            Payment.booking_id == payment_data.booking_id,
            Payment.status != PaymentStatus.CANCELLED
        ).first()
        if existing_payment:
            raise HTTPException(status_code=400, detail="Payment already exists for this booking")

        # Create payment intent with selected gateway
        payment_intent = self._create_payment_intent(payment_data, user_id)
        
        # Calculate fraud score and risk level
        fraud_score = get_fraud_score(payment_data, user_id)
        risk_level = get_risk_level(fraud_score)

        # Create payment record
        payment = Payment(
            user_id=user_id,
            booking_id=payment_data.booking_id,
            amount=payment_data.amount,
            currency=payment_data.currency,
            method=payment_data.method,
            gateway=payment_data.gateway,
            status=PaymentStatus.PENDING,
            payment_intent_id=payment_intent.id,
            security_level=self._get_security_level(risk_level),
            fraud_score=fraud_score,
            risk_level=risk_level,
            payment_metadata=payment_data.payment_metadata
        )

        try:
            self.db.add(payment)
            self.db.commit()
            self.db.refresh(payment)
            
            # Log security event
            self._log_security_event(
                payment.id,
                "payment_created",
                {"fraud_score": fraud_score, "risk_level": risk_level}
            )
            
            # Log analytics event
            self._log_analytics_event(
                payment.id,
                "payment_created",
                {"amount": payment_data.amount, "method": payment_data.method.value}
            )
            
            return payment
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Error creating payment")

    def process_payment(self, payment_id: int, user_id: int, request: Request) -> Payment:
        """Process a payment with the selected payment method."""
        payment = self._get_payment(payment_id, user_id)
        
        if payment.status != PaymentStatus.PENDING:
            raise HTTPException(status_code=400, detail="Payment cannot be processed")

        try:
            # Process payment with selected gateway
            if payment.gateway == PaymentGateway.STRIPE:
                result = self._process_stripe_payment(payment)
            else:
                raise HTTPException(status_code=400, detail="Unsupported payment gateway")

            # Update payment status
            payment.status = PaymentStatus.COMPLETED
            payment.transaction_id = result.get("transaction_id")
            payment.completed_at = datetime.utcnow()
            metadata = result.get("metadata", {})
            if not isinstance(metadata, dict):
                metadata = {}
            payment.payment_metadata = {**(payment.payment_metadata or {}), **metadata}

            self.db.commit()
            self.db.refresh(payment)

            # Create invoice
            self._create_invoice(payment)

            # Log events
            self._log_security_event(payment.id, "payment_processed", {"status": "success"})
            self._log_analytics_event(payment.id, "payment_processed", {"amount": payment.amount})

            return payment
        except PaymentGatewayError as e:
            payment.status = PaymentStatus.FAILED
            payment.error_details = {"error": str(e)}
            self.db.commit()
            self._log_security_event(payment.id, "payment_failed", {"error": str(e)})
            raise HTTPException(status_code=400, detail=str(e))

    def create_refund(self, refund_data: RefundCreate, user_id: int) -> PaymentRefund:
        """Create a refund for a payment."""
        payment = self._get_payment(refund_data.payment_id, user_id)
        
        if payment.status != PaymentStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Payment must be completed to refund")
        
        if payment.refund_id:
            raise HTTPException(status_code=400, detail="Payment already refunded")

        amount = refund_data.amount or payment.amount

        try:
            # Process refund with selected gateway
            if payment.gateway == PaymentGateway.STRIPE:
                result = self._process_stripe_refund(payment, amount)
            else:
                raise HTTPException(status_code=400, detail="Unsupported payment gateway")

            # Create refund record
            refund = PaymentRefund(
                payment_id=payment.id,
                amount=amount,
                currency=payment.currency,
                reason=refund_data.reason,
                status="completed",
                gateway_refund_id=result.get("refund_id"),
                payment_metadata=refund_data.metadata
            )

            # Update payment
            payment.status = PaymentStatus.REFUNDED
            payment.refund_id = refund.id
            payment.refunded_at = datetime.utcnow()

            self.db.add(refund)
            self.db.commit()
            self.db.refresh(refund)

            # Log events
            self._log_security_event(payment.id, "refund_created", {"amount": amount})
            self._log_analytics_event(payment.id, "refund_created", {"amount": amount})

            return refund
        except PaymentGatewayError as e:
            self._log_security_event(payment.id, "refund_failed", {"error": str(e)})
            raise HTTPException(status_code=400, detail=str(e))

    def create_dispute(self, dispute_data: DisputeCreate, user_id: int) -> PaymentDispute:
        """Create a dispute for a payment."""
        payment = self._get_payment(dispute_data.payment_id, user_id)
        
        if payment.status != PaymentStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Payment must be completed to dispute")
        
        if payment.dispute_id:
            raise HTTPException(status_code=400, detail="Payment already disputed")

        try:
            # Create dispute with selected gateway
            if payment.gateway == PaymentGateway.STRIPE:
                result = self._create_stripe_dispute(payment, dispute_data)
            else:
                raise HTTPException(status_code=400, detail="Unsupported payment gateway")

            # Create dispute record
            dispute = PaymentDispute(
                payment_id=payment.id,
                dispute_id=result.get("dispute_id"),
                reason=dispute_data.reason,
                status="open",
                amount=payment.amount,
                currency=payment.currency,
                evidence=dispute_data.evidence,
                payment_metadata=dispute_data.payment_metadata
            )

            # Update payment
            payment.status = PaymentStatus.DISPUTED
            payment.dispute_id = dispute.id
            payment.disputed_at = datetime.utcnow()

            self.db.add(dispute)
            self.db.commit()
            self.db.refresh(dispute)

            # Log events
            self._log_security_event(payment.id, "dispute_created", {"reason": dispute_data.reason})
            self._log_analytics_event(payment.id, "dispute_created", {"amount": payment.amount})

            return dispute
        except PaymentGatewayError as e:
            self._log_security_event(payment.id, "dispute_failed", {"error": str(e)})
            raise HTTPException(status_code=400, detail=str(e))

    def create_invoice(self, invoice_data: InvoiceCreate) -> PaymentInvoice:
        """Create an invoice for a payment."""
        payment = self._get_payment(invoice_data.payment_id, None)
        
        if not payment.invoice_id:
            invoice = PaymentInvoice(
                payment_id=payment.id,
                invoice_number=generate_invoice_number(),
                status="draft",
                amount=payment.amount,
                currency=payment.currency,
                billing_name=invoice_data.billing_name,
                billing_email=invoice_data.billing_email,
                billing_address=invoice_data.billing_address,
                items=invoice_data.items,
                tax_amount=invoice_data.tax_amount,
                discount_amount=invoice_data.discount_amount,
                due_date=invoice_data.due_date,
                notes=invoice_data.notes,
                payment_metadata=invoice_data.payment_metadata
            )

            self.db.add(invoice)
            self.db.commit()
            self.db.refresh(invoice)

            # Generate PDF invoice
            pdf_url = create_pdf_invoice(invoice)
            invoice.pdf_url = pdf_url
            invoice.status = "sent"
            
            # Update payment
            payment.invoice_id = invoice.id
            payment.invoice_number = invoice.invoice_number
            
            self.db.commit()
            self.db.refresh(invoice)

            # Log analytics event
            self._log_analytics_event(payment.id, "invoice_created", {"invoice_number": invoice.invoice_number})

            return invoice
        else:
            raise HTTPException(status_code=400, detail="Invoice already exists for this payment")

    def get_payment_methods(self, user_id: int) -> List[SavedPaymentMethod]:
        """Get all saved payment methods for a user."""
        return self.db.query(SavedPaymentMethod).filter(
            SavedPaymentMethod.user_id == user_id
        ).all()

    def add_payment_method(self, payment_method_data: Dict[str, Any], user_id: int) -> SavedPaymentMethod:
        """Add a new payment method for a user."""
        try:
            # Create payment method with selected gateway
            if payment_method_data["gateway"] == PaymentGateway.STRIPE:
                result = self._create_stripe_payment_method(payment_method_data, user_id)
            else:
                raise HTTPException(status_code=400, detail="Unsupported payment gateway")

            # Create saved payment method record
            payment_method = SavedPaymentMethod(
                user_id=user_id,
                gateway=payment_method_data["gateway"],
                method_type=payment_method_data["method_type"],
                payment_method_id=result.get("payment_method_id"),
                card_last4=result.get("card_last4"),
                card_brand=result.get("card_brand"),
                card_exp_month=result.get("card_exp_month"),
                card_exp_year=result.get("card_exp_year"),
                bank_name=result.get("bank_name"),
                bank_account_last4=result.get("bank_account_last4"),
                is_default=payment_method_data.get("is_default", False),
                payment_metadata=payment_method_data.get("payment_metadata")
            )

            self.db.add(payment_method)
            self.db.commit()
            self.db.refresh(payment_method)

            # Log security event
            self._log_security_event(
                None,
                "payment_method_added",
                {"method_type": payment_method_data["method_type"].value},
                user_id
            )

            return payment_method
        except PaymentGatewayError as e:
            raise HTTPException(status_code=400, detail=str(e))

    def search_payments(self, params: PaymentSearchParams, user_id: Optional[int] = None) -> Tuple[List[Payment], int]:
        """Search payments with various filters."""
        query = self.db.query(Payment)

        if user_id:
            query = query.filter(Payment.user_id == user_id)

        if params.start_date:
            query = query.filter(Payment.created_at >= params.start_date)
        if params.end_date:
            query = query.filter(Payment.created_at <= params.end_date)
        if params.status:
            query = query.filter(Payment.status == params.status)
        if params.method:
            query = query.filter(Payment.method == params.method)
        if params.gateway:
            query = query.filter(Payment.gateway == params.gateway)
        if params.min_amount:
            query = query.filter(Payment.amount >= params.min_amount)
        if params.max_amount:
            query = query.filter(Payment.amount <= params.max_amount)
        if params.currency:
            query = query.filter(Payment.currency == params.currency)

        total = query.count()
        payments = query.order_by(Payment.created_at.desc()).all()

        return payments, total

    def get_payment_analytics(self, params: PaymentAnalyticsParams) -> Dict[str, Any]:
        """Get payment analytics data."""
        query = self.db.query(PaymentAnalyticsEvent)

        if params.start_date:
            query = query.filter(PaymentAnalyticsEvent.created_at >= params.start_date)
        if params.end_date:
            query = query.filter(PaymentAnalyticsEvent.created_at <= params.end_date)
        if params.gateway:
            query = query.filter(Payment.gateway == params.gateway)
        if params.method:
            query = query.filter(Payment.method == params.method)

        events = query.all()

        # Process analytics data
        analytics = {
            "total_payments": 0,
            "total_amount": 0,
            "successful_payments": 0,
            "failed_payments": 0,
            "refunded_payments": 0,
            "disputed_payments": 0,
            "average_amount": 0,
            "payment_methods": {},
            "gateways": {},
            "timeline": {}
        }

        for event in events:
            if event.event_type == "payment_created":
                analytics["total_payments"] += 1
                amount = event.properties.get("amount", 0)
                analytics["total_amount"] += amount
                analytics["average_amount"] = analytics["total_amount"] / analytics["total_payments"]
                
                method = event.properties.get("method")
                if method:
                    analytics["payment_methods"][method] = analytics["payment_methods"].get(method, 0) + 1

            elif event.event_type == "payment_processed":
                analytics["successful_payments"] += 1
            elif event.event_type == "payment_failed":
                analytics["failed_payments"] += 1
            elif event.event_type == "refund_created":
                analytics["refunded_payments"] += 1
            elif event.event_type == "dispute_created":
                analytics["disputed_payments"] += 1

        return analytics

    def _get_payment(self, payment_id: int, user_id: Optional[int]) -> Payment:
        """Get a payment by ID with optional user validation."""
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        if user_id and payment.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this payment")
        
        return payment

    def _create_payment_intent(self, payment_data: PaymentCreate, user_id: int) -> Any:
        """Create a payment intent with the selected gateway."""
        try:
            if payment_data.gateway == PaymentGateway.STRIPE:
                intent = stripe.PaymentIntent.create(
                    amount=int(payment_data.amount * 100),  # Convert to cents
                    currency=payment_data.currency.lower(),
                    payment_method_types=[payment_data.method.value],
                    metadata={
                        "user_id": user_id,
                        "booking_id": payment_data.booking_id
                    }
                )
                return intent
            else:
                raise PaymentGatewayError("Unsupported payment gateway")
        except stripe.error.StripeError as e:
            raise PaymentGatewayError(str(e))

    def _process_stripe_payment(self, payment: Payment) -> Dict[str, Any]:
        """Process a payment with Stripe."""
        try:
            intent = stripe.PaymentIntent.retrieve(payment.payment_intent_id)
            if intent.status == "succeeded":
                return {
                    "transaction_id": intent.charges.data[0].id,
                    "metadata": intent.metadata
                }
            else:
                raise PaymentGatewayError(f"Payment intent status: {intent.status}")
        except stripe.error.StripeError as e:
            raise PaymentGatewayError(str(e))

    def _process_stripe_refund(self, payment: Payment, amount: float) -> Dict[str, Any]:
        """Process a refund with Stripe."""
        try:
            refund = stripe.Refund.create(
                payment_intent=payment.payment_intent_id,
                amount=int(amount * 100)  # Convert to cents
            )
            return {
                "refund_id": refund.id,
                "status": refund.status
            }
        except stripe.error.StripeError as e:
            raise PaymentGatewayError(str(e))

    def _create_stripe_dispute(self, payment: Payment, dispute_data: DisputeCreate) -> Dict[str, Any]:
        """Create a dispute with Stripe."""
        try:
            dispute = stripe.Dispute.create(
                payment_intent=payment.payment_intent_id,
                reason=dispute_data.reason,
                evidence=dispute_data.evidence
            )
            return {
                "dispute_id": dispute.id,
                "status": dispute.status
            }
        except stripe.error.StripeError as e:
            raise PaymentGatewayError(str(e))

    def _create_stripe_payment_method(self, payment_method_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Create a payment method with Stripe."""
        try:
            if payment_method_data["method_type"] == PaymentMethod.CARD:
                method = stripe.PaymentMethod.create(
                    type="card",
                    card={
                        "number": payment_method_data["card_number"],
                        "exp_month": payment_method_data["card_exp_month"],
                        "exp_year": payment_method_data["card_exp_year"],
                        "cvc": payment_method_data["card_cvc"]
                    },
                    metadata={"user_id": user_id}
                )
                return {
                    "payment_method_id": method.id,
                    "card_last4": method.card.last4,
                    "card_brand": method.card.brand,
                    "card_exp_month": method.card.exp_month,
                    "card_exp_year": method.card.exp_year
                }
            elif payment_method_data["method_type"] == PaymentMethod.BANK_TRANSFER:
                method = stripe.PaymentMethod.create(
                    type="bank_transfer",
                    bank_transfer={
                        "account_number": payment_method_data["account_number"],
                        "routing_number": payment_method_data["routing_number"],
                        "account_holder_name": payment_method_data["account_holder_name"]
                    },
                    metadata={"user_id": user_id}
                )
                return {
                    "payment_method_id": method.id,
                    "bank_name": payment_method_data["bank_name"],
                    "bank_account_last4": method.bank_transfer.last4
                }
            else:
                raise PaymentGatewayError("Unsupported payment method type")
        except stripe.error.StripeError as e:
            raise PaymentGatewayError(str(e))

    def _get_security_level(self, risk_level: str) -> str:
        """Determine security level based on risk level."""
        if risk_level == "high":
            return "high"
        elif risk_level == "medium":
            return "medium"
        else:
            return "low"

    def _log_security_event(
        self,
        payment_id: Optional[int],
        event_type: str,
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None
    ) -> None:
        """Log a security event."""
        log = PaymentSecurityLog(
            payment_id=payment_id,
            user_id=user_id,
            event_type=event_type,
            details=details
        )
        self.db.add(log)
        self.db.commit()

    def _log_analytics_event(
        self,
        payment_id: int,
        event_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an analytics event."""
        event = PaymentAnalyticsEvent(
            payment_id=payment_id,
            event_type=event_type,
            properties=properties
        )
        self.db.add(event)
        self.db.commit()

async def create_payment(
    db: Session,
    payment_data: PaymentCreate,
    user_id: int
) -> Payment:
    """
    Create a new payment record.
    
    Args:
        db: Database session
        payment_data: Payment creation data
        user_id: ID of the user making the payment
    
    Returns:
        Payment: Created payment record
    """
    payment = Payment(
        user_id=user_id,
        booking_id=payment_data.booking_id,
        amount=payment_data.amount,
        currency=payment_data.currency,
        method=payment_data.method,
        status=PaymentStatus.PENDING,
        payment_metadata=payment_data.payment_metadata
    )
    
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

async def process_payment(
    db: Session,
    payment_id: int,
    payment_method_id: str
) -> Payment:
    """
    Process a payment using Stripe.
    
    Args:
        db: Database session
        payment_id: ID of the payment to process
        payment_method_id: Stripe payment method ID
    
    Returns:
        Payment: Updated payment record
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise NotFoundError("Payment not found")
    
    if payment.status != PaymentStatus.PENDING:
        raise BusinessLogicError("Payment is not in pending status")
    
    try:
        # Create payment intent
        intent = await stripe_client.create_payment_intent(
            amount=payment.amount,
            currency=payment.currency,
            payment_method=payment_method_id,
            metadata={
                "payment_id": payment.id,
                "booking_id": payment.booking_id,
                "user_id": payment.user_id
            }
        )
        
        # Update payment record
        payment.payment_intent_id = intent.id
        payment.transaction_id = intent.latest_charge
        payment.status = PaymentStatus.COMPLETED
        payment.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(payment)

        # --- Notification Triggering ---
        notification_title = "Payment Confirmation"
        notification_message = f"Your payment of {payment.amount:.2f} {payment.currency.upper()} for booking {payment.booking_id} was successful."
        
        # Assuming payment.user is a loaded relationship
        user_settings = payment.user.settings if payment.user and payment.user.settings else None
        
        if user_settings:
            if user_settings.enable_local_notifications:
                 create_notification(
                    db=db,
                    user_id=payment.user_id,
                    notification_type=NotificationType.PAYMENT_CONFIRMATION,
                    title=notification_title,
                    message=notification_message,
                    method="local"
                )
            if user_settings.enable_email_notifications:
                 create_notification(
                    db=db,
                    user_id=payment.user_id,
                    notification_type=NotificationType.PAYMENT_CONFIRMATION,
                    title=notification_title,
                    message=notification_message,
                    method="email"
                )
            if user_settings.enable_sms_notifications:
                 create_notification(
                    db=db,
                    user_id=payment.user_id,
                    notification_type=NotificationType.PAYMENT_CONFIRMATION,
                    title=notification_title,
                    message=notification_message,
                    method="sms"
                )
        # --- End Notification Triggering ---
        
        return payment
    except Exception as e:
        payment.status = PaymentStatus.FAILED
        db.commit()
        logger.error(f"Payment processing failed for payment {payment_id}: {e}", exc_info=True)
        raise BusinessLogicError(f"Payment processing failed: {str(e)}")

async def get_payment(db: Session, payment_id: int) -> Payment:
    """
    Get a payment by ID.
    
    Args:
        db: Database session
        payment_id: ID of the payment to retrieve
    
    Returns:
        Payment: Payment record
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise NotFoundError("Payment not found")
    return payment

async def get_user_payments(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Payment]:
    """
    Get all payments for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        skip: Number of records to skip
        limit: Maximum number of records to return
    
    Returns:
        List[Payment]: List of payment records
    """
    return db.query(Payment)\
        .filter(Payment.user_id == user_id)\
        .offset(skip)\
        .limit(limit)\
        .all()

async def refund_payment(
    db: Session,
    payment_id: int,
    amount: Optional[float] = None,
    reason: Optional[str] = None
) -> Payment:
    """
    Refund a payment.
    
    Args:
        db: Database session
        payment_id: ID of the payment to refund
        amount: Amount to refund (optional, defaults to full amount)
        reason: Reason for refund (optional)
    
    Returns:
        Payment: Updated payment record
    """
    payment = await get_payment(db, payment_id)
    
    if payment.status != PaymentStatus.COMPLETED:
        raise BusinessLogicError("Only completed payments can be refunded")
    
    if not payment.payment_intent_id:
        raise BusinessLogicError("Payment intent ID not found")
    
    try:
        # Create refund in Stripe
        refund = await stripe_client.create_refund(
            payment_intent_id=payment.payment_intent_id,
            amount=amount,
            reason=reason
        )
        
        # Update payment record
        payment.status = PaymentStatus.REFUNDED
        payment.refund_id = refund.id
        payment.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(payment)
        return payment
    except Exception as e:
        raise BusinessLogicError(f"Refund failed: {str(e)}")

async def validate_payment(
    db: Session,
    payment_id: int,
    payment_method_id: str
) -> bool:
    """
    Validate a payment and its payment method.
    
    Args:
        db: Database session
        payment_id: ID of the payment to validate
        payment_method_id: Stripe payment method ID
    
    Returns:
        bool: True if payment is valid, False otherwise
    """
    payment = await get_payment(db, payment_id)
    
    if payment.status != PaymentStatus.PENDING:
        return False
    
    return await stripe_client.validate_payment_method(payment_method_id) 