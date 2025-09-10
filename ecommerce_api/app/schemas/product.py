from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: bool = True


class CategoryCreate(CategoryBase):
    parent_id: Optional[int] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    parent_id: Optional[int] = None


class CategoryResponse(CategoryBase):
    id: int
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    sku: str = Field(..., min_length=1, max_length=100)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    compare_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    cost_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    track_inventory: bool = True
    inventory_quantity: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    weight: Optional[Decimal] = Field(None, ge=0, decimal_places=3)
    dimensions: Optional[str] = Field(None, max_length=100)
    is_active: bool = True
    is_featured: bool = False
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = Field(None, max_length=500)


class ProductCreate(ProductBase):
    category_id: int
    images: Optional[List[str]] = []
    tags: Optional[List[str]] = []


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    compare_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    cost_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    category_id: Optional[int] = None
    track_inventory: Optional[bool] = None
    inventory_quantity: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    weight: Optional[Decimal] = Field(None, ge=0, decimal_places=3)
    dimensions: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = Field(None, max_length=500)
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class ProductResponse(ProductBase):
    id: int
    category_id: int
    category: Optional[CategoryResponse] = None
    images: List[str] = []
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    id: int
    name: str
    short_description: Optional[str] = None
    sku: str
    price: Decimal
    compare_price: Optional[Decimal] = None
    is_active: bool
    is_featured: bool
    category: Optional[CategoryResponse] = None
    images: List[str] = []
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProductSearchQuery(BaseModel):
    q: Optional[str] = None  # Search query
    category_id: Optional[int] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = True
    tags: Optional[List[str]] = None
    sort_by: Optional[str] = "created_at"  # name, price, created_at
    sort_order: Optional[str] = "desc"  # asc, desc
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)


class ProductSearchResponse(BaseModel):
    products: List[ProductListResponse]
    total: int
    page: int
    limit: int
    pages: int
    
    model_config = ConfigDict(from_attributes=True)