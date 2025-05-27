from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, EmailStr
from payments.models import PaymentStatus, PaymentMethod, PaymentGateway, PaymentSecurityLevel

# Base Payment Schemas
class PaymentBase(BaseModel):
    booking_id: int
    amount: float = Field(gt=0)
    currency: str = "RON"
    method: PaymentMethod
    gateway: PaymentGateway
    payment_metadata: Optional[Dict[str, Any]] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    payment_metadata: Optional[Dict[str, Any]] = None
    refund_reason: Optional[str] = None
    dispute_reason: Optional[str] = None

class PaymentResponse(PaymentBase):
    id: int
    user_id: int
    status: PaymentStatus
    security_level: PaymentSecurityLevel
    transaction_id: Optional[str] = None
    payment_intent_id: Optional[str] = None
    refund_id: Optional[str] = None
    dispute_id: Optional[str] = None
    fraud_score: Optional[float] = None
    risk_level: Optional[str] = None
    invoice_id: Optional[str] = None
    invoice_number: Optional[str] = None
    receipt_url: Optional[str] = None
    invoice_url: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None
    disputed_at: Optional[datetime] = None
    dispute_resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Payment Intent Schemas
class PaymentIntentCreate(BaseModel):
    amount: float = Field(gt=0)
    currency: str = "RON"
    payment_method: str
    booking_id: int
    gateway: PaymentGateway
    payment_metadata: Optional[Dict[str, Any]] = None

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return round(v, 2)

class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    amount: float
    currency: str
    status: str
    gateway: PaymentGateway
    requires_action: bool = False
    next_action: Optional[Dict[str, Any]] = None

# Refund Schemas
class RefundCreate(BaseModel):
    payment_id: int
    amount: Optional[float] = None
    reason: Optional[str] = None
    payment_metadata: Optional[Dict[str, Any]] = None

class RefundResponse(BaseModel):
    id: int
    payment_id: int
    amount: float
    currency: str
    reason: Optional[str] = None
    status: str
    gateway_refund_id: Optional[str] = None
    payment_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Dispute Schemas
class DisputeCreate(BaseModel):
    payment_id: int
    reason: str
    payment_metadata: Optional[Dict[str, Any]] = None

class DisputeResponse(BaseModel):
    id: int
    payment_id: int
    dispute_id: str
    reason: str
    status: str
    amount: float
    currency: str
    payment_metadata: Optional[Dict[str, Any]] = None
    resolution: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Payment Method Schemas
class PaymentMethodBase(BaseModel):
    gateway: PaymentGateway
    method_type: PaymentMethod
    is_default: bool = False
    payment_metadata: Optional[Dict[str, Any]] = None

class CardPaymentMethodCreate(PaymentMethodBase):
    card_number: str = Field(..., min_length=13, max_length=19)
    card_exp_month: int = Field(..., ge=1, le=12)
    card_exp_year: int = Field(..., ge=2024)
    card_cvc: str = Field(..., min_length=3, max_length=4)

class BankPaymentMethodCreate(PaymentMethodBase):
    bank_name: str
    account_number: str
    routing_number: str
    account_holder_name: str

class PaymentMethodResponse(PaymentMethodBase):
    id: int
    user_id: int
    payment_method_id: str
    card_last4: Optional[str] = None
    card_brand: Optional[str] = None
    card_exp_month: Optional[int] = None
    card_exp_year: Optional[int] = None
    bank_name: Optional[str] = None
    bank_account_last4: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Invoice Schemas
class InvoiceItem(BaseModel):
    description: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    tax_rate: Optional[float] = None
    discount: Optional[float] = None

class InvoiceCreate(BaseModel):
    payment_id: int
    billing_name: str
    billing_email: EmailStr
    billing_address: Optional[Dict[str, Any]] = None
    items: List[InvoiceItem]
    tax_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None

class InvoiceResponse(BaseModel):
    id: int
    payment_id: int
    invoice_number: str
    status: str
    amount: float
    currency: str
    billing_name: str
    billing_email: str
    billing_address: Optional[Dict[str, Any]] = None
    items: List[Dict[str, Any]]
    tax_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    due_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    pdf_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Analytics Schemas
class PaymentAnalyticsEventCreate(BaseModel):
    payment_id: int
    event_type: str
    payment_metadata: Optional[Dict[str, Any]] = None

class PaymentAnalyticsEventResponse(BaseModel):
    id: int
    payment_id: int
    event_type: str
    payment_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Security Schemas
class PaymentSecurityLogCreate(BaseModel):
    payment_id: int
    event_type: str
    payment_metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class PaymentSecurityLogResponse(BaseModel):
    id: int
    payment_id: int
    event_type: str
    payment_metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Search and Filter Schemas
class PaymentSearchParams(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[PaymentStatus] = None
    method: Optional[PaymentMethod] = None
    gateway: Optional[PaymentGateway] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    currency: Optional[str] = None
    include_refunds: bool = True
    include_disputes: bool = True

class PaymentAnalyticsParams(BaseModel):
    start_date: datetime
    end_date: datetime
    group_by: Optional[str] = None  # e.g., "day", "week", "month"
    include_refunds: bool = True
    include_disputes: bool = True
    gateway: Optional[PaymentGateway] = None
    method: Optional[PaymentMethod] = None

class PaymentMethodAttach(BaseModel):
    user_id: int
    payment_method_id: str
    is_default: Optional[bool] = False

class SavedPaymentMethodResponse(BaseModel):
    id: int
    user_id: int
    gateway: PaymentGateway
    payment_method_id: str
    method_type: PaymentMethod
    is_default: bool
    card_last4: Optional[str] = None
    card_brand: Optional[str] = None
    card_exp_month: Optional[int] = None
    card_exp_year: Optional[int] = None
    bank_name: Optional[str] = None
    bank_account_last4: Optional[str] = None
    payment_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True 