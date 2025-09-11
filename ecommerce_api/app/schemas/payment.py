from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum


class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    BANK_TRANSFER = "bank_transfer"
    CASH_ON_DELIVERY = "cash_on_delivery"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentIntentCreate(BaseModel):
    order_id: int
    payment_method: PaymentMethod
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    currency: str = Field("USD", min_length=3, max_length=3)
    return_url: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None


class PaymentIntentResponse(BaseModel):
    id: int
    order_id: int
    payment_method: PaymentMethod
    status: PaymentStatus
    amount: Decimal
    currency: str
    client_secret: Optional[str] = None  # For Stripe
    payment_url: Optional[str] = None  # For PayPal
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PaymentConfirm(BaseModel):
    payment_intent_id: str
    payment_method_id: Optional[str] = None  # For Stripe
    return_url: Optional[str] = None


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    payment_method: PaymentMethod
    status: PaymentStatus
    amount: Decimal
    currency: str
    transaction_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    stripe_charge_id: Optional[str] = None
    paypal_transaction_id: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None
    failure_reason: Optional[str] = None
    notes: Optional[str] = None
    refund_amount: Decimal = Decimal('0.00')
    refund_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class RefundRequest(BaseModel):
    payment_id: int
    amount: Optional[Decimal] = None  # If None, full refund
    reason: str = Field(..., min_length=1, max_length=500)


class RefundResponse(BaseModel):
    id: int
    payment_id: int
    order_id: int
    amount: Decimal
    reason: str
    status: str
    refund_id: Optional[str] = None  # External refund ID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PaymentMethodResponse(BaseModel):
    id: str
    type: str
    card: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class WebhookEvent(BaseModel):
    id: str
    type: str
    data: Dict[str, Any]
    created: int


# Stripe specific schemas
class StripePaymentMethod(BaseModel):
    card_number: str = Field(..., min_length=13, max_length=19)
    exp_month: int = Field(..., ge=1, le=12)
    exp_year: int = Field(..., ge=2024)
    cvc: str = Field(..., min_length=3, max_length=4)
    name: str = Field(..., min_length=1)


class StripeCustomerCreate(BaseModel):
    email: str
    name: str
    phone: Optional[str] = None
    address: Optional[Dict[str, str]] = None


# PayPal specific schemas
class PayPalPaymentCreate(BaseModel):
    order_id: int
    amount: Decimal
    currency: str = "USD"
    return_url: str
    cancel_url: str