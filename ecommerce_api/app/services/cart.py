from sqlalchemy.orm import Session
from decimal import Decimal
from app.models.cart import CartItem
from app.models.product import Product
from app.schemas.cart import CartItemCreate, CartItemUpdate


class CartService:
    def __init__(self, db: Session):
        self.db = db

    async def get_user_cart(self, user_id: int):
        """Get user's cart"""
        cart_items = self.db.query(CartItem).filter(CartItem.user_id == user_id).all()
        total_items = len(cart_items)
        total_price = sum(item.total_price for item in cart_items)
        
        return {
            "items": cart_items,
            "total_items": total_items,
            "total_price": total_price
        }

    async def get_cart_summary(self, user_id: int):
        """Get cart summary"""
        cart_items = self.db.query(CartItem).filter(CartItem.user_id == user_id).all()
        total_items = len(cart_items)
        total_price = sum(item.total_price for item in cart_items)
        
        # Basic tax and shipping calculation (placeholder)
        estimated_tax = total_price * Decimal('0.08')  # 8% tax
        estimated_shipping = Decimal('10.00') if total_price < 50 else Decimal('0.00')
        estimated_total = total_price + estimated_tax + estimated_shipping
        
        return {
            "total_items": total_items,
            "total_price": total_price,
            "estimated_tax": estimated_tax,
            "estimated_shipping": estimated_shipping,
            "estimated_total": estimated_total
        }

    async def add_item_to_cart(self, user_id: int, item_data: CartItemCreate):
        """Add item to cart"""
        # Check if product exists
        product = self.db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise ValueError("Product not found")
        
        # Check if item already exists in cart
        existing_item = self.db.query(CartItem).filter(
            CartItem.user_id == user_id,
            CartItem.product_id == item_data.product_id
        ).first()
        
        if existing_item:
            # Update quantity
            existing_item.quantity += item_data.quantity
            self.db.commit()
            self.db.refresh(existing_item)
            return existing_item
        else:
            # Create new cart item
            cart_item = CartItem(
                user_id=user_id,
                product_id=item_data.product_id,
                quantity=item_data.quantity
            )
            self.db.add(cart_item)
            self.db.commit()
            self.db.refresh(cart_item)
            return cart_item

    async def update_cart_item(self, user_id: int, item_id: int, item_data: CartItemUpdate):
        """Update cart item"""
        cart_item = self.db.query(CartItem).filter(
            CartItem.id == item_id,
            CartItem.user_id == user_id
        ).first()
        
        if cart_item:
            cart_item.quantity = item_data.quantity
            self.db.commit()
            self.db.refresh(cart_item)
        
        return cart_item

    async def remove_item_from_cart(self, user_id: int, item_id: int):
        """Remove item from cart"""
        cart_item = self.db.query(CartItem).filter(
            CartItem.id == item_id,
            CartItem.user_id == user_id
        ).first()
        
        if cart_item:
            self.db.delete(cart_item)
            self.db.commit()
            return True
        
        return False

    async def clear_cart(self, user_id: int):
        """Clear all items from cart"""
        self.db.query(CartItem).filter(CartItem.user_id == user_id).delete()
        self.db.commit()
        return True

    async def increment_item_quantity(self, user_id: int, product_id: int):
        """Increment item quantity"""
        cart_item = self.db.query(CartItem).filter(
            CartItem.user_id == user_id,
            CartItem.product_id == product_id
        ).first()
        
        if cart_item:
            cart_item.quantity += 1
            self.db.commit()
            self.db.refresh(cart_item)
        
        return cart_item

    async def decrement_item_quantity(self, user_id: int, product_id: int):
        """Decrement item quantity"""
        cart_item = self.db.query(CartItem).filter(
            CartItem.user_id == user_id,
            CartItem.product_id == product_id
        ).first()
        
        if cart_item:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                self.db.commit()
                self.db.refresh(cart_item)
            else:
                # Remove item if quantity becomes 0
                self.db.delete(cart_item)
                self.db.commit()
                cart_item = None
        
        return cart_item