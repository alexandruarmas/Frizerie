from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy import func
from sqlalchemy.orm import Session

from payments.models import Payment, PaymentStatus, PaymentMethod
from analytics.models import AnalyticsEvent, EventType
from analytics.services import track_event

async def track_payment_event(
    db: Session,
    event_type: EventType,
    payment: Payment,
    properties: Dict[str, Any] = None
):
    """Track a payment-related analytics event."""
    event_properties = {
        "payment_id": payment.id,
        "amount": payment.amount,
        "currency": payment.currency,
        "method": payment.method,
        "status": payment.status,
        "booking_id": payment.booking_id,
        **(properties or {})
    }
    
    await track_event(
        db=db,
        event_data={
            "user_id": payment.user_id,
            "event_type": event_type,
            "properties": event_properties
        }
    )

async def get_payment_analytics(
    db: Session,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """Get payment analytics for the specified time period."""
    # Get total revenue
    total_revenue = db.query(func.sum(Payment.amount))\
        .filter(
            Payment.status == PaymentStatus.COMPLETED,
            Payment.created_at.between(start_date, end_date)
        ).scalar() or 0.0
    
    # Get payment method distribution
    payment_methods = db.query(
        Payment.method,
        func.count(Payment.id).label('count'),
        func.sum(Payment.amount).label('amount')
    ).filter(
        Payment.created_at.between(start_date, end_date)
    ).group_by(Payment.method).all()
    
    # Get payment status distribution
    payment_statuses = db.query(
        Payment.status,
        func.count(Payment.id).label('count')
    ).filter(
        Payment.created_at.between(start_date, end_date)
    ).group_by(Payment.status).all()
    
    # Get daily revenue
    daily_revenue = db.query(
        func.date_trunc('day', Payment.created_at).label('date'),
        func.sum(Payment.amount).label('amount')
    ).filter(
        Payment.status == PaymentStatus.COMPLETED,
        Payment.created_at.between(start_date, end_date)
    ).group_by('date').order_by('date').all()
    
    # Get average transaction value
    avg_transaction = db.query(
        func.avg(Payment.amount)
    ).filter(
        Payment.status == PaymentStatus.COMPLETED,
        Payment.created_at.between(start_date, end_date)
    ).scalar() or 0.0
    
    # Get refund rate
    total_payments = db.query(func.count(Payment.id))\
        .filter(Payment.created_at.between(start_date, end_date))\
        .scalar() or 1
    refunded_payments = db.query(func.count(Payment.id))\
        .filter(
            Payment.status == PaymentStatus.REFUNDED,
            Payment.created_at.between(start_date, end_date)
        ).scalar()
    refund_rate = (refunded_payments / total_payments * 100) if total_payments > 0 else 0.0
    
    return {
        "total_revenue": total_revenue,
        "payment_methods": [
            {
                "method": method,
                "count": count,
                "amount": amount
            }
            for method, count, amount in payment_methods
        ],
        "payment_statuses": [
            {
                "status": status,
                "count": count
            }
            for status, count in payment_statuses
        ],
        "daily_revenue": [
            {
                "date": date.isoformat(),
                "amount": amount
            }
            for date, amount in daily_revenue
        ],
        "average_transaction_value": avg_transaction,
        "refund_rate": refund_rate
    }

async def get_user_payment_analytics(
    db: Session,
    user_id: int,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """Get payment analytics for a specific user."""
    # Get user's total spent
    total_spent = db.query(func.sum(Payment.amount))\
        .filter(
            Payment.user_id == user_id,
            Payment.status == PaymentStatus.COMPLETED,
            Payment.created_at.between(start_date, end_date)
        ).scalar() or 0.0
    
    # Get user's payment methods
    payment_methods = db.query(
        Payment.method,
        func.count(Payment.id).label('count'),
        func.sum(Payment.amount).label('amount')
    ).filter(
        Payment.user_id == user_id,
        Payment.created_at.between(start_date, end_date)
    ).group_by(Payment.method).all()
    
    # Get user's payment history
    payment_history = db.query(Payment)\
        .filter(
            Payment.user_id == user_id,
            Payment.created_at.between(start_date, end_date)
        ).order_by(Payment.created_at.desc()).all()
    
    # Get user's average transaction value
    avg_transaction = db.query(
        func.avg(Payment.amount)
    ).filter(
        Payment.user_id == user_id,
        Payment.status == PaymentStatus.COMPLETED,
        Payment.created_at.between(start_date, end_date)
    ).scalar() or 0.0
    
    return {
        "total_spent": total_spent,
        "payment_methods": [
            {
                "method": method,
                "count": count,
                "amount": amount
            }
            for method, count, amount in payment_methods
        ],
        "payment_history": [
            {
                "id": payment.id,
                "amount": payment.amount,
                "currency": payment.currency,
                "status": payment.status,
                "method": payment.method,
                "created_at": payment.created_at.isoformat()
            }
            for payment in payment_history
        ],
        "average_transaction_value": avg_transaction
    } 