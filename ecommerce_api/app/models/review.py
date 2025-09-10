from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User and Product relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Review content
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String(200), nullable=True)
    comment = Column(Text, nullable=True)
    
    # Status
    is_verified_purchase = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    # Helpfulness voting
    helpful_count = Column(Integer, default=0)
    unhelpful_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='valid_rating'),
    )
    
    def __repr__(self):
        return f"<Review(id={self.id}, user_id={self.user_id}, product_id={self.product_id}, rating={self.rating})>"
    
    @property
    def helpfulness_ratio(self):
        """Calculate helpfulness ratio"""
        total_votes = self.helpful_count + self.unhelpful_count
        if total_votes == 0:
            return 0
        return self.helpful_count / total_votes