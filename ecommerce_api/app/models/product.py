from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Numeric, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)
    
    # Pricing
    price = Column(Numeric(10, 2), nullable=False)
    compare_price = Column(Numeric(10, 2), nullable=True)  # Original price for discounts
    cost_price = Column(Numeric(10, 2), nullable=True)     # Cost for profit calculation
    
    # Inventory
    sku = Column(String(100), unique=True, nullable=False, index=True)
    stock_quantity = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=10)
    track_inventory = Column(Boolean, default=True)
    allow_backorders = Column(Boolean, default=False)
    
    # Physical attributes
    weight = Column(Numeric(8, 2), nullable=True)  # in kg
    dimensions = Column(JSON, nullable=True)        # {"length": 10, "width": 5, "height": 3}
    
    # Images and media
    images = Column(JSON, nullable=True)  # List of image URLs
    featured_image = Column(String(500), nullable=True)
    
    # SEO and metadata
    meta_title = Column(String(150), nullable=True)
    meta_description = Column(String(300), nullable=True)
    tags = Column(JSON, nullable=True)  # List of tags
    
    # Status and visibility
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    is_digital = Column(Boolean, default=False)
    requires_shipping = Column(Boolean, default=True)
    
    # Category relationship
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")
    reviews = relationship("Review", back_populates="product")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', sku='{self.sku}')>"
    
    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0 or self.allow_backorders
    
    @property
    def is_low_stock(self):
        """Check if product is low in stock"""
        if not self.track_inventory:
            return False
        return self.stock_quantity <= self.low_stock_threshold
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if compare_price is set"""
        if self.compare_price and self.compare_price > self.price:
            return round(((self.compare_price - self.price) / self.compare_price) * 100, 2)
        return 0