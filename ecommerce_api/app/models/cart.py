from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Product relationship
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Cart item details
    quantity = Column(Integer, nullable=False, default=1)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")
    
    # Ensure one cart item per user per product
    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name='unique_user_product_cart'),
    )
    
    def __repr__(self):
        return f"<CartItem(id={self.id}, user_id={self.user_id}, product_id={self.product_id}, quantity={self.quantity})>"
    
    @property
    def total_price(self):
        """Calculate total price for this cart item"""
        if self.product:
            return self.product.price * self.quantity
        return 0