from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from .product import ProductListResponse


class CartItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0, le=100)


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0, le=100)


class CartItemResponse(CartItemBase):
    id: int
    user_id: int
    product: ProductListResponse
    total_price: Decimal
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total_items: int
    total_price: Decimal
    
    model_config = ConfigDict(from_attributes=True)


class CartSummary(BaseModel):
    total_items: int
    total_price: Decimal
    estimated_tax: Decimal = Decimal('0.00')
    estimated_shipping: Decimal = Decimal('0.00')
    estimated_total: Decimal
    
    model_config = ConfigDict(from_attributes=True)