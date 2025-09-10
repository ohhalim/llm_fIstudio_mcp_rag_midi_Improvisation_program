from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.cart import (
    CartItemCreate,
    CartItemUpdate,
    CartItemResponse,
    CartResponse,
    CartSummary
)
from app.schemas.common import MessageResponse
from app.services.cart import CartService
from app.core.security import get_current_user
from app.models.user import User


router = APIRouter()


@router.get("/", response_model=CartResponse)
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's cart"""
    try:
        cart_service = CartService(db)
        cart = await cart_service.get_user_cart(current_user.id)
        return cart
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch cart"
        )


@router.get("/summary", response_model=CartSummary)
async def get_cart_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get cart summary with totals"""
    try:
        cart_service = CartService(db)
        summary = await cart_service.get_cart_summary(current_user.id)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch cart summary"
        )


@router.post("/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    item_data: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add item to cart"""
    try:
        cart_service = CartService(db)
        cart_item = await cart_service.add_item_to_cart(
            user_id=current_user.id,
            item_data=item_data
        )
        return cart_item
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item to cart"
        )


@router.put("/items/{item_id}", response_model=CartItemResponse)
async def update_cart_item(
    item_id: int,
    item_data: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update cart item quantity"""
    try:
        cart_service = CartService(db)
        cart_item = await cart_service.update_cart_item(
            user_id=current_user.id,
            item_id=item_id,
            item_data=item_data
        )
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )
        return cart_item
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update cart item"
        )


@router.delete("/items/{item_id}", response_model=MessageResponse)
async def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from cart"""
    try:
        cart_service = CartService(db)
        success = await cart_service.remove_item_from_cart(
            user_id=current_user.id,
            item_id=item_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )
        return MessageResponse(message="Item removed from cart successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove item from cart"
        )


@router.delete("/clear", response_model=MessageResponse)
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all items from cart"""
    try:
        cart_service = CartService(db)
        await cart_service.clear_cart(current_user.id)
        return MessageResponse(message="Cart cleared successfully")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear cart"
        )


@router.post("/items/{product_id}/increment", response_model=CartItemResponse)
async def increment_cart_item(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Increment cart item quantity by 1"""
    try:
        cart_service = CartService(db)
        cart_item = await cart_service.increment_item_quantity(
            user_id=current_user.id,
            product_id=product_id
        )
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )
        return cart_item
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to increment cart item"
        )


@router.post("/items/{product_id}/decrement", response_model=CartItemResponse)
async def decrement_cart_item(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Decrement cart item quantity by 1"""
    try:
        cart_service = CartService(db)
        cart_item = await cart_service.decrement_item_quantity(
            user_id=current_user.id,
            product_id=product_id
        )
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )
        return cart_item
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to decrement cart item"
        )