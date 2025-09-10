from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class PaymentMethod(str, enum.Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    BANK_TRANSFER = "bank_transfer"
    CASH_ON_DELIVERY = "cash_on_delivery"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Order relationship
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    # Payment details
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")  # ISO currency code
    
    # External payment system references
    transaction_id = Column(String(255), nullable=True, index=True)  # From payment provider
    stripe_payment_intent_id = Column(String(255), nullable=True)
    stripe_charge_id = Column(String(255), nullable=True)
    paypal_transaction_id = Column(String(255), nullable=True)
    
    # Payment metadata
    gateway_response = Column(JSON, nullable=True)  # Raw response from payment gateway
    failure_reason = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Refund information
    refund_amount = Column(Numeric(10, 2), default=0)
    refund_reason = Column(String(500), nullable=True)
    refunded_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    order = relationship("Order", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, order_id={self.order_id}, method='{self.payment_method}', status='{self.status}', amount={self.amount})>"
    
    @property
    def is_successful(self):
        """Check if payment was successful"""
        return self.status == PaymentStatus.COMPLETED
    
    @property
    def can_be_refunded(self):
        """Check if payment can be refunded"""
        return (
            self.status == PaymentStatus.COMPLETED and 
            self.refund_amount < self.amount
        )
    
    @property
    def remaining_refundable_amount(self):
        """Calculate remaining amount that can be refunded"""
        if not self.can_be_refunded:
            return 0
        return self.amount - self.refund_amount