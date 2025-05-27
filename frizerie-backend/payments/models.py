from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Boolean, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from config.database import Base

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"
    PARTIALLY_REFUNDED = "partially_refunded"
    DISPUTED = "disputed"
    DISPUTE_RESOLVED = "dispute_resolved"

class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"

class PaymentGateway(str, Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"

class PaymentSecurityLevel(str, Enum):
    STANDARD = "standard"
    ENHANCED = "enhanced"
    HIGH = "high"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    booking_id = Column(String(36), ForeignKey("bookings.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="RON")
    status = Column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    method = Column(SQLEnum(PaymentMethod), nullable=False)
    gateway = Column(SQLEnum(PaymentGateway), nullable=False)
    security_level = Column(SQLEnum(PaymentSecurityLevel), default=PaymentSecurityLevel.STANDARD)
    
    # Transaction details
    transaction_id = Column(String(100), nullable=True)
    payment_intent_id = Column(String(100), nullable=True)
    refund_id = Column(String(100), nullable=True)
    dispute_id = Column(String(100), nullable=True)
    
    # Enhanced security and tracking
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    fraud_score = Column(Float, nullable=True)
    risk_level = Column(String(20), nullable=True)
    verification_attempts = Column(Integer, default=0)
    last_verification_attempt = Column(DateTime, nullable=True)
    
    # Invoice and receipt
    invoice_id = Column(String(100), nullable=True)
    invoice_number = Column(String(50), nullable=True)
    receipt_url = Column(String(500), nullable=True)
    invoice_url = Column(String(500), nullable=True)
    
    # Additional metadata
    payment_metadata = Column(JSON, nullable=True)
    error_details = Column(JSON, nullable=True)
    refund_reason = Column(Text, nullable=True)
    dispute_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    refunded_at = Column(DateTime, nullable=True)
    disputed_at = Column(DateTime, nullable=True)
    dispute_resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="payments")
    booking = relationship("Booking", back_populates="payment")
    refunds = relationship("PaymentRefund", back_populates="payment", cascade="all, delete-orphan")
    disputes = relationship("PaymentDispute", back_populates="payment", cascade="all, delete-orphan")
    security_logs = relationship("PaymentSecurityLog", back_populates="payment", cascade="all, delete-orphan")
    analytics_events = relationship("PaymentAnalyticsEvent", back_populates="payment", cascade="all, delete-orphan")

class PaymentRefund(Base):
    __tablename__ = "payment_refunds"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    gateway_refund_id = Column(String(100), nullable=True)
    payment_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    payment = relationship("Payment", back_populates="refunds")

class PaymentDispute(Base):
    __tablename__ = "payment_disputes"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    dispute_id = Column(String(100), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="open")
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    evidence = Column(JSON, nullable=True)
    resolution = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    payment = relationship("Payment", back_populates="disputes")

class PaymentSecurityLog(Base):
    __tablename__ = "payment_security_logs"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    event_type = Column(String(50), nullable=False)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    payment = relationship("Payment", back_populates="security_logs")

class PaymentAnalyticsEvent(Base):
    __tablename__ = "payment_analytics_events"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    event_type = Column(String(50), nullable=False)
    properties = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    payment = relationship("Payment", back_populates="analytics_events")

class SavedPaymentMethod(Base):
    __tablename__ = "saved_payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    gateway = Column(SQLEnum(PaymentGateway), nullable=False)
    payment_method_id = Column(String(100), nullable=False)
    method_type = Column(SQLEnum(PaymentMethod), nullable=False)
    is_default = Column(Boolean, default=False)
    
    # Card details (for card payments)
    card_last4 = Column(String(4), nullable=True)
    card_brand = Column(String(20), nullable=True)
    card_exp_month = Column(Integer, nullable=True)
    card_exp_year = Column(Integer, nullable=True)
    
    # Bank details (for bank transfers)
    bank_name = Column(String(100), nullable=True)
    bank_account_last4 = Column(String(4), nullable=True)
    
    # Metadata
    payment_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="saved_payment_methods")

class PaymentInvoice(Base):
    __tablename__ = "payment_invoices"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    invoice_number = Column(String(50), nullable=False, unique=True)
    status = Column(String(20), nullable=False, default="draft")
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    due_date = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    
    # Invoice details
    billing_name = Column(String(100), nullable=False)
    billing_email = Column(String(100), nullable=False)
    billing_address = Column(JSON, nullable=True)
    items = Column(JSON, nullable=False)  # List of items with descriptions and amounts
    tax_amount = Column(Float, nullable=True)
    discount_amount = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    
    # File storage
    pdf_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    payment = relationship("Payment", foreign_keys=[payment_id])

# Update User model relationships
from users.models import User
User.payments = relationship("Payment", back_populates="user")
User.saved_payment_methods = relationship("SavedPaymentMethod", back_populates="user", cascade="all, delete-orphan") 