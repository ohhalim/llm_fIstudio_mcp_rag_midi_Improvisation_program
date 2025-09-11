from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum
from .product import ProductListResponse


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class ShippingAddressBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    address_line_1: str = Field(..., max_length=255)
    address_line_2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    postal_code: str = Field(..., max_length=20)
    country: str = Field(..., max_length=100)


class BillingAddressBase(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address_line_1: Optional[str] = Field(None, max_length=255)
    address_line_2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0, decimal_places=2)


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_sku: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    product_image: Optional[str] = None
    product_description: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    shipping_address: ShippingAddressBase
    billing_address: Optional[BillingAddressBase] = None
    notes: Optional[str] = Field(None, max_length=1000)
    use_shipping_for_billing: bool = True


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    tracking_number: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)


class OrderResponse(BaseModel):
    id: int
    order_number: str
    user_id: int
    subtotal: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    status: OrderStatus
    payment_status: PaymentStatus
    
    # Shipping address
    shipping_first_name: str
    shipping_last_name: str
    shipping_email: str
    shipping_phone: Optional[str] = None
    shipping_address_line_1: str
    shipping_address_line_2: Optional[str] = None
    shipping_city: str
    shipping_state: str
    shipping_postal_code: str
    shipping_country: str
    
    # Billing address
    billing_first_name: Optional[str] = None
    billing_last_name: Optional[str] = None
    billing_email: Optional[str] = None
    billing_phone: Optional[str] = None
    billing_address_line_1: Optional[str] = None
    billing_address_line_2: Optional[str] = None
    billing_city: Optional[str] = None
    billing_state: Optional[str] = None
    billing_postal_code: Optional[str] = None
    billing_country: Optional[str] = None
    
    notes: Optional[str] = None
    tracking_number: Optional[str] = None
    order_items: List[OrderItemResponse] = []
    
    created_at: datetime
    updated_at: datetime
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class OrderListResponse(BaseModel):
    id: int
    order_number: str
    total_amount: Decimal
    status: OrderStatus
    payment_status: PaymentStatus
    items_count: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class OrderSearchQuery(BaseModel):
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    order_number: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_total: Optional[Decimal] = None
    max_total: Optional[Decimal] = None
    sort_by: Optional[str] = "created_at"  # created_at, total_amount, order_number
    sort_order: Optional[str] = "desc"  # asc, desc
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)


class OrderSearchResponse(BaseModel):
    orders: List[OrderListResponse]
    total: int
    page: int
    limit: int
    pages: int
    
    model_config = ConfigDict(from_attributes=True)