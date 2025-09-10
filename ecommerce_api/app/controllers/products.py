from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
    ProductSearchQuery,
    ProductSearchResponse,
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse
)
from app.schemas.common import MessageResponse, PaginationParams
from app.services.product import ProductService
from app.core.security import get_current_user, require_admin_or_seller
from app.models.user import User


router = APIRouter()


# Product endpoints
@router.get("/", response_model=ProductSearchResponse)
async def search_products(
    q: Optional[str] = Query(None, description="Search query"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    is_featured: Optional[bool] = Query(None, description="Filter featured products"),
    is_active: Optional[bool] = Query(True, description="Filter active products"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Search and filter products"""
    try:
        search_query = ProductSearchQuery(
            q=q,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            is_featured=is_featured,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            limit=limit
        )
        
        product_service = ProductService(db)
        results = await product_service.search_products(search_query)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search products"
        )


@router.get("/featured", response_model=List[ProductListResponse])
async def get_featured_products(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get featured products"""
    try:
        product_service = ProductService(db)
        products = await product_service.get_featured_products(limit=limit)
        return products
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch featured products"
        )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get product by ID"""
    try:
        product_service = ProductService(db)
        product = await product_service.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch product"
        )


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(require_admin_or_seller),
    db: Session = Depends(get_db)
):
    """Create a new product (Admin/Seller only)"""
    try:
        product_service = ProductService(db)
        product = await product_service.create_product(product_data, created_by=current_user.id)
        return product
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product"
        )


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(require_admin_or_seller),
    db: Session = Depends(get_db)
):
    """Update product (Admin/Seller only)"""
    try:
        product_service = ProductService(db)
        product = await product_service.update_product(
            product_id=product_id,
            product_data=product_data,
            updated_by=current_user.id
        )
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product
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
            detail="Failed to update product"
        )


@router.delete("/{product_id}", response_model=MessageResponse)
async def delete_product(
    product_id: int,
    current_user: User = Depends(require_admin_or_seller),
    db: Session = Depends(get_db)
):
    """Delete product (Admin/Seller only)"""
    try:
        product_service = ProductService(db)
        success = await product_service.delete_product(product_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return MessageResponse(message="Product deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product"
        )


# Category endpoints
@router.get("/categories/", response_model=List[CategoryResponse])
async def get_categories(
    parent_id: Optional[int] = Query(None, description="Filter by parent category"),
    db: Session = Depends(get_db)
):
    """Get product categories"""
    try:
        product_service = ProductService(db)
        categories = await product_service.get_categories(parent_id=parent_id)
        return categories
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch categories"
        )


@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Get category by ID"""
    try:
        product_service = ProductService(db)
        category = await product_service.get_category_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        return category
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch category"
        )


@router.post("/categories/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(require_admin_or_seller),
    db: Session = Depends(get_db)
):
    """Create a new category (Admin/Seller only)"""
    try:
        product_service = ProductService(db)
        category = await product_service.create_category(category_data)
        return category
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create category"
        )


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(require_admin_or_seller),
    db: Session = Depends(get_db)
):
    """Update category (Admin/Seller only)"""
    try:
        product_service = ProductService(db)
        category = await product_service.update_category(category_id, category_data)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        return category
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
            detail="Failed to update category"
        )


@router.delete("/categories/{category_id}", response_model=MessageResponse)
async def delete_category(
    category_id: int,
    current_user: User = Depends(require_admin_or_seller),
    db: Session = Depends(get_db)
):
    """Delete category (Admin/Seller only)"""
    try:
        product_service = ProductService(db)
        success = await product_service.delete_category(category_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        return MessageResponse(message="Category deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete category"
        )