from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Numeric, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Order totals
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0)
    shipping_amount = Column(Numeric(10, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    
    # Status
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Shipping address
    shipping_first_name = Column(String(50), nullable=False)
    shipping_last_name = Column(String(50), nullable=False)
    shipping_email = Column(String(255), nullable=False)
    shipping_phone = Column(String(20), nullable=True)
    shipping_address_line_1 = Column(String(255), nullable=False)
    shipping_address_line_2 = Column(String(255), nullable=True)
    shipping_city = Column(String(100), nullable=False)
    shipping_state = Column(String(100), nullable=False)
    shipping_postal_code = Column(String(20), nullable=False)
    shipping_country = Column(String(100), nullable=False)
    
    # Billing address (optional - can be same as shipping)
    billing_first_name = Column(String(50), nullable=True)
    billing_last_name = Column(String(50), nullable=True)
    billing_email = Column(String(255), nullable=True)
    billing_phone = Column(String(20), nullable=True)
    billing_address_line_1 = Column(String(255), nullable=True)
    billing_address_line_2 = Column(String(255), nullable=True)
    billing_city = Column(String(100), nullable=True)
    billing_state = Column(String(100), nullable=True)
    billing_postal_code = Column(String(20), nullable=True)
    billing_country = Column(String(100), nullable=True)
    
    # Additional information
    notes = Column(Text, nullable=True)
    tracking_number = Column(String(100), nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order")
    
    def __repr__(self):
        return f"<Order(id={self.id}, order_number='{self.order_number}', status='{self.status}')>"


class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Order relationship
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    # Product relationship
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Item details (snapshot at time of order)
    product_name = Column(String(255), nullable=False)
    product_sku = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    
    # Product snapshot data
    product_image = Column(String(500), nullable=True)
    product_description = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, product='{self.product_name}', quantity={self.quantity})>"